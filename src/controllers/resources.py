"""
Resources controller - CRUD operations for resources
"""
import os
import json
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_login.utils import _get_user
from src.data_access.resource_dal import ResourceDAL
from src.models.models import db

# Configure upload settings
UPLOAD_FOLDER = Path('src/static/uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Ensure upload directory exists
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_resource_images(resource):
    """Helper function to parse images from resource"""
    images_parsed = []
    if resource.images:
        try:
            images_parsed = json.loads(resource.images)
            
            # Recursively decode nested JSON strings (handle double/triple encoding)
            max_iterations = 5  # Prevent infinite loops
            iteration = 0
            while iteration < max_iterations:
                iteration += 1
                changed = False
                
                # If it's a string that looks like JSON, parse it
                if isinstance(images_parsed, str):
                    if images_parsed.strip().startswith('[') or images_parsed.strip().startswith('{'):
                        try:
                            images_parsed = json.loads(images_parsed)
                            changed = True
                        except (json.JSONDecodeError, TypeError):
                            break
                
                # If it's a list with one string element that looks like JSON, parse it
                if isinstance(images_parsed, list) and len(images_parsed) == 1:
                    if isinstance(images_parsed[0], str):
                        if images_parsed[0].strip().startswith('[') or images_parsed[0].strip().startswith('{'):
                            try:
                                images_parsed = json.loads(images_parsed[0])
                                changed = True
                            except (json.JSONDecodeError, TypeError):
                                break
                
                # If nothing changed, we're done
                if not changed:
                    break
            
            # Ensure it's a list
            if not isinstance(images_parsed, list):
                images_parsed = [images_parsed]
            
            # Filter out any None or empty values and ensure URLs are valid
            cleaned_images = []
            for img in images_parsed:
                if img and isinstance(img, str):
                    # Clean up the URL - remove any extra quotes or whitespace
                    img = img.strip().strip('"').strip("'")
                    # Only add if it's a valid URL (starts with http:// or https://) or is a relative path
                    if img.startswith('http://') or img.startswith('https://') or img.startswith('/'):
                        cleaned_images.append(img)
            images_parsed = cleaned_images
            
        except (json.JSONDecodeError, TypeError):
            # If not JSON, treat as comma-separated
            images_parsed = [img.strip() for img in resource.images.split(',') if img.strip()]
    
    return images_parsed

resources_bp = Blueprint('resources', __name__)


@resources_bp.route('/resources')
def index():
    """List all published resources with filtering"""
    from datetime import datetime, timedelta
    from src.data_access.booking_dal import BookingDAL
    from src.data_access.review_dal import ReviewDAL
    
    category = request.args.get('category', '').strip() or None
    status = request.args.get('status', 'published')
    search_query = request.args.get('q', '').strip()
    owner_id = request.args.get('owner')
    owner_id = int(owner_id) if owner_id and owner_id.isdigit() else None
    limit = int(request.args.get('limit', 50))
    
    # Get new filter parameters
    min_capacity = request.args.get('min_capacity')
    min_capacity = int(min_capacity) if min_capacity and min_capacity.isdigit() else None
    sort_by = request.args.get('sort', 'recent')  # recent, most_booked, top_rated
    
    # Get date/time filters
    date_filter = request.args.get('date', '').strip()
    time_filter = request.args.get('time', '').strip()
    filter_datetime = None
    if date_filter and time_filter:
        try:
            filter_datetime = datetime.strptime(f'{date_filter} {time_filter}', '%Y-%m-%d %H:%M')
        except ValueError:
            pass
    
    # Only show published to non-authenticated users
    try:
        is_authenticated = current_user.is_authenticated
    except:
        is_authenticated = False
    
    if not is_authenticated:
        status = 'published'
    
    # Perform search or get all
    if search_query:
        resources = ResourceDAL.search(search_term=search_query, category=category, status=status, limit=limit)
    else:
        resources = ResourceDAL.get_all(category=category, status=status, owner_id=owner_id, limit=limit)
    
    # Filter by capacity if provided
    if min_capacity:
        resources = [r for r in resources if r.capacity and r.capacity >= min_capacity]
    
    # Filter by date/time availability if provided
    if filter_datetime:
        # Check availability for each resource at the specified date/time
        # Use a 1-hour slot for the check
        end_datetime = filter_datetime + timedelta(hours=1)
        available_resources = []
        for r in resources:
            try:
                # Check if resource is available at the requested time
                is_available = BookingDAL.check_availability(r.resource_id, filter_datetime, end_datetime)
                if is_available:
                    available_resources.append(r)
            except Exception as e:
                # If check fails due to error, include resource anyway
                # This handles cases where availability rules might be malformed
                import traceback
                print(f"Availability check error for resource {r.resource_id} ({r.title}): {e}")
                print(traceback.format_exc())
                # Include resource if there's an error (fail open)
                available_resources.append(r)
        # Only filter if we found some available resources, otherwise show all
        if available_resources:
            resources = available_resources
    
    # Sort results
    if sort_by == 'most_booked':
        # Sort by booking count
        resources_with_counts = []
        for r in resources:
            bookings = BookingDAL.get_all(resource_id=r.resource_id, status=None)
            booking_count = len([b for b in bookings if b.status in ['approved', 'completed']])
            resources_with_counts.append((r, booking_count))
        resources_with_counts.sort(key=lambda x: x[1], reverse=True)
        resources = [r[0] for r in resources_with_counts]
    elif sort_by == 'top_rated':
        # Sort by average rating
        resources_with_ratings = []
        for r in resources:
            stats = ReviewDAL.get_resource_rating_stats(r.resource_id)
            resources_with_ratings.append((r, stats.get('average_rating', 0)))
        resources_with_ratings.sort(key=lambda x: x[1], reverse=True)
        resources = [r[0] for r in resources_with_ratings]
    # 'recent' is default (already sorted by created_at desc in DAL)
    
    # Parse images for each resource
    resources_with_images = []
    for resource in resources:
        images_parsed = parse_resource_images(resource)
        resources_with_images.append({
            'resource': resource,
            'images_parsed': images_parsed
        })
    
    return render_template('resources/index.html', resources=resources_with_images)


@resources_bp.route('/resources/<int:resource_id>')
def detail(resource_id):
    """Resource detail page"""
    resource = ResourceDAL.get_by_id(resource_id)
    if not resource:
        flash('Resource not found.', 'danger')
        return redirect(url_for('resources.index'))
    
    # Only show published resources to non-owners
    try:
        is_authenticated = current_user.is_authenticated
        user_id = current_user.user_id if is_authenticated else None
    except:
        is_authenticated = False
        user_id = None
    
    # Allow admins to view any resource (including drafts)
    is_admin = is_authenticated and current_user.role == 'admin'
    
    if resource.status != 'published' and (not is_authenticated or (resource.owner_id != user_id and not is_admin)):
        flash('Resource not found.', 'danger')
        return redirect(url_for('resources.index'))
    
    # Get existing bookings for this resource
    from src.data_access.booking_dal import BookingDAL
    from src.data_access.waitlist_dal import WaitlistDAL
    import json
    existing_bookings = BookingDAL.get_all(resource_id=resource.resource_id, status=None)
    # Filter to only show approved and pending bookings, and sort by date
    active_bookings = [b for b in existing_bookings if b.status in ['approved', 'pending']]
    active_bookings.sort(key=lambda x: x.start_datetime)
    
    # Get waitlist information for current user (if authenticated)
    user_waitlist_entry = None
    user_waitlist_position = 0
    if is_authenticated:
        try:
            user_waitlist_entry = WaitlistDAL.get_by_resource_and_user(
                resource.resource_id, 
                user_id, 
                status='active'
            )
            if user_waitlist_entry:
                user_waitlist_position = WaitlistDAL.get_position_in_queue(
                    resource.resource_id, 
                    user_id,
                    user_waitlist_entry.requested_datetime
                )
        except:
            pass
    
    # Get total active waitlist count for this resource
    waitlist_count = len(WaitlistDAL.get_all(resource_id=resource.resource_id, status='active'))
    
    # Calculate available slots for today and next 7 days
    from datetime import datetime, timedelta, date
    today = date.today()
    availability_summary = []
    
    # Parse availability rules once (exclude metadata)
    availability_rules = {}
    if resource.availability_rules:
        try:
            # Handle both dict and JSON string
            if isinstance(resource.availability_rules, dict):
                rules_dict = resource.availability_rules
            else:
                rules_dict = json.loads(resource.availability_rules)
            
            # Ensure it's a dict and filter out metadata
            if isinstance(rules_dict, dict):
                availability_rules = {k: v for k, v in rules_dict.items() if k != '_metadata'}
            else:
                availability_rules = {}
        except (json.JSONDecodeError, TypeError, AttributeError):
            availability_rules = {}
    
    for day_offset in range(7):  # Check next 7 days
        check_date = today + timedelta(days=day_offset)
        day_name = check_date.strftime('%A').lower()
        
        # Get availability rules for this day - only process if rules exist for this day
        # Ensure availability_rules is a dict before calling .get()
        if not isinstance(availability_rules, dict):
            availability_rules = {}
        day_availability = availability_rules.get(day_name)
        
        # If no rules for this day, skip it (don't add to summary)
        if not day_availability:
            continue
        
        # Parse time range
        if '-' in day_availability:
            start_str, end_str = day_availability.split('-')
            try:
                start_hour, start_min = map(int, start_str.split(':'))
                end_hour, end_min = map(int, end_str.split(':'))
                
                start_time = datetime.combine(check_date, datetime.min.time().replace(hour=start_hour, minute=start_min))
                end_time = datetime.combine(check_date, datetime.min.time().replace(hour=end_hour, minute=end_min))
                
                # Generate 30-minute slots
                slot_duration = timedelta(minutes=30)
                total_slots = 0
                available_slots = 0
                current_time = start_time
                
                while current_time + slot_duration <= end_time:
                    total_slots += 1
                    slot_end = current_time + slot_duration
                    # Check if this slot is available
                    if BookingDAL.check_availability(resource.resource_id, current_time, slot_end):
                        available_slots += 1
                    current_time += slot_duration
                
                availability_summary.append({
                    'date': check_date,
                    'date_str': check_date.strftime('%Y-%m-%d'),
                    'day_name': check_date.strftime('%A'),
                    'total_slots': total_slots,
                    'available_slots': available_slots,
                    'booked_slots': total_slots - available_slots,
                    'not_available': False
                })
            except (ValueError, AttributeError):
                # If parsing fails, skip this day
                continue
        else:
            # Invalid format, skip this day
            continue
    
    # Parse availability rules for template (exclude metadata)
    availability_rules_parsed = None
    if resource.availability_rules:
        try:
            # Handle both dict and JSON string
            if isinstance(resource.availability_rules, dict):
                rules_dict = resource.availability_rules
            else:
                rules_dict = json.loads(resource.availability_rules)
            
            # Remove metadata from display
            if isinstance(rules_dict, dict):
                availability_rules_parsed = {k: v for k, v in rules_dict.items() if k != '_metadata'}
                # If only metadata exists, set to None
                if not availability_rules_parsed:
                    availability_rules_parsed = None
        except (json.JSONDecodeError, TypeError, AttributeError):
            availability_rules_parsed = None
    
    # Parse images for template
    images_parsed = parse_resource_images(resource)
    
    # Get reviews for this resource (only non-hidden, limit to 3 for preview)
    from src.data_access.review_dal import ReviewDAL
    # get_by_resource already filters out hidden reviews by default
    visible_reviews = ReviewDAL.get_by_resource(resource.resource_id, include_hidden=False)
    # Get first 3 reviews for preview
    preview_reviews = visible_reviews[:3]
    total_reviews_count = len(visible_reviews)
    
    # Get review stats for display
    review_stats = ReviewDAL.get_resource_rating_stats(resource.resource_id)
    
    # Check if user came from approvals page
    return_to = request.args.get('return_to', '')
    
    return render_template('resources/detail.html', 
                         resource=resource, 
                         bookings=active_bookings,
                         availability_rules_parsed=availability_rules_parsed,
                         images_parsed=images_parsed,
                         user_waitlist_entry=user_waitlist_entry,
                         user_waitlist_position=user_waitlist_position,
                         waitlist_count=waitlist_count,
                         availability_summary=availability_summary,
                         preview_reviews=preview_reviews,
                         total_reviews_count=total_reviews_count,
                         review_stats=review_stats,
                         return_to=return_to)


@resources_bp.route('/resources/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new resource"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip() or None
        category = request.form.get('category', '').strip() or None
        location = request.form.get('location', '').strip() or None
        capacity = request.form.get('capacity')
        capacity = int(capacity) if capacity and capacity.isdigit() else None
        
        # Validate required fields
        if not title:
            flash('Title is required.', 'danger')
            return render_template('resources/create.html')
        if not category:
            flash('Category is required.', 'danger')
            return render_template('resources/create.html')
        if not location:
            flash('Location is required.', 'danger')
            return render_template('resources/create.html')
        if not capacity or capacity < 1:
            flash('Capacity is required and must be at least 1.', 'danger')
            return render_template('resources/create.html')
        
        # Handle file uploads
        uploaded_files = request.files.getlist('image_files')
        images_list = []
        
        for file in uploaded_files:
            if file and file.filename and allowed_file(file.filename):
                # Check file size
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)
                
                if file_size > MAX_FILE_SIZE:
                    flash(f'File {file.filename} is too large. Maximum size is 5MB.', 'warning')
                    continue
                
                # Save file
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file_path = UPLOAD_FOLDER / filename
                file.save(str(file_path))
                
                # Add URL to images list
                images_list.append(f'/static/uploads/{filename}')
        
        # Also handle text input for image URLs
        images_text = request.form.get('images', '').strip()
        if images_text:
            images_list.extend([img.strip() for img in images_text.split(',') if img.strip()])
        
        images_list = images_list if images_list else None
        
        # Handle availability rules - convert from form fields to JSON
        availability_rules = {}
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in days:
            enabled = request.form.get(f'availability_{day}_enabled')
            start_time = request.form.get(f'availability_{day}_start', '').strip()
            end_time = request.form.get(f'availability_{day}_end', '').strip()
            if enabled and start_time and end_time:
                availability_rules[day] = f"{start_time}-{end_time}"
        
        # Validate that at least one day has availability schedule
        if not availability_rules:
            flash('At least one day must be selected with valid start and end times in the availability schedule.', 'danger')
            return render_template('resources/create.html')
        
        # Convert to JSON string if there are any rules, otherwise None
        # Handle requires_approval metadata
        requires_approval = request.form.get('requires_approval') == '1'
        
        # If we have availability rules, preserve them and add metadata
        if availability_rules:
            rules_dict = availability_rules
            if requires_approval:
                rules_dict['_metadata'] = {'requires_approval': True}
            availability_rules = json.dumps(rules_dict)
        elif requires_approval:
            # If no availability rules but requires_approval is set, create structure with just metadata
            availability_rules = json.dumps({'_metadata': {'requires_approval': True}})
        
        # Determine status based on user role
        # Students must have resources approved by admin (status='draft')
        # Staff and admins can publish directly
        if current_user.role == 'student':
            status = 'draft'  # Students' resources require approval
        else:
            # Staff and admins can choose status, default to 'published'
            status = request.form.get('status', 'published')
        
        if not title:
            flash('Title is required.', 'danger')
            return render_template('resources/create.html')
        
        try:
            resource = ResourceDAL.create(
                owner_id=current_user.user_id,
                title=title,
                description=description,
                category=category,
                location=location,
                capacity=capacity,
                images=images_list,
                availability_rules=availability_rules,
                status=status
            )
            
            # Different flash message based on status
            if status == 'draft':
                flash('Resource created successfully! It is pending admin approval and will be visible once approved.', 'success')
            else:
                flash('Resource created successfully!', 'success')
                # Send automated message to creator when resource is published
                try:
                    from src.data_access.message_dal import MessageDAL
                    # System sends message to the creator
                    # Use admin user as sender (or system user if available)
                    # For now, we'll use the current user as sender (self-message)
                    # In a real system, you might have a system user ID
                    message_content = (
                        f"✅ Your resource '{resource.title}' has been successfully published!\n\n"
                        f"📋 Resource Details:\n"
                        f"• Category: {resource.category or 'N/A'}\n"
                        f"• Location: {resource.location or 'N/A'}\n"
                        f"• Capacity: {resource.capacity or 'N/A'}\n\n"
                        f"Your resource is now visible to all users and available for booking."
                    )
                    MessageDAL.create(
                        sender_id=current_user.user_id,  # Self-message from creator
                        receiver_id=current_user.user_id,
                        content=message_content
                    )
                except Exception as msg_error:
                    # Don't fail resource creation if messaging fails
                    print(f"Error sending resource publication message: {msg_error}")
            
            return redirect(url_for('resources.detail', resource_id=resource.resource_id))
        except Exception as e:
            flash(f'Error creating resource: {str(e)}', 'danger')
            db.session.rollback()
    
    return render_template('resources/create.html')


@resources_bp.route('/resources/<int:resource_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(resource_id):
    """Edit a resource"""
    resource = ResourceDAL.get_by_id(resource_id)
    if not resource:
        flash('Resource not found.', 'danger')
        return redirect(url_for('resources.index'))
    
    # Check ownership
    if resource.owner_id != current_user.user_id and current_user.role != 'admin':
        flash('You do not have permission to edit this resource.', 'danger')
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip() or None
        category = request.form.get('category', '').strip() or None
        location = request.form.get('location', '').strip() or None
        capacity = request.form.get('capacity')
        capacity = int(capacity) if capacity and capacity.isdigit() else None
        
        # Get existing images
        existing_images = parse_resource_images(resource)
        images_list = list(existing_images) if existing_images else []
        
        # Handle file uploads
        uploaded_files = request.files.getlist('image_files')
        for file in uploaded_files:
            if file and file.filename and allowed_file(file.filename):
                # Check file size
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)
                
                if file_size > MAX_FILE_SIZE:
                    flash(f'File {file.filename} is too large. Maximum size is 5MB.', 'warning')
                    continue
                
                # Save file
                filename = secure_filename(file.filename)
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file_path = UPLOAD_FOLDER / filename
                file.save(str(file_path))
                
                # Add URL to images list
                images_list.append(f'/static/uploads/{filename}')
        
        # Also handle text input for image URLs
        images_text = request.form.get('images', '').strip()
        if images_text:
            # Replace existing images with new ones from text input
            text_images = [img.strip() for img in images_text.split(',') if img.strip()]
            # Only add new URLs that aren't already in the list
            for img_url in text_images:
                if img_url not in images_list:
                    images_list.append(img_url)
        
        images_list = images_list if images_list else None
        
        # Handle availability rules - convert from form fields to JSON
        # Only include days where checkbox is checked AND both times are provided
        availability_rules = {}
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in days:
            # Check if checkbox is checked (will be 'on' if checked, None if unchecked)
            enabled = request.form.get(f'availability_{day}_enabled')
            start_time = request.form.get(f'availability_{day}_start', '').strip()
            end_time = request.form.get(f'availability_{day}_end', '').strip()
            
            # Only add day if checkbox is checked AND both times are provided
            if enabled == 'on' and start_time and end_time:
                availability_rules[day] = f"{start_time}-{end_time}"
        
        # Handle requires_approval metadata - preserve existing metadata
        requires_approval = request.form.get('requires_approval') == '1'
        
        # Preserve existing metadata if it exists
        existing_metadata = {}
        if resource.availability_rules:
            try:
                existing_rules = json.loads(resource.availability_rules)
                if isinstance(existing_rules, dict) and '_metadata' in existing_rules:
                    existing_metadata = existing_rules['_metadata']
            except (json.JSONDecodeError, TypeError, AttributeError):
                pass
        
        # Add requires_approval to metadata
        if requires_approval:
            existing_metadata['requires_approval'] = True
        else:
            existing_metadata.pop('requires_approval', None)
        
        # Add metadata to availability_rules if we have metadata or rules
        if existing_metadata:
            availability_rules['_metadata'] = existing_metadata
        
        # Convert to JSON string - use empty dict if no rules to clear previously set rules
        # This ensures we clear out days that were previously enabled but are now unchecked
        availability_rules = json.dumps(availability_rules) if availability_rules else None
        
        # Determine status based on user role
        # Students cannot publish resources - they must remain 'draft' until admin approval
        # Staff and admins can change status
        if current_user.role == 'student':
            # Students' resources must remain as 'draft' until approved
            # If resource is already published (shouldn't happen, but just in case), keep it published
            status = resource.status if resource.status == 'published' else 'draft'
        else:
            # Staff and admins can change status
            status = request.form.get('status', resource.status or 'draft')
        
        if not title:
            flash('Title is required.', 'danger')
            images_parsed = parse_resource_images(resource)
            # Parse availability rules for template (exclude metadata)
            availability_rules_parsed = None
            if resource.availability_rules:
                try:
                    if isinstance(resource.availability_rules, dict):
                        rules_dict = resource.availability_rules
                    else:
                        rules_dict = json.loads(resource.availability_rules)
                    # Remove metadata from display
                    if isinstance(rules_dict, dict):
                        availability_rules_parsed = {k: v for k, v in rules_dict.items() if k != '_metadata'}
                        if not availability_rules_parsed:
                            availability_rules_parsed = None
                except (json.JSONDecodeError, TypeError, AttributeError):
                    availability_rules_parsed = None
            return render_template('resources/edit.html', 
                                 resource=resource, 
                                 images_parsed=images_parsed,
                                 availability_rules_parsed=availability_rules_parsed)
        
        try:
            updated = ResourceDAL.update(
                resource_id=resource_id,
                title=title,
                description=description,
                category=category,
                location=location,
                capacity=capacity,
                images=images_list,
                availability_rules=availability_rules,
                status=status
            )
            flash('Resource updated successfully!', 'success')
            return redirect(url_for('resources.detail', resource_id=resource_id))
        except Exception as e:
            flash(f'Error updating resource: {str(e)}', 'danger')
            db.session.rollback()
    
    # Parse images and availability rules for template (exclude metadata)
    images_parsed = parse_resource_images(resource)
    availability_rules_parsed = None
    if resource.availability_rules:
        try:
            if isinstance(resource.availability_rules, dict):
                rules_dict = resource.availability_rules
            else:
                rules_dict = json.loads(resource.availability_rules)
            # Remove metadata from display
            if isinstance(rules_dict, dict):
                availability_rules_parsed = {k: v for k, v in rules_dict.items() if k != '_metadata'}
                if not availability_rules_parsed:
                    availability_rules_parsed = None
        except (json.JSONDecodeError, TypeError, AttributeError):
            availability_rules_parsed = None
    
    return render_template('resources/edit.html', 
                         resource=resource, 
                         images_parsed=images_parsed,
                         availability_rules_parsed=availability_rules_parsed)


@resources_bp.route('/resources/<int:resource_id>/delete', methods=['POST'])
@login_required
def delete(resource_id):
    """Delete a resource"""
    resource = ResourceDAL.get_by_id(resource_id)
    if not resource:
        flash('Resource not found.', 'danger')
        return redirect(url_for('resources.index'))
    
    # Check ownership or admin
    if resource.owner_id != current_user.user_id and current_user.role != 'admin':
        flash('You do not have permission to delete this resource.', 'danger')
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    try:
        ResourceDAL.delete(resource_id)
        flash('Resource deleted successfully.', 'success')
        return redirect(url_for('resources.index'))
    except Exception as e:
        flash(f'Error deleting resource: {str(e)}', 'danger')
        return redirect(url_for('resources.detail', resource_id=resource_id))

