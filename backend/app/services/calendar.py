from typing import List, Dict, Optional
from datetime import datetime
import uuid
import icalendar
import pytz
import caldav
from urllib.parse import urljoin
from .baikal_client import BaikalClient
from ..utils.settings import log_error

class CalendarService:
    """Service for handling calendar operations"""
    
    def __init__(self):
        self.baikal_client = BaikalClient()
    
    def _get_client(self, user_data: Dict) -> caldav.DAVClient:
        if not user_data:
            raise ValueError('User data required')
            
        creds = user_data.get('baikal_credentials')
        if not creds:
            raise ValueError('Missing Baikal credentials')
            
        try:
            success, client_or_error = self.baikal_client.verify_connection(creds)
            if not success:
                raise ValueError(f'Connection failed: {client_or_error}')
                
            success, client_or_error = self.baikal_client.get_client()
            if not success:
                raise ValueError(f'Failed to get client: {client_or_error}')
                
            return client_or_error
        except caldav.lib.error.DAVError as e:
            raise ValueError(f"DAV connection error: {str(e)}")
    
    def _get_calendar(self, user_data: Dict, calendar_id: str = None) -> Optional[caldav.Calendar]:
        if not user_data:
            raise ValueError('User data required')
        client = self._get_client(user_data)
        try:
            # Get calendar path from user settings
            creds = user_data.get('baikal_credentials', {})
            calendar_path = creds.get('calendarPath', '/calendars/test/default/')
            
            # Log the path we're trying to access
            log_error(user_data.get('user_id', 'unknown'), f"Attempting to access calendar at path: {calendar_path}")
            
            # Get the calendar directly using the path
            calendar = client.principal().calendar(calendar_path)
            
            if not calendar:
                raise ValueError('Calendar not found')
            
            # Log successful access
            log_error(user_data.get('user_id', 'unknown'), f"Successfully accessed calendar at path: {calendar_path}")
            return calendar
        except caldav.lib.error.DAVError as e:
            log_error(user_data.get('user_id', 'unknown'), f"Failed to access calendar: {str(e)}")
            raise ValueError(f"Failed to access calendar: {str(e)}")
    
    def get_calendars(self, user_data: Dict) -> List[Dict]:
        """Get list of available calendars"""
        client = self._get_client(user_data)
        try:
            # Get calendar path from user settings
            creds = user_data.get('baikal_credentials', {})
            calendar_path = creds.get('calendarPath', '/calendars/test/default/')
            
            # Get the calendar directly using the path
            calendar = client.principal().calendar(calendar_path)
            
            if not calendar:
                raise ValueError('Calendar not found')
            
            return [{
                'id': str(calendar.url),
                'name': calendar.name or 'Calendar'
            }]
        except caldav.lib.error.DAVError as e:
            raise ValueError(f"Failed to fetch calendar: {str(e)}")
    
    def _make_event(self, title: str, start: datetime, end: datetime, description: str = '', 
                    all_day: bool = False, color: str = 'blue', uid: str = None) -> bytes:
        event = icalendar.Calendar()
        event.add('prodid', '-//Baikal Calendar//EN')
        event.add('version', '2.0')
        event.add('calscale', 'GREGORIAN')
        
        vevent = icalendar.Event()
        # Preserve existing UID or create new one
        vevent.add('uid', uid or str(uuid.uuid4()))
        vevent.add('summary', title)
        vevent.add('description', description)
        
        # Ensure timezone-aware dates for non-all-day events
        if all_day:
            vevent.add('dtstart', start.date())
            vevent.add('dtend', end.date())
        else:
            # Ensure UTC timezone for consistency
            start_utc = start.astimezone(pytz.UTC) if start.tzinfo else pytz.UTC.localize(start)
            end_utc = end.astimezone(pytz.UTC) if end.tzinfo else pytz.UTC.localize(end)
            vevent.add('dtstart', start_utc)
            vevent.add('dtend', end_utc)
        
        vevent.add('color', color)
        vevent.add('created', datetime.now(pytz.UTC))
        vevent.add('last-modified', datetime.now(pytz.UTC))
        
        event.add_component(vevent)
        return event.to_ical()
    
    def get_events(self, user_data: Dict, start: str, end: str, calendar_id: str = None) -> List[Dict]:
        """Get events for a date range"""
        if not start or not end:
            raise ValueError('Missing date range parameters')
        
        calendar = self._get_calendar(user_data, calendar_id)
        if not calendar:
            return []
            
        try:
            # Parse dates and ensure they're in UTC
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
            
            # Convert to UTC if they have timezone info
            if start_dt.tzinfo:
                start_dt = start_dt.astimezone(pytz.UTC)
            else:
                start_dt = pytz.UTC.localize(start_dt)
                
            if end_dt.tzinfo:
                end_dt = end_dt.astimezone(pytz.UTC)
            else:
                end_dt = pytz.UTC.localize(end_dt)
            
            # Log the date range we're querying
            log_error(user_data.get('user_id', 'unknown'), f"Fetching events from {start_dt} to {end_dt}")
            
            events = calendar.date_search(
                start=start_dt,
                end=end_dt,
                expand=True,
                comp_filter="VEVENT"  # Explicitly request only events
            )
            
            # Log the number of events found
            log_error(user_data.get('user_id', 'unknown'), f"Found {len(events)} events")
            
            return [self._event_to_json(event) for event in events]
        except caldav.lib.error.DAVError as e:
            log_error(user_data.get('user_id', 'unknown'), f"Failed to fetch events: {str(e)}")
            raise ValueError(f"Failed to fetch events: {str(e)}")
        except ValueError as e:
            raise ValueError(f"Invalid date format: {str(e)}")
    
    def _event_to_json(self, event: caldav.Event) -> Dict:
        try:
            vcal = icalendar.Calendar.from_ical(event.data)
            vevent = next(comp for comp in vcal.walk() if comp.name == 'VEVENT')
            
            start = vevent.get('dtstart').dt
            end = vevent.get('dtend', vevent.get('dtstart')).dt
            
            # Handle both datetime and date objects
            if isinstance(start, datetime):
                start = start.astimezone(pytz.UTC)
                end = end.astimezone(pytz.UTC)
                all_day = False
            else:
                all_day = True
            
            return {
                'id': str(event.url),
                'title': str(vevent.get('summary', '')),
                'description': str(vevent.get('description', '')),
                'start': start.isoformat(),
                'end': end.isoformat(),
                'allDay': all_day,
                'color': str(vevent.get('color', 'blue')),
                'calendarId': str(event.calendar.url)
            }
        except Exception as e:
            raise ValueError(f"Failed to parse event data: {str(e)}")
    
    def create_event(self, user_data: Dict, calendar_id: str, event_data: Dict) -> Dict:
        """Create a new calendar event"""
        calendar = self._get_calendar(user_data, calendar_id)
        if not calendar:
            raise ValueError('Calendar not found')
            
        try:
            start = datetime.fromisoformat(event_data['start'])
            end = datetime.fromisoformat(event_data['end'])
            
            event = calendar.add_event(
                ical=self._make_event(
                    title=event_data.get('title', ''),
                    start=start,
                    end=end,
                    description=event_data.get('description', ''),
                    all_day=event_data.get('allDay', False),
                    color=event_data.get('color', 'blue')
                )
            )
            return self._event_to_json(event)
        except caldav.lib.error.DAVError as e:
            raise ValueError(f"Failed to create event: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to process event data: {str(e)}")
    
    def update_event(self, user_data: Dict, calendar_id: str, event_id: str, event_data: Dict) -> Dict:
        """Update an existing calendar event"""
        calendar = self._get_calendar(user_data, calendar_id)
        if not calendar:
            raise ValueError('Calendar not found')
            
        try:
            for event in calendar.events():
                if str(event.url) == event_id:
                    # Get existing event data to preserve UID
                    existing_vcal = icalendar.Calendar.from_ical(event.data)
                    existing_vevent = next(comp for comp in existing_vcal.walk() if comp.name == 'VEVENT')
                    existing_uid = str(existing_vevent.get('uid'))
                    
                    start = datetime.fromisoformat(event_data['start'])
                    end = datetime.fromisoformat(event_data['end'])
                    
                    event.data = self._make_event(
                        title=event_data.get('title', ''),
                        start=start,
                        end=end,
                        description=event_data.get('description', ''),
                        all_day=event_data.get('allDay', False),
                        color=event_data.get('color', 'blue'),
                        uid=existing_uid
                    )
                    event.save()
                    return self._event_to_json(event)
                    
            raise ValueError('Event not found')
        except caldav.lib.error.DAVError as e:
            raise ValueError(f"Failed to update event: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to process event data: {str(e)}")
    
    def delete_event(self, user_data: Dict, event_id: str, calendar_id: str) -> Dict:
        """Delete a calendar event"""
        calendar = self._get_calendar(user_data, calendar_id)
        if not calendar:
            raise ValueError('Calendar not found')
            
        try:
            # Find the event
            event = None
            for obj in calendar.objects():
                if str(obj.url) == event_id:
                    event = obj
                    break
                    
            if not event:
                raise ValueError('Event not found')
            
            # Delete the event
            event.delete()
            return {'message': 'Event deleted'}
        except caldav.lib.error.DAVError as e:
            raise ValueError(f"Failed to delete event: {str(e)}") 