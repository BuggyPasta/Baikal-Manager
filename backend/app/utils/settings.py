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

def load_settings():
    """Load user settings from the user store."""
    user_id = session.get('user_id')
    logger.debug(f"Loading settings for user {user_id}")
    
    try:
        user_store = get_user_store()
        user_data = user_store.get_user(user_id)
        
        if not user_data:
            logger.warning(f"No user data found for user {user_id}")
            return None
            
        logger.debug(f"Settings loaded for user {user_id}: {user_data}")
        return user_data
    except Exception as e:
        logger.error(f"Failed to load settings for user {user_id}: {str(e)}")
        raise

def save_settings(settings):
    """Save user settings to the user store."""
    user_id = session.get('user_id')
    logger.debug(f"Saving settings for user {user_id}")
    
    try:
        user_store = get_user_store()
        user_data = user_store.get_user(user_id)
        
        if not user_data:
            logger.warning(f"No user data found for user {user_id}")
            return
            
        # Update user data with new settings
        user_data.update(settings)
        user_store.update_user(user_id, user_data)
        
        # Update session with new user data
        session['user_data'] = user_data
        
        logger.debug(f"Settings saved for user {user_id}: {user_data}")
    except Exception as e:
        logger.error(f"Failed to save settings for user {user_id}: {str(e)}")
        raise

def log_error(username: str, message: str):
    """Log errors through the console logger"""
    logger.error(f"Error for user {username}: {message}")

def update_settings(settings):
    """Update specific settings while preserving others."""
    user_id = session.get('user_id')
    logger.debug(f"Updating settings for user {user_id}")
    
    try:
        current_settings = load_settings()
        if not current_settings:
            logger.warning(f"No current settings found for user {user_id}")
            return
            
        # Update only the specified settings
        current_settings.update(settings)
        save_settings(current_settings)
        
        logger.debug(f"Settings updated for user {user_id}: {current_settings}")
    except Exception as e:
        logger.error(f"Failed to update settings for user {user_id}: {str(e)}")
        raise

def get_user_data():
    """Get the current user's data from the session, falling back to user store if needed."""
    user_id = session.get('user_id')
    logger.debug(f"Getting user data for user {user_id}")
    
    try:
        # Try to get data from session first
        user_data = session.get('user_data')
        if user_data:
            logger.debug(f"User data retrieved from session for user {user_id}: {user_data}")
            return user_data
            
        # Fall back to user store if session data is missing
        logger.debug(f"No session data found for user {user_id}, trying user store")
        user_store = get_user_store()
        user_data = user_store.get_user(user_id)
        
        if not user_data:
            logger.warning(f"No user data found in store for user {user_id}")
            return None
            
        # Update session with data from store
        session['user_data'] = user_data
        logger.debug(f"User data retrieved from store for user {user_id}: {user_data}")
        return user_data
    except Exception as e:
        logger.error(f"Failed to get user data for user {user_id}: {str(e)}")
        return None

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