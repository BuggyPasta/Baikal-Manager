from typing import Dict, Tuple, Optional
import caldav
from urllib.parse import urlparse
import requests
from requests.auth import HTTPDigestAuth, HTTPBasicAuth
from requests.exceptions import ConnectionError, Timeout, SSLError
import time
from functools import wraps
import logging
import os

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Ensure log directory exists
os.makedirs('/data/logs', exist_ok=True)

# Create a file handler
handler = logging.FileHandler('/data/logs/baikal.log', mode='a')
handler.setLevel(logging.DEBUG)

# Also add a stream handler for immediate console output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(handler)
logger.addHandler(console_handler)

# Test log write
logger.debug("Baikal client logger initialized")

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
                    print(f"Connection error: {error_msg}")  # Direct console output
                    if attempt < max_retries - 1:
                        raise ConnectionError(error_msg)
                    time.sleep(delay)
                    continue
            error_msg = f"All {max_retries} connection attempts failed. Last error: {str(last_exception)}"
            logger.error(error_msg)
            print(f"Final error: {error_msg}")  # Direct console output
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
            print(f"Attempting to verify connection to: {settings['serverUrl']}")  # Direct console output
            logger.debug(f"Verifying connection to server: {settings['serverUrl']}")
            
            # Validate URL format and accessibility
            parsed_url = urlparse(settings['serverUrl'])
            if not all([parsed_url.scheme, parsed_url.netloc]):
                msg = f"Invalid URL format: {settings['serverUrl']}"
                print(msg)  # Direct console output
                logger.error(msg)
                return False, "Invalid server URL format"

            # Try a basic HTTP(S) connection first
            try:
                print("Attempting basic HTTP connection...")  # Direct console output
                logger.debug("Attempting basic HTTP connection...")
                
                # Try direct CalDAV connection first
                print("Attempting CalDAV connection...")  # Direct console output
                logger.debug("Attempting CalDAV connection...")
                try:
                    auth_type = settings.get('authType', os.getenv('BAIKAL_AUTH_TYPE', 'basic')).lower()
                    logger.debug(f"Using authentication type: {auth_type}")
                    
                    # Create appropriate auth handler based on type
                    if auth_type == 'digest':
                        auth = HTTPDigestAuth(settings['username'], settings['password'])
                    else:  # default to basic
                        auth = HTTPBasicAuth(settings['username'], settings['password'])
                        
                    client = caldav.DAVClient(
                        url=settings['serverUrl'],
                        username=settings['username'],
                        password=settings['password'],
                        auth=auth
                    )
                    
                    # Test principal connection
                    logger.debug("Testing principal connection...")
                    principal = client.principal()
                    logger.debug("Principal connection successful")
                    
                    # Try to access calendar path
                    logger.debug(f"Verifying calendar path: {settings['calendarPath']}")
                    calendar_path = settings['calendarPath'].lstrip('/')
                    calendars = principal.calendars()
                    calendar_urls = [str(cal.url) for cal in calendars]
                    logger.debug(f"Available calendars: {calendar_urls}")
                    
                    if not any(calendar_path in str(cal) for cal in calendar_urls):
                        msg = f"Calendar path not found: {calendar_path}"
                        logger.error(msg)
                        return False, msg
                    
                    # Try to access address book path
                    logger.debug(f"Verifying address book path: {settings['addressBookPath']}")
                    abook_path = settings['addressBookPath'].lstrip('/')
                    abooks = principal.address_books()
                    abook_urls = [str(ab.url) for ab in abooks]
                    logger.debug(f"Available address books: {abook_urls}")
                    
                    if not any(abook_path in str(ab) for ab in abook_urls):
                        msg = f"Address book path not found: {abook_path}"
                        logger.error(msg)
                        return False, msg
                    
                    logger.debug("All paths verified successfully")
                    return True, None
                    
                except caldav.lib.error.AuthorizationError as e:
                    msg = f"Authentication failed: {str(e)}"
                    logger.error(msg)
                    return False, msg
                except caldav.lib.error.NotFoundError as e:
                    msg = f"Resource not found: {str(e)}"
                    logger.error(msg)
                    return False, msg
                except Exception as e:
                    msg = f"CalDAV connection error: {str(e)}"
                    logger.error(msg)
                    logger.exception("Full traceback:")
                    return False, msg
                
            except SSLError as e:
                msg = f"SSL Error: {str(e)}"
                logger.error(msg)
                return False, "SSL/TLS connection failed. If using local network, ensure URL uses http://"
            except Timeout as e:
                msg = f"Timeout Error: {str(e)}"
                logger.error(msg)
                return False, "Connection timed out. Please check the server URL and network connection"
            except Exception as e:
                msg = f"HTTP connection error: {str(e)}"
                logger.error(msg)
                logger.exception("Full traceback:")
                return False, f"Connection error: {str(e)}"
                
        except Exception as e:
            msg = f"Unexpected error: {str(e)}"
            logger.error(msg)
            logger.exception("Full traceback:")
            return False, f"Unexpected error: {str(e)}"

    def get_client(self) -> caldav.DAVClient:
        """Get the cached client or raise error if not connected"""
        if not self.client:
            raise ValueError("Not connected to Baikal server")
        return self.client 