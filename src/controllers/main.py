"""
Main controller - Homepage and general routes
"""
from flask import Blueprint, render_template, request
from src.data_access.resource_dal import ResourceDAL
from src.data_access.review_dal import ReviewDAL

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Homepage with search and featured resources"""
    # Get search query and filters
    search_query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip() or None
    quick_filter = request.args.get('filter', '').strip() or None
    
    # Get featured/popular resources
    if search_query:
        resources = ResourceDAL.search(search_query, category=category, status='published', limit=12)
    else:
        resources = ResourceDAL.get_all(category=category, status='published', limit=12)
    
    # Apply quick filters
    if quick_filter == 'top_rated':
        # Sort by rating
        resources_with_ratings = []
        for r in resources:
            stats = ReviewDAL.get_resource_rating_stats(r.resource_id)
            avg_rating = stats.get('average_rating', 0)
            resources_with_ratings.append((r, avg_rating))
        resources_with_ratings.sort(key=lambda x: x[1], reverse=True)
        resources = [r[0] for r in resources_with_ratings if r[1] > 0]  # Only show rated resources
    elif quick_filter == 'available_today':
        # Filter by availability today (simplified - check if resource has no bookings today)
        from datetime import datetime, date
        from src.data_access.booking_dal import BookingDAL
        today = date.today()
        available_resources = []
        for r in resources:
            # Check if resource has any bookings today
            bookings_today = BookingDAL.get_all(resource_id=r.resource_id, status='approved', limit=100)
            has_booking_today = any(
                booking.start_datetime.date() == today or booking.end_datetime.date() == today
                for booking in bookings_today
            )
            if not has_booking_today:
                available_resources.append(r)
        resources = available_resources if available_resources else resources
    elif quick_filter == 'near_me':
        # Placeholder for "Near Me" - would require geolocation
        # For now, just show all resources (could be enhanced with location-based filtering)
        pass
    
    # Get categories for filter
    categories = ['Study Rooms', 'Equipment', 'Labs', 'Events', 'Tutoring']
    
    # Get ratings for each resource and parse images
    import json
    resources_with_stats = []
    for resource in resources:
        stats = ReviewDAL.get_resource_rating_stats(resource.resource_id)
        # Parse images
        images_parsed = []
        if resource.images:
            try:
                images_parsed = json.loads(resource.images)
                if not isinstance(images_parsed, list):
                    images_parsed = [images_parsed]
            except (json.JSONDecodeError, TypeError):
                images_parsed = [img.strip() for img in resource.images.split(',') if img.strip()]
        
        resources_with_stats.append({
            'resource': resource,
            'rating': stats.get('average_rating', 0),
            'review_count': stats.get('total_reviews', 0),
            'images_parsed': images_parsed
        })
    
    return render_template('index.html', 
                         resources_with_stats=resources_with_stats,
                         search_query=search_query, 
                         category=category, 
                         categories=categories,
                         quick_filter=quick_filter)


@main_bp.route('/search')
def search():
    """Advanced search page with date/time filtering"""
    from datetime import datetime, timedelta
    from src.data_access.booking_dal import BookingDAL
    
    search_query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip() or None
    location = request.args.get('location', '').strip() or None
    min_capacity = request.args.get('min_capacity')
    min_capacity = int(min_capacity) if min_capacity and min_capacity.isdigit() else None
    sort_by = request.args.get('sort', 'recent')  # recent, most_booked, top_rated
    
    # Get date/time filters
    date_filter = request.args.get('date', '').strip()
    time_filter = request.args.get('time', '').strip()
    filter_datetime = None
    date_only = False
    if date_filter and time_filter:
        try:
            filter_datetime = datetime.strptime(f'{date_filter} {time_filter}', '%Y-%m-%d %H:%M')
        except ValueError:
            pass
    elif date_filter:
        # If only date is provided, we'll use each resource's earliest available time for that day
        try:
            # Parse the date to get the day name
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            date_only = True
        except ValueError:
            pass
    
    # Perform search
    if search_query:
        resources = ResourceDAL.search(search_query, category=category, status='published', limit=50)
    else:
        resources = ResourceDAL.get_all(category=category, status='published', limit=50)
    
    # Filter by location if provided
    if location:
        resources = [r for r in resources if r.location and location.lower() in r.location.lower()]
    
    # Filter by capacity if provided
    if min_capacity:
        resources = [r for r in resources if r.capacity and r.capacity >= min_capacity]
    
    # Filter by date/time availability if provided
    if filter_datetime or date_only:
        available_resources = []
        for r in resources:
            try:
                # If only date provided, get the earliest available time for this resource on that day
                if date_only:
                    # Get the day name (e.g., "monday", "tuesday")
                    day_name = filter_date.strftime('%A').lower()
                    
                    # Parse resource's availability rules
                    import json
                    earliest_time = None
                    if r.availability_rules:
                        try:
                            availability_rules = json.loads(r.availability_rules) if isinstance(r.availability_rules, str) else r.availability_rules
                            if isinstance(availability_rules, dict):
                                availability_rules = {k: v for k, v in availability_rules.items() if k != '_metadata'}
                            
                            # Check if this day has availability rules
                            day_availability = availability_rules.get(day_name)
                            if day_availability and '-' in day_availability:
                                # Extract the start time (e.g., "07:00" from "07:00-12:00")
                                start_str = day_availability.split('-')[0].strip()
                                start_hour, start_min = map(int, start_str.split(':'))
                                earliest_time = datetime.combine(filter_date, datetime.min.time().replace(hour=start_hour, minute=start_min))
                        except (json.JSONDecodeError, ValueError, AttributeError, KeyError):
                            pass
                    
                    # If no rules for this day, resource is not available
                    if earliest_time is None:
                        continue  # Skip this resource
                    
                    # Use the earliest time for this resource
                    resource_filter_datetime = earliest_time
                else:
                    # Use the provided datetime
                    resource_filter_datetime = filter_datetime
                
                # Check availability for a 1-hour slot starting at the filter time
                end_datetime = resource_filter_datetime + timedelta(hours=1)
                is_available = BookingDAL.check_availability(r.resource_id, resource_filter_datetime, end_datetime)
                if is_available:
                    available_resources.append(r)
            except Exception as e:
                # If check fails due to error, exclude resource (fail closed)
                # This ensures resources with malformed availability rules don't show up incorrectly
                import traceback
                print(f"Availability check error for resource {r.resource_id} ({r.title}): {e}")
                print(traceback.format_exc())
                # Don't include resource if there's an error - be strict about filtering
        # Always filter to available resources only (even if empty)
        resources = available_resources
    
    # Sort results
    if sort_by == 'most_booked':
        # TODO: Sort by booking count (requires booking count calculation)
        pass
    elif sort_by == 'top_rated':
        # Sort by average rating
        resources_with_ratings = []
        for r in resources:
            stats = ReviewDAL.get_resource_rating_stats(r.resource_id)
            resources_with_ratings.append((r, stats.get('average_rating', 0)))
        resources_with_ratings.sort(key=lambda x: x[1], reverse=True)
        resources = [r[0] for r in resources_with_ratings]
    # 'recent' is default (already sorted by created_at desc in DAL)
    
    # Parse images for each resource (similar to resources index)
    from src.controllers.resources import parse_resource_images
    resources_with_images = []
    for resource in resources:
        images_parsed = parse_resource_images(resource)
        resources_with_images.append({
            'resource': resource,
            'images_parsed': images_parsed
        })
    
    categories = ['Study Rooms', 'Equipment', 'Labs', 'Events', 'Tutoring']
    
    return render_template('resources/search.html', resources=resources_with_images, search_query=search_query,
                         category=category, location=location, min_capacity=min_capacity, 
                         sort_by=sort_by, categories=categories,
                         date_filter=date_filter, time_filter=time_filter)

