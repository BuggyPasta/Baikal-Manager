import json
import os
import logging
from typing import Dict, Any, Optional
from flask import session
from .user_store import get_user_store
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
    """Load user settings from user store"""
    try:
        if user_data := get_user_store().get_user(user_id):
            return user_data
        return {}
    except Exception as e:
        logger.error(f"Failed to load settings for user {user_id}: {str(e)}")
        return {}

def save_settings(user_id: str, settings: Dict[str, Any]) -> None:
    """Save user settings to user store"""
    try:
        get_user_store().update_user(user_id, settings)
        # Update session data after saving
        if user_data := get_user_store().get_user(user_id):
            session['user_data'] = user_data
    except Exception as e:
        logger.error(f"Failed to save settings for user {user_id}: {str(e)}")
        raise

def log_error(user_id: str, error: str) -> None:
    """Log errors through the console logger"""
    logger.error(f"User {user_id}: {error}")

def update_settings(user_id: str, category: str, settings: Dict) -> None:
    """Update settings for a specific category"""
    try:
        if category == 'baikal':
            get_user_store().update_user(user_id, {'baikal_credentials': settings})
        elif category == 'app':
            get_user_store().update_user(user_id, {'app_settings': settings})
        # Update session data after saving
        if user_data := get_user_store().get_user(user_id):
            session['user_data'] = user_data
    except Exception as e:
        logger.error(f"Failed to update {category} settings for user {user_id}: {str(e)}")
        raise

def get_user_data() -> Optional[Dict]:
    """Get user data from session first, falling back to user store if needed"""
    if not (user_id := session.get('user_id')):
        return None
        
    # Try to get data from session first
    if user_data := session.get('user_data'):
        return user_data
        
    # Fall back to user store if session data is missing
    try:
        if user_data := get_user_store().get_user(user_id):
            session['user_data'] = user_data
            return user_data
    except Exception as e:
        logger.error(f"Failed to get user data from store for user {user_id}: {str(e)}")
        
    return None 