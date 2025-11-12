"""
End-to-end test for booking a resource through the UI
This simulates the full booking flow
"""
import pytest
from datetime import datetime, timedelta
from flask import url_for


def test_booking_flow_e2e(client, app, sample_resource, sample_user):
    """End-to-end test: Login → View Resource → Book Resource → View Booking"""
    with app.app_context():
        # Step 1: Login
        login_response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert login_response.status_code == 200
        
        # Step 2: View resource detail page
        resource_detail_response = client.get(f'/resources/{sample_resource.resource_id}')
        assert resource_detail_response.status_code == 200
        assert b'Test Resource' in resource_detail_response.data
        
        # Step 3: Access booking page
        booking_page_response = client.get(f'/resources/{sample_resource.resource_id}/book')
        assert booking_page_response.status_code == 200
        
        # Step 4: Create booking (using a future date/time)
        base_time = datetime.now() + timedelta(days=1)
        # Ensure it's a weekday
        while base_time.weekday() > 4:
            base_time += timedelta(days=1)
        
        start_datetime = base_time.replace(hour=10, minute=0)
        end_datetime = base_time.replace(hour=11, minute=0)
        
        booking_response = client.post(
            f'/resources/{sample_resource.resource_id}/book',
            data={
                'start_datetime': start_datetime.isoformat(),
                'end_datetime': end_datetime.isoformat()
            },
            follow_redirects=True
        )
        
        # Booking should be created (redirect to booking detail or dashboard)
        assert booking_response.status_code == 200
        
        # Step 5: Verify booking was created by checking dashboard or booking list
        dashboard_response = client.get('/dashboard')
        assert dashboard_response.status_code == 200
        # Should show the booking in the dashboard
        assert b'Test Resource' in dashboard_response.data or b'booking' in dashboard_response.data.lower()


def test_booking_with_conflict_e2e(client, app, sample_resource, sample_user):
    """End-to-end test: Try to book a time slot that's already booked"""
    with app.app_context():
        from src.data_access.booking_dal import BookingDAL
        
        # Login
        client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        # Create an existing booking
        base_time = datetime.now() + timedelta(days=1)
        while base_time.weekday() > 4:
            base_time += timedelta(days=1)
        
        existing_booking = BookingDAL.create(
            resource_id=sample_resource.resource_id,
            requester_id=sample_user.user_id,
            start_datetime=base_time.replace(hour=10, minute=0),
            end_datetime=base_time.replace(hour=11, minute=0),
            status='approved'
        )
        
        # Try to book overlapping time
        booking_response = client.post(
            f'/resources/{sample_resource.resource_id}/book',
            data={
                'start_datetime': base_time.replace(hour=10, minute=30).isoformat(),
                'end_datetime': base_time.replace(hour=11, minute=30).isoformat()
            },
            follow_redirects=True
        )
        
        # Should show unavailable message
        assert b'unavailable' in booking_response.data.lower() or b'waitlist' in booking_response.data.lower()

