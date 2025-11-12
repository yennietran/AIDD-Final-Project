"""
Database models for Campus Resource Hub
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import json

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student', 'staff', 'admin'
    profile_image = db.Column(db.String(500), nullable=True)
    department = db.Column(db.String(255), nullable=True)
    is_suspended = db.Column(db.Boolean, default=False, nullable=False)  # Admin can suspend users
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Flask-Login requires get_id() method, which UserMixin provides
    # But we need to override it to use user_id instead of id
    def get_id(self):
        """Return the user_id as the unique identifier for Flask-Login"""
        return str(self.user_id)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'profile_image': self.profile_image,
            'department': self.department,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Resource(db.Model):
    """Resource model for campus resources (rooms, equipment, etc.)"""
    __tablename__ = 'resources'
    
    resource_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    capacity = db.Column(db.Integer, nullable=True)
    images = db.Column(db.Text, nullable=True)  # comma separated paths or JSON array
    availability_rules = db.Column(db.Text, nullable=True)  # JSON blob
    status = db.Column(db.String(20), nullable=False)  # 'draft', 'published', 'archived'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    owner = db.relationship('User', backref='resources')
    
    def __repr__(self):
        return f'<Resource {self.title}>'
    
    def _get_metadata(self):
        """Get metadata from availability_rules JSON"""
        if not self.availability_rules:
            return {}
        try:
            rules = json.loads(self.availability_rules)
            return rules.get('_metadata', {})
        except (json.JSONDecodeError, AttributeError):
            return {}
    
    def _set_metadata(self, metadata):
        """Set metadata in availability_rules JSON"""
        import json
        rules = {}
        if self.availability_rules:
            try:
                rules = json.loads(self.availability_rules)
                # Remove _metadata key if it exists
                rules.pop('_metadata', None)
            except (json.JSONDecodeError, AttributeError):
                rules = {}
        
        # Add metadata
        if metadata:
            rules['_metadata'] = metadata
        
        # Only set if we have rules or metadata
        if rules:
            self.availability_rules = json.dumps(rules)
        elif not metadata:
            # If no metadata and no rules, keep existing or set to None
            pass
    
    @property
    def requires_approval(self):
        """Check if resource requires approval for bookings"""
        metadata = self._get_metadata()
        return metadata.get('requires_approval', False)
    
    @requires_approval.setter
    def requires_approval(self, value):
        """Set requires_approval flag"""
        metadata = self._get_metadata()
        metadata['requires_approval'] = bool(value)
        self._set_metadata(metadata)
    
    def to_dict(self):
        """Convert resource object to dictionary"""
        # Parse JSON fields if they exist
        images_list = None
        if self.images:
            try:
                images_list = json.loads(self.images)
            except json.JSONDecodeError:
                # If not JSON, treat as comma-separated
                images_list = [img.strip() for img in self.images.split(',') if img.strip()]
        
        availability = None
        if self.availability_rules:
            try:
                availability = json.loads(self.availability_rules)
                # Remove metadata from availability display
                if isinstance(availability, dict):
                    availability = {k: v for k, v in availability.items() if k != '_metadata'}
            except json.JSONDecodeError:
                availability = self.availability_rules
        
        return {
            'resource_id': self.resource_id,
            'owner_id': self.owner_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'location': self.location,
            'capacity': self.capacity,
            'images': images_list,
            'availability_rules': availability,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'requires_approval': self.requires_approval
        }


class Booking(db.Model):
    """Booking model for resource reservations"""
    __tablename__ = 'bookings'
    
    booking_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.resource_id'), nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'pending', 'approved', 'rejected', 'cancelled', 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    resource = db.relationship('Resource', backref='bookings')
    requester = db.relationship('User', backref='bookings')
    
    def __repr__(self):
        return f'<Booking {self.booking_id} - Resource {self.resource_id}>'
    
    def to_dict(self):
        """Convert booking object to dictionary"""
        return {
            'booking_id': self.booking_id,
            'resource_id': self.resource_id,
            'requester_id': self.requester_id,
            'start_datetime': self.start_datetime.isoformat() if self.start_datetime else None,
            'end_datetime': self.end_datetime.isoformat() if self.end_datetime else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Message(db.Model):
    """Message model for user-to-user communication"""
    __tablename__ = 'messages'
    
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    thread_id = db.Column(db.Integer, nullable=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
    
    def __repr__(self):
        return f'<Message {self.message_id} - From {self.sender_id} to {self.receiver_id}>'
    
    def to_dict(self):
        """Convert message object to dictionary"""
        return {
            'message_id': self.message_id,
            'thread_id': self.thread_id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'is_read': self.is_read,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class Review(db.Model):
    """Review model for resource ratings and comments"""
    __tablename__ = 'reviews'
    
    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.resource_id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_hidden = db.Column(db.Boolean, default=False, nullable=False)  # Admin can hide inappropriate reviews
    
    # Relationships
    resource = db.relationship('Resource', backref='reviews')
    reviewer = db.relationship('User', backref='reviews')
    
    def __repr__(self):
        return f'<Review {self.review_id} - Resource {self.resource_id} - Rating {self.rating}>'
    
    def to_dict(self):
        """Convert review object to dictionary"""
        return {
            'review_id': self.review_id,
            'resource_id': self.resource_id,
            'reviewer_id': self.reviewer_id,
            'rating': self.rating,
            'comment': self.comment,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class AdminLog(db.Model):
    """Admin log model for tracking administrative actions (optional)"""
    __tablename__ = 'admin_logs'
    
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    action = db.Column(db.String(255), nullable=True)
    target_table = db.Column(db.String(100), nullable=True)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    admin = db.relationship('User', backref='admin_logs')
    
    def __repr__(self):
        return f'<AdminLog {self.log_id} - Admin {self.admin_id} - {self.action}>'
    
    def to_dict(self):
        """Convert admin log object to dictionary"""
        return {
            'log_id': self.log_id,
            'admin_id': self.admin_id,
            'action': self.action,
            'target_table': self.target_table,
            'details': self.details,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class Waitlist(db.Model):
    """Waitlist model for users waiting for fully booked resources"""
    __tablename__ = 'waitlist'
    
    waitlist_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.resource_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    requested_datetime = db.Column(db.DateTime, nullable=False)  # The datetime they want to book
    notified_at = db.Column(db.DateTime, nullable=True)  # When they were notified of availability
    status = db.Column(db.String(20), nullable=False, default='active')  # 'active', 'notified', 'converted', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    resource = db.relationship('Resource', backref='waitlist_entries')
    user = db.relationship('User', backref='waitlist_entries')
    
    def __repr__(self):
        return f'<Waitlist {self.waitlist_id} - Resource {self.resource_id} - User {self.user_id}>'
    
    def to_dict(self):
        """Convert waitlist object to dictionary"""
        return {
            'waitlist_id': self.waitlist_id,
            'resource_id': self.resource_id,
            'user_id': self.user_id,
            'requested_datetime': self.requested_datetime.isoformat() if self.requested_datetime else None,
            'notified_at': self.notified_at.isoformat() if self.notified_at else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ReviewFlag(db.Model):
    """
    Model for tracking when users flag inappropriate reviews
    
    AI Contribution: This model was AI-suggested and implemented as part of the content
    moderation system. The unique constraint and relationship structure were AI-generated
    with team review.
    """
    __tablename__ = 'review_flags'
    
    flag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.review_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # User who flagged
    reason = db.Column(db.Text, nullable=True)  # Optional reason for flagging
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    review = db.relationship('Review', backref='flags')
    user = db.relationship('User', backref='review_flags')
    
    # Unique constraint: one user can only flag a review once
    __table_args__ = (db.UniqueConstraint('review_id', 'user_id', name='unique_review_flag'),)
    
    def __repr__(self):
        return f'<ReviewFlag {self.flag_id} - Review {self.review_id} - User {self.user_id}>'


class MessageReport(db.Model):
    """
    Model for tracking when users report inappropriate messages
    
    AI Contribution: This model was AI-suggested and implemented as part of the content
    moderation system. The unique constraint and relationship structure were AI-generated
    with team review.
    """
    __tablename__ = 'message_reports'
    
    report_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.message_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # User who reported
    reason = db.Column(db.Text, nullable=True)  # Optional reason for reporting
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    message = db.relationship('Message', backref='reports')
    user = db.relationship('User', backref='message_reports')
    
    # Unique constraint: one user can only report a message once
    __table_args__ = (db.UniqueConstraint('message_id', 'user_id', name='unique_message_report'),)
    
    def __repr__(self):
        return f'<MessageReport {self.report_id} - Message {self.message_id} - User {self.user_id}>'


class RoleChangeRequest(db.Model):
    """Role change request model for users requesting role upgrades"""
    __tablename__ = 'role_change_requests'
    
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    requested_role = db.Column(db.String(20), nullable=False)  # 'staff' or 'admin'
    reason = db.Column(db.Text, nullable=True)  # Optional reason for the request
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'approved', 'denied'
    admin_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)  # Admin who processed it
    admin_notes = db.Column(db.Text, nullable=True)  # Admin's notes when approving/denying
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    processed_at = db.Column(db.DateTime, nullable=True)  # When admin processed it
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='role_change_requests')
    admin = db.relationship('User', foreign_keys=[admin_id])
    
    def __repr__(self):
        return f'<RoleChangeRequest {self.request_id} - User {self.user_id} - Role {self.requested_role}>'
    
    def to_dict(self):
        """Convert role change request object to dictionary"""
        return {
            'request_id': self.request_id,
            'user_id': self.user_id,
            'requested_role': self.requested_role,
            'reason': self.reason,
            'status': self.status,
            'admin_id': self.admin_id,
            'admin_notes': self.admin_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }

