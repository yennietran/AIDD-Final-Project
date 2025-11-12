"""
API Controller - RESTful API endpoints for Campus Resource Hub
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from src.data_access.user_dal import UserDAL
from src.data_access.resource_dal import ResourceDAL
from src.data_access.booking_dal import BookingDAL
from src.data_access.message_dal import MessageDAL
from src.data_access.review_dal import ReviewDAL
from src.data_access.admin_dal import AdminDAL
from src.models.models import db
from datetime import datetime
import json

api_bp = Blueprint('api', __name__, url_prefix='/api')


# ============================================================================
# Authentication Endpoints
# ============================================================================

@api_bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new user
    
    Request Body:
        {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
            "role": "student",
            "department": "Computer Science"
        }
    
    Response:
        201 Created:
        {
            "success": true,
            "message": "User created successfully",
            "user": {
                "user_id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "role": "student"
            }
        }
        
        400 Bad Request:
        {
            "success": false,
            "error": "Email already exists"
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    role = data.get('role', 'student').strip()
    department = data.get('department', '').strip() or None
    
    if not name or not email or not password:
        return jsonify({"success": False, "error": "Name, email, and password are required"}), 400
    
    if role not in ['student', 'staff', 'admin']:
        return jsonify({"success": False, "error": "Invalid role. Must be student, staff, or admin"}), 400
    
    # Check if email exists
    existing_user = UserDAL.get_by_email(email)
    if existing_user:
        return jsonify({"success": False, "error": "Email already exists"}), 400
    
    try:
        user = UserDAL.create(
            name=name,
            email=email,
            password=password,
            role=role,
            department=department
        )
        return jsonify({
            "success": True,
            "message": "User created successfully",
            "user": {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "department": user.department
            }
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/auth/login', methods=['POST'])
def login():
    """Login and obtain session
    
    Request Body:
        {
            "email": "john@example.com",
            "password": "password123"
        }
    
    Response:
        200 OK:
        {
            "success": true,
            "message": "Login successful",
            "user": {
                "user_id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "role": "student"
            }
        }
        
        401 Unauthorized:
        {
            "success": false,
            "error": "Invalid email or password"
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required"}), 400
    
    user = UserDAL.get_by_email(email)
    if not user or not UserDAL.verify_password(user, password):
        return jsonify({"success": False, "error": "Invalid email or password"}), 401
    
    # Note: In a real API, you'd return a JWT token here
    # For now, we rely on Flask-Login session management
    from flask_login import login_user
    login_user(user)
    
    return jsonify({
        "success": True,
        "message": "Login successful",
        "user": {
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "department": user.department
        }
    }), 200


# ============================================================================
# Resource Endpoints
# ============================================================================

@api_bp.route('/resources', methods=['GET'])
def list_resources():
    """List/search resources
    
    Query Parameters:
        - q: search query (optional)
        - category: filter by category (optional)
        - status: filter by status (optional, default: published)
        - owner_id: filter by owner (optional)
        - limit: max results (optional, default: 50)
    
    Response:
        200 OK:
        {
            "success": true,
            "count": 10,
            "resources": [
                {
                    "resource_id": 1,
                    "title": "Study Room 201",
                    "description": "Quiet study space",
                    "category": "Study Rooms",
                    "location": "Library 2F",
                    "capacity": 4,
                    "status": "published",
                    "owner_id": 1,
                    "created_at": "2024-01-01T00:00:00"
                }
            ]
        }
    """
    search_query = request.args.get('q', '').strip() or None
    category = request.args.get('category', '').strip() or None
    status = request.args.get('status', 'published')
    owner_id = request.args.get('owner_id')
    owner_id = int(owner_id) if owner_id and owner_id.isdigit() else None
    limit = int(request.args.get('limit', 50))
    
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
    
    resources_list = []
    for resource in resources:
        resource_dict = resource.to_dict()
        # Parse JSON fields
        if resource_dict.get('images'):
            try:
                resource_dict['images'] = json.loads(resource_dict['images'])
            except:
                resource_dict['images'] = []
        if resource_dict.get('availability_rules'):
            try:
                resource_dict['availability_rules'] = json.loads(resource_dict['availability_rules'])
            except:
                resource_dict['availability_rules'] = None
        resources_list.append(resource_dict)
    
    return jsonify({
        "success": True,
        "count": len(resources_list),
        "resources": resources_list
    }), 200


@api_bp.route('/resources/<int:resource_id>', methods=['GET'])
def get_resource(resource_id):
    """Get resource detail
    
    Response:
        200 OK:
        {
            "success": true,
            "resource": {
                "resource_id": 1,
                "title": "Study Room 201",
                "description": "Quiet study space",
                "category": "Study Rooms",
                "location": "Library 2F",
                "capacity": 4,
                "images": ["url1", "url2"],
                "availability_rules": {"monday": "9:00-17:00"},
                "status": "published",
                "owner_id": 1,
                "created_at": "2024-01-01T00:00:00"
            }
        }
        
        404 Not Found:
        {
            "success": false,
            "error": "Resource not found"
        }
    """
    resource = ResourceDAL.get_by_id(resource_id)
    if not resource:
        return jsonify({"success": False, "error": "Resource not found"}), 404
    
    # Check access permissions
    try:
        is_authenticated = current_user.is_authenticated
        user_id = current_user.user_id if is_authenticated else None
    except:
        is_authenticated = False
        user_id = None
    
    if resource.status != 'published' and (not is_authenticated or resource.owner_id != user_id):
        return jsonify({"success": False, "error": "Resource not found"}), 404
    
    resource_dict = resource.to_dict()
    # Parse JSON fields
    if resource_dict.get('images'):
        try:
            resource_dict['images'] = json.loads(resource_dict['images'])
        except:
            resource_dict['images'] = []
    if resource_dict.get('availability_rules'):
        try:
            resource_dict['availability_rules'] = json.loads(resource_dict['availability_rules'])
        except:
            resource_dict['availability_rules'] = None
    
    return jsonify({
        "success": True,
        "resource": resource_dict
    }), 200


@api_bp.route('/resources', methods=['POST'])
@login_required
def create_resource():
    """Create a resource (auth required)
    
    Request Body:
        {
            "title": "Study Room 201",
            "description": "Quiet study space",
            "category": "Study Rooms",
            "location": "Library 2F",
            "capacity": 4,
            "images": ["url1", "url2"],
            "availability_rules": {"monday": "9:00-17:00"},
            "status": "draft"
        }
    
    Response:
        201 Created:
        {
            "success": true,
            "message": "Resource created successfully",
            "resource": { ... }
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    title = data.get('title', '').strip()
    if not title:
        return jsonify({"success": False, "error": "Title is required"}), 400
    
    try:
        resource = ResourceDAL.create(
            owner_id=current_user.user_id,
            title=title,
            description=data.get('description', '').strip() or None,
            category=data.get('category', '').strip() or None,
            location=data.get('location', '').strip() or None,
            capacity=int(data.get('capacity')) if data.get('capacity') else None,
            images=data.get('images', []),
            availability_rules=data.get('availability_rules'),
            status=data.get('status', 'draft')
        )
        
        resource_dict = resource.to_dict()
        if resource_dict.get('images'):
            try:
                resource_dict['images'] = json.loads(resource_dict['images'])
            except:
                resource_dict['images'] = []
        
        return jsonify({
            "success": True,
            "message": "Resource created successfully",
            "resource": resource_dict
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/resources/<int:resource_id>', methods=['PUT'])
@login_required
def update_resource(resource_id):
    """Update a resource
    
    Request Body: (all fields optional except those being updated)
        {
            "title": "Updated Title",
            "description": "Updated description",
            "status": "published"
        }
    
    Response:
        200 OK:
        {
            "success": true,
            "message": "Resource updated successfully",
            "resource": { ... }
        }
        
        403 Forbidden:
        {
            "success": false,
            "error": "You do not have permission to update this resource"
        }
    """
    resource = ResourceDAL.get_by_id(resource_id)
    if not resource:
        return jsonify({"success": False, "error": "Resource not found"}), 404
    
    # Check ownership
    if resource.owner_id != current_user.user_id and current_user.role != 'admin':
        return jsonify({"success": False, "error": "You do not have permission to update this resource"}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    # Build update dict
    update_data = {}
    if 'title' in data:
        update_data['title'] = data['title'].strip()
    if 'description' in data:
        update_data['description'] = data['description'].strip() or None
    if 'category' in data:
        update_data['category'] = data['category'].strip() or None
    if 'location' in data:
        update_data['location'] = data['location'].strip() or None
    if 'capacity' in data:
        update_data['capacity'] = int(data['capacity']) if data['capacity'] else None
    if 'images' in data:
        update_data['images'] = data['images']
    if 'availability_rules' in data:
        update_data['availability_rules'] = data['availability_rules']
    if 'status' in data:
        update_data['status'] = data['status']
    
    try:
        updated = ResourceDAL.update(resource_id, **update_data)
        resource_dict = updated.to_dict()
        if resource_dict.get('images'):
            try:
                resource_dict['images'] = json.loads(resource_dict['images'])
            except:
                resource_dict['images'] = []
        
        return jsonify({
            "success": True,
            "message": "Resource updated successfully",
            "resource": resource_dict
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/resources/<int:resource_id>', methods=['DELETE'])
@login_required
def delete_resource(resource_id):
    """Delete a resource
    
    Response:
        200 OK:
        {
            "success": true,
            "message": "Resource deleted successfully"
        }
        
        403 Forbidden:
        {
            "success": false,
            "error": "You do not have permission to delete this resource"
        }
    """
    resource = ResourceDAL.get_by_id(resource_id)
    if not resource:
        return jsonify({"success": False, "error": "Resource not found"}), 404
    
    # Check ownership or admin
    if resource.owner_id != current_user.user_id and current_user.role != 'admin':
        return jsonify({"success": False, "error": "You do not have permission to delete this resource"}), 403
    
    try:
        ResourceDAL.delete(resource_id)
        return jsonify({
            "success": True,
            "message": "Resource deleted successfully"
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# Booking Endpoints
# ============================================================================

@api_bp.route('/bookings', methods=['POST'])
@login_required
def create_booking():
    """Request a booking
    
    Request Body:
        {
            "resource_id": 1,
            "start_datetime": "2024-12-15T10:00:00",
            "end_datetime": "2024-12-15T12:00:00"
        }
    
    Response:
        201 Created:
        {
            "success": true,
            "message": "Booking request created",
            "booking": {
                "booking_id": 1,
                "resource_id": 1,
                "requester_id": 2,
                "start_datetime": "2024-12-15T10:00:00",
                "end_datetime": "2024-12-15T12:00:00",
                "status": "pending"
            }
        }
        
        400 Bad Request:
        {
            "success": false,
            "error": "Time conflict detected"
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    resource_id = data.get('resource_id')
    start_datetime_str = data.get('start_datetime')
    end_datetime_str = data.get('end_datetime')
    
    if not resource_id or not start_datetime_str or not end_datetime_str:
        return jsonify({"success": False, "error": "resource_id, start_datetime, and end_datetime are required"}), 400
    
    try:
        start_datetime = datetime.fromisoformat(start_datetime_str.replace('Z', '+00:00'))
        end_datetime = datetime.fromisoformat(end_datetime_str.replace('Z', '+00:00'))
    except:
        return jsonify({"success": False, "error": "Invalid datetime format. Use ISO 8601 format"}), 400
    
    # Check for conflicts
    conflicts = BookingDAL.check_conflicts(resource_id, start_datetime, end_datetime)
    if conflicts:
        return jsonify({
            "success": False, 
            "error": "Time conflict detected. Resource is already booked for this time",
            "conflicts": [b.to_dict() for b in conflicts]
        }), 400
    
    # Determine status based on resource owner, user role, and requires_approval flag
    resource = ResourceDAL.get_by_id(resource_id)
    if not resource:
        return jsonify({"success": False, "error": "Resource not found"}), 404
    
    # If resource owner, always approved
    if resource.owner_id == current_user.user_id:
        status = 'approved'
    # If resource requires approval, all bookings go to pending (except owner)
    elif resource.requires_approval:
        status = 'pending'
    # If resource doesn't require approval and slot is available, auto-approve
    else:
        # Auto-approve for all users when resource doesn't require approval
        status = 'approved'
    
    try:
        booking = BookingDAL.create(
            resource_id=resource_id,
            requester_id=current_user.user_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            status=status
        )
        
        # Send notification (approved or pending)
        from src.controllers.bookings import send_booking_notification
        send_booking_notification(booking, 'created')
        
        return jsonify({
            "success": True,
            "message": "Booking request created",
            "booking": booking.to_dict()
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/bookings/<int:booking_id>', methods=['GET'])
@login_required
def get_booking(booking_id):
    """Get booking detail
    
    Response:
        200 OK:
        {
            "success": true,
            "booking": {
                "booking_id": 1,
                "resource_id": 1,
                "requester_id": 2,
                "start_datetime": "2024-12-15T10:00:00",
                "end_datetime": "2024-12-15T12:00:00",
                "status": "pending",
                "created_at": "2024-12-01T00:00:00"
            }
        }
    """
    booking = BookingDAL.get_by_id(booking_id)
    if not booking:
        return jsonify({"success": False, "error": "Booking not found"}), 404
    
    # Check access - requester, owner, or admin
    resource = ResourceDAL.get_by_id(booking.resource_id)
    if (booking.requester_id != current_user.user_id and 
        resource.owner_id != current_user.user_id and 
        current_user.role != 'admin'):
        return jsonify({"success": False, "error": "You do not have permission to view this booking"}), 403
    
    return jsonify({
        "success": True,
        "booking": booking.to_dict()
    }), 200


@api_bp.route('/bookings/<int:booking_id>/approve', methods=['PUT'])
@login_required
def approve_booking(booking_id):
    """Approve a booking (staff/admin or owner)
    
    Response:
        200 OK:
        {
            "success": true,
            "message": "Booking approved",
            "booking": { ... }
        }
        
        403 Forbidden:
        {
            "success": false,
            "error": "You do not have permission to approve this booking"
        }
    """
    booking = BookingDAL.get_by_id(booking_id)
    if not booking:
        return jsonify({"success": False, "error": "Booking not found"}), 404
    
    resource = ResourceDAL.get_by_id(booking.resource_id)
    if not resource:
        return jsonify({"success": False, "error": "Resource not found"}), 404
    
    # Check permissions
    if (resource.owner_id != current_user.user_id and 
        current_user.role not in ['staff', 'admin']):
        return jsonify({"success": False, "error": "You do not have permission to approve this booking"}), 403
    
    try:
        updated = BookingDAL.update(booking_id, status='approved')
        
        # Send approval notification
        from src.controllers.bookings import send_booking_notification
        send_booking_notification(updated, 'approved')
        
        return jsonify({
            "success": True,
            "message": "Booking approved",
            "booking": updated.to_dict()
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# Message Endpoints
# ============================================================================

@api_bp.route('/messages', methods=['POST'])
@login_required
def send_message():
    """Send a message
    
    Request Body:
        {
            "receiver_id": 2,
            "content": "Hello, I'm interested in your resource"
        }
    
    Response:
        201 Created:
        {
            "success": true,
            "message": "Message sent successfully",
            "message_data": {
                "message_id": 1,
                "sender_id": 1,
                "receiver_id": 2,
                "content": "Hello...",
                "timestamp": "2024-12-01T00:00:00"
            }
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    receiver_id = data.get('receiver_id')
    content = data.get('content', '').strip()
    
    if not receiver_id or not content:
        return jsonify({"success": False, "error": "receiver_id and content are required"}), 400
    
    if receiver_id == current_user.user_id:
        return jsonify({"success": False, "error": "Cannot send message to yourself"}), 400
    
    try:
        message = MessageDAL.create(
            sender_id=current_user.user_id,
            receiver_id=receiver_id,
            content=content
        )
        
        return jsonify({
            "success": True,
            "message": "Message sent successfully",
            "message_data": message.to_dict()
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# Review Endpoints
# ============================================================================

@api_bp.route('/reviews', methods=['POST'])
@login_required
def create_review():
    """Submit a review
    
    Request Body:
        {
            "resource_id": 1,
            "rating": 5,
            "comment": "Great resource!"
        }
    
    Response:
        201 Created:
        {
            "success": true,
            "message": "Review submitted successfully",
            "review": {
                "review_id": 1,
                "resource_id": 1,
                "reviewer_id": 2,
                "rating": 5,
                "comment": "Great resource!",
                "timestamp": "2024-12-01T00:00:00"
            }
        }
        
        400 Bad Request:
        {
            "success": false,
            "error": "You can only review resources you have booked and completed"
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    resource_id = data.get('resource_id')
    rating = data.get('rating')
    comment = data.get('comment', '').strip() or None
    
    if not resource_id or not rating:
        return jsonify({"success": False, "error": "resource_id and rating are required"}), 400
    
    if rating < 1 or rating > 5:
        return jsonify({"success": False, "error": "Rating must be between 1 and 5"}), 400
    
    # Check if user has completed a booking for this resource
    # First check if user has any approved bookings
    user_bookings = BookingDAL.get_by_resource_and_user(resource_id, current_user.user_id)
    completed_bookings = [b for b in user_bookings if b.status == 'completed']
    approved_bookings = [b for b in user_bookings if b.status == 'approved']
    
    # Allow review if user has completed booking OR has approved booking that has passed
    from datetime import datetime
    now = datetime.now()
    has_valid_booking = False
    
    if completed_bookings:
        has_valid_booking = True
    elif approved_bookings:
        # Check if any approved booking has ended
        for booking in approved_bookings:
            if booking.end_datetime < now:
                has_valid_booking = True
                break
    
    if not has_valid_booking:
        return jsonify({
            "success": False,
            "error": "You can only review resources you have booked and completed"
        }), 400
    
    # Check if user already reviewed
    existing_review = ReviewDAL.get_by_resource_and_user(resource_id, current_user.user_id)
    if existing_review:
        return jsonify({"success": False, "error": "You have already reviewed this resource"}), 400
    
    try:
        review = ReviewDAL.create(
            resource_id=resource_id,
            reviewer_id=current_user.user_id,
            rating=rating,
            comment=comment
        )
        
        return jsonify({
            "success": True,
            "message": "Review submitted successfully",
            "review": review.to_dict()
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# Admin Endpoints
# ============================================================================

@api_bp.route('/admin/stats', methods=['GET'])
@login_required
def get_admin_stats():
    """Get usage metrics (admin only)
    
    Response:
        200 OK:
        {
            "success": true,
            "stats": {
                "total_users": 150,
                "total_resources": 45,
                "total_bookings": 320,
                "pending_bookings": 12,
                "total_reviews": 89,
                "average_rating": 4.2
            }
        }
        
        403 Forbidden:
        {
            "success": false,
            "error": "Admin access required"
        }
    """
    if current_user.role != 'admin':
        return jsonify({"success": False, "error": "Admin access required"}), 403
    
    try:
        stats = AdminDAL.get_statistics()
        return jsonify({
            "success": True,
            "stats": stats
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

