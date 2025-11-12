"""
Unit tests for UserDAL
"""
import pytest
from src.data_access.user_dal import UserDAL
from src.models.models import db, User


@pytest.fixture
def app():
    """Create test Flask app"""
    from app import app
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


def test_create_user(app):
    """Test user creation"""
    with app.app_context():
        user = UserDAL.create(
            name="Test User",
            email="test@example.com",
            password="password123",
            role="student"
        )
        assert user is not None
        assert user.email == "test@example.com"
        assert user.role == "student"


def test_get_user_by_email(app):
    """Test getting user by email"""
    with app.app_context():
        UserDAL.create(
            name="Test User",
            email="test@example.com",
            password="password123",
            role="student"
        )
        user = UserDAL.get_by_email("test@example.com")
        assert user is not None
        assert user.email == "test@example.com"


def test_verify_password(app):
    """Test password verification"""
    with app.app_context():
        user = UserDAL.create(
            name="Test User",
            email="test@example.com",
            password="password123",
            role="student"
        )
        assert UserDAL.verify_password(user, "password123") is True
        assert UserDAL.verify_password(user, "wrongpassword") is False

