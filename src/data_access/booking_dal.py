"""
Data Access Layer for Booking operations
Encapsulates all database interactions for Booking model
"""
from src.models.models import db, Booking
from datetime import datetime
from typing import Optional, List
from sqlalchemy import or_


class BookingDAL:
    """Data Access Layer for Booking CRUD operations"""
    
    @staticmethod
    def create(resource_id: int, requester_id: int, start_datetime: datetime,
               end_datetime: datetime, status: str = 'pending') -> Booking:
        """
        Create a new booking
        
        Args:
            resource_id: ID of the resource being booked
            requester_id: ID of the user making the booking
            start_datetime: Booking start date and time
            end_datetime: Booking end date and time
            status: Booking status (default: 'pending')
            
        Returns:
            Created Booking object
        """
        booking = Booking(
            resource_id=resource_id,
            requester_id=requester_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            status=status
        )
        db.session.add(booking)
        db.session.commit()
        return booking
    
    @staticmethod
    def get_by_id(booking_id: int) -> Optional[Booking]:
        """Get booking by ID"""
        return Booking.query.get(booking_id)
    
    @staticmethod
    def get_all(resource_id: int = None, requester_id: int = None,
                status: str = None, limit: int = None) -> List[Booking]:
        """
        Get all bookings with optional filtering
        
        Args:
            resource_id: Filter by resource
            requester_id: Filter by requester
            status: Filter by status
            limit: Maximum number of results
            
        Returns:
            List of Booking objects
        """
        query = Booking.query
        
        if resource_id:
            query = query.filter_by(resource_id=resource_id)
        if requester_id:
            query = query.filter_by(requester_id=requester_id)
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(Booking.start_datetime.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def check_availability(resource_id: int, start_datetime: datetime,
                          end_datetime: datetime) -> bool:
        """
        Check if a resource is available for a given time period
        
        Args:
            resource_id: ID of the resource
            start_datetime: Start date and time
            end_datetime: End date and time
            
        Returns:
            True if available, False if conflicts exist
        """
        from src.data_access.resource_dal import ResourceDAL
        import json
        
        # First check if time is within resource availability rules
        resource = ResourceDAL.get_by_id(resource_id)
        if resource:
            # Parse availability rules if they exist
            availability_rules = None
            if resource.availability_rules:
                try:
                    # Handle both string and dict formats
                    if isinstance(resource.availability_rules, str):
                        availability_rules = json.loads(resource.availability_rules)
                    else:
                        availability_rules = resource.availability_rules
                    
                    # Ensure it's a dict and ignore metadata key when checking availability
                    if isinstance(availability_rules, dict):
                        availability_rules = {k: v for k, v in availability_rules.items() if k != '_metadata'}
                    else:
                        availability_rules = None
                except (json.JSONDecodeError, ValueError, AttributeError, TypeError):
                    # If parsing fails, treat as no rules (will check conflicts only)
                    availability_rules = None
            
            # If resource has availability rules defined, we MUST check them
            if availability_rules and isinstance(availability_rules, dict) and len(availability_rules) > 0:
                day_name = start_datetime.strftime('%A').lower()
                day_availability = availability_rules.get(day_name)
                
                # If the day has no explicit rules but resource has rules for other days,
                # this day is NOT available - return False immediately
                if day_availability is None:
                    return False
                
                # Day has rules - check if time is within window
                if day_availability:
                    # Parse time range (e.g., "9:00-17:00" or "17:00-19:00")
                    if '-' in day_availability:
                        start_str, end_str = day_availability.split('-')
                        start_hour, start_min = map(int, start_str.split(':'))
                        end_hour, end_min = map(int, end_str.split(':'))
                        
                        # Check if requested time is within availability window
                        slot_start_time = start_datetime.time()
                        slot_end_time = end_datetime.time()
                        available_start = datetime.min.time().replace(hour=start_hour, minute=start_min)
                        available_end = datetime.min.time().replace(hour=end_hour, minute=end_min)
                        
                        # Check if slot is outside availability hours
                        if slot_start_time < available_start or slot_end_time > available_end:
                            return False
            # If no availability rules at all, resource is always available (only check conflicts)
        
        # Check for booking conflicts
        conflicts = Booking.query.filter(
            Booking.resource_id == resource_id,
            Booking.status.in_(['pending', 'approved']),
            (
                (Booking.start_datetime <= start_datetime) & (Booking.end_datetime > start_datetime) |
                (Booking.start_datetime < end_datetime) & (Booking.end_datetime >= end_datetime) |
                (Booking.start_datetime >= start_datetime) & (Booking.end_datetime <= end_datetime)
            )
        ).first()
        
        return conflicts is None
    
    @staticmethod
    def check_conflicts(resource_id: int, start_datetime: datetime,
                       end_datetime: datetime) -> List[Booking]:
        """
        Check for booking conflicts and return conflicting bookings
        
        Args:
            resource_id: ID of the resource
            start_datetime: Start date and time
            end_datetime: End date and time
            
        Returns:
            List of conflicting Booking objects
        """
        conflicts = Booking.query.filter(
            Booking.resource_id == resource_id,
            Booking.status.in_(['pending', 'approved']),
            or_(
                (Booking.start_datetime <= start_datetime) & (Booking.end_datetime >= start_datetime),
                (Booking.start_datetime <= end_datetime) & (Booking.end_datetime >= end_datetime),
                (Booking.start_datetime >= start_datetime) & (Booking.end_datetime <= end_datetime)
            )
        ).all()
        
        return conflicts
    
    @staticmethod
    def get_by_resource_and_user(resource_id: int, user_id: int, 
                                 status: str = None) -> List[Booking]:
        """
        Get bookings for a resource by a specific user
        
        Args:
            resource_id: Resource ID
            user_id: User ID
            status: Optional status filter
            
        Returns:
            List of Booking objects
        """
        query = Booking.query.filter_by(
            resource_id=resource_id,
            requester_id=user_id
        )
        
        if status:
            query = query.filter_by(status=status)
        
        return query.all()
    
    @staticmethod
    def update(booking_id: int, **kwargs) -> Optional[Booking]:
        """
        Update booking information
        
        Args:
            booking_id: Booking ID to update
            **kwargs: Fields to update
            
        Returns:
            Updated Booking object or None if not found
        """
        booking = BookingDAL.get_by_id(booking_id)
        if not booking:
            return None
        
        for key, value in kwargs.items():
            if hasattr(booking, key):
                setattr(booking, key, value)
        
        db.session.commit()
        return booking
    
    @staticmethod
    def delete(booking_id: int) -> bool:
        """
        Delete a booking
        
        Args:
            booking_id: Booking ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        booking = BookingDAL.get_by_id(booking_id)
        if not booking:
            return False
        
        db.session.delete(booking)
        db.session.commit()
        return True

