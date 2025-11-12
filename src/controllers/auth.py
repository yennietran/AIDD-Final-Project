"""
Authentication controller - Login, logout, registration routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from src.data_access.user_dal import UserDAL
from src.models.models import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))
        
        if not email or not password:
            flash('Please fill in all fields.', 'danger')
            return render_template('auth/login.html')
        
        # Get user by email (normalize to lowercase for consistency)
        user = UserDAL.get_by_email(email)
        
        if user and UserDAL.verify_password(user, password):
            # Check if user is suspended
            if getattr(user, 'is_suspended', False):
                flash('Your account has been suspended. Please contact an administrator.', 'danger')
                return render_template('auth/login.html')
            
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = 'student'  # Force all new registrations to be students
        department = request.form.get('department', '').strip() or None
        
        # Validation
        errors = []
        if not name:
            errors.append('Name is required.')
        if not email:
            errors.append('Email is required.')
        elif '@' not in email:
            errors.append('Invalid email format.')
        if not password:
            errors.append('Password is required.')
        elif len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check if email already exists
        if email and UserDAL.get_by_email(email):
            errors.append('Email already registered.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html')
        
        # Create user
        try:
            user = UserDAL.create(
                name=name,
                email=email,
                password=password,
                role=role,
                department=department
            )
            flash('Account created successfully! Please sign in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('An error occurred during registration. Please try again.', 'danger')
            db.session.rollback()
    
    return render_template('auth/register.html')


@auth_bp.route('/request-role-change', methods=['POST'])
@login_required
def request_role_change():
    """Request a role change"""
    from src.data_access.role_change_request_dal import RoleChangeRequestDAL
    
    # Only students can request role changes
    if current_user.role != 'student':
        flash('Only students can request role changes.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    requested_role = request.form.get('requested_role', '').strip()
    reason = request.form.get('reason', '').strip() or None
    
    if not requested_role or requested_role not in ['staff', 'admin']:
        flash('Please select a valid role (Staff or Admin).', 'danger')
        return redirect(url_for('dashboard.index'))
    
    try:
        RoleChangeRequestDAL.create(
            user_id=current_user.user_id,
            requested_role=requested_role,
            reason=reason
        )
        flash(f'Your request to become a {requested_role.title()} has been submitted. An admin will review it soon.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash(f'Error submitting request: {str(e)}', 'danger')
        db.session.rollback()
    
    return redirect(url_for('dashboard.index'))

