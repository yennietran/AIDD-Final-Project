"""
Data Access Layer for Admin operations
Encapsulates admin-related database queries and statistics
"""
from src.models.models import db, User, Resource, Booking, Review
from typing import Dict
from sqlalchemy import func


class AdminDAL:
    """Data Access Layer for Admin operations"""
    
    @staticmethod
    def get_statistics() -> Dict:
        """
        Get system-wide statistics for admin dashboard
        
        Returns:
            Dictionary with statistics
        """
        total_users = User.query.count()
        total_resources = Resource.query.count()
        total_bookings = Booking.query.count()
        pending_bookings = Booking.query.filter_by(status='pending').count()
        total_reviews = Review.query.count()
        
        # Calculate average rating
        avg_rating_result = db.session.query(func.avg(Review.rating)).scalar()
        average_rating = round(float(avg_rating_result), 2) if avg_rating_result else 0.0
        
        return {
            'total_users': total_users,
            'total_resources': total_resources,
            'total_bookings': total_bookings,
            'pending_bookings': pending_bookings,
            'total_reviews': total_reviews,
            'average_rating': average_rating
        }

