"""
Campus Resource Hub - Main Application Entry Point
"""
import os
from pathlib import Path
from flask import Flask
from src.models import db
from src.controllers.main import main_bp
from src.controllers.auth import auth_bp
from src.controllers.dashboard import dashboard_bp
from src.controllers.resources import resources_bp
from src.controllers.bookings import bookings_bp
from src.controllers.messages import messages_bp
from src.controllers.reviews import reviews_bp
from src.controllers.admin import admin_bp
from src.controllers.api import api_bp
from flask_login import LoginManager

# Ensure instance directory exists
instance_path = Path('instance')
instance_path.mkdir(exist_ok=True)

# Initialize Flask app
app = Flask(__name__, 
            template_folder='src/views',
            static_folder='src/static',
            instance_path=str(instance_path.absolute()))

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database path - use absolute path for Windows compatibility
db_path = instance_path / 'campus_resource_hub.db'
# Convert Windows backslashes to forward slashes for SQLite URI
db_uri = str(db_path.absolute()).replace('\\', '/')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    f'sqlite:///{db_uri}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(resources_bp)
app.register_blueprint(bookings_bp)
app.register_blueprint(messages_bp)
app.register_blueprint(reviews_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(api_bp)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    from src.models import User
    try:
        return User.query.get(int(user_id))
    except (ValueError, TypeError):
        return None


# Context processor to make unread message count available globally
@app.context_processor
def inject_unread_count():
    """Make unread message count available to all templates"""
    from flask_login import current_user
    from src.data_access.message_dal import MessageDAL
    
    total_unread = 0
    if current_user.is_authenticated:
        try:
            # Get count of unread messages
            total_unread = MessageDAL.get_unread_count(current_user.user_id)
        except:
            pass
    
    return dict(total_unread=total_unread)


# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

