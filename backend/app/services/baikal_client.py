from typing import Dict, Tuple, Optional, Union
import logging
import threading
import time
from functools import wraps
from urllib.parse import urlparse, urljoin

import caldav
from caldav.davclient import DAVClient
import requests
from requests.auth import HTTPDigestAuth, HTTPBasicAuth
from requests.exceptions import ConnectionError, Timeout, SSLError
from caldav.objects import Principal
from urllib.parse import unquote
from pathlib import Path

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
    logger.debug("Baikal client logger initialized")

def normalize_url_path(path: str) -> str:
    """Normalize a URL path for consistent comparison"""
    # Ensure path starts with a slash
    if not path.startswith('/'):
        path = '/' + path
    # Remove trailing slash
    path = path.rstrip('/')
    # Normalize multiple slashes while preserving leading slash
    parts = path.split('/')
    return '/' + '/'.join(filter(None, parts))

def retry_on_connection_error(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    success, error_msg = func(*args, **kwargs)
                    # Don't retry on validation errors, auth failures, or missing resources
                    if success or any(x in str(error_msg) for x in [
                        "Invalid server URL format",
                        "Missing required fields",
                        "Authentication failed",
                        "not found",
                        "path mismatch",
                        "No calendars found"
                    ]):
                        return success, error_msg
                    # Only retry on connection/timeout issues
                    last_error = error_msg
                    if attempt < max_retries - 1:
                        error_msg += f". Retrying in {delay} seconds..."
                        logger.error(error_msg)
                        time.sleep(delay)
                        continue
                    break
                except (ConnectionError, Timeout, SSLError, requests.exceptions.RequestException) as e:
                    last_error = str(e)
                    error_msg = f"Attempt {attempt + 1}/{max_retries} failed: {last_error}"
                    if attempt < max_retries - 1:
                        error_msg += f". Retrying in {delay} seconds..."
                        logger.error(error_msg)
                        time.sleep(delay)
                        continue
                    break
            return False, f"All attempts failed. Last error: {last_error}"
        return wrapper
    return decorator

class BaikalClient:
    def __init__(self):
        self._client = None
        self._lock = threading.Lock()
        
    @property
    def client(self) -> Optional[caldav.DAVClient]:
        """Thread-safe access to the client"""
        with self._lock:
            return self._client
            
    @client.setter
    def client(self, value: Optional[caldav.DAVClient]):
        """Thread-safe setting of the client"""
        with self._lock:
            self._client = value
        
    def verify_connection(self, settings: Dict) -> Tuple[bool, Optional[str]]:
        """
        Verify connection to Baikal server with detailed error handling
        Returns: (success: bool, error_message: Optional[str])
        """
        # Clear any existing client before verification
        self.client = None
        
        try:
            # Validate required fields
            required_fields = ['serverUrl', 'username', 'password', 'addressBookPath', 'calendarPath']
            missing_fields = [field for field in required_fields if not settings.get(field)]
            if missing_fields:
                msg = f"Missing required fields: {', '.join(missing_fields)}"
                logger.error(msg)
                return False, msg

            logger.debug(f"Verifying connection to server: {settings['serverUrl']}")
            
            # Validate URL format
            parsed_url = urlparse(settings['serverUrl'])
            if not all([parsed_url.scheme, parsed_url.netloc]):
                msg = f"Invalid URL format: {settings['serverUrl']}"
                logger.error(msg)
                return False, "Invalid server URL format"

            # Create authentication handler
            auth_type = settings.get('authType', 'digest').lower()
            verify_ssl = settings.get('verifySSL', False)  # Default to False for local development
            logger.debug(f"Using authentication type: {auth_type}, SSL verification: {verify_ssl}")
            
            if auth_type == 'basic':
                auth = HTTPBasicAuth(settings['username'], settings['password'])
            else:  # default to digest
                auth = HTTPDigestAuth(settings['username'], settings['password'])
                
            # Create a single client for verification and use
            self.client = caldav.DAVClient(
                url=settings['serverUrl'],
                auth=auth,
                verify=verify_ssl
            )
            
            # Test principal connection
            logger.debug("Testing principal connection...")
            principal = self.client.principal()
            logger.debug("Principal connection successful")
            
            # Verify address book path first (simpler check)
            logger.debug(f"Verifying address book path: {settings['addressBookPath']}")
            abook_path = normalize_url_path(settings['addressBookPath'])
            
            # Get all addressbooks and verify the path exists
            addressbooks = principal.address_books()
            if not addressbooks:
                msg = "No address books found on server"
                logger.error(msg)
                self.client = None
                return False, msg
                
            # Check if the requested path exists
            abook_found = False
            for book in addressbooks:
                book_path = normalize_url_path(urlparse(str(book.url)).path)
                if book_path == abook_path or book_path + '/' == abook_path or book_path == abook_path + '/':
                    abook_found = True
                    break
                    
            if not abook_found:
                msg = f"Address book not found at: {settings['addressBookPath']}"
                logger.error(msg)
                self.client = None
                return False, msg
                
            logger.debug("Address book access verified")
            
            # Now verify calendar path
            logger.debug(f"Verifying calendar path: {settings['calendarPath']}")
            calendar_path = normalize_url_path(settings['calendarPath'])
            
            # Get calendar homes first
            cal_homes = principal.calendar_homes()
            if not cal_homes:
                msg = "No calendar homes found on server"
                logger.error(msg)
                self.client = None
                return False, msg
                
            # Get all calendars from all homes
            calendars = []
            for home in cal_homes:
                calendars.extend(home.calendars())
            
            calendar_urls = [str(cal.url) for cal in calendars]
            
            if not calendar_urls:
                msg = "No calendars found on server. Please create a calendar first."
                logger.error(msg)
                self.client = None
                return False, msg
                
            logger.debug(f"Available calendars: {calendar_urls}")
            
            # More precise calendar path verification
            calendar_found = False
            for cal_url in calendar_urls:
                cal_path = normalize_url_path(urlparse(cal_url).path)
                if cal_path == calendar_path or cal_path + '/' == calendar_path or cal_path == calendar_path + '/':
                    calendar_found = True
                    break
            
            if not calendar_found:
                msg = f"Calendar path not found: {settings['calendarPath']}"
                logger.error(msg)
                self.client = None
                return False, msg
            
            logger.debug("All paths verified successfully")
            
            return True, None
                
        except caldav.lib.error.AuthorizationError as e:
            msg = f"Authentication failed: {str(e)}"
            logger.error(msg)
            self.client = None
            return False, msg
        except caldav.lib.error.NotFoundError as e:
            msg = f"Resource not found: {str(e)}"
            logger.error(msg)
            self.client = None
            return False, msg
        except (ConnectionError, Timeout, SSLError) as e:
            msg = f"Connection error: {str(e)}"
            logger.error(msg)
            self.client = None
            return False, msg
        except caldav.lib.error.DAVError as e:
            msg = f"Baikal server error: {str(e)}"
            logger.error(msg)
            self.client = None
            return False, msg
        except Exception as e:
            msg = f"Unexpected error: {str(e)}"
            logger.error(msg)
            self.client = None
            return False, msg

    def get_client(self) -> Tuple[bool, Union[caldav.DAVClient, str]]:
        """Thread-safe access to get the cached client or return error tuple"""
        client = self.client
        if not client:
            return False, "Not connected to Baikal server"
        return True, client 