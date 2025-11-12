"""
Bookings controller - Booking and scheduling routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from src.data_access.booking_dal import BookingDAL
from src.data_access.resource_dal import ResourceDAL
from src.data_access.waitlist_dal import WaitlistDAL
from src.data_access.message_dal import MessageDAL
from src.models.models import db


def send_booking_notification(booking, notification_type='approved'):
    """
    Send automated message notification for booking status changes
    
    Args:
        booking: Booking object
        notification_type: Type of notification ('approved', 'rejected', 'cancelled', 'created')
    """
    try:
        resource = ResourceDAL.get_by_id(booking.resource_id)
        if not resource:
            return
        
        # Determine sender (resource owner or system)
        sender_id = resource.owner_id
        
        # Determine receiver (booking requester)
        receiver_id = booking.requester_id
        
        # Don't send message if requester is the owner
        if sender_id == receiver_id:
            return
        
        # Create message content based on notification type
        if notification_type == 'approved':
            content = (
                f"✅ Your booking request for '{resource.title}' has been approved!\n\n"
                f"📅 Date: {booking.start_datetime.strftime('%B %d, %Y')}\n"
                f"⏰ Time: {booking.start_datetime.strftime('%I:%M %p')} - {booking.end_datetime.strftime('%I:%M %p')}\n"
                f"📍 Location: {resource.location or 'See resource details'}\n\n"
                f"Your booking is confirmed. We look forward to seeing you!"
            )
        elif notification_type == 'rejected':
            content = (
                f"❌ Your booking request for '{resource.title}' has been rejected.\n\n"
                f"📅 Requested: {booking.start_datetime.strftime('%B %d, %Y')} "
                f"{booking.start_datetime.strftime('%I:%M %p')} - {booking.end_datetime.strftime('%I:%M %p')}\n\n"
                f"Please try selecting a different time slot or contact the resource owner for more information."
            )
        elif notification_type == 'cancelled':
            content = (
                f"ℹ️ Your booking for '{resource.title}' has been cancelled.\n\n"
                f"📅 Was scheduled for: {booking.start_datetime.strftime('%B %d, %Y')} "
                f"{booking.start_datetime.strftime('%I:%M %p')} - {booking.end_datetime.strftime('%I:%M %p')}\n\n"
                f"If you need to book this resource again, please visit the resource page."
            )
        elif notification_type == 'created':
            # Only send if automatically approved
            if booking.status == 'approved':
                content = (
                    f"✅ Your booking for '{resource.title}' has been confirmed!\n\n"
                    f"📅 Date: {booking.start_datetime.strftime('%B %d, %Y')}\n"
                    f"⏰ Time: {booking.start_datetime.strftime('%I:%M %p')} - {booking.end_datetime.strftime('%I:%M %p')}\n"
                    f"📍 Location: {resource.location or 'See resource details'}\n\n"
                    f"Your booking is confirmed. We look forward to seeing you!"
                )
            else:
                content = (
                    f"📋 Your booking request for '{resource.title}' has been submitted.\n\n"
                    f"📅 Requested: {booking.start_datetime.strftime('%B %d, %Y')} "
                    f"{booking.start_datetime.strftime('%I:%M %p')} - {booking.end_datetime.strftime('%I:%M %p')}\n\n"
                    f"⏳ Status: Pending approval\n\n"
                    f"You will receive a notification once your request is reviewed."
                )
        else:
            return
        
        # Send the message
        MessageDAL.create(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content
        )
    except Exception as e:
        # Log error but don't fail the booking operation
        print(f"Error sending booking notification: {str(e)}")
        pass

bookings_bp = Blueprint('bookings', __name__)


@bookings_bp.route('/resources/<int:resource_id>/book', methods=['GET', 'POST'])
@login_required
def create(resource_id):
    """Create a booking for a resource"""
    resource = ResourceDAL.get_by_id(resource_id)
    if not resource or resource.status != 'published':
        flash('Resource not available for booking.', 'danger')
        return redirect(url_for('resources.index'))
    
    # Parse availability rules for display (exclude metadata)
    import json
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
    
    if request.method == 'POST':
        # Try to get datetime from hidden fields first (from time slot selection)
        start_datetime_str = request.form.get('start_datetime')
        end_datetime_str = request.form.get('end_datetime')
        
        if start_datetime_str and end_datetime_str:
            try:
                start_datetime = datetime.fromisoformat(start_datetime_str.replace('Z', '+00:00'))
                end_datetime = datetime.fromisoformat(end_datetime_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                # Fallback to old method
                start_date = request.form.get('start_date')
                start_time = request.form.get('start_time')
                end_date = request.form.get('end_date')
                end_time = request.form.get('end_time')
                
                if not all([start_date, start_time, end_date, end_time]):
                    flash('Please fill in all date and time fields.', 'danger')
                    return render_template('bookings/create.html', resource=resource, availability_rules_parsed=availability_rules_parsed)
                
                try:
                    start_datetime = datetime.strptime(f'{start_date} {start_time}', '%Y-%m-%d %H:%M')
                    end_datetime = datetime.strptime(f'{end_date} {end_time}', '%Y-%m-%d %H:%M')
                except ValueError:
                    flash('Invalid date or time format.', 'danger')
                    return render_template('bookings/create.html', resource=resource, availability_rules_parsed=availability_rules_parsed)
        else:
            # Fallback to old method
            start_date = request.form.get('start_date')
            start_time = request.form.get('start_time')
            end_date = request.form.get('end_date')
            end_time = request.form.get('end_time')
            
            if not all([start_date, start_time, end_date, end_time]):
                flash('Please fill in all date and time fields.', 'danger')
                return render_template('bookings/create.html', resource=resource, availability_rules_parsed=availability_rules_parsed)
            
            try:
                start_datetime = datetime.strptime(f'{start_date} {start_time}', '%Y-%m-%d %H:%M')
                end_datetime = datetime.strptime(f'{end_date} {end_time}', '%Y-%m-%d %H:%M')
            except ValueError:
                flash('Invalid date or time format.', 'danger')
                return render_template('bookings/create.html', resource=resource, availability_rules_parsed=availability_rules_parsed)
        
        notes = request.form.get('notes', '').strip() or None
        
        # Validate dates
        if end_datetime <= start_datetime:
            flash('End time must be after start time.', 'danger')
            return render_template('bookings/create.html', resource=resource, availability_rules_parsed=availability_rules_parsed)
        
        # Check if booking time is in the past (allow 15 minute buffer for same-day bookings)
        now = datetime.now()
        # Allow bookings that start at least 15 minutes from now (for same-day bookings)
        if start_datetime <= now - timedelta(minutes=15):
            flash('Cannot book time slots in the past. Please select a time that starts at least 15 minutes from now.', 'danger')
            return render_template('bookings/create.html', resource=resource, availability_rules_parsed=availability_rules_parsed)
        
        # Check availability
        if not BookingDAL.check_availability(resource_id, start_datetime, end_datetime):
            # Offer to join waitlist
            flash('This time slot is not available. Would you like to join the waitlist?', 'warning')
            # Store the booking attempt in session or pass as query param
            return render_template('bookings/create.html', 
                                 resource=resource, 
                                 unavailable=True,
                                 requested_start=start_datetime,
                                 requested_end=end_datetime)
        
        # Determine booking status based on resource owner, user role, and requires_approval flag
        # If resource owner, always approved
        if resource.owner_id == current_user.user_id:
            status = 'approved'
        # If resource requires approval, all bookings go to pending (except owner)
        elif resource.requires_approval:
            status = 'pending'
        # If resource doesn't require approval and slot is available, auto-approve
        # (We already checked availability above, so if we get here, slot is available)
        else:
            # Auto-approve for all users (staff, admin, students) when resource doesn't require approval
            status = 'approved'
        
        try:
            booking = BookingDAL.create(
                resource_id=resource_id,
                requester_id=current_user.user_id,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                status=status
            )
            
            if status == 'approved':
                flash('Booking confirmed!', 'success')
                # Send approval notification
                send_booking_notification(booking, 'created')
            else:
                flash('Booking request submitted. Waiting for approval.', 'info')
                # Send pending notification
                send_booking_notification(booking, 'created')
            
            return redirect(url_for('bookings.detail', booking_id=booking.booking_id))
        except Exception as e:
            flash(f'Error creating booking: {str(e)}', 'danger')
            db.session.rollback()
    
    return render_template('bookings/create.html', resource=resource, availability_rules_parsed=availability_rules_parsed)


@bookings_bp.route('/bookings/<int:booking_id>')
@login_required
def detail(booking_id):
    """View booking details"""
    from src.models.models import AdminLog
    
    booking = BookingDAL.get_by_id(booking_id)
    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Check access (requester, resource owner, or admin)
    if (booking.requester_id != current_user.user_id and 
        booking.resource.owner_id != current_user.user_id and 
        current_user.role != 'admin'):
        flash('You do not have permission to view this booking.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Check if booking has ended (for review button)
    from datetime import datetime as dt
    booking_has_ended = booking.end_datetime < dt.now()
    
    # Check if user has already reviewed this resource
    existing_review = None
    if booking.resource and booking_has_ended:
        from src.data_access.review_dal import ReviewDAL
        existing_review = ReviewDAL.get_by_resource_and_user(booking.resource_id, current_user.user_id)
    
    # Get approval notes from admin_logs if booking is approved
    approval_notes = None
    if booking.status == 'approved':
        try:
            approval_log = AdminLog.query.filter_by(
                action='approve_booking',
                target_table='bookings'
            ).filter(
                AdminLog.details.like(f'%Approved booking {booking_id}%')
            ).order_by(AdminLog.timestamp.desc()).first()
            
            if approval_log and approval_log.details:
                # Extract notes from log details
                details = approval_log.details
                if 'Approval Notes:' in details:
                    notes_part = details.split('Approval Notes:')[1].strip()
                    approval_notes = {
                        'notes': notes_part,
                        'approved_by': approval_log.admin.name if approval_log.admin else f'User #{approval_log.admin_id}',
                        'approved_at': approval_log.timestamp
                    }
        except Exception as e:
            # If there's an error fetching notes, just continue without them
            print(f"Error fetching approval notes: {e}")
    
    return render_template('bookings/detail.html', booking=booking, approval_notes=approval_notes, 
                         booking_has_ended=booking_has_ended, existing_review=existing_review)


@bookings_bp.route('/bookings/<int:booking_id>/approve', methods=['POST'])
@login_required
def approve(booking_id):
    """Approve a booking (resource owner or admin only)"""
    from src.models.models import AdminLog
    
    booking = BookingDAL.get_by_id(booking_id)
    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Check permission
    if (booking.resource.owner_id != current_user.user_id and current_user.role != 'admin'):
        flash('You do not have permission to approve this booking.', 'danger')
        return redirect(url_for('bookings.detail', booking_id=booking_id))
    
    if booking.status != 'pending':
        flash('This booking cannot be approved.', 'danger')
        return redirect(url_for('bookings.detail', booking_id=booking_id))
    
    # Get approval notes from form
    approval_notes = request.form.get('approval_notes', '').strip()
    
    try:
        BookingDAL.update(booking_id, status='approved')
        
        # Store approval notes in admin_logs
        if approval_notes or current_user.role in ['staff', 'admin']:
            log_details = f"Approved booking {booking_id} for resource '{booking.resource.title if booking.resource else 'N/A'}'"
            if approval_notes:
                log_details += f"\n\nApproval Notes: {approval_notes}"
            
            try:
                admin_log = AdminLog(
                    admin_id=current_user.user_id,
                    action='approve_booking',
                    target_table='bookings',
                    details=log_details
                )
                db.session.add(admin_log)
                db.session.commit()
            except Exception as log_error:
                # Don't fail the approval if logging fails
                db.session.rollback()
                print(f"Error logging approval: {log_error}")
        
        flash('Booking approved!', 'success')
        
        # Send approval notification to requester
        booking = BookingDAL.get_by_id(booking_id)  # Refresh booking object
        send_booking_notification(booking, 'approved')
    except Exception as e:
        flash(f'Error approving booking: {str(e)}', 'danger')
        db.session.rollback()
    
    return redirect(url_for('bookings.detail', booking_id=booking_id))


@bookings_bp.route('/bookings/<int:booking_id>/reject', methods=['POST'])
@login_required
def reject(booking_id):
    """Reject a booking (resource owner or admin only)"""
    from src.models.models import AdminLog
    
    booking = BookingDAL.get_by_id(booking_id)
    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Check permission
    if (booking.resource.owner_id != current_user.user_id and current_user.role != 'admin'):
        flash('You do not have permission to reject this booking.', 'danger')
        return redirect(url_for('bookings.detail', booking_id=booking_id))
    
    if booking.status != 'pending':
        flash('This booking cannot be rejected.', 'danger')
        return redirect(url_for('bookings.detail', booking_id=booking_id))
    
    # Get rejection notes from form
    rejection_notes = request.form.get('rejection_notes', '').strip()
    
    try:
        BookingDAL.update(booking_id, status='rejected')
        
        # Store rejection notes in admin_logs
        log_details = f"Rejected booking {booking_id} for resource '{booking.resource.title if booking.resource else 'N/A'}'"
        if rejection_notes:
            log_details += f"\n\nRejection Notes: {rejection_notes}"
        
        try:
            admin_log = AdminLog(
                admin_id=current_user.user_id,
                action='reject_booking',
                target_table='bookings',
                details=log_details
            )
            db.session.add(admin_log)
            db.session.commit()
        except Exception as log_error:
            # Don't fail the rejection if logging fails
            db.session.rollback()
            print(f"Error logging rejection: {log_error}")
        
        flash('Booking rejected.', 'info')
        
        # Send rejection notification to requester
        booking = BookingDAL.get_by_id(booking_id)  # Refresh booking object
        send_booking_notification(booking, 'rejected')
    except Exception as e:
        flash(f'Error rejecting booking: {str(e)}', 'danger')
        db.session.rollback()
    
    return redirect(url_for('bookings.detail', booking_id=booking_id))


@bookings_bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel(booking_id):
    """Cancel a booking (requester only) and notify waitlist"""
    booking = BookingDAL.get_by_id(booking_id)
    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if booking.requester_id != current_user.user_id:
        flash('You can only cancel your own bookings.', 'danger')
        return redirect(url_for('bookings.detail', booking_id=booking_id))
    
    if booking.status in ['cancelled', 'completed']:
        flash('This booking cannot be cancelled.', 'danger')
        return redirect(url_for('bookings.detail', booking_id=booking_id))
    
    try:
        # Store booking details before cancelling
        resource_id = booking.resource_id
        start_datetime = booking.start_datetime
        end_datetime = booking.end_datetime
        
        # Cancel the booking
        BookingDAL.update(booking_id, status='cancelled')
        flash('Booking cancelled.', 'info')
        
        # Check waitlist and notify next person
        next_in_queue = WaitlistDAL.get_next_in_queue(resource_id, start_datetime)
        if next_in_queue:
            # Notify the user
            WaitlistDAL.notify_user(next_in_queue.waitlist_id)
            
            # Send a message notification
            try:
                resource = ResourceDAL.get_by_id(resource_id)
                message_content = (
                    f"Good news! A spot has opened up for {resource.title} "
                    f"on {start_datetime.strftime('%B %d, %Y')} from "
                    f"{start_datetime.strftime('%I:%M %p')} to {end_datetime.strftime('%I:%M %p')}. "
                    f"Visit the resource page to book it now!"
                )
                MessageDAL.create(
                    sender_id=booking.resource.owner_id,
                    receiver_id=next_in_queue.user_id,
                    content=message_content
                )
            except Exception as e:
                # If message creation fails, continue anyway
                pass
            
            flash(f'Next person in waitlist has been notified.', 'success')
        
    except Exception as e:
        flash(f'Error cancelling booking: {str(e)}', 'danger')
    
    return redirect(url_for('bookings.detail', booking_id=booking_id))


@bookings_bp.route('/api/availability/<int:resource_id>')
def check_availability_api(resource_id):
    """API endpoint to check resource availability for a date range"""
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    if not start_date or not end_date:
        return jsonify({'error': 'Start and end dates required'}), 400
    
    try:
        start_datetime = datetime.fromisoformat(start_date)
        end_datetime = datetime.fromisoformat(end_date)
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    is_available = BookingDAL.check_availability(resource_id, start_datetime, end_datetime)
    
    return jsonify({
        'available': is_available,
        'resource_id': resource_id,
        'start': start_date,
        'end': end_date
    })


@bookings_bp.route('/api/time-slots/<int:resource_id>')
def get_time_slots_api(resource_id):
    """API endpoint to get available time slots for a specific date"""
    from datetime import timedelta
    import json
    
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'error': 'Date parameter required'}), 400
    
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    resource = ResourceDAL.get_by_id(resource_id)
    if not resource:
        return jsonify({'error': 'Resource not found'}), 404
    
    # Parse availability rules
    availability_rules = {}
    if resource.availability_rules:
        try:
            availability_rules = json.loads(resource.availability_rules)
            # Filter out metadata
            if isinstance(availability_rules, dict):
                availability_rules = {k: v for k, v in availability_rules.items() if k != '_metadata'}
        except json.JSONDecodeError:
            pass
    
    # Get day name (lowercase)
    day_name = selected_date.strftime('%A').lower()
    
    # Check if day has availability rules
    if availability_rules and len(availability_rules) > 0:
        if day_name not in availability_rules:
            # Day not in rules - return empty slots
            return jsonify({
                'date': date_str,
                'resource_id': resource_id,
                'all_slots': [],
                'available_slots': [],
                'day_available': False,
                'day_has_slots': False,
                'error': 'This day is not available for booking'
            })
        day_availability = availability_rules.get(day_name)
    else:
        # No rules - default availability
        day_availability = '9:00-17:00'
    
    # Parse time range (e.g., "8:00-22:00")
    if '-' in day_availability:
        start_str, end_str = day_availability.split('-')
        start_hour, start_min = map(int, start_str.split(':'))
        end_hour, end_min = map(int, end_str.split(':'))
        
        start_time = datetime.combine(selected_date, datetime.min.time().replace(hour=start_hour, minute=start_min))
        end_time = datetime.combine(selected_date, datetime.min.time().replace(hour=end_hour, minute=end_min))
    else:
        # Default to 9 AM - 5 PM if format is invalid
        start_time = datetime.combine(selected_date, datetime.min.time().replace(hour=9, minute=0))
        end_time = datetime.combine(selected_date, datetime.min.time().replace(hour=17, minute=0))
    
    # Generate 30-minute time slots
    time_slots = []
    current_time = start_time
    slot_duration = timedelta(minutes=30)
    now = datetime.now()
    
    while current_time + slot_duration <= end_time:
        slot_end = current_time + slot_duration
        
        # If this is today, only include slots that start in the future
        # Add a small buffer (15 minutes) to allow booking slots that start soon
        if selected_date == now.date():
            # Only show slots that start at least 15 minutes from now
            # This allows same-day bookings if the slot hasn't started yet
            # Skip slots that start before (now + 15 minutes)
            if current_time < now + timedelta(minutes=15):
                current_time += slot_duration
                continue
        
        time_slots.append({
            'start': current_time.strftime('%H:%M'),
            'end': slot_end.strftime('%H:%M'),
            'start_datetime': current_time.isoformat(),
            'end_datetime': slot_end.isoformat()
        })
        current_time += slot_duration
    
    # Get existing bookings for this date
    existing_bookings = BookingDAL.get_all(resource_id=resource_id, status=None)
    booked_slots = []
    for booking in existing_bookings:
        if booking.status in ['approved', 'pending']:
            booking_date = booking.start_datetime.date()
            if booking_date == selected_date:
                booked_slots.append({
                    'start': booking.start_datetime.strftime('%H:%M'),
                    'end': booking.end_datetime.strftime('%H:%M')
                })
    
    # Mark each slot as available or booked
    all_slots = []
    for slot in time_slots:
        slot_start = datetime.strptime(slot['start'], '%H:%M').time()
        slot_end = datetime.strptime(slot['end'], '%H:%M').time()
        
        is_available = True
        for booked in booked_slots:
            booked_start = datetime.strptime(booked['start'], '%H:%M').time()
            booked_end = datetime.strptime(booked['end'], '%H:%M').time()
            
            # Check for overlap
            if not (slot_end <= booked_start or slot_start >= booked_end):
                is_available = False
                break
        
        slot['available'] = is_available
        all_slots.append(slot)
    
    # Also return available_slots for backward compatibility
    available_slots = [slot for slot in all_slots if slot['available']]
    
    # Check if day is available (has rules) and if it has any available slots
    day_has_rules = False
    if availability_rules:
        # Filter out metadata
        if isinstance(availability_rules, dict):
            rules_filtered = {k: v for k, v in availability_rules.items() if k != '_metadata'}
            if rules_filtered:
                day_has_rules = day_name in rules_filtered
                if not day_has_rules:
                    # Day not in rules - not available
                    return jsonify({
                        'date': date_str,
                        'resource_id': resource_id,
                        'all_slots': [],
                        'available_slots': [],
                        'day_available': False,
                        'day_has_slots': False,
                        'error': 'This day is not available for booking'
                    })
    
    has_available_slots = len(available_slots) > 0
    
    return jsonify({
        'date': date_str,
        'resource_id': resource_id,
        'all_slots': all_slots,  # All slots with availability status
        'available_slots': available_slots,  # Only available slots (for backward compatibility)
        'day_available': day_has_rules or not availability_rules,  # Day is available if it has rules or no rules exist
        'day_has_slots': has_available_slots,  # Day has available slots
        'booked_slots': booked_slots
    })


@bookings_bp.route('/api/day-availability/<int:resource_id>')
def get_day_availability_api(resource_id):
    """API endpoint to get day availability for the next few weeks"""
    from datetime import timedelta, date
    import json
    
    resource = ResourceDAL.get_by_id(resource_id)
    if not resource:
        return jsonify({'error': 'Resource not found'}), 404
    
    # Parse availability rules
    availability_rules = {}
    if resource.availability_rules:
        try:
            availability_rules = json.loads(resource.availability_rules)
            # Filter out metadata
            if isinstance(availability_rules, dict):
                availability_rules = {k: v for k, v in availability_rules.items() if k != '_metadata'}
        except json.JSONDecodeError:
            pass
    
    # Get existing bookings
    existing_bookings = BookingDAL.get_all(resource_id=resource_id, status=None)
    approved_pending_bookings = [b for b in existing_bookings if b.status in ['approved', 'pending']]
    
    # Generate day availability for next 3 weeks (21 days)
    today = date.today()
    day_availability_map = {}
    
    for day_offset in range(21):
        check_date = today + timedelta(days=day_offset)
        day_name = check_date.strftime('%A').lower()
        date_str = check_date.strftime('%Y-%m-%d')
        
        # Check if day has availability rules
        if availability_rules and len(availability_rules) > 0:
            if day_name not in availability_rules:
                # Day not available
                day_availability_map[date_str] = {
                    'available': False,
                    'has_slots': False,
                    'status': 'unavailable'
                }
                continue
            day_availability = availability_rules.get(day_name)
        else:
            # No rules - always available
            day_availability = '9:00-17:00'
        
        # Parse time range
        if '-' in day_availability:
            start_str, end_str = day_availability.split('-')
            start_hour, start_min = map(int, start_str.split(':'))
            end_hour, end_min = map(int, end_str.split(':'))
            
            start_time = datetime.combine(check_date, datetime.min.time().replace(hour=start_hour, minute=start_min))
            end_time = datetime.combine(check_date, datetime.min.time().replace(hour=end_hour, minute=end_min))
            
            # Generate slots and check availability
            slot_duration = timedelta(minutes=30)
            current_time = start_time
            total_slots = 0
            available_slots = 0
            
            while current_time + slot_duration <= end_time:
                total_slots += 1
                slot_end = current_time + slot_duration
                
                # Check if this slot conflicts with any booking
                is_available = True
                for booking in approved_pending_bookings:
                    if (current_time < booking.end_datetime and slot_end > booking.start_datetime):
                        is_available = False
                        break
                
                if is_available:
                    available_slots += 1
                
                current_time += slot_duration
            
            day_availability_map[date_str] = {
                'available': True,
                'has_slots': available_slots > 0,
                'total_slots': total_slots,
                'available_slots': available_slots,
                'status': 'fully_booked' if available_slots == 0 else 'has_slots'
            }
        else:
            day_availability_map[date_str] = {
                'available': True,
                'has_slots': False,
                'status': 'unavailable'
            }
    
    return jsonify({
        'resource_id': resource_id,
        'day_availability': day_availability_map
    })


@bookings_bp.route('/resources/<int:resource_id>/waitlist', methods=['POST'])
@login_required
def join_waitlist(resource_id):
    """Join the waitlist for a resource"""
    resource = ResourceDAL.get_by_id(resource_id)
    if not resource or resource.status != 'published':
        flash('Resource not available.', 'danger')
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    # Get requested datetime from form
    requested_datetime_str = request.form.get('requested_datetime')
    if not requested_datetime_str:
        flash('Please specify when you want to book this resource.', 'danger')
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    try:
        requested_datetime = datetime.fromisoformat(requested_datetime_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        flash('Invalid date format.', 'danger')
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    # Check if user is already on waitlist
    existing = WaitlistDAL.get_by_resource_and_user(resource_id, current_user.user_id, status='active')
    if existing:
        flash('You are already on the waitlist for this resource.', 'info')
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    # Check if resource is actually unavailable (to prevent unnecessary waitlist entries)
    # Use a 30-minute slot for the check
    from datetime import timedelta
    requested_end = requested_datetime + timedelta(minutes=30)
    
    if BookingDAL.check_availability(resource_id, requested_datetime, requested_end):
        flash('This time slot is available! You can book it directly instead of joining the waitlist.', 'info')
        return redirect(url_for('bookings.create', resource_id=resource_id))
    
    try:
        waitlist_entry = WaitlistDAL.create(
            resource_id=resource_id,
            user_id=current_user.user_id,
            requested_datetime=requested_datetime
        )
        
        position = WaitlistDAL.get_position_in_queue(resource_id, current_user.user_id, requested_datetime)
        flash(f'You have been added to the waitlist (position #{position}). You will be notified when a spot opens up.', 'success')
    except Exception as e:
        flash(f'Error joining waitlist: {str(e)}', 'danger')
        db.session.rollback()
    
    return redirect(url_for('resources.detail', resource_id=resource_id))


@bookings_bp.route('/waitlist/<int:waitlist_id>/cancel', methods=['POST'])
@login_required
def leave_waitlist(waitlist_id):
    """Leave the waitlist"""
    waitlist_entry = WaitlistDAL.get_by_id(waitlist_id)
    if not waitlist_entry:
        flash('Waitlist entry not found.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if waitlist_entry.user_id != current_user.user_id:
        flash('You can only remove your own waitlist entries.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    try:
        WaitlistDAL.cancel(waitlist_id)
        flash('You have been removed from the waitlist.', 'info')
    except Exception as e:
        flash(f'Error removing from waitlist: {str(e)}', 'danger')
    
    return redirect(url_for('resources.detail', resource_id=waitlist_entry.resource_id))

