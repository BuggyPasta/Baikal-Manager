from flask import Blueprint, request, jsonify, session
from ..utils.auth import login_required
from ..utils.settings import get_user_data, log_error
from ..services.calendar import CalendarService

bp = Blueprint('calendar', __name__, url_prefix='/api/calendar')
calendar_service = CalendarService()

@bp.route('/calendars', methods=['GET'])
@login_required
def get_calendars():
    """Get list of available calendars"""
    try:
        return jsonify(calendar_service.get_calendars(get_user_data()))
    except Exception as e:
        log_error(session.get('user_id', 'unknown'), str(e))
        return jsonify({'error': str(e)}), 500

@bp.route('/events', methods=['GET'])
@login_required
def get_events():
    """Get events for a date range"""
    if not (user_data := get_user_data()):
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        calendar_id = request.args.get('calendarId')
        
        if not start or not end:
            raise ValueError('Missing date range parameters')
            
        return jsonify(calendar_service.get_events(user_data, start, end, calendar_id))
    except Exception as e:
        log_error(session.get('user_id', 'unknown'), str(e))
        return jsonify({'error': str(e)}), 500

@bp.route('/events', methods=['POST'])
@login_required
def create_event():
    """Create a new calendar event"""
    if not (user_data := get_user_data()):
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        calendar_id = request.args.get('calendarId')
        event_data = request.get_json()
        
        if not calendar_id or not event_data:
            raise ValueError('Missing required parameters')
            
        return jsonify(calendar_service.create_event(user_data, calendar_id, event_data))
    except Exception as e:
        log_error(session.get('user_id', 'unknown'), str(e))
        return jsonify({'error': str(e)}), 500

@bp.route('/events/<event_id>', methods=['PUT'])
@login_required
def update_event(event_id):
    """Update an existing calendar event"""
    if not (user_data := get_user_data()):
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        calendar_id = request.args.get('calendarId')
        event_data = request.get_json()
        
        if not calendar_id or not event_data:
            raise ValueError('Missing required parameters')
            
        return jsonify(calendar_service.update_event(user_data, calendar_id, event_id, event_data))
    except Exception as e:
        log_error(session.get('user_id', 'unknown'), str(e))
        return jsonify({'error': str(e)}), 500

@bp.route('/events/<event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id):
    """Delete a calendar event"""
    if not request.args.get('calendar'):
        return jsonify({'error': 'Calendar ID is required'}), 400
        
    try:
        return jsonify(calendar_service.delete_event(get_user_data(), event_id, request.args['calendar']))
    except Exception as e:
        log_error(session.get('user_id', 'unknown'), str(e))
        return jsonify({'error': str(e)}), 400 if isinstance(e, ValueError) else 500 