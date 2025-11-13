"""
Admin controller - Admin panel routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src.data_access.user_dal import UserDAL
from src.data_access.resource_dal import ResourceDAL
from src.data_access.booking_dal import BookingDAL
from src.data_access.review_dal import ReviewDAL
from src.models.models import db, AdminLog

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin role"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def log_admin_action(action: str, target_table: str, details: str = None):
    """Log an admin action"""
    try:
        log = AdminLog(
            admin_id=current_user.user_id,
            action=action,
            target_table=target_table,
            details=details
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()


@admin_bp.route('/admin')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    from src.data_access.role_change_request_dal import RoleChangeRequestDAL
    
    # Get statistics
    total_users = len(UserDAL.get_all())
    total_resources = len(ResourceDAL.get_all())
    total_bookings = len(BookingDAL.get_all())
    pending_bookings = len(BookingDAL.get_all(status='pending'))
    pending_resources = ResourceDAL.get_all(status='draft')
    pending_role_requests_count = len(RoleChangeRequestDAL.get_all(status='pending'))
    
    # Get recent activity
    recent_bookings = BookingDAL.get_all(limit=10)
    recent_resources = ResourceDAL.get_all(limit=10)
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_resources=total_resources,
                         total_bookings=total_bookings,
                         pending_bookings=pending_bookings,
                         pending_resources=pending_resources,
                         pending_role_requests_count=pending_role_requests_count,
                         recent_bookings=recent_bookings,
                         recent_resources=recent_resources)


@admin_bp.route('/admin/summary')
@login_required
@admin_required
def summary():
    """
    Generate and display AI-powered system summary
    
    AI Contribution: This route and the summary generation feature were AI-suggested
    and implemented. The LLM provider selection and fallback logic were AI-generated
    with team review and modification.
    """
    from src.utils.summary_generator import gather_statistics, generate_summary_with_llm
    
    # Get LLM provider from query params or use default
    llm_provider = request.args.get('provider', 'ollama')  # ollama, lm_studio, openai
    model = request.args.get('model', 'llama3.2')
    use_llm = request.args.get('use_llm', 'true').lower() == 'true'
    
    try:
        # Gather statistics
        stats = gather_statistics()
        
        # Generate summary
        if use_llm:
            try:
                summary_text = generate_summary_with_llm(stats, llm_provider=llm_provider, model=model)
                llm_used = True
                llm_error = None
            except Exception as e:
                # Fallback to non-LLM summary if LLM fails
                from src.utils.summary_generator import _generate_fallback_summary
                summary_text = _generate_fallback_summary(stats)
                llm_used = False
                llm_error = str(e)
        else:
            from src.utils.summary_generator import _generate_fallback_summary
            summary_text = _generate_fallback_summary(stats)
            llm_used = False
            llm_error = None
        
        return render_template('admin/summary.html',
                             summary=summary_text,
                             stats=stats,
                             llm_used=llm_used,
                             llm_error=llm_error,
                             llm_provider=llm_provider,
                             model=model,
                             use_llm=use_llm)
    except Exception as e:
        flash(f'Error generating summary: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/admin/users')
@login_required
@admin_required
def users():
    """Manage users"""
    role_filter = request.args.get('role')
    users_list = UserDAL.get_all(role=role_filter)
    
    return render_template('admin/users.html', users=users_list, role_filter=role_filter)


@admin_bp.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user"""
    user = UserDAL.get_by_id(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.users'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        role = request.form.get('role')
        department = request.form.get('department', '').strip() or None
        
        if not name or not email or role not in ['student', 'staff', 'admin']:
            flash('Invalid input.', 'danger')
            return render_template('admin/edit_user.html', user=user)
        
        try:
            UserDAL.update(user_id, name=name, email=email, role=role, department=department)
            log_admin_action('update_user', 'users', f'Updated user {user_id}')
            flash('User updated successfully.', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            flash(f'Error updating user: {str(e)}', 'danger')
            db.session.rollback()
    
    return render_template('admin/edit_user.html', user=user)


@admin_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user"""
    if user_id == current_user.user_id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    
    try:
        UserDAL.delete(user_id)
        log_admin_action('delete_user', 'users', f'Deleted user {user_id}')
        flash('User deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'danger')
    
    return redirect(url_for('admin.users'))


@admin_bp.route('/admin/resources')
@login_required
@admin_required
def resources():
    """Manage all resources"""
    status_filter = request.args.get('status')
    resources_list = ResourceDAL.get_all(status=status_filter)
    
    return render_template('admin/resources.html', resources=resources_list, status_filter=status_filter)


@admin_bp.route('/admin/bookings')
@login_required
@admin_required
def bookings():
    """Manage all bookings"""
    status_filter = request.args.get('status')
    bookings_list = BookingDAL.get_all(status=status_filter)
    
    return render_template('admin/bookings.html', bookings=bookings_list, status_filter=status_filter)


@admin_bp.route('/admin/approvals')
@login_required
@admin_required
def approvals():
    """Approvals queue - pending resources and bookings"""
    pending_resources = ResourceDAL.get_all(status='draft')
    pending_bookings = BookingDAL.get_all(status='pending')
    
    return render_template('admin/approvals.html', 
                         pending_resources=pending_resources,
                         pending_bookings=pending_bookings)


@admin_bp.route('/admin/resources/<int:resource_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_resource(resource_id):
    """Approve a resource"""
    try:
        ResourceDAL.update(resource_id, status='published')
        log_admin_action('approve_resource', 'resources', f'Approved resource {resource_id}')
        flash('Resource approved and published.', 'success')
    except Exception as e:
        flash(f'Error approving resource: {str(e)}', 'danger')
    
    return redirect(url_for('admin.approvals'))


@admin_bp.route('/admin/resources/<int:resource_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_resource(resource_id):
    """Reject a resource (archive it)"""
    try:
        ResourceDAL.update(resource_id, status='archived')
        log_admin_action('reject_resource', 'resources', f'Rejected resource {resource_id}')
        flash('Resource rejected and archived.', 'success')
    except Exception as e:
        flash(f'Error rejecting resource: {str(e)}', 'danger')
    
    return redirect(url_for('admin.approvals'))


@admin_bp.route('/admin/reviews')
@login_required
@admin_required
def reviews():
    """Moderate reviews - show flagged reviews first"""
    from src.models.models import Review, ReviewFlag
    from sqlalchemy import func
    
    # Get all reviews with flag counts
    reviews_list = db.session.query(
        Review,
        func.count(ReviewFlag.flag_id).label('flag_count')
    ).outerjoin(ReviewFlag, Review.review_id == ReviewFlag.review_id)\
     .group_by(Review.review_id)\
     .order_by(func.count(ReviewFlag.flag_id).desc(), Review.timestamp.desc()).all()
    
    # Separate flagged and non-flagged reviews
    flagged_reviews = [(r, count) for r, count in reviews_list if count > 0]
    other_reviews = [(r, count) for r, count in reviews_list if count == 0]
    
    return render_template('admin/reviews.html', 
                         flagged_reviews=flagged_reviews,
                         other_reviews=other_reviews)


@admin_bp.route('/admin/reviews/<int:review_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_review(review_id):
    """Delete a review (moderation)"""
    try:
        ReviewDAL.delete(review_id)
        log_admin_action('delete_review', 'reviews', f'Deleted review {review_id}')
        flash('Review deleted.', 'success')
    except Exception as e:
        flash(f'Error deleting review: {str(e)}', 'danger')
    
    return redirect(url_for('admin.reviews'))


@admin_bp.route('/admin/reviews/<int:review_id>/hide', methods=['POST'])
@login_required
@admin_required
def hide_review(review_id):
    """Hide a review (moderation)"""
    from src.models.models import Review
    try:
        review = Review.query.get(review_id)
        if review:
            review.is_hidden = True
            db.session.commit()
            log_admin_action('hide_review', 'reviews', f'Hid review {review_id}')
            flash('Review hidden.', 'success')
        else:
            flash('Review not found.', 'danger')
    except Exception as e:
        flash(f'Error hiding review: {str(e)}', 'danger')
        db.session.rollback()
    
    return redirect(url_for('admin.reviews'))


@admin_bp.route('/admin/reviews/<int:review_id>/ignore', methods=['POST'])
@login_required
@admin_required
def ignore_review_flags(review_id):
    """Ignore flags for a review (remove all flags)"""
    from src.models.models import ReviewFlag
    try:
        # Delete all flags for this review
        deleted_count = ReviewFlag.query.filter_by(review_id=review_id).delete()
        db.session.commit()
        log_admin_action('ignore_review_flags', 'reviews', f'Ignored flags for review {review_id} ({deleted_count} flags removed)')
        flash(f'Flags ignored. Removed {deleted_count} flag(s).', 'success')
    except Exception as e:
        flash(f'Error ignoring flags: {str(e)}', 'danger')
        db.session.rollback()
    
    return redirect(url_for('admin.reviews'))


@admin_bp.route('/admin/reviews/<int:review_id>/unhide', methods=['POST'])
@login_required
@admin_required
def unhide_review(review_id):
    """Unhide a review (moderation)"""
    from src.models.models import Review
    try:
        review = Review.query.get(review_id)
        if review:
            review.is_hidden = False
            db.session.commit()
            log_admin_action('unhide_review', 'reviews', f'Unhid review {review_id}')
            flash('Review unhidden.', 'success')
        else:
            flash('Review not found.', 'danger')
    except Exception as e:
        flash(f'Error unhiding review: {str(e)}', 'danger')
        db.session.rollback()
    
    return redirect(url_for('admin.reviews'))


@admin_bp.route('/admin/messages/reported')
@login_required
@admin_required
def reported_messages():
    """View reported messages"""
    from src.models.models import MessageReport, Message
    from sqlalchemy import func
    
    # Get all reported messages with report counts
    reported_messages_list = db.session.query(
        Message,
        func.count(MessageReport.report_id).label('report_count')
    ).join(MessageReport, Message.message_id == MessageReport.message_id)\
     .group_by(Message.message_id)\
     .order_by(func.count(MessageReport.report_id).desc(), Message.timestamp.desc()).all()
    
    return render_template('admin/reported_messages.html', 
                         reported_messages=reported_messages_list)


@admin_bp.route('/admin/messages/<int:message_id>/ignore', methods=['POST'])
@login_required
@admin_required
def ignore_message_reports(message_id):
    """Ignore reports for a message (remove all reports)"""
    from src.models.models import MessageReport
    try:
        # Delete all reports for this message
        deleted_count = MessageReport.query.filter_by(message_id=message_id).delete()
        db.session.commit()
        log_admin_action('ignore_message_reports', 'messages', f'Ignored reports for message {message_id} ({deleted_count} reports removed)')
        flash(f'Reports ignored. Removed {deleted_count} report(s).', 'success')
    except Exception as e:
        flash(f'Error ignoring reports: {str(e)}', 'danger')
        db.session.rollback()
    
    return redirect(url_for('admin.reported_messages'))


@admin_bp.route('/admin/messages/<int:message_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_message(message_id):
    """Delete a message (moderation)"""
    from src.data_access.message_dal import MessageDAL
    try:
        MessageDAL.delete(message_id)
        log_admin_action('delete_message', 'messages', f'Deleted message {message_id}')
        flash('Message deleted.', 'success')
    except Exception as e:
        flash(f'Error deleting message: {str(e)}', 'danger')
    
    return redirect(url_for('admin.reported_messages'))


@admin_bp.route('/admin/users/<int:user_id>/suspend', methods=['POST'])
@login_required
@admin_required
def suspend_user(user_id):
    """Suspend a user"""
    from src.models.models import User
    if user_id == current_user.user_id:
        flash('You cannot suspend your own account.', 'danger')
        return redirect(url_for('admin.users'))
    
    try:
        user = User.query.get(user_id)
        if user:
            # Add suspended status to user (we'll store it in a JSON field or add a column)
            # For now, we'll use a workaround: store in department field as JSON or add a status field
            # Since we can't modify DB schema, let's use a different approach
            # We'll add an 'is_suspended' property that checks a metadata field
            # Actually, let's just add a suspended field to the User model
            user.is_suspended = True
            db.session.commit()
            log_admin_action('suspend_user', 'users', f'Suspended user {user_id} ({user.email})')
            flash(f'User {user.name} has been suspended.', 'success')
        else:
            flash('User not found.', 'danger')
    except AttributeError:
        # If is_suspended doesn't exist, we need to add it to the model first
        flash('Suspension feature requires database update. Please add is_suspended column to users table.', 'warning')
    except Exception as e:
        flash(f'Error suspending user: {str(e)}', 'danger')
        db.session.rollback()
    
    return redirect(url_for('admin.users'))


@admin_bp.route('/admin/users/<int:user_id>/unsuspend', methods=['POST'])
@login_required
@admin_required
def unsuspend_user(user_id):
    """Unsuspend a user"""
    from src.models.models import User
    try:
        user = User.query.get(user_id)
        if user:
            user.is_suspended = False
            db.session.commit()
            log_admin_action('unsuspend_user', 'users', f'Unsuspended user {user_id} ({user.email})')
            flash(f'User {user.name} has been unsuspended.', 'success')
        else:
            flash('User not found.', 'danger')
    except AttributeError:
        flash('Suspension feature requires database update.', 'warning')
    except Exception as e:
        flash(f'Error unsuspending user: {str(e)}', 'danger')
        db.session.rollback()
    
    return redirect(url_for('admin.users'))


@admin_bp.route('/admin/role-change-requests')
@login_required
@admin_required
def role_change_requests():
    """View all role change requests"""
    from src.data_access.role_change_request_dal import RoleChangeRequestDAL
    
    status_filter = request.args.get('status', 'pending')
    all_requests = RoleChangeRequestDAL.get_all(status=status_filter if status_filter in ['pending', 'approved', 'denied'] else None)
    
    return render_template('admin/role_change_requests.html', 
                         requests=all_requests, 
                         status_filter=status_filter)


@admin_bp.route('/admin/role-change-requests/<int:request_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_role_change(request_id):
    """Approve a role change request"""
    from src.data_access.role_change_request_dal import RoleChangeRequestDAL
    
    admin_notes = request.form.get('admin_notes', '').strip() or None
    
    try:
        request_obj = RoleChangeRequestDAL.approve(request_id, current_user.user_id, admin_notes)
        if request_obj:
            log_admin_action('approve_role_change', 'role_change_requests', 
                           f'Approved role change request {request_id} for user {request_obj.user_id} to {request_obj.requested_role}')
            flash(f'Role change request approved. User is now a {request_obj.requested_role}.', 'success')
        else:
            flash('Role change request not found.', 'danger')
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash(f'Error approving request: {str(e)}', 'danger')
        db.session.rollback()
    
    return redirect(url_for('admin.role_change_requests'))


@admin_bp.route('/admin/role-change-requests/<int:request_id>/deny', methods=['POST'])
@login_required
@admin_required
def deny_role_change(request_id):
    """Deny a role change request"""
    from src.data_access.role_change_request_dal import RoleChangeRequestDAL
    
    admin_notes = request.form.get('admin_notes', '').strip() or None
    
    try:
        request_obj = RoleChangeRequestDAL.deny(request_id, current_user.user_id, admin_notes)
        if request_obj:
            log_admin_action('deny_role_change', 'role_change_requests', 
                           f'Denied role change request {request_id} for user {request_obj.user_id}')
            flash('Role change request denied.', 'success')
        else:
            flash('Role change request not found.', 'danger')
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash(f'Error denying request: {str(e)}', 'danger')
        db.session.rollback()
    
    return redirect(url_for('admin.role_change_requests'))

