from flask import Blueprint, request, jsonify, session
from ..utils.auth import login_required
from ..utils.settings import get_user_data, log_error
from ..services.calendar import CalendarService
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
    logger.debug("Calendar routes logger initialized")

bp = Blueprint('calendar', __name__, url_prefix='/api/calendar')
calendar_service = CalendarService()

@bp.route('/calendars', methods=['GET'])
@login_required
def get_calendars():
    """Get list of available calendars"""
    logger.debug(f"Calendar list request received for user {session.get('user_id')}")
    try:
        user_data = get_user_data()
        if not user_data:
            logger.warning(f"No user data found for user {session.get('user_id')}")
            return jsonify({'error': 'Not authenticated'}), 401
            
        calendars = calendar_service.get_calendars(user_data)
        logger.debug(f"Calendars retrieved for user {session.get('user_id')}: {calendars}")
        return jsonify(calendars)
    except Exception as e:
        logger.error(f"Failed to get calendars for user {session.get('user_id')}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/events', methods=['GET'])
@login_required
def get_events():
    """Get events for a date range"""
    logger.debug(f"Events request received for user {session.get('user_id')}")
    if not (user_data := get_user_data()):
        logger.warning(f"No user data found for user {session.get('user_id')}")
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        calendar_id = request.args.get('calendarId')
        
        if not start or not end:
            logger.warning(f"Missing date range parameters for user {session.get('user_id')}")
            raise ValueError('Missing date range parameters')
            
        events = calendar_service.get_events(user_data, start, end, calendar_id)
        logger.debug(f"Events retrieved for user {session.get('user_id')}: {events}")
        return jsonify(events)
    except Exception as e:
        logger.error(f"Failed to get events for user {session.get('user_id')}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/events', methods=['POST'])
@login_required
def create_event():
    """Create a new calendar event"""
    logger.debug(f"Create event request received for user {session.get('user_id')}")
    if not (user_data := get_user_data()):
        logger.warning(f"No user data found for user {session.get('user_id')}")
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        calendar_id = request.args.get('calendarId')
        event_data = request.get_json()
        
        if not calendar_id or not event_data:
            logger.warning(f"Missing required parameters for user {session.get('user_id')}")
            raise ValueError('Missing required parameters')
            
        event = calendar_service.create_event(user_data, calendar_id, event_data)
        logger.debug(f"Event created for user {session.get('user_id')}: {event}")
        return jsonify(event)
    except Exception as e:
        logger.error(f"Failed to create event for user {session.get('user_id')}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/events/<event_id>', methods=['PUT'])
@login_required
def update_event(event_id):
    """Update an existing calendar event"""
    logger.debug(f"Update event request received for user {session.get('user_id')}")
    if not (user_data := get_user_data()):
        logger.warning(f"No user data found for user {session.get('user_id')}")
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        calendar_id = request.args.get('calendarId')
        event_data = request.get_json()
        
        if not calendar_id or not event_data:
            logger.warning(f"Missing required parameters for user {session.get('user_id')}")
            raise ValueError('Missing required parameters')
            
        event = calendar_service.update_event(user_data, calendar_id, event_id, event_data)
        logger.debug(f"Event updated for user {session.get('user_id')}: {event}")
        return jsonify(event)
    except Exception as e:
        logger.error(f"Failed to update event for user {session.get('user_id')}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/events/<event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id):
    """Delete a calendar event"""
    logger.debug(f"Delete event request received for user {session.get('user_id')}")
    if not request.args.get('calendar'):
        logger.warning(f"Missing calendar ID for user {session.get('user_id')}")
        return jsonify({'error': 'Calendar ID is required'}), 400
        
    try:
        result = calendar_service.delete_event(get_user_data(), event_id, request.args['calendar'])
        logger.debug(f"Event deleted for user {session.get('user_id')}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Failed to delete event for user {session.get('user_id')}: {str(e)}")
        return jsonify({'error': str(e)}), 400 if isinstance(e, ValueError) else 500 