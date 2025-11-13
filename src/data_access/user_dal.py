"""
Data Access Layer for User operations
Encapsulates all database interactions for User model
"""
from src.models.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash


class UserDAL:
    """Data Access Layer for User CRUD operations"""
    
    @staticmethod
    def create(name: str, email: str, password: str, role: str, 
               department: str = None, profile_image: str = None) -> User:
        """
        Create a new user
        
        Args:
            name: User's full name
            email: User's email address
            password: Plain text password (will be hashed)
            role: User role ('student', 'staff', 'admin')
            department: Optional department
            profile_image: Optional profile image path
            
        Returns:
            Created User object
        """
        password_hash = generate_password_hash(password)
        # Normalize email to lowercase for consistency
        email_normalized = email.lower().strip()
        user = User(
            name=name,
            email=email_normalized,
            password_hash=password_hash,
            role=role,
            department=department,
            profile_image=profile_image
        )
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def get_by_id(user_id: int) -> User:
        """Get user by ID"""
        return User.query.get(user_id)
    
    @staticmethod
    def get_by_email(email: str) -> User:
        """Get user by email (case-insensitive)"""
        from sqlalchemy import func
        # Normalize email to lowercase for case-insensitive lookup
        email_lower = email.lower().strip()
        # Use func.lower() for case-insensitive comparison
        return User.query.filter(func.lower(User.email) == email_lower).first()
    
    @staticmethod
    def update(user_id: int, **kwargs) -> User:
        """
        Update user information
        
        Args:
            user_id: User ID to update
            **kwargs: Fields to update (name, email, role, department, profile_image)
            
        Returns:
            Updated User object
        """
        user = UserDAL.get_by_id(user_id)
        if not user:
            return None
        
        if 'password' in kwargs:
            kwargs['password_hash'] = generate_password_hash(kwargs.pop('password'))
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        db.session.commit()
        return user
    
    @staticmethod
    def delete(user_id: int) -> bool:
        """
        Delete a user and handle all related records
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        from src.models.models import Booking, Review, Message, Waitlist, ReviewFlag, MessageReport, RoleChangeRequest, AdminLog, Resource
        
        user = UserDAL.get_by_id(user_id)
        if not user:
            return False
        
        # Check if user owns any resources - prevent deletion if they do
        # Admin should transfer ownership or delete resources first
        owned_resources = Resource.query.filter_by(owner_id=user_id).all()
        if owned_resources:
            raise ValueError(f"Cannot delete user: User owns {len(owned_resources)} resource(s). Please transfer ownership or delete resources first.")
        
        # Delete all bookings where user is requester
        bookings = Booking.query.filter_by(requester_id=user_id).all()
        for booking in bookings:
            db.session.delete(booking)
        
        # Delete all reviews written by user
        reviews = Review.query.filter_by(reviewer_id=user_id).all()
        for review in reviews:
            db.session.delete(review)
        
        # Delete all messages sent or received by user
        sent_messages = Message.query.filter_by(sender_id=user_id).all()
        received_messages = Message.query.filter_by(receiver_id=user_id).all()
        for message in sent_messages + received_messages:
            db.session.delete(message)
        
        # Delete all waitlist entries
        waitlist_entries = Waitlist.query.filter_by(user_id=user_id).all()
        for entry in waitlist_entries:
            db.session.delete(entry)
        
        # Delete all review flags by user
        review_flags = ReviewFlag.query.filter_by(user_id=user_id).all()
        for flag in review_flags:
            db.session.delete(flag)
        
        # Delete all message reports by user
        message_reports = MessageReport.query.filter_by(user_id=user_id).all()
        for report in message_reports:
            db.session.delete(report)
        
        # Delete all role change requests by user
        role_requests = RoleChangeRequest.query.filter_by(user_id=user_id).all()
        for request in role_requests:
            db.session.delete(request)
        
        # Delete admin logs if user is admin
        admin_logs = AdminLog.query.filter_by(admin_id=user_id).all()
        for log in admin_logs:
            db.session.delete(log)
        
        # Now delete the user
        db.session.delete(user)
        db.session.commit()
        return True
    
    @staticmethod
    def verify_password(user: User, password: str) -> bool:
        """Verify user password"""
        return check_password_hash(user.password_hash, password)
    
    @staticmethod
    def get_all(role: str = None, limit: int = None) -> list:
        """
        Get all users with optional filtering
        
        Args:
            role: Filter by role
            limit: Maximum number of results
            
        Returns:
            List of User objects
        """
        query = User.query
        if role:
            query = query.filter_by(role=role)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()

