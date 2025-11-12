"""
Pytest configuration and shared fixtures
"""
import pytest
from app import app as flask_app
from src.models.models import db


@pytest.fixture
def app():
    """Create test Flask app with in-memory database"""
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.config['SECRET_KEY'] = 'test-secret-key'
    flask_app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def sample_user(app):
    """Create a sample user for testing"""
    from src.data_access.user_dal import UserDAL
    with app.app_context():
        user = UserDAL.create(
            name="Test User",
            email="test@example.com",
            password="password123",
            role="student"
        )
        # Refresh to ensure it's attached to session
        db.session.refresh(user)
        return user


@pytest.fixture
def sample_staff(app):
    """Create a sample staff user for testing"""
    from src.data_access.user_dal import UserDAL
    with app.app_context():
        user = UserDAL.create(
            name="Staff User",
            email="staff@example.com",
            password="password123",
            role="staff"
        )
        # Refresh to ensure it's attached to session
        db.session.refresh(user)
        return user


@pytest.fixture
def sample_admin(app):
    """Create a sample admin user for testing"""
    from src.data_access.user_dal import UserDAL
    with app.app_context():
        user = UserDAL.create(
            name="Admin User",
            email="admin@example.com",
            password="password123",
            role="admin"
        )
        # Refresh to ensure it's attached to session
        db.session.refresh(user)
        return user


@pytest.fixture
def sample_resource(app, sample_staff):
    """Create a sample resource for testing"""
    from src.data_access.resource_dal import ResourceDAL
    import json
    with app.app_context():
        # Get the user_id directly to avoid session issues
        staff_id = sample_staff.user_id
        resource = ResourceDAL.create(
            owner_id=staff_id,
            title="Test Resource",
            description="A test resource",
            category="Equipment",
            location="Room 101",
            capacity=10,
            availability_rules=json.dumps({
                "monday": "9:00-17:00",
                "tuesday": "9:00-17:00",
                "wednesday": "9:00-17:00",
                "thursday": "9:00-17:00",
                "friday": "9:00-17:00"
            }),
            status="published"
        )
        # Refresh to ensure it's attached to session
        db.session.refresh(resource)
        return resource

