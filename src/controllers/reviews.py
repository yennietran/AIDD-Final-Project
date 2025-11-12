"""
Reviews controller - Rating and review routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src.data_access.review_dal import ReviewDAL
from src.data_access.booking_dal import BookingDAL
from src.data_access.resource_dal import ResourceDAL
from src.models.models import db

reviews_bp = Blueprint('reviews', __name__)


@reviews_bp.route('/reviews/my-reviews')
@login_required
def my_reviews():
    """View current user's reviews and resources available to review"""
    from datetime import datetime
    from src.data_access.review_dal import ReviewDAL
    
    # Get all reviews written by the user
    reviews = ReviewDAL.get_by_reviewer(current_user.user_id)
    
    # Get resources the user can review (booked, used, but not reviewed yet)
    from src.models.models import Booking
    from sqlalchemy.orm import joinedload
    
    now = datetime.now()
    # Use eager loading to ensure resources are loaded
    user_bookings = db.session.query(Booking).options(
        joinedload(Booking.resource)
    ).filter_by(requester_id=current_user.user_id).order_by(Booking.start_datetime.desc()).all()
    
    # Get resources from bookings that have ended and are approved/completed
    resources_to_review = []
    reviewed_resource_ids = {review.resource_id for review in reviews}
    
    for booking in user_bookings:
        if (booking.status in ['approved', 'completed'] and 
            booking.end_datetime < now and 
            booking.resource and
            booking.resource_id not in reviewed_resource_ids):
            # Check if we already added this resource
            if not any(r.resource_id == booking.resource_id for r in resources_to_review):
                resources_to_review.append(booking.resource)
    
    return render_template('reviews/my_reviews.html', 
                         reviews=reviews, 
                         resources_to_review=resources_to_review)


@reviews_bp.route('/resources/<int:resource_id>/reviews')
def index(resource_id):
    """List all reviews for a resource"""
    resource = ResourceDAL.get_by_id(resource_id)
    if not resource:
        flash('Resource not found.', 'danger')
        return redirect(url_for('resources.index'))
    
    reviews = ReviewDAL.get_by_resource(resource_id)
    stats = ReviewDAL.get_resource_rating_stats(resource_id)
    
    return render_template('reviews/index.html', resource=resource, reviews=reviews, stats=stats)


@reviews_bp.route('/resources/<int:resource_id>/reviews/create', methods=['GET', 'POST'])
@login_required
def create(resource_id):
    """Create a review for a resource"""
    resource = ResourceDAL.get_by_id(resource_id)
    if not resource:
        flash('Resource not found.', 'danger')
        return redirect(url_for('resources.index'))
    
    # Check if user has bookings for this resource that have ended
    from datetime import datetime
    now = datetime.now()
    user_bookings = BookingDAL.get_all(requester_id=current_user.user_id, resource_id=resource_id, status=None)
    
    # Check if user has any approved/completed bookings that have ended
    has_valid_booking = False
    for booking in user_bookings:
        if booking.status in ['approved', 'completed'] and booking.end_datetime < now:
            has_valid_booking = True
            break
    
    if not has_valid_booking:
        flash('You can only review resources you have booked and used. The booking must be approved and the time slot must have ended.', 'danger')
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    # Check if user already reviewed this resource
    existing_reviews = ReviewDAL.get_by_resource(resource_id)
    if any(r.reviewer_id == current_user.user_id for r in existing_reviews):
        flash('You have already reviewed this resource.', 'info')
        return redirect(url_for('reviews.index', resource_id=resource_id))
    
    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment', '').strip() or None
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
        except (ValueError, TypeError):
            flash('Invalid rating. Please select a rating between 1 and 5.', 'danger')
            return render_template('reviews/create.html', resource=resource)
        
        try:
            review = ReviewDAL.create(
                resource_id=resource_id,
                reviewer_id=current_user.user_id,
                rating=rating,
                comment=comment
            )
            flash('Review submitted successfully!', 'success')
            return redirect(url_for('reviews.index', resource_id=resource_id))
        except Exception as e:
            flash(f'Error creating review: {str(e)}', 'danger')
            db.session.rollback()
    
    return render_template('reviews/create.html', resource=resource)


@reviews_bp.route('/reviews/<int:review_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(review_id):
    """Edit a review"""
    review = ReviewDAL.get_by_id(review_id)
    if not review:
        flash('Review not found.', 'danger')
        return redirect(url_for('resources.index'))
    
    if review.reviewer_id != current_user.user_id:
        flash('You can only edit your own reviews.', 'danger')
        return redirect(url_for('reviews.index', resource_id=review.resource_id))
    
    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment', '').strip() or None
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
        except (ValueError, TypeError):
            flash('Invalid rating.', 'danger')
            return render_template('reviews/edit.html', review=review)
        
        try:
            ReviewDAL.update(review_id, rating=rating, comment=comment)
            flash('Review updated successfully!', 'success')
            return redirect(url_for('reviews.index', resource_id=review.resource_id))
        except Exception as e:
            flash(f'Error updating review: {str(e)}', 'danger')
            db.session.rollback()
    
    return render_template('reviews/edit.html', review=review)


@reviews_bp.route('/reviews/<int:review_id>/delete', methods=['POST'])
@login_required
def delete(review_id):
    """Delete a review"""
    review = ReviewDAL.get_by_id(review_id)
    if not review:
        flash('Review not found.', 'danger')
        return redirect(url_for('resources.index'))
    
    if review.reviewer_id != current_user.user_id and current_user.role != 'admin':
        flash('You do not have permission to delete this review.', 'danger')
        return redirect(url_for('reviews.index', resource_id=review.resource_id))
    
    resource_id = review.resource_id
    try:
        ReviewDAL.delete(review_id)
        flash('Review deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting review: {str(e)}', 'danger')
    
    return redirect(url_for('reviews.index', resource_id=resource_id))


@reviews_bp.route('/reviews/<int:review_id>/flag', methods=['POST'])
@login_required
def flag_review(review_id):
    """
    Flag a review as inappropriate
    
    AI Contribution: This route was AI-suggested and implemented as part of the content
    moderation system. The duplicate flag checking logic was AI-generated with team review.
    """
    from src.models.models import ReviewFlag
    
    review = ReviewDAL.get_by_id(review_id)
    if not review:
        flash('Review not found.', 'danger')
        return redirect(url_for('resources.index'))
    
    reason = request.form.get('reason', '').strip() or None
    
    # Check if user already flagged this review
    existing_flag = ReviewFlag.query.filter_by(
        review_id=review_id,
        user_id=current_user.user_id
    ).first()
    
    if existing_flag:
        flash('You have already flagged this review.', 'info')
    else:
        try:
            flag = ReviewFlag(
                review_id=review_id,
                user_id=current_user.user_id,
                reason=reason
            )
            db.session.add(flag)
            db.session.commit()
            flash('Review flagged successfully. An admin will review it.', 'success')
        except Exception as e:
            flash(f'Error flagging review: {str(e)}', 'danger')
            db.session.rollback()
    
    return redirect(request.referrer or url_for('reviews.index', resource_id=review.resource_id))

