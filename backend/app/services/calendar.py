from typing import List, Dict, Optional
from datetime import datetime
import uuid
import icalendar
import pytz
import caldav
from urllib.parse import urljoin

class CalendarService:
    """Service for handling calendar operations"""
    
    def _get_client(self, user_data: Dict) -> caldav.DAVClient:
        creds = user_data.get('baikal_credentials')
        if not creds:
            raise ValueError('Missing Baikal credentials')
            
        # Construct calendar URL
        base_url = creds['serverUrl'].rstrip('/')
        calendar_path = creds.get('calendarPath', '').strip()
        if not calendar_path:
            calendar_path = f"/calendars/{creds['username']}/default/"
        
        calendar_url = urljoin(base_url, calendar_path.lstrip('/'))
            
        return caldav.DAVClient(
            url=calendar_url,
            username=creds['username'],
            password=creds['password']
        )
    
    def _get_calendar(self, user_data: Dict, calendar_id: str = None) -> Optional[caldav.Calendar]:
        client = self._get_client(user_data)
        calendars = client.principal().calendars()
        
        if not calendar_id:
            return calendars[0] if calendars else None
            
        if not (calendar := next((c for c in calendars if c.id == calendar_id), None)):
            raise ValueError('Calendar not found')
        return calendar
    
    def get_calendars(self, user_data: Dict) -> List[Dict]:
        """Get list of available calendars"""
        return [
            {'id': cal.id, 'name': cal.name or 'Calendar'} 
            for cal in self._get_client(user_data).principal().calendars()
        ]
    
    def _make_event(self, title: str, start: datetime, end: datetime, description: str = '', 
                    all_day: bool = False, color: str = 'blue') -> bytes:
        event = icalendar.Calendar()
        event.add('prodid', '-//Baikal Calendar//EN')
        event.add('version', '2.0')
        
        vevent = icalendar.Event()
        vevent.add('uid', str(uuid.uuid4()))
        vevent.add('summary', title)
        vevent.add('description', description)
        vevent.add('dtstart', start.date() if all_day else start)
        vevent.add('dtend', end.date() if all_day else end)
        vevent.add('color', color)
        
        event.add_component(vevent)
        return event.to_ical()
    
    def get_events(self, user_data: Dict, start: str, end: str, calendar_id: str = None) -> List[Dict]:
        """Get events for a date range"""
        if not start or not end:
            raise ValueError('Missing date range parameters')
        
        calendar = self._get_calendar(user_data, calendar_id)
        if not calendar:
            return []
            
        events = calendar.search(
            start=datetime.fromisoformat(start),
            end=datetime.fromisoformat(end),
            event=True,
            expand=True
        )
        
        return [self._event_to_json(event) for event in events]
    
    def _event_to_json(self, event: caldav.Event) -> Dict:
        vcal = icalendar.Calendar.from_ical(event.data)
        vevent = next(comp for comp in vcal.walk() if comp.name == 'VEVENT')
        
        start = vevent.get('dtstart').dt
        end = vevent.get('dtend').dt if vevent.get('dtend') else start
        
        if isinstance(start, datetime):
            start = start.astimezone(pytz.UTC)
            end = end.astimezone(pytz.UTC)
        
        return {
            'id': str(event.id),
            'title': str(vevent.get('summary', '')),
            'description': str(vevent.get('description', '')),
            'start': start.isoformat(),
            'end': end.isoformat(),
            'allDay': not isinstance(start, datetime),
            'color': str(vevent.get('color', 'blue')),
            'calendarId': event.calendar.id
        }
    
    def create_event(self, user_data: Dict, calendar_id: str, event_data: Dict) -> Dict:
        """Create a new calendar event"""
        calendar = self._get_calendar(user_data, calendar_id)
        if not calendar:
            raise ValueError('Calendar not found')
            
        start = datetime.fromisoformat(event_data['start'])
        end = datetime.fromisoformat(event_data['end'])
        
        event = calendar.save_event(
            self._make_event(
                title=event_data.get('title', ''),
                start=start,
                end=end,
                description=event_data.get('description', ''),
                all_day=event_data.get('allDay', False),
                color=event_data.get('color', 'blue')
            )
        )
        return self._event_to_json(event)
    
    def update_event(self, user_data: Dict, calendar_id: str, event_id: str, event_data: Dict) -> Dict:
        """Update an existing calendar event"""
        calendar = self._get_calendar(user_data, calendar_id)
        if not calendar:
            raise ValueError('Calendar not found')
            
        for event in calendar.events():
            if event.id == event_id:
                start = datetime.fromisoformat(event_data['start'])
                end = datetime.fromisoformat(event_data['end'])
                
                event.data = self._make_event(
                    title=event_data.get('title', ''),
                    start=start,
                    end=end,
                    description=event_data.get('description', ''),
                    all_day=event_data.get('allDay', False),
                    color=event_data.get('color', 'blue')
                )
                event.save()
                return self._event_to_json(event)
                
        raise ValueError('Event not found')
    
    def delete_event(self, user_data: Dict, calendar_id: str, event_id: str) -> None:
        """Delete a calendar event"""
        calendar = self._get_calendar(user_data, calendar_id)
        if not calendar:
            raise ValueError('Calendar not found')
            
        for event in calendar.events():
            if event.id == event_id:
                event.delete()
                return
                
        raise ValueError('Event not found') 