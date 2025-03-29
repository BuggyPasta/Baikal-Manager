import json
import os
import logging
from typing import Dict, Any, Optional
from flask import session
from .encryption import encrypt_data, decrypt_data
from ..config.config import Config

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
    logger.debug("Settings utils logger initialized")

def load_settings(user_id: str) -> Dict[str, Any]:
    """Load user settings from file"""
    path = os.path.join(Config.DATA_PATH, f"{user_id}_settings.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            return decrypt_data(data) if data else {}
    except (OSError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load settings for user {user_id}: {str(e)}")
        return {}

def save_settings(user_id: str, settings: Dict[str, Any]) -> None:
    """Save user settings to file"""
    path = os.path.join(Config.DATA_PATH, f"{user_id}_settings.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(encrypt_data(settings), f)

def log_error(user_id: str, error: str) -> None:
    """Log errors through the console logger"""
    logger.error(f"User {user_id}: {error}")

def update_settings(user_id: str, category: str, settings: Dict) -> None:
    """Update settings for a specific category"""
    current = load_settings(user_id)
    current[category] = settings
    save_settings(user_id, current)

def get_user_data() -> Optional[Dict]:
    """Get user data from session using user_id"""
    if not (user_id := session.get('user_id')):
        return None
    return load_settings(user_id) 