"""
Model Context Protocol (MCP) Tools
Read-only database query tools for AI agents

All queries are read-only and use parameterized statements for security.
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any


class MCPDatabaseError(Exception):
    """Custom exception for MCP database operations"""
    pass


def get_db_connection(db_path: str = 'instance/campus_resource_hub.db') -> sqlite3.Connection:
    """
    Get a read-only database connection
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        sqlite3.Connection: Read-only database connection
    """
    db_file = Path(db_path)
    if not db_file.exists():
        raise MCPDatabaseError(f"Database not found at {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


def execute_read_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """
    Execute a read-only query safely
    
    Args:
        query: SQL SELECT query (must start with SELECT)
        params: Query parameters for parameterized queries
        
    Returns:
        List of dictionaries representing query results
    """
    # Security check: Only allow SELECT queries
    query_upper = query.strip().upper()
    if not query_upper.startswith('SELECT'):
        raise MCPDatabaseError("Only SELECT queries are allowed")
    
    # Block dangerous keywords
    dangerous_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE']
    if any(keyword in query_upper for keyword in dangerous_keywords):
        raise MCPDatabaseError("Write operations are not allowed")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Convert rows to dictionaries
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        raise MCPDatabaseError(f"Database query error: {str(e)}")


def query_resources(
    category: Optional[str] = None,
    location: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Query resources with optional filters
    
    Args:
        category: Filter by resource category
        location: Filter by location
        status: Filter by status ('draft', 'published', 'archived')
        limit: Maximum number of results
        
    Returns:
        List of resource dictionaries
    """
    query = "SELECT * FROM resources WHERE 1=1"
    params = []
    
    if category:
        query += " AND category LIKE ?"
        params.append(f"%{category}%")
    
    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    return execute_read_query(query, tuple(params))


def get_resource_summary(resource_id: int) -> Dict[str, Any]:
    """
    Get detailed summary of a resource including bookings and reviews
    
    Args:
        resource_id: ID of the resource
        
    Returns:
        Dictionary with resource details, booking stats, and review stats
    """
    # Get resource details
    resource_query = "SELECT * FROM resources WHERE resource_id = ?"
    resources = execute_read_query(resource_query, (resource_id,))
    
    if not resources:
        return {"error": "Resource not found"}
    
    resource = resources[0]
    
    # Get booking statistics
    booking_query = """
        SELECT 
            COUNT(*) as total_bookings,
            COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved_bookings,
            COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_bookings,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_bookings
        FROM bookings
        WHERE resource_id = ?
    """
    booking_stats = execute_read_query(booking_query, (resource_id,))
    
    # Get review statistics
    review_query = """
        SELECT 
            COUNT(*) as total_reviews,
            AVG(rating) as average_rating
        FROM reviews
        WHERE resource_id = ?
    """
    review_stats = execute_read_query(review_query, (resource_id,))
    
    return {
        "resource": dict(resource),
        "booking_stats": dict(booking_stats[0]) if booking_stats else {},
        "review_stats": dict(review_stats[0]) if review_stats else {}
    }


