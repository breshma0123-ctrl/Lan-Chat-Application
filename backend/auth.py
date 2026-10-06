"""
Authentication and security helpers for LAN Chat Application.
Provides password hashing, verification, session management, and auth decorators.
"""

from functools import wraps
from flask import session, jsonify, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from models import User

def hash_password(password: str) -> str:
    """Hashes a plaintext password using secure PBKDF2 with SHA256."""
    return generate_password_hash(password)

def verify_password(stored_hash: str, password: str) -> bool:
    """Checks plaintext password against stored hash."""
    return check_password_hash(stored_hash, password)

def login_user(user: User):
    """Saves authenticated user identity in the Flask session."""
    session['user_id'] = user.id
    session['username'] = user.username

def logout_user():
    """Clears current user session."""
    session.pop('user_id', None)
    session.pop('username', None)

def get_current_user():
    """Returns the currently logged-in User instance or None."""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)

def get_client_ip():
    """Returns the remote IP of the client, taking proxies into account."""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or '127.0.0.1'

def login_required(f):
    """
    Decorator to ensure user is logged in.
    Returns 401 JSON for API calls or redirects to /login for HTML requests.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Check if this is an API call or regular web page request
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': 'Unauthorized. Please log in.'}), 401
            return redirect(url_for('routes.login_page'))
        return f(*args, **kwargs)
    return decorated_function
