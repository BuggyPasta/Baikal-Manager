from typing import Dict, Tuple, Optional
import caldav
from urllib.parse import urlparse
import requests
from requests.exceptions import ConnectionError, Timeout, SSLError
import time
from functools import wraps

def retry_on_connection_error(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (ConnectionError, Timeout) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        # Include retry information in the error
                        error_msg = f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}. Retrying in {delay} seconds..."
                        raise ConnectionError(error_msg)
                    time.sleep(delay)
                    continue
            # Final failure message
            error_msg = f"All {max_retries} connection attempts failed. Last error: {str(last_exception)}"
            raise ConnectionError(error_msg)
        return wrapper
    return decorator

class BaikalClient:
    def __init__(self):
        self.client = None
        
    @retry_on_connection_error()
    def verify_connection(self, settings: Dict) -> Tuple[bool, Optional[str]]:
        """
        Verify connection to Baikal server with detailed error handling
        Returns: (success: bool, error_message: Optional[str])
        """
        try:
            # Validate URL format and accessibility
            parsed_url = urlparse(settings['serverUrl'])
            if not all([parsed_url.scheme, parsed_url.netloc]):
                return False, "Invalid server URL format"

            # Try a basic HTTP(S) connection first
            try:
                response = requests.get(settings['serverUrl'], timeout=5)
                if response.status_code >= 400:
                    return False, f"Server returned error: {response.status_code}"
                
                # Check if we're getting a DAV response
                content_type = response.headers.get('Content-Type', '').lower()
                if not any(t in content_type for t in ['dav', 'xml', 'text/plain']):
                    return False, "Server response doesn't appear to be a CalDAV/CardDAV server. Please check the URL and ensure it points to the DAV endpoint (usually ending in dav.php)"
                
            except SSLError:
                return False, "SSL/TLS connection failed. If using local network, ensure URL uses http://"
            except Timeout:
                return False, "Connection timed out. Please check the server URL and network connection"
            except ConnectionError:
                return False, "Could not connect to server. Please verify the URL and server status"

            # Try CalDAV connection
            client = caldav.DAVClient(
                url=settings['serverUrl'],
                username=settings['username'],
                password=settings['password']
            )
            
            # Verify principal
            principal = client.principal()
            
            # Verify calendar path
            calendars = principal.calendars()
            calendar_path = settings['calendarPath'].lstrip('/')
            calendar_found = any(calendar_path in cal.url for cal in calendars)
            if not calendar_found:
                return False, f"Calendar path '{settings['calendarPath']}' not found"
            
            # Verify addressbook path
            addressbooks = principal.addressbooks()
            addressbook_path = settings['addressBookPath'].lstrip('/')
            addressbook_found = any(addressbook_path in book.url for book in addressbooks)
            if not addressbook_found:
                return False, f"Address book path '{settings['addressBookPath']}' not found"
            
            # Store client if all verifications pass
            self.client = client
            return True, None
            
        except caldav.lib.error.AuthenticationError:
            return False, "Authentication failed. Please check username and password"
        except caldav.lib.error.NotFoundError:
            return False, "Server URL not found. Please check the URL"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def get_client(self) -> caldav.DAVClient:
        """Get the cached client or raise error if not connected"""
        if not self.client:
            raise ValueError("Not connected to Baikal server")
        return self.client 