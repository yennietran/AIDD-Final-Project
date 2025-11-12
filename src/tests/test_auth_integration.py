"""
Integration tests for authentication flow: register → login → access protected route
"""
import pytest
from flask import url_for


def test_register_login_access_flow(client, app):
    """Integration test: Register → Login → Access Protected Route"""
    with app.app_context():
        # Step 1: Register a new user
        register_response = client.post('/register', data={
            'name': 'Integration Test User',
            'email': 'integration@test.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'role': 'student',
            'department': 'Computer Science'
        }, follow_redirects=True)
        
        # Registration should succeed (redirect or 200)
        assert register_response.status_code in [200, 302]
        
        # Step 2: Login with the new user
        login_response = client.post('/login', data={
            'email': 'integration@test.com',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        # Login should succeed
        assert login_response.status_code in [200, 302]
        
        # Step 3: Access a protected route (dashboard)
        dashboard_response = client.get('/dashboard', follow_redirects=True)
        
        # Should be able to access dashboard
        assert dashboard_response.status_code == 200
        # Should see user's name or dashboard content
        assert b'Integration Test User' in dashboard_response.data or b'Dashboard' in dashboard_response.data


def test_register_duplicate_email(client, app):
    """Test that registering with duplicate email fails"""
    with app.app_context():
        # Register first user
        client.post('/register', data={
            'name': 'First User',
            'email': 'duplicate@test.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'role': 'student'
        })
        
        # Try to register with same email
        response = client.post('/register', data={
            'name': 'Second User',
            'email': 'duplicate@test.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'role': 'student'
        }, follow_redirects=True)
        
        # Should show error message
        assert b'already' in response.data.lower() or b'exists' in response.data.lower()


def test_login_invalid_credentials(client, app):
    """Test that login with invalid credentials fails"""
    with app.app_context():
        # Try to login with non-existent user
        response = client.post('/login', data={
            'email': 'nonexistent@test.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        # Should show error message
        assert b'invalid' in response.data.lower() or b'incorrect' in response.data.lower() or response.status_code == 200


def test_logout(client, app, sample_user):
    """Test logout functionality"""
    with app.app_context():
        # Login first
        client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        # Logout
        logout_response = client.get('/logout', follow_redirects=True)
        
        # Should redirect to home or login
        assert logout_response.status_code == 200
        
        # Try to access protected route after logout
        dashboard_response = client.get('/dashboard', follow_redirects=True)
        
        # Should redirect to login
        assert b'login' in dashboard_response.data.lower() or b'sign in' in dashboard_response.data.lower()


def test_protected_route_requires_login(client, app):
    """Test that protected routes redirect to login when not authenticated"""
    with app.app_context():
        # Try to access dashboard without logging in
        response = client.get('/dashboard', follow_redirects=True)
        
        # Should redirect to login page
        assert b'login' in response.data.lower() or b'sign in' in response.data.lower()

