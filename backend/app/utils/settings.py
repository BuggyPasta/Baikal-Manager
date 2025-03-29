import json
import os
from typing import Dict, Any
from .encryption import encrypt_data, decrypt_data
from ..config.config import Config

def load_settings(user_id: str) -> Dict[str, Any]:
    """Load user settings from file"""
    path = os.path.join(Config.DATA_PATH, f"{user_id}_settings.json")
    if not os.path.exists(path):
        return {}
    with open(path, 'r') as f:
        data = json.load(f)
        return decrypt_data(data) if data else {}

def save_settings(user_id: str, settings: Dict[str, Any]) -> None:
    """Save user settings to file"""
    path = os.path.join(Config.DATA_PATH, f"{user_id}_settings.json")
    with open(path, 'w') as f:
        json.dump(encrypt_data(settings), f)

def log_error(username: str, error: str) -> None:
    """Simple error logging"""
    path = os.path.join(Config.DATA_PATH, 'logs', f"{username}_errors.log")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a') as f:
        f.write(f"{error}\n")

def get_logs(user_id: str) -> str:
    """Get user logs"""
    path = os.path.join(Config.DATA_PATH, 'logs', f"{user_id}_errors.log")
    if not os.path.exists(path):
        return ""
    with open(path, 'r') as f:
        return f.read()

def clear_logs(user_id: str) -> None:
    """Clear user logs"""
    path = os.path.join(Config.DATA_PATH, 'logs', f"{user_id}_errors.log")
    if os.path.exists(path):
        os.remove(path)

def get_baikal_settings(username: str) -> Optional[Dict]:
    return load_settings(username).get('baikal')

def update_settings(username: str, category: str, settings: Dict) -> bool:
    current = load_settings(username)
    current[category] = settings
    return save_settings(username, current)

def get_settings(username: str = None) -> Optional[Dict]:
    if not username:
        from flask import session
        username = session.get('username')
    try:
        return load_settings(username) if username else None
    except ValueError:
        return None 