"""
Dashboard controller - User dashboard routes
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from src.data_access.role_change_request_dal import RoleChangeRequestDAL

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    """User dashboard"""
    # Check for pending role change request if user is a student
    pending_role_request = None
    if current_user.role == 'student':
        pending_role_request = RoleChangeRequestDAL.get_pending_by_user(current_user.user_id)
    
    return render_template('dashboard/index.html', pending_role_request=pending_role_request)

