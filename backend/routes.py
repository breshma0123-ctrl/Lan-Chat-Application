"""
HTTP Routes and REST API Endpoints for LAN Chat Application.
Serves frontend web pages and provides RESTful endpoints for authentication,
user lists, message history, and server diagnostics.
"""

import os
from datetime import datetime
from flask import Blueprint, request, jsonify, session, redirect, url_for, send_from_directory
from database import db
from models import User, Message, OnlineUser
from auth import hash_password, verify_password, login_user, logout_user, get_current_user, login_required, get_client_ip

# Determine frontend directory path
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

routes_bp = Blueprint('routes', __name__)

# ==============================================================================
# HTML Page Serving Routes
# ==============================================================================

@routes_bp.route('/')
def index():
    """Redirect to chat dashboard if logged in, otherwise to login page."""
    if 'user_id' in session:
        return redirect('/chat')
    return redirect('/login')

@routes_bp.route('/login')
def login_page():
    """Serve the user login page."""
    if 'user_id' in session:
        return redirect('/chat')
    return send_from_directory(FRONTEND_DIR, 'login.html')

@routes_bp.route('/register')
def register_page():
    """Serve the user registration page."""
    if 'user_id' in session:
        return redirect('/chat')
    return send_from_directory(FRONTEND_DIR, 'register.html')

@routes_bp.route('/chat')
@login_required
def chat_page():
    """Serve the main real-time chat dashboard."""
    return send_from_directory(FRONTEND_DIR, 'chat.html')

@routes_bp.route('/profile')
@login_required
def profile_page():
    """Serve user profile and network stats page."""
    return send_from_directory(FRONTEND_DIR, 'profile.html')

@routes_bp.route('/about')
def about_page():
    """Serve the Computer Networks concepts educational page."""
    return send_from_directory(FRONTEND_DIR, 'about.html')

@routes_bp.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS static assets."""
    css_dir = os.path.join(FRONTEND_DIR, 'css')
    return send_from_directory(css_dir, filename)

@routes_bp.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript static assets."""
    js_dir = os.path.join(FRONTEND_DIR, 'js')
    return send_from_directory(js_dir, filename)


# ==============================================================================
# REST API Endpoints
# ==============================================================================

@routes_bp.route('/api/register', methods=['POST'])
def api_register():
    """
    POST /api/register
    Registers a new user with hashed password.
    Request JSON: { "username": "...", "password": "...", "confirm_password": "..." }
    """
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    confirm_password = data.get('confirm_password') or ''

    # Input validation
    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and password are required.'}), 400

    if len(username) < 3:
        return jsonify({'success': False, 'error': 'Username must be at least 3 characters long.'}), 400

    if len(username) > 30:
        return jsonify({'success': False, 'error': 'Username must not exceed 30 characters.'}), 400

    if not username.isalnum() and '_' not in username:
        return jsonify({'success': False, 'error': 'Username can only contain letters, numbers, and underscores.'}), 400

    if len(password) < 4:
        return jsonify({'success': False, 'error': 'Password must be at least 4 characters long.'}), 400

    if password != confirm_password:
        return jsonify({'success': False, 'error': 'Passwords do not match.'}), 400

    # Check for existing user
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'success': False, 'error': f'Username "{username}" is already taken. Please choose another.'}), 409

    # Create new user
    hashed = hash_password(password)
    new_user = User(username=username, password=hashed)
    db.session.add(new_user)

    # Initialize online_users record
    client_ip = get_client_ip()
    online_record = OnlineUser(username=username, ip_address=client_ip, status='offline', last_seen=datetime.utcnow())
    db.session.add(online_record)

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Account created successfully! You can now log in.'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Database error: {str(e)}'}), 500


@routes_bp.route('/api/login', methods=['POST'])
def api_login():
    """
    POST /api/login
    Authenticates user, sets up session, and updates status.
    Request JSON: { "username": "...", "password": "..." }
    """
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'success': False, 'error': 'Please enter both username and password.'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not verify_password(user.password, password):
        return jsonify({'success': False, 'error': 'Invalid username or password.'}), 401

    # Login session
    login_user(user)

    # Update online_users table
    client_ip = get_client_ip()
    online_record = OnlineUser.query.filter_by(username=username).first()
    if not online_record:
        online_record = OnlineUser(username=username, ip_address=client_ip, status='online', last_seen=datetime.utcnow())
        db.session.add(online_record)
    else:
        online_record.ip_address = client_ip
        online_record.status = 'online'
        online_record.last_seen = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Welcome back, {user.username}!',
        'user': {
            'id': user.id,
            'username': user.username,
            'ip': client_ip
        }
    })


@routes_bp.route('/api/logout', methods=['POST'])
def api_logout():
    """
    POST /api/logout
    Logs out the user and marks them offline.
    """
    username = session.get('username')
    if username:
        online_record = OnlineUser.query.filter_by(username=username).first()
        if online_record:
            online_record.status = 'offline'
            online_record.last_seen = datetime.utcnow()
            db.session.commit()

    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully.'})