def query_bookings(
    resource_id: Optional[int] = None,
    requester_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Query bookings with optional filters
    
    Args:
        resource_id: Filter by resource
        requester_id: Filter by requester
        status: Filter by booking status
        start_date: Filter bookings starting after this date (YYYY-MM-DD)
        end_date: Filter bookings ending before this date (YYYY-MM-DD)
        limit: Maximum number of results
        
    Returns:
        List of booking dictionaries
    """
    query = "SELECT * FROM bookings WHERE 1=1"
    params = []
    
    if resource_id:
        query += " AND resource_id = ?"
        params.append(resource_id)
    
    if requester_id:
        query += " AND requester_id = ?"
        params.append(requester_id)
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    if start_date:
        query += " AND start_datetime >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND end_datetime <= ?"
        params.append(end_date)
    
    query += " ORDER BY start_datetime DESC LIMIT ?"
    params.append(limit)
    
    return execute_read_query(query, tuple(params))


def check_availability(resource_id: int, start_datetime: str, end_datetime: str) -> Dict[str, Any]:
    """
    Check if a resource is available for a given time period
    
    Args:
        resource_id: ID of the resource
        start_datetime: Start datetime (YYYY-MM-DD HH:MM:SS)
        end_datetime: End datetime (YYYY-MM-DD HH:MM:SS)
        
    Returns:
        Dictionary with availability status and conflicting bookings
    """
    query = """
        SELECT * FROM bookings
        WHERE resource_id = ?
        AND status IN ('pending', 'approved')
        AND (
            (start_datetime <= ? AND end_datetime >= ?)
            OR (start_datetime <= ? AND end_datetime >= ?)
            OR (start_datetime >= ? AND end_datetime <= ?)
        )
    """
    params = (
        resource_id,
        start_datetime, start_datetime,
        end_datetime, end_datetime,
        start_datetime, end_datetime
    )
    
    conflicts = execute_read_query(query, params)
    
    return {
        "available": len(conflicts) == 0,
        "conflicts": [dict(c) for c in conflicts]
    }


def query_reviews(
    resource_id: Optional[int] = None,
    reviewer_id: Optional[int] = None,
    min_rating: Optional[int] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Query reviews with optional filters
    
    Args:
        resource_id: Filter by resource
        reviewer_id: Filter by reviewer
        min_rating: Minimum rating (1-5)
        limit: Maximum number of results
        
    Returns:
        List of review dictionaries
    """
    query = "SELECT * FROM reviews WHERE 1=1"
    params = []
    
    if resource_id:
        query += " AND resource_id = ?"
        params.append(resource_id)
    
    if reviewer_id:
        query += " AND reviewer_id = ?"
        params.append(reviewer_id)
    
    if min_rating:
        query += " AND rating >= ?"
        params.append(min_rating)
    
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    
    return execute_read_query(query, tuple(params))


def get_resource_ratings(resource_id: int) -> Dict[str, Any]:
    """
    Get rating statistics for a resource
    
    Args:
        resource_id: ID of the resource
        
    Returns:
        Dictionary with rating statistics
    """
    query = """
        SELECT 
            COUNT(*) as total_reviews,
            AVG(rating) as average_rating,
            COUNT(CASE WHEN rating = 5 THEN 1 END) as five_star,
            COUNT(CASE WHEN rating = 4 THEN 1 END) as four_star,
            COUNT(CASE WHEN rating = 3 THEN 1 END) as three_star,
            COUNT(CASE WHEN rating = 2 THEN 1 END) as two_star,
            COUNT(CASE WHEN rating = 1 THEN 1 END) as one_star
        FROM reviews
        WHERE resource_id = ?
    """
    results = execute_read_query(query, (resource_id,))
    
    return dict(results[0]) if results else {}


def get_popular_resources(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get most popular resources based on booking count
    
    Args:
        limit: Maximum number of results
        
    Returns:
        List of resources with booking counts
    """
    query = """
        SELECT 
            r.*,
            COUNT(b.booking_id) as booking_count,
            AVG(rev.rating) as average_rating
        FROM resources r
        LEFT JOIN bookings b ON r.resource_id = b.resource_id
        LEFT JOIN reviews rev ON r.resource_id = rev.resource_id
        WHERE r.status = 'published'
        GROUP BY r.resource_id
        ORDER BY booking_count DESC, average_rating DESC
        LIMIT ?
    """
    return execute_read_query(query, (limit,))


def query_users(
    role: Optional[str] = None,
    department: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Query users with optional filters (limited fields for privacy)
    
    Args:
        role: Filter by user role
        department: Filter by department
        limit: Maximum number of results
        
    Returns:
        List of user dictionaries (excluding sensitive fields)
    """
    query = """
        SELECT 
            user_id, name, role, department, created_at
        FROM users
        WHERE 1=1
    """
    params = []
    
    if role:
        query += " AND role = ?"
        params.append(role)
    
    if department:
        query += " AND department LIKE ?"
        params.append(f"%{department}%")
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    return execute_read_query(query, tuple(params))

