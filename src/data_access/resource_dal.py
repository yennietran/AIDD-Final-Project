"""
Data Access Layer for Resource operations
Encapsulates all database interactions for Resource model
"""
from src.models.models import db, Resource
from typing import Optional, List, Dict, Any
import json


class ResourceDAL:
    """Data Access Layer for Resource CRUD operations"""
    
    @staticmethod
    def create(owner_id: int, title: str, description: str = None,
               category: str = None, location: str = None, capacity: int = None,
               images: List[str] = None, availability_rules: Dict[str, Any] = None,
               status: str = 'draft') -> Resource:
        """
        Create a new resource
        
        Args:
            owner_id: ID of the resource owner
            title: Resource title
            description: Resource description
            category: Resource category
            location: Resource location
            capacity: Maximum capacity
            images: List of image paths
            availability_rules: Dictionary of availability rules (will be JSON encoded)
            status: Resource status ('draft', 'published', 'archived')
            
        Returns:
            Created Resource object
        """
        images_str = None
        if images:
            images_str = json.dumps(images)
        
        availability_str = None
        if availability_rules:
            availability_str = json.dumps(availability_rules)
        
        resource = Resource(
            owner_id=owner_id,
            title=title,
            description=description,
            category=category,
            location=location,
            capacity=capacity,
            images=images_str,
            availability_rules=availability_str,
            status=status
        )
        db.session.add(resource)
        db.session.commit()
        return resource
    
    @staticmethod
    def get_by_id(resource_id: int) -> Optional[Resource]:
        """Get resource by ID"""
        return Resource.query.get(resource_id)
    
    @staticmethod
    def get_all(category: str = None, status: str = None, 
                owner_id: int = None, limit: int = None) -> List[Resource]:
        """
        Get all resources with optional filtering
        
        Args:
            category: Filter by category
            status: Filter by status
            owner_id: Filter by owner
            limit: Maximum number of results
            
        Returns:
            List of Resource objects
        """
        query = Resource.query
        
        if category:
            query = query.filter_by(category=category)
        if status:
            query = query.filter_by(status=status)
        if owner_id:
            query = query.filter_by(owner_id=owner_id)
        
        query = query.order_by(Resource.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def search(search_term: str = None, category: str = None, 
              status: str = 'published', limit: int = 50) -> List[Resource]:
        """
        Search resources by title, description, or location
        
        Args:
            search_term: Search keyword (optional)
            category: Filter by category
            status: Filter by status
            limit: Maximum number of results
            
        Returns:
            List of matching Resource objects
        """
        query = Resource.query
        
        if search_term:
            query = query.filter(
                (Resource.title.contains(search_term)) |
                (Resource.description.contains(search_term)) |
                (Resource.location.contains(search_term))
            )
        
        if category:
            query = query.filter_by(category=category)
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(Resource.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def update(resource_id: int, **kwargs) -> Optional[Resource]:
        """
        Update resource information
        
        Args:
            resource_id: Resource ID to update
            **kwargs: Fields to update
            
        Returns:
            Updated Resource object or None if not found
        """
        resource = ResourceDAL.get_by_id(resource_id)
        if not resource:
            return None
        
        # Handle JSON fields
        if 'images' in kwargs and isinstance(kwargs['images'], list):
            kwargs['images'] = json.dumps(kwargs['images'])
        
        if 'availability_rules' in kwargs and isinstance(kwargs['availability_rules'], dict):
            kwargs['availability_rules'] = json.dumps(kwargs['availability_rules'])
        
        for key, value in kwargs.items():
            if hasattr(resource, key):
                setattr(resource, key, value)
        
        db.session.commit()
        return resource
    
    @staticmethod
    def delete(resource_id: int) -> bool:
        """
        Delete a resource and all associated bookings, reviews, and uploaded images
        
        Args:
            resource_id: Resource ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        import os
        import json
        from pathlib import Path
        from src.models.models import Booking, Review
        
        resource = ResourceDAL.get_by_id(resource_id)
        if not resource:
            return False
        
        # Delete uploaded image files before deleting the resource
        if resource.images:
            try:
                # Parse images (could be JSON string or comma-separated)
                images_list = []
                if isinstance(resource.images, str):
                    try:
                        images_list = json.loads(resource.images)
                        if not isinstance(images_list, list):
                            images_list = [images_list]
                    except (json.JSONDecodeError, TypeError):
                        # If not JSON, treat as comma-separated
                        images_list = [img.strip() for img in resource.images.split(',') if img.strip()]
                elif isinstance(resource.images, list):
                    images_list = resource.images
                
                # Delete local files only (not external URLs)
                uploads_dir = Path('src/static/uploads')
                for image_path in images_list:
                    if isinstance(image_path, str):
                        # Check if it's a local file path (starts with /static/uploads/)
                        if image_path.startswith('/static/uploads/') or image_path.startswith('static/uploads/'):
                            # Extract filename
                            filename = image_path.split('/')[-1]
                            file_path = uploads_dir / filename
                            
                            # Delete file if it exists
                            if file_path.exists() and file_path.is_file():
                                try:
                                    os.remove(str(file_path))
                                except OSError as e:
                                    # Log error but don't fail deletion if file can't be removed
                                    print(f"Error deleting image file {file_path}: {e}")
            except Exception as e:
                # Don't fail resource deletion if image deletion fails
                print(f"Error processing images for deletion: {e}")
        
        # Delete all associated bookings first
        bookings = Booking.query.filter_by(resource_id=resource_id).all()
        for booking in bookings:
            db.session.delete(booking)
        
        # Delete all associated reviews
        reviews = Review.query.filter_by(resource_id=resource_id).all()
        for review in reviews:
            db.session.delete(review)
        
        # Now delete the resource
        db.session.delete(resource)
        db.session.commit()
        return True

