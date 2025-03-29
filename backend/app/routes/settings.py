from flask import Blueprint, request, jsonify, session
from ..utils.user_store import get_user_store
from ..config.config import Config
import caldav
import os
import json
from datetime import datetime, timedelta

bp = Blueprint('settings', __name__, url_prefix='/api/settings')

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
    
    if not (data := request.get_json()) or not all(k in data for k in ['serverUrl', 'username', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        get_user_store().update_user(user_id, {'baikal_credentials': data})
        return jsonify({'message': 'Settings saved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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