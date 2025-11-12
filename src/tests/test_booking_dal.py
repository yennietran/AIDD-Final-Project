"""
Unit tests for BookingDAL - Data Access Layer CRUD operations
"""
import pytest
from datetime import datetime, timedelta
from src.data_access.booking_dal import BookingDAL
from src.data_access.resource_dal import ResourceDAL
from src.data_access.user_dal import UserDAL
import json


def test_create_booking(app, sample_resource, sample_user):
    """Test booking creation (CREATE operation)"""
    with app.app_context():
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        booking = BookingDAL.create(
            resource_id=sample_resource.resource_id,
            requester_id=sample_user.user_id,
            start_datetime=start_time,
            end_datetime=end_time,
            status='pending'
        )
        
        assert booking is not None
        assert booking.booking_id is not None
        assert booking.resource_id == sample_resource.resource_id
        assert booking.requester_id == sample_user.user_id
        assert booking.status == 'pending'


def test_get_booking_by_id(app, sample_resource, sample_user):
    """Test getting booking by ID (READ operation)"""
    with app.app_context():
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        created_booking = BookingDAL.create(
            resource_id=sample_resource.resource_id,
            requester_id=sample_user.user_id,
            start_datetime=start_time,
            end_datetime=end_time,
            status='pending'
        )
        
        retrieved_booking = BookingDAL.get_by_id(created_booking.booking_id)
        
        assert retrieved_booking is not None
        assert retrieved_booking.booking_id == created_booking.booking_id
        assert retrieved_booking.resource_id == sample_resource.resource_id


def test_update_booking_status(app, sample_resource, sample_user):
    """Test updating booking status (UPDATE operation)"""
    with app.app_context():
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        booking = BookingDAL.create(
            resource_id=sample_resource.resource_id,
            requester_id=sample_user.user_id,
            start_datetime=start_time,
            end_datetime=end_time,
            status='pending'
        )
        
        # Update status to approved
        updated_booking = BookingDAL.update(booking.booking_id, status='approved')
        
        assert updated_booking.status == 'approved'
        assert updated_booking.booking_id == booking.booking_id


def test_delete_booking(app, sample_resource, sample_user):
    """Test deleting booking (DELETE operation)"""
    with app.app_context():
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        booking = BookingDAL.create(
            resource_id=sample_resource.resource_id,
            requester_id=sample_user.user_id,
            start_datetime=start_time,
            end_datetime=end_time,
            status='pending'
        )
        
        booking_id = booking.booking_id
        result = BookingDAL.delete(booking_id)
        
        assert result is True
        deleted_booking = BookingDAL.get_by_id(booking_id)
        assert deleted_booking is None


def test_get_all_bookings(app, sample_resource, sample_user):
    """Test getting all bookings with filters"""
    with app.app_context():
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        # Create multiple bookings
        booking1 = BookingDAL.create(
            resource_id=sample_resource.resource_id,
            requester_id=sample_user.user_id,
            start_datetime=start_time,
            end_datetime=end_time,
            status='pending'
        )
        
        booking2 = BookingDAL.create(
            resource_id=sample_resource.resource_id,
            requester_id=sample_user.user_id,
            start_datetime=start_time + timedelta(days=2),
            end_datetime=end_time + timedelta(days=2),
            status='approved'
        )
        
        # Get all bookings for resource
        all_bookings = BookingDAL.get_all(resource_id=sample_resource.resource_id)
        assert len(all_bookings) == 2
        
        # Filter by status
        pending_bookings = BookingDAL.get_all(resource_id=sample_resource.resource_id, status='pending')
        assert len(pending_bookings) == 1
        assert pending_bookings[0].status == 'pending'
        
        # Filter by requester
        user_bookings = BookingDAL.get_all(requester_id=sample_user.user_id)
        assert len(user_bookings) == 2

