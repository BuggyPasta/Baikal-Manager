from flask import Blueprint, request, jsonify, session
from ..utils.user_store import get_user_store
from werkzeug.security import generate_password_hash, check_password_hash
from ..utils.settings import load_settings
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Only add handler if none exist
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.debug("Auth routes logger initialized")

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def sanitize_user_data(user_data):
    """Remove sensitive data from user object while preserving Baikal credentials"""
    if not user_data:
        return None
        
    # Create a copy of the user data
    sanitized = user_data.copy()
    
    # Only remove the user's password, keep everything else including Baikal credentials
    if 'password' in sanitized:
        del sanitized['password']
        
    return sanitized

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    logger.debug("Registration request received")
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
        
        logger.debug(f"User {username} registered successfully")
        return jsonify({
            'message': 'User registered',
            'user': sanitize_user_data(user_data)
        })
    except ValueError as e:
        logger.error(f"Registration failed for user {username}: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Registration failed for user {username}: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@bp.route('/login', methods=['POST'])
def login():
    """Login a user."""
    logger.debug("Login request received")
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify({'error': 'Missing username or password'}), 400
    
    try:
        username = request.json['username']
        user_store = get_user_store()
        user_data = user_store.get_user(username)
        
        if not user_data or not check_password_hash(user_data['password'], request.json['password']):
            logger.warning(f"Failed login attempt for user {username}")
            return jsonify({'error': 'Invalid username or password'}), 401
        
        user_store.update_last_login(username)
        
        # Store user_id and user data in session
        session['user_id'] = user_data['username']
        session['user_data'] = sanitize_user_data(user_data)
        
        logger.debug(f"User {username} logged in successfully")
        logger.debug(f"Session data for {username}: {session.get('user_data')}")
        
        return jsonify({
            'message': 'Login successful',
            'user': sanitize_user_data(user_data)
        })
    except Exception as e:
        logger.error(f"Login failed for user {username}: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@bp.route('/logout', methods=['POST'])
def logout():
    """Logout the current user."""
    user_id = session.get('user_id')
    logger.debug(f"Logout request received for user {user_id}")
    session.clear()
    logger.debug(f"User {user_id} logged out successfully")
    return jsonify({'message': 'Logged out'})

@bp.route('/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated and get user data."""
    user_id = session.get('user_id')
    logger.debug(f"Auth check request received for user {user_id}")
    
    if not user_id:
        logger.debug("No user_id in session")
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user_store = get_user_store()
        if not (user_data := user_store.get_user(user_id)):
            logger.warning(f"User {user_id} not found in store")
            session.clear()
            return jsonify({'error': 'User not found'}), 401
        
        # Update session with latest user data
        session['user_data'] = sanitize_user_data(user_data)
        logger.debug(f"Session data for {user_id}: {session.get('user_data')}")
        
        return jsonify({
            'user': sanitize_user_data(user_data)
        })
    except Exception as e:
        logger.error(f"Auth check failed for user {user_id}: {str(e)}")
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