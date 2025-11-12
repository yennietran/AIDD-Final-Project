"""
Data Access Layer for RoleChangeRequest operations
Encapsulates all database interactions for RoleChangeRequest model
"""
from src.models.models import db, RoleChangeRequest
from typing import Optional, List
from datetime import datetime


class RoleChangeRequestDAL:
    """Data Access Layer for RoleChangeRequest CRUD operations"""
    
    @staticmethod
    def create(user_id: int, requested_role: str, reason: str = None) -> RoleChangeRequest:
        """
        Create a new role change request
        
        Args:
            user_id: ID of the user requesting role change
            requested_role: Role being requested ('staff' or 'admin')
            reason: Optional reason for the request
            
        Returns:
            Created RoleChangeRequest object
        """
        if requested_role not in ['staff', 'admin']:
            raise ValueError("Requested role must be 'staff' or 'admin'")
        
        # Check if user already has a pending request
        existing = RoleChangeRequestDAL.get_pending_by_user(user_id)
        if existing:
            raise ValueError("You already have a pending role change request")
        
        request = RoleChangeRequest(
            user_id=user_id,
            requested_role=requested_role,
            reason=reason,
            status='pending'
        )
        db.session.add(request)
        db.session.commit()
        return request
    
    @staticmethod
    def get_by_id(request_id: int) -> Optional[RoleChangeRequest]:
        """Get role change request by ID"""
        return RoleChangeRequest.query.get(request_id)
    
    @staticmethod
    def get_pending_by_user(user_id: int) -> Optional[RoleChangeRequest]:
        """Get pending role change request for a user"""
        return RoleChangeRequest.query.filter_by(
            user_id=user_id,
            status='pending'
        ).first()
    
    @staticmethod
    def get_all(status: str = None) -> List[RoleChangeRequest]:
        """
        Get all role change requests with optional filtering
        
        Args:
            status: Filter by status ('pending', 'approved', 'denied')
            
        Returns:
            List of RoleChangeRequest objects, ordered by created_at (newest first)
        """
        query = RoleChangeRequest.query
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(RoleChangeRequest.created_at.desc()).all()
    
    @staticmethod
    def approve(request_id: int, admin_id: int, admin_notes: str = None) -> Optional[RoleChangeRequest]:
        """
        Approve a role change request
        
        Args:
            request_id: ID of the request to approve
            admin_id: ID of the admin approving the request
            admin_notes: Optional notes from admin
            
        Returns:
            Updated RoleChangeRequest object or None if not found
        """
        request = RoleChangeRequestDAL.get_by_id(request_id)
        if not request:
            return None
        
        if request.status != 'pending':
            raise ValueError("Request has already been processed")
        
        # Update request status
        request.status = 'approved'
        request.admin_id = admin_id
        request.admin_notes = admin_notes
        request.processed_at = datetime.utcnow()
        
        # Update user's role
        from src.data_access.user_dal import UserDAL
        UserDAL.update(request.user_id, role=request.requested_role)
        
        db.session.commit()
        return request
    
    @staticmethod
    def deny(request_id: int, admin_id: int, admin_notes: str = None) -> Optional[RoleChangeRequest]:
        """
        Deny a role change request
        
        Args:
            request_id: ID of the request to deny
            admin_id: ID of the admin denying the request
            admin_notes: Optional notes from admin
            
        Returns:
            Updated RoleChangeRequest object or None if not found
        """
        request = RoleChangeRequestDAL.get_by_id(request_id)
        if not request:
            return None
        
        if request.status != 'pending':
            raise ValueError("Request has already been processed")
        
        request.status = 'denied'
        request.admin_id = admin_id
        request.admin_notes = admin_notes
        request.processed_at = datetime.utcnow()
        
        db.session.commit()
        return request
    
    @staticmethod
    def delete(request_id: int) -> bool:
        """
        Delete a role change request
        
        Args:
            request_id: ID of the request to delete
            
        Returns:
            True if deleted, False if not found
        """
        request = RoleChangeRequestDAL.get_by_id(request_id)
        if not request:
            return False
        
        db.session.delete(request)
        db.session.commit()
        return True

