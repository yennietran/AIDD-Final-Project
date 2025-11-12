"""
Data Access Layer for Review operations
Encapsulates all database interactions for Review model
"""
from src.models.models import db, Review
from typing import Optional, List, Dict


class ReviewDAL:
    """Data Access Layer for Review CRUD operations"""
    
    @staticmethod
    def create(resource_id: int, reviewer_id: int, rating: int,
               comment: str = None) -> Review:
        """
        Create a new review
        
        Args:
            resource_id: ID of the resource being reviewed
            reviewer_id: ID of the user writing the review
            rating: Rating (1-5)
            comment: Optional review comment
            
        Returns:
            Created Review object
        """
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        
        review = Review(
            resource_id=resource_id,
            reviewer_id=reviewer_id,
            rating=rating,
            comment=comment
        )
        db.session.add(review)
        db.session.commit()
        return review
    
    @staticmethod
    def get_by_id(review_id: int) -> Optional[Review]:
        """Get review by ID"""
        return Review.query.get(review_id)
    
    @staticmethod
    def get_by_resource(resource_id: int, limit: int = None, include_hidden: bool = False) -> List[Review]:
        """
        Get all reviews for a resource
        
        Args:
            resource_id: Resource ID
            limit: Maximum number of results
            include_hidden: If True, include hidden reviews. Default False.
            
        Returns:
            List of Review objects
        """
        # First, try to check if is_hidden column exists
        from src.models import db
        from sqlalchemy import text
        
        has_is_hidden_column = False
        try:
            result = db.session.execute(
                text("SELECT COUNT(*) FROM pragma_table_info('reviews') WHERE name='is_hidden'")
            ).scalar()
            has_is_hidden_column = result > 0
        except Exception:
            # If check fails, assume column doesn't exist
            pass
        
        # Build query
        query = Review.query.filter_by(resource_id=resource_id)
        
        # Only filter by is_hidden if column exists and we don't want hidden reviews
        if has_is_hidden_column and not include_hidden:
            try:
                query = query.filter(Review.is_hidden == False)
            except Exception:
                # If filter fails, continue without it
                pass
        
        query = query.order_by(Review.timestamp.desc())
        
        if limit:
            query = query.limit(limit)
        
        try:
            reviews = query.all()
            # If column doesn't exist but we tried to filter, filter in Python
            if not has_is_hidden_column and not include_hidden:
                reviews = [r for r in reviews if not getattr(r, 'is_hidden', False)]
            return reviews
        except Exception as e:
            # If query fails due to missing column, use raw SQL
            if 'is_hidden' in str(e) or 'no such column' in str(e).lower():
                # Fallback: use raw SQL to get reviews without is_hidden
                sql = "SELECT review_id, resource_id, reviewer_id, rating, comment, timestamp FROM reviews WHERE resource_id = :resource_id ORDER BY timestamp DESC"
                if limit:
                    sql += f" LIMIT {limit}"
                result = db.session.execute(text(sql), {'resource_id': resource_id})
                reviews = []
                for row in result:
                    # Create Review object manually
                    review = Review()
                    review.review_id = row[0]
                    review.resource_id = row[1]
                    review.reviewer_id = row[2]
                    review.rating = row[3]
                    review.comment = row[4]
                    review.timestamp = row[5]
                    review.is_hidden = False  # Default to False if column doesn't exist
                    reviews.append(review)
                return reviews
            raise
    
    @staticmethod
    def get_by_reviewer(reviewer_id: int, limit: int = None) -> List[Review]:
        """
        Get all reviews by a specific reviewer
        
        Args:
            reviewer_id: User ID of the reviewer
            limit: Maximum number of results
            
        Returns:
            List of Review objects
        """
        query = Review.query.filter_by(reviewer_id=reviewer_id)\
            .order_by(Review.timestamp.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_by_resource_and_user(resource_id: int, user_id: int) -> Optional[Review]:
        """
        Get review for a resource by a specific user
        
        Args:
            resource_id: Resource ID
            user_id: User ID
            
        Returns:
            Review object or None if not found
        """
        return Review.query.filter_by(
            resource_id=resource_id,
            reviewer_id=user_id
        ).first()
    
    @staticmethod
    def get_resource_rating_stats(resource_id: int) -> Dict:
        """
        Get rating statistics for a resource
        
        Args:
            resource_id: Resource ID
            
        Returns:
            Dictionary with rating statistics
        """
        from sqlalchemy import func, case
        
        stats = db.session.query(
            func.count(Review.review_id).label('total_reviews'),
            func.avg(Review.rating).label('average_rating'),
            func.sum(case((Review.rating == 5, 1), else_=0)).label('five_star'),
            func.sum(case((Review.rating == 4, 1), else_=0)).label('four_star'),
            func.sum(case((Review.rating == 3, 1), else_=0)).label('three_star'),
            func.sum(case((Review.rating == 2, 1), else_=0)).label('two_star'),
            func.sum(case((Review.rating == 1, 1), else_=0)).label('one_star')
        ).filter_by(resource_id=resource_id).first()
        
        if stats and stats.total_reviews:
            return {
                'total_reviews': stats.total_reviews,
                'average_rating': round(float(stats.average_rating), 2),
                'five_star': stats.five_star or 0,
                'four_star': stats.four_star or 0,
                'three_star': stats.three_star or 0,
                'two_star': stats.two_star or 0,
                'one_star': stats.one_star or 0
            }
        return {
            'total_reviews': 0,
            'average_rating': 0.0,
            'five_star': 0,
            'four_star': 0,
            'three_star': 0,
            'two_star': 0,
            'one_star': 0
        }
    
    @staticmethod
    def update(review_id: int, rating: int = None, comment: str = None) -> Optional[Review]:
        """
        Update a review
        
        Args:
            review_id: Review ID to update
            rating: New rating (1-5)
            comment: New comment
            
        Returns:
            Updated Review object or None if not found
        """
        review = ReviewDAL.get_by_id(review_id)
        if not review:
            return None
        
        if rating is not None:
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
            review.rating = rating
        
        if comment is not None:
            review.comment = comment
        
        db.session.commit()
        return review
    
    @staticmethod
    def delete(review_id: int) -> bool:
        """
        Delete a review
        
        Args:
            review_id: Review ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        review = ReviewDAL.get_by_id(review_id)
        if not review:
            return False
        
        db.session.delete(review)
        db.session.commit()
        return True

