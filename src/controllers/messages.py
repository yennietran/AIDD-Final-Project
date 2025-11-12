"""
Messages controller - User messaging routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from src.data_access.message_dal import MessageDAL
from src.data_access.user_dal import UserDAL
from src.models.models import db

messages_bp = Blueprint('messages', __name__)


@messages_bp.route('/messages')
@login_required
def index():
    """List all message threads for current user"""
    # Get all conversations
    sent_messages = MessageDAL.get_user_messages(current_user.user_id, sent=True)
    received_messages = MessageDAL.get_user_messages(current_user.user_id, sent=False)
    
    # Group by thread or other user
    threads = {}
    all_messages = sent_messages + received_messages
    
    for msg in all_messages:
        if msg.sender_id == current_user.user_id:
            other_user_id = msg.receiver_id
        else:
            other_user_id = msg.sender_id
        
        if other_user_id not in threads:
            other_user = UserDAL.get_by_id(other_user_id)
            if other_user:  # Only add if user exists
                threads[other_user_id] = {
                    'user': other_user,
                    'messages': [],
                    'unread_count': 0
                }
        
        if other_user_id in threads:
            threads[other_user_id]['messages'].append(msg)
            # Count unread messages (only messages received by current user that are not read)
            if msg.receiver_id == current_user.user_id and not msg.is_read:
                threads[other_user_id]['unread_count'] += 1
    
    # Sort threads by most recent message
    for thread_id in threads:
        threads[thread_id]['messages'].sort(key=lambda x: x.timestamp, reverse=True)
    
    from datetime import datetime as dt
    sorted_threads = sorted(threads.values(), 
                          key=lambda x: x['messages'][0].timestamp if x['messages'] else dt.min,
                          reverse=True)
    
    # Calculate total unread count
    total_unread = sum(thread['unread_count'] for thread in sorted_threads)
    
    return render_template('messages/index.html', threads=sorted_threads, total_unread=total_unread)


@messages_bp.route('/messages/<int:user_id>', methods=['GET', 'POST'])
@login_required
def conversation(user_id):
    """View and send messages in a conversation"""
    other_user = UserDAL.get_by_id(user_id)
    if not other_user:
        flash('User not found.', 'danger')
        return redirect(url_for('messages.index'))
    
    # Check if we should return to reported messages page
    return_to = request.args.get('return_to')
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if not content:
            flash('Message cannot be empty.', 'danger')
        else:
            try:
                # Get existing thread_id if conversation exists
                existing_messages = MessageDAL.get_conversation(current_user.user_id, user_id)
                thread_id = existing_messages[0].thread_id if existing_messages else None
                
                # If no thread exists, create new thread_id
                if not thread_id:
                    # Use the first message ID as thread_id (will be set after creation)
                    pass
                
                message = MessageDAL.create(
                    sender_id=current_user.user_id,
                    receiver_id=user_id,
                    content=content,
                    thread_id=thread_id
                )
                
                # Set thread_id to first message's ID if this is the first message
                if not thread_id:
                    message.thread_id = message.message_id
                    db.session.commit()
                
                flash('Message sent!', 'success')
                redirect_url = url_for('messages.conversation', user_id=user_id)
                if return_to:
                    redirect_url += f'?return_to={return_to}'
                return redirect(redirect_url)
            except Exception as e:
                flash(f'Error sending message: {str(e)}', 'danger')
                db.session.rollback()
    
    # Get conversation messages
    messages = MessageDAL.get_conversation(current_user.user_id, user_id)
    messages.sort(key=lambda x: x.timestamp)
    
    # Mark all unread messages in this conversation as read
    MessageDAL.mark_conversation_as_read(current_user.user_id, user_id, current_user.user_id)
    
    return render_template('messages/conversation.html', 
                         other_user=other_user, 
                         messages=messages,
                         return_to=return_to)


@messages_bp.route('/messages/new', methods=['GET', 'POST'])
@login_required
def new():
    """Start a new conversation - select user to message"""
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        if not user_id:
            flash('Please select a user to message.', 'danger')
            return redirect(url_for('messages.new'))
        
        try:
            user_id = int(user_id)
            # Redirect to conversation page
            return redirect(url_for('messages.conversation', user_id=user_id))
        except (ValueError, TypeError):
            flash('Invalid user selected.', 'danger')
            return redirect(url_for('messages.new'))
    
    # Get list of users to message
    # For admins: show all users (except themselves)
    # For others: show users they've interacted with (resource owners, booking requesters, etc.)
    if current_user.role == 'admin':
        all_users = UserDAL.get_all()
        # Filter out current user
        users = [u for u in all_users if u.user_id != current_user.user_id]
    else:
        # Get users from interactions (resource owners, booking requesters, etc.)
        from src.data_access.resource_dal import ResourceDAL
        from src.data_access.booking_dal import BookingDAL
        
        user_ids = set()
        
        # Get resource owners
        resources = ResourceDAL.get_all()
        for resource in resources:
            if resource.owner_id and resource.owner_id != current_user.user_id:
                user_ids.add(resource.owner_id)
        
        # Get booking requesters and resource owners from bookings
        bookings = BookingDAL.get_all()
        for booking in bookings:
            if booking.requester_id and booking.requester_id != current_user.user_id:
                user_ids.add(booking.requester_id)
            if booking.resource and booking.resource.owner_id and booking.resource.owner_id != current_user.user_id:
                user_ids.add(booking.resource.owner_id)
        
        # Get all users if admin, otherwise just the ones they've interacted with
        users = [UserDAL.get_by_id(uid) for uid in user_ids if UserDAL.get_by_id(uid)]
        users = [u for u in users if u]  # Remove None values
    
    return render_template('messages/new.html', users=users)


@messages_bp.route('/messages/<int:message_id>/report', methods=['POST'])
@login_required
def report_message(message_id):
    """
    Report a message as inappropriate
    
    AI Contribution: This route was AI-suggested and implemented as part of the content
    moderation system. The duplicate report checking logic was AI-generated with team review.
    """
    from src.models.models import MessageReport
    from src.data_access.message_dal import MessageDAL
    
    message = MessageDAL.get_by_id(message_id)
    if not message:
        flash('Message not found.', 'danger')
        return redirect(url_for('messages.index'))
    
    # Users can only report messages they received or sent
    if message.sender_id != current_user.user_id and message.receiver_id != current_user.user_id:
        flash('You can only report messages in your conversations.', 'danger')
        return redirect(url_for('messages.index'))
    
    reason = request.form.get('reason', '').strip() or None
    
    # Check if user already reported this message
    existing_report = MessageReport.query.filter_by(
        message_id=message_id,
        user_id=current_user.user_id
    ).first()
    
    if existing_report:
        flash('You have already reported this message.', 'info')
    else:
        try:
            report = MessageReport(
                message_id=message_id,
                user_id=current_user.user_id,
                reason=reason
            )
            db.session.add(report)
            db.session.commit()
            flash('Message reported successfully. An admin will review it.', 'success')
        except Exception as e:
            flash(f'Error reporting message: {str(e)}', 'danger')
            db.session.rollback()
    
    return redirect(request.referrer or url_for('messages.index'))


@messages_bp.route('/messages/send/<int:user_id>', methods=['POST'])
@login_required
def send(user_id):
    """Send a message (AJAX endpoint)"""
    content = request.json.get('content', '').strip() if request.is_json else request.form.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    try:
        message = MessageDAL.create(
            sender_id=current_user.user_id,
            receiver_id=user_id,
            content=content
        )
        return jsonify({
            'success': True,
            'message_id': message.message_id,
            'timestamp': message.timestamp.isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

