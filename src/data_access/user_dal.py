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
        Delete a user
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        user = UserDAL.get_by_id(user_id)
        if not user:
            return False
        
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

