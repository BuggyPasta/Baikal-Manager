from flask import Blueprint, request, jsonify, session
from ..utils.user_store import get_user_store
from ..config.config import Config
from ..services.baikal_client import BaikalClient
import caldav
import json
from datetime import datetime, timedelta
import logging
from ..utils.auth import login_required
from ..utils.settings import load_settings, save_settings, log_error

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
    logger.debug("Settings routes logger initialized")

bp = Blueprint('settings', __name__, url_prefix='/api/settings')
baikal_client = BaikalClient()

DEFAULT_APP_SETTINGS = {
    'defaultCalendarView': 'month',
    'autoLogoutMinutes': Config.DEFAULT_INACTIVITY_TIMEOUT,
    'theme': Config.DEFAULT_MODE
}

def require_auth():
    if not (user_id := session.get('user_id')):
        return None, {'error': 'Not authenticated'}, 401
    
    if not (user_data := get_user_store().get_user(user_id)):
        return None, {'error': 'User not found'}, 404
    
    return user_id, user_data, None

@bp.route('/baikal', methods=['GET'])
def get_baikal_settings():
    user_id, user_data, error = require_auth()
    if error:
        return jsonify(error), error['code']
    return jsonify(user_data.get('baikal_credentials', {}))

@bp.route('/baikal', methods=['POST'])
def save_baikal_settings():
    user_id, user_data, error = require_auth()
    if error:
        return jsonify(error), error['code']
    
    if not (data := request.get_json()):
        return jsonify({'error': 'No settings provided'}), 400

    # Validate required fields
    required_fields = ['serverUrl', 'username', 'password', 'addressBookPath', 'calendarPath']
    if not all(field in data for field in required_fields):
        return jsonify({
            'error': 'Missing required fields',
            'details': f"Required fields: {', '.join(required_fields)}"
        }), 400
    
    # Verify connection before saving
    success, error_message = baikal_client.verify_connection(data)
    if not success:
        return jsonify({
            'error': 'Connection verification failed',
            'details': error_message
        }), 400
    
    try:
        # Save settings only if connection verification passed
        get_user_store().update_user(user_id, {'baikal_credentials': data})
        logger.debug(f"Settings saved successfully for user {user_id}")
        return jsonify({
            'message': 'Settings saved successfully',
            'settings': {k: v for k, v in data.items() if k != 'password'}
        })
    except Exception as e:
        logger.error(f"Failed to save settings for user {user_id}: {str(e)}")
        return jsonify({
            'error': 'Failed to save settings',
            'details': str(e)
        }), 500

@bp.route('/baikal/verify', methods=['POST'])
def verify_baikal_connection():
    """Endpoint for explicitly testing the connection"""
    logger.debug("Received verification request")
    
    if not (data := request.get_json()):
        logger.error("No settings data provided")
        return jsonify({'error': 'No settings provided'}), 400
    
    # Log the request data (excluding password)
    safe_data = {k: v for k, v in data.items() if k != 'password'}
    logger.debug(f"Verifying connection with settings: {safe_data}")
    
    # Validate required fields
    required_fields = ['serverUrl', 'username', 'password', 'addressBookPath', 'calendarPath']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        error_msg = f"Missing required fields: {', '.join(missing_fields)}"
        logger.error(error_msg)
        return jsonify({
            'error': 'Missing required fields',
            'details': error_msg
        }), 400
    
    try:
        success, error_message = baikal_client.verify_connection(data)
        logger.debug(f"Verification result - Success: {success}, Error: {error_message}")
        
        if success:
            logger.debug("Connection verification successful")
            return jsonify({'message': 'Connection successful'})
        else:
            logger.error(f"Connection verification failed: {error_message}")
            return jsonify({
                'error': 'Connection verification failed',
                'details': error_message
            }), 400
    except ConnectionError as e:
        error_msg = f"Connection error during verification: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'error': 'Connection error',
            'details': str(e)
        }), 400
    except Exception as e:
        error_msg = f"Unexpected error during verification: {str(e)}"
        logger.exception(error_msg)
        return jsonify({
            'error': 'Verification error',
            'details': str(e)
        }), 500

@bp.route('/test-baikal', methods=['POST'])
def test_baikal_connection():
    if not (data := request.get_json()) or not all(k in data for k in ['serverUrl', 'username', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        success, error_message = baikal_client.verify_connection(data)
        if success:
            return jsonify({'message': 'Connected'})
        else:
            return jsonify({'error': error_message}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/app', methods=['GET'])
def get_app_settings():
    user_id, user_data, error = require_auth()
    if error:
        return jsonify(error), error['code']
    return jsonify(user_data.get('app_settings', DEFAULT_APP_SETTINGS))

@bp.route('/app', methods=['POST'])
def save_app_settings():
    user_id, user_data, error = require_auth()
    if error:
        return jsonify(error), error['code']
    
    if not (data := request.get_json()):
        return jsonify({'error': 'No settings provided'}), 400
    
    try:
        get_user_store().update_user(user_id, {'app_settings': data})
        return jsonify({'message': 'Settings saved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['GET'])
def get_settings():
    user_id, user_data, error = require_auth()
    if error:
        return jsonify(error), error['code']
    
    # Combine all settings
    settings = {
        'baikal': user_data.get('baikal_credentials', {}),
        'app': user_data.get('app_settings', DEFAULT_APP_SETTINGS)
    }
    return jsonify(settings)

@bp.route('/', methods=['POST'])
def save_settings():
    user_id, user_data, error = require_auth()
    if error:
        return jsonify(error), error['code']
    
    if not (data := request.get_json()):
        return jsonify({'error': 'No settings provided'}), 400
    
    try:
        # Update user with combined settings
        updates = {}
        if 'baikal' in data:
            updates['baikal_credentials'] = data['baikal']
        if 'app' in data:
            updates['app_settings'] = data['app']
            
        get_user_store().update_user(user_id, updates)
        return jsonify({'message': 'Settings saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/load', methods=['GET'])
@login_required
def get_settings_load():
    """Load user settings."""
    logger.debug(f"Settings load request received for user {session.get('user_id')}")
    try:
        settings = load_settings()
        logger.debug(f"Settings loaded for user {session.get('user_id')}: {settings}")
        return jsonify(settings)
    except Exception as e:
        logger.error(f"Failed to load settings for user {session.get('user_id')}: {str(e)}")
        return jsonify({'error': 'Failed to load settings'}), 500

@bp.route('/save', methods=['POST'])
@login_required
def save_user_settings():
    """Save user settings."""
    logger.debug(f"Settings save request received for user {session.get('user_id')}")
    if not request.json:
        return jsonify({'error': 'No settings data provided'}), 400
    
    try:
        settings = request.json
        logger.debug(f"Settings to save for user {session.get('user_id')}: {settings}")
        save_settings(settings)
        logger.debug(f"Settings saved successfully for user {session.get('user_id')}")
        return jsonify({'message': 'Settings saved'})
    except Exception as e:
        logger.error(f"Failed to save settings for user {session.get('user_id')}: {str(e)}")
        return jsonify({'error': 'Failed to save settings'}), 500

def log_error(username: str, message: str):
    """Log errors through the console logger"""
    logger.error(f"User {username}: {message}") 