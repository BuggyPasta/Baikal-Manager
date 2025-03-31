from flask import Blueprint, request, jsonify, session
from ..utils.user_store import get_user_store
from werkzeug.security import generate_password_hash, check_password_hash
from ..utils.settings import load_settings

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def sanitize_user_data(user_data):
    """Remove sensitive data from user object"""
    return {k: v for k, v in user_data.items() if k != 'password'} if user_data else None

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    if not (data := request.json):
        return jsonify({'error': 'No data provided'}), 400
        
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    full_name = data.get('fullName')
    
    if not username or not password or not full_name:
        return jsonify({'error': 'Missing required fields'}), 400
    
    if ' ' in username or ' ' in password:
        return jsonify({'error': 'Invalid username or password, no spaces allowed'}), 400
    
    try:
        user_store = get_user_store()
        user_data = user_store.create_user(
            username=username,
            password=generate_password_hash(password),
            full_name=full_name
        )
        
        # Store user_id and user data in session
        session['user_id'] = user_data['username']
        session['user_data'] = sanitize_user_data(user_data)
        
        return jsonify({
            'message': 'User registered',
            'user': sanitize_user_data(user_data)
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        return jsonify({'error': 'Registration failed'}), 500

@bp.route('/login', methods=['POST'])
def login():
    """Login a user."""
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify({'error': 'Missing username or password'}), 400
    
    try:
        user_store = get_user_store()
        user_data = user_store.get_user(request.json['username'])
        
        if not user_data or not check_password_hash(user_data['password'], request.json['password']):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        user_store.update_last_login(request.json['username'])
        
        # Store user_id and user data in session
        session['user_id'] = user_data['username']
        session['user_data'] = sanitize_user_data(user_data)
        
        # Load settings from user store
        settings = load_settings(user_data['username'])
        
        return jsonify({
            'message': 'Login successful',
            'user': sanitize_user_data(user_data),
            'settings': settings
        })
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500

@bp.route('/logout', methods=['POST'])
def logout():
    """Logout the current user."""
    session.clear()
    return jsonify({'message': 'Logged out'})

@bp.route('/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated and get user data."""
    if not (user_id := session.get('user_id')):
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user_store = get_user_store()
        if not (user_data := user_store.get_user(user_id)):
            session.clear()
            return jsonify({'error': 'User not found'}), 401
        
        # Update session with latest user data
        session['user_data'] = sanitize_user_data(user_data)
        
        # Load settings from user store
        settings = load_settings(user_id)
        
        return jsonify({
            'user': sanitize_user_data(user_data),
            'settings': settings
        })
    except Exception as e:
        return jsonify({'error': 'Authentication check failed'}), 500

@bp.route('/delete', methods=['DELETE'])
def delete_account():
    """Delete the current user's account."""
    if not (user_id := session.get('user_id')):
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user_store = get_user_store()
        if user_store.delete_user(user_id):
            session.clear()
            return jsonify({'message': 'Account deleted'})
        return jsonify({'error': 'Account not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Failed to delete account'}), 500 