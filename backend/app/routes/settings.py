from flask import Blueprint, request, jsonify, session
from ..utils.user_store import get_user_store
from ..config.config import Config
from ..services.baikal_client import BaikalClient
import caldav
import os
import json
from datetime import datetime, timedelta
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a file handler
handler = logging.FileHandler('/data/logs/settings.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

bp = Blueprint('settings', __name__, url_prefix='/api/settings')
baikal_client = BaikalClient()

DEFAULT_APP_SETTINGS = {
    'defaultCalendarView': 'month',
    'autoLogoutMinutes': Config.DEFAULT_INACTIVITY_TIMEOUT,
    'theme': Config.DEFAULT_MODE
}

def get_logs_path(username: str) -> str:
    return os.path.join(Config.LOG_PATH, f'{username}.log')

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
        return jsonify({
            'message': 'Settings saved successfully',
            'settings': data
        })
    except Exception as e:
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
        logger.error(f"Connection error during verification: {str(e)}")
        return jsonify({
            'error': 'Connection error',
            'details': str(e)
        }), 400
    except Exception as e:
        logger.exception("Unexpected error during verification")
        return jsonify({
            'error': 'Verification error',
            'details': str(e)
        }), 500

@bp.route('/test-baikal', methods=['POST'])
def test_baikal_connection():
    if not (data := request.get_json()) or not all(k in data for k in ['serverUrl', 'username', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        caldav.DAVClient(
            url=data['serverUrl'],
            username=data['username'],
            password=data['password']
        ).principal()
        return jsonify({'message': 'Connected'})
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

@bp.route('/logs', methods=['GET'])
def get_logs():
    user_id, user_data, error = require_auth()
    if error:
        return jsonify(error), error['code']
    
    logs_path = get_logs_path(user_id)
    if not os.path.exists(logs_path):
        return jsonify([])
    
    try:
        one_month_ago = datetime.now() - timedelta(days=30)
        logs = []
        with open(logs_path, 'r') as f:
            for line in f:
                try:
                    if (log := json.loads(line)) and datetime.fromtimestamp(log['timestamp']) > one_month_ago:
                        logs.append(log)
                except:
                    continue
        return jsonify(logs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/logs', methods=['DELETE'])
def clear_logs():
    user_id, user_data, error = require_auth()
    if error:
        return jsonify(error), error['code']
    
    try:
        logs_path = get_logs_path(user_id)
        if os.path.exists(logs_path):
            os.remove(logs_path)
        return jsonify({'message': 'Logs cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def log_error(username: str, message: str):
    try:
        logs_path = get_logs_path(username)
        os.makedirs(os.path.dirname(logs_path), exist_ok=True)
        with open(logs_path, 'a') as f:
            json.dump({'timestamp': datetime.now().timestamp(), 'message': message}, f)
            f.write('\n')
    except:
        pass  # Fail silently as this is just logging 