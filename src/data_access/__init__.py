"""
Data Access Layer - Encapsulated CRUD operations
"""
from .user_dal import UserDAL
from .resource_dal import ResourceDAL
from .booking_dal import BookingDAL
from .message_dal import MessageDAL
from .review_dal import ReviewDAL

__all__ = ['UserDAL', 'ResourceDAL', 'BookingDAL', 'MessageDAL', 'ReviewDAL']

