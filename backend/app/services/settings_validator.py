from typing import Dict, Any
from urllib.parse import urlparse

def validate_baikal_settings(settings: Dict[str, Any]) -> str:
    """Validate Baikal server settings. Returns error message if invalid, None if valid."""
    if not all(settings.get(field) for field in ['serverUrl', 'username', 'password']):
        return "Missing required fields"
    
    try:
        parsed = urlparse(settings['serverUrl'])
        if not all([parsed.scheme, parsed.netloc]):
            return "Invalid server URL"
    except:
        return "Invalid server URL"
    
    return None

def validate_app_settings(settings: Dict[str, Any]) -> str:
    """Validate application settings. Returns error message if invalid, None if valid."""
    if settings.get('theme') and settings['theme'] not in ['light', 'dark']:
        return "Theme must be either 'light' or 'dark'"
    
    if (timeout := settings.get('inactivityTimeout')) is not None:
        try:
            if int(timeout) < 0:
                return "Inactivity timeout cannot be negative"
        except:
            return "Inactivity timeout must be a number"
    
    if settings.get('defaultCalendarView') and settings['defaultCalendarView'] not in ['month', 'week', 'day', 'list']:
        return "Invalid default calendar view"
    
    return None

def validate_user_settings(settings: Dict[str, Any]) -> str:
    """Validate user profile settings. Returns error message if invalid, None if valid."""
    if settings.get('fullName') and not isinstance(settings['fullName'], str):
        return "Full name must be a string"
    
    return None 