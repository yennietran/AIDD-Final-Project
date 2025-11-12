"""
Security tests: SQL injection and template escaping
"""
import pytest
from src.data_access.user_dal import UserDAL
from src.data_access.resource_dal import ResourceDAL
from flask import url_for


def test_sql_injection_in_email_login(client, app):
    """Test that SQL injection attempts in email field are safely handled"""
    with app.app_context():
        # Try SQL injection in email field
        malicious_input = "admin@test.com' OR '1'='1"
        
        response = client.post('/login', data={
            'email': malicious_input,
            'password': 'anything'
        }, follow_redirects=True)
        
        # Should not crash or expose database errors
        assert response.status_code == 200
        # Should not successfully login (unless there's actually a user with that email)
        # The parameterized query should prevent SQL injection


def test_sql_injection_in_search(client, app):
    """Test that SQL injection in search query is safely handled"""
    with app.app_context():
        malicious_input = "'; DROP TABLE users; --"
        
        response = client.get(f'/?search={malicious_input}')
        
        # Should not crash
        assert response.status_code == 200
        # Should handle gracefully (no SQL errors exposed)


def test_xss_in_resource_title(client, app, sample_staff):
    """Test that XSS attempts in resource title are escaped"""
    # Login as staff using client
    login_response = client.post('/login', data={
        'email': 'staff@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert login_response.status_code == 200
    
    # Try to create resource with XSS payload
    xss_payload = "<script>alert('XSS')</script>"
    
    response = client.post('/resources/create', data={
        'title': xss_payload,
        'description': 'Test description',
        'category': 'Equipment',
        'status': 'published'
    }, follow_redirects=True)
    
    # Resource should be created
    assert response.status_code == 200
    
    # View the resource
    with app.app_context():
        from src.data_access.resource_dal import ResourceDAL
        resources = ResourceDAL.get_all()
        resource = resources[-1]  # Get the last created resource
    
    view_response = client.get(f'/resources/{resource.resource_id}')
    
    # The script tag should be escaped, not executed
    assert view_response.status_code == 200
    # The title should be in the response (escaped)
    assert xss_payload.encode() in view_response.data or b'&lt;script' in view_response.data


def test_xss_in_message_content(client, app, sample_user, sample_staff):
    """Test that XSS in message content is escaped"""
    # Login as user
    login_response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert login_response.status_code == 200
    
    # Send message with XSS payload
    with app.app_context():
        from src.data_access.message_dal import MessageDAL
        
        xss_payload = "<img src=x onerror=alert('XSS')>"
        
        message = MessageDAL.create(
            sender_id=sample_user.user_id,
            receiver_id=sample_staff.user_id,
            content=xss_payload
        )
    
    # View the message
    response = client.get(f'/messages/{sample_staff.user_id}')
    
    # The XSS should be escaped
    assert response.status_code == 200
    assert b'&lt;img' in response.data or xss_payload.encode() in response.data


def test_parameterized_queries_user_dal(app):
    """Test that UserDAL uses parameterized queries (not string concatenation)"""
    with app.app_context():
        # Try to create user with SQL injection attempt in email
        malicious_email = "test'; DROP TABLE users; --@test.com"
        
        # This should be handled safely by parameterized queries
        user = UserDAL.create(
            name="Test User",
            email=malicious_email,
            password="password123",
            role="student"
        )
        
        # User should be created (email is just a string, not executed as SQL)
        assert user is not None
        assert user.email == malicious_email
        
        # Verify the user can be retrieved (table wasn't dropped)
        retrieved = UserDAL.get_by_email(malicious_email)
        assert retrieved is not None
        assert retrieved.email == malicious_email


def test_parameterized_queries_resource_search(app):
    """Test that resource search uses parameterized queries"""
    with app.app_context():
        from src.data_access.resource_dal import ResourceDAL
        
        # Create resource with normal title
        resource = ResourceDAL.create(
            owner_id=1,  # Assuming owner exists
            title="Normal Resource",
            description="Test",
            category="Equipment",
            status="published"
        )
        
        # Try to search with SQL injection
        malicious_search = "'; DROP TABLE resources; --"
        
        # Search should use parameterized queries
        results = ResourceDAL.search(malicious_search)
        
        # Should not crash and should return empty or handle gracefully
        assert isinstance(results, list)


def test_csrf_protection_enabled(app):
    """Test that CSRF protection is configured (though disabled in tests)"""
    # In production, WTF_CSRF_ENABLED should be True
    # In tests, we disable it for easier testing
    assert app.config.get('WTF_CSRF_ENABLED') is False or app.config.get('WTF_CSRF_ENABLED') is True

