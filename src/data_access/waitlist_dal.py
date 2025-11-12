"""
Data Access Layer for Waitlist operations
Encapsulates all database interactions for Waitlist model
"""
from src.models.models import db, Waitlist
from datetime import datetime
from typing import Optional, List


class WaitlistDAL:
    """Data Access Layer for Waitlist CRUD operations"""
    
    @staticmethod
    def create(resource_id: int, user_id: int, requested_datetime: datetime,
               status: str = 'active') -> Waitlist:
        """
        Add a user to the waitlist for a resource
        
        Args:
            resource_id: ID of the resource
            user_id: ID of the user joining waitlist
            requested_datetime: The datetime they want to book
            status: Waitlist status (default: 'active')
            
        Returns:
            Created Waitlist object
        """
        waitlist_entry = Waitlist(
            resource_id=resource_id,
            user_id=user_id,
            requested_datetime=requested_datetime,
            status=status
        )
        db.session.add(waitlist_entry)
        db.session.commit()
        return waitlist_entry
    
    @staticmethod
    def get_by_id(waitlist_id: int) -> Optional[Waitlist]:
        """Get waitlist entry by ID"""
        return Waitlist.query.get(waitlist_id)
    
    @staticmethod
    def get_by_resource_and_user(resource_id: int, user_id: int,
                                 status: str = None) -> Optional[Waitlist]:
        """
        Get waitlist entry for a specific resource and user
        
        Args:
            resource_id: Resource ID
            user_id: User ID
            status: Optional status filter
            
        Returns:
            Waitlist object or None if not found
        """
        query = Waitlist.query.filter_by(
            resource_id=resource_id,
            user_id=user_id
        )
        
        if status:
            query = query.filter_by(status=status)
        
        return query.first()
    
    @staticmethod
    def get_all(resource_id: int = None, user_id: int = None,
                status: str = None, limit: int = None) -> List[Waitlist]:
        """
        Get all waitlist entries with optional filtering
        
        Args:
            resource_id: Filter by resource
            user_id: Filter by user
            status: Filter by status
            limit: Maximum number of results
            
        Returns:
            List of Waitlist objects, ordered by created_at (FIFO)
        """
        query = Waitlist.query
        
        if resource_id:
            query = query.filter_by(resource_id=resource_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        
        # Order by created_at to maintain FIFO queue
        query = query.order_by(Waitlist.created_at.asc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_next_in_queue(resource_id: int, requested_datetime: datetime = None) -> Optional[Waitlist]:
        """
        Get the next person in the waitlist queue for a resource
        
        Args:
            resource_id: Resource ID
            requested_datetime: Optional datetime filter (get next person waiting for this specific time)
            
        Returns:
            Next Waitlist object in queue or None
        """
        query = Waitlist.query.filter_by(
            resource_id=resource_id,
            status='active'
        )
        
        if requested_datetime:
            # Get people waiting for this specific datetime
            query = query.filter_by(requested_datetime=requested_datetime)
        
        # Get the first person in queue (oldest entry)
        return query.order_by(Waitlist.created_at.asc()).first()
    
    @staticmethod
    def get_position_in_queue(resource_id: int, user_id: int,
                              requested_datetime: datetime = None) -> int:
        """
        Get user's position in the waitlist queue
        
        Args:
            resource_id: Resource ID
            user_id: User ID
            requested_datetime: Optional datetime filter
            
        Returns:
            Position in queue (1-based), or 0 if not in queue
        """
        query = Waitlist.query.filter_by(
            resource_id=resource_id,
            status='active'
        )
        
        if requested_datetime:
            query = query.filter_by(requested_datetime=requested_datetime)
        
        # Get all active entries ordered by creation time
        all_entries = query.order_by(Waitlist.created_at.asc()).all()
        
        for index, entry in enumerate(all_entries, start=1):
            if entry.user_id == user_id:
                return index
        
        return 0
    
    @staticmethod
    def update(waitlist_id: int, **kwargs) -> Optional[Waitlist]:
        """
        Update waitlist entry
        
        Args:
            waitlist_id: Waitlist ID to update
            **kwargs: Fields to update
            
        Returns:
            Updated Waitlist object or None if not found
        """
        waitlist_entry = WaitlistDAL.get_by_id(waitlist_id)
        if not waitlist_entry:
            return None
        
        for key, value in kwargs.items():
            if hasattr(waitlist_entry, key):
                setattr(waitlist_entry, key, value)
        
        db.session.commit()
        return waitlist_entry
    
    @staticmethod
    def notify_user(waitlist_id: int) -> Optional[Waitlist]:
        """
        Mark a waitlist entry as notified
        
        Args:
            waitlist_id: Waitlist ID to mark as notified
            
        Returns:
            Updated Waitlist object or None if not found
        """
        return WaitlistDAL.update(waitlist_id, status='notified', notified_at=datetime.utcnow())
    
    @staticmethod
    def convert_to_booking(waitlist_id: int) -> Optional[Waitlist]:
        """
        Mark a waitlist entry as converted (user successfully booked)
        
        Args:
            waitlist_id: Waitlist ID to mark as converted
            
        Returns:
            Updated Waitlist object or None if not found
        """
        return WaitlistDAL.update(waitlist_id, status='converted')
    
    @staticmethod
    def cancel(waitlist_id: int) -> bool:
        """
        Cancel a waitlist entry
        
        Args:
            waitlist_id: Waitlist ID to cancel
            
        Returns:
            True if cancelled, False if not found
        """
        waitlist_entry = WaitlistDAL.get_by_id(waitlist_id)
        if not waitlist_entry:
            return False
        
        waitlist_entry.status = 'cancelled'
        db.session.commit()
        return True
    
    @staticmethod
    def delete(waitlist_id: int) -> bool:
        """
        Delete a waitlist entry
        
        Args:
            waitlist_id: Waitlist ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        waitlist_entry = WaitlistDAL.get_by_id(waitlist_id)
        if not waitlist_entry:
            return False
        
        db.session.delete(waitlist_entry)
        db.session.commit()
        return True