@routes_bp.route('/api/users', methods=['GET'])
@login_required
def api_get_users():
    """
    GET /api/users
    Returns all registered users with their current online/offline status.
    """
    current_username = session.get('username')
    users = User.query.order_by(User.username.asc()).all()

    # Query all online records in bulk
    online_records = {u.username: u for u in OnlineUser.query.all()}

    user_list = []
    for u in users:
        record = online_records.get(u.username)
        user_list.append({
            'id': u.id,
            'username': u.username,
            'is_current_user': (u.username == current_username),
            'status': record.status if record else 'offline',
            'ip_address': record.ip_address if record else 'Unknown',
            'last_seen': record.to_dict()['last_seen'] if record else ''
        })

    return jsonify({'success': True, 'users': user_list})


@routes_bp.route('/api/messages', methods=['GET'])
@login_required
def api_get_general_messages():
    """
    GET /api/messages
    Returns recent message history for General LAN Chat.
    """
    messages = Message.query.filter_by(receiver_id=None)\
                            .order_by(Message.timestamp.asc())\
                            .limit(200)\
                            .all()
    return jsonify({
        'success': True,
        'chat_type': 'general',
        'messages': [m.to_dict() for m in messages]
    })


@routes_bp.route('/api/messages/<username>', methods=['GET'])
@login_required
def api_get_private_messages(username):
    """
    GET /api/messages/<username>
    Returns private message history between current user and target username.
    """
    current_user_id = session.get('user_id')
    target_user = User.query.filter_by(username=username).first()

    if not target_user:
        return jsonify({'success': False, 'error': f'User "{username}" not found.'}), 404

    # Query bidirectional private messages
    messages = Message.query.filter(
        Message.message_type == 'private',
        (
            (Message.sender_id == current_user_id) & (Message.receiver_id == target_user.id)
        ) | (
            (Message.sender_id == target_user.id) & (Message.receiver_id == current_user_id)
        )
    ).order_by(Message.timestamp.asc()).limit(200).all()

    return jsonify({
        'success': True,
        'chat_type': 'private',
        'with_user': target_user.username,
        'messages': [m.to_dict() for m in messages]
    })


@routes_bp.route('/api/messages', methods=['POST'])
@login_required
def api_send_message():
    """
    POST /api/messages
    REST fallback to send a message.
    JSON: { "message": "...", "receiver": "target_username" (optional) }
    """
    data = request.get_json() or {}
    msg_text = (data.get('message') or '').strip()
    receiver_username = data.get('receiver')

    if not msg_text:
        return jsonify({'success': False, 'error': 'Message text cannot be empty.'}), 400

    sender_id = session.get('user_id')
    receiver_id = None
    msg_type = 'public'

    if receiver_username and receiver_username != 'general':
        receiver = User.query.filter_by(username=receiver_username).first()
        if not receiver:
            return jsonify({'success': False, 'error': f'Recipient "{receiver_username}" does not exist.'}), 404
        receiver_id = receiver.id
        msg_type = 'private'

    new_msg = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        message=msg_text,
        message_type=msg_type,
        timestamp=datetime.utcnow()
    )
    db.session.add(new_msg)
    db.session.commit()

    return jsonify({'success': True, 'message': new_msg.to_dict()}), 201


@routes_bp.route('/api/status', methods=['GET'])
def api_status():
    """
    GET /api/status
    Returns server network status, LAN configuration, and connection stats.
    """
    import socket
    def detect_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except Exception:
            try:
                ip = socket.gethostbyname(socket.gethostname())
            except Exception:
                ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    total_users = User.query.count()
    online_count = OnlineUser.query.filter_by(status='online').count()
    total_messages = Message.query.count()

    return jsonify({
        'success': True,
        'server': 'Flask-SocketIO',
        'status': 'online',
        'host': '0.0.0.0',
        'port': 5000,
        'lan_ip': detect_ip(),
        'lan_url': f'http://{detect_ip()}:5000',
        'local_url': 'http://127.0.0.1:5000',
        'stats': {
            'total_users': total_users,
            'online_users': online_count,
            'total_messages': total_messages
        }
    })


@routes_bp.route('/api/profile', methods=['GET'])
@login_required
def api_profile():
    """
    GET /api/profile
    Returns profile details for the currently logged-in user.
    """
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found.'}), 404

    online_record = OnlineUser.query.filter_by(username=user.username).first()
    sent_count = Message.query.filter_by(sender_id=user.id).count()
    client_ip = get_client_ip()

    return jsonify({
        'success': True,
        'profile': {
            'id': user.id,
            'username': user.username,
            'created_at': user.created_at.strftime('%B %d, %Y at %I:%M %p') if user.created_at else 'N/A',
            'client_ip': client_ip,
            'status': online_record.status if online_record else 'online',
            'total_messages_sent': sent_count
        }
    })
