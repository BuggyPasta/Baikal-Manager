from typing import Dict, Tuple, Optional
import caldav
from urllib.parse import urlparse
import requests
from requests.exceptions import ConnectionError, Timeout, SSLError
import time
from functools import wraps
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a file handler
handler = logging.FileHandler('/data/logs/baikal.log')
handler.setLevel(logging.DEBUG)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

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
                    error_msg = f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}. Retrying in {delay} seconds..."
                    logger.error(error_msg)
                    if attempt < max_retries - 1:
                        raise ConnectionError(error_msg)
                    time.sleep(delay)
                    continue
            error_msg = f"All {max_retries} connection attempts failed. Last error: {str(last_exception)}"
            logger.error(error_msg)
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
            logger.debug(f"Verifying connection to server: {settings['serverUrl']}")
            
            # Validate URL format and accessibility
            parsed_url = urlparse(settings['serverUrl'])
            if not all([parsed_url.scheme, parsed_url.netloc]):
                logger.error(f"Invalid URL format: {settings['serverUrl']}")
                return False, "Invalid server URL format"

            # Try a basic HTTP(S) connection first
            try:
                logger.debug("Attempting basic HTTP connection...")
                response = requests.get(settings['serverUrl'], timeout=5)
                content_type = response.headers.get('Content-Type', '').lower()
                
                # Log response details
                logger.debug(f"Server Response - Status: {response.status_code}")
                logger.debug(f"Content-Type: {content_type}")
                logger.debug(f"Response Headers: {dict(response.headers)}")
                logger.debug(f"Response Content: {response.text[:200]}...")
                
                if response.status_code >= 400:
                    logger.error(f"Server error response: {response.status_code}")
                    return False, f"Server returned error: {response.status_code}"
                
                # Check if we're getting a DAV response
                if not any(t in content_type for t in ['dav', 'xml', 'text/plain']):
                    logger.error(f"Invalid content type: {content_type}")
                    return False, f"Server response doesn't appear to be a CalDAV/CardDAV server (Content-Type: {content_type})"

                # Try CalDAV connection
                logger.debug("Attempting CalDAV connection...")
                try:
                    client = caldav.DAVClient(
                        url=settings['serverUrl'],
                        username=settings['username'],
                        password=settings['password']
                    )
                    principal = client.principal()
                    logger.debug("CalDAV connection successful")
                    
                    # Try to access calendar path
                    logger.debug(f"Verifying calendar path: {settings['calendarPath']}")
                    calendar_path = settings['calendarPath'].lstrip('/')
                    calendars = [cal.url for cal in principal.calendars()]
                    logger.debug(f"Available calendars: {calendars}")
                    if not any(calendar_path in cal for cal in calendars):
                        logger.error(f"Calendar path not found: {calendar_path}")
                        return False, f"Calendar path not found: {calendar_path}"
                    
                    # Try to access address book path
                    logger.debug(f"Verifying address book path: {settings['addressBookPath']}")
                    abook_path = settings['addressBookPath'].lstrip('/')
                    abooks = [ab.url for ab in principal.address_books()]
                    logger.debug(f"Available address books: {abooks}")
                    if not any(abook_path in ab for ab in abooks):
                        logger.error(f"Address book path not found: {abook_path}")
                        return False, f"Address book path not found: {abook_path}"
                    
                    return True, None
                    
                except Exception as e:
                    logger.error(f"CalDAV connection error: {str(e)}")
                    return False, f"CalDAV connection failed: {str(e)}"
                
            except SSLError as e:
                logger.error(f"SSL Error: {str(e)}")
                return False, "SSL/TLS connection failed. If using local network, ensure URL uses http://"
            except Timeout as e:
                logger.error(f"Timeout Error: {str(e)}")
                return False, "Connection timed out. Please check the server URL and network connection"
            except Exception as e:
                logger.error(f"HTTP connection error: {str(e)}")
                return False, f"Connection error: {str(e)}"
                
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return False, f"Unexpected error: {str(e)}"

    def get_client(self) -> caldav.DAVClient:
        """Get the cached client or raise error if not connected"""
        if not self.client:
            raise ValueError("Not connected to Baikal server")
        return self.client 