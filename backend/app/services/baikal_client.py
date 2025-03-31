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
                ssl_verify_cert=verify_ssl
            )
            
            # Test principal connection
            logger.debug("Testing principal connection...")
            principal = self.client.principal()
            logger.debug("Principal connection successful")
            
            # Verify address book path first (simpler check)
            logger.debug(f"Verifying address book path: {settings['addressBookPath']}")
            abook_path = normalize_url_path(settings['addressBookPath'])
            
            # Use principal to get the root URL and verify paths
            root_url = str(principal.url)
            logger.debug(f"Principal root URL: {root_url}")
            
            # Verify addressbook path exists
            try:
                # Build the full URL properly based on the principal URL
                principal_path = urlparse(root_url).path
                base_path = principal_path.split('/principals/')[0]  # Get the base DAV path
                abook_url = urljoin(settings['serverUrl'], base_path + abook_path)
                
                logger.debug(f"Checking address book URL: {abook_url}")
                response = requests.get(abook_url, auth=auth, verify=verify_ssl)
                
                if response.status_code == 404:
                    msg = f"Address book not found at: {settings['addressBookPath']}"
                    logger.error(msg)
                    self.client = None
                    return False, msg
                elif response.status_code == 401:
                    msg = "Authentication failed for address book access"
                    logger.error(msg)
                    self.client = None
                    return False, msg
                elif response.status_code >= 400:
                    msg = f"Error accessing address book: HTTP {response.status_code}"
                    logger.error(msg)
                    self.client = None
                    return False, msg
                    
                logger.debug("Address book access verified")
                
            except Exception as e:
                msg = f"Error accessing address book: {str(e)}"
                logger.error(msg)
                self.client = None
                return False, msg
            
            # Now verify calendar path
            logger.debug(f"Verifying calendar path: {settings['calendarPath']}")
            calendar_path = normalize_url_path(settings['calendarPath'])
            
            # Use the same approach that worked for address books
            try:
                # Build the calendar URL using the same base path
                calendar_url = urljoin(settings['serverUrl'], base_path + calendar_path)
                
                logger.debug(f"Checking calendar URL: {calendar_url}")
                response = requests.get(calendar_url, auth=auth, verify=verify_ssl)
                
                if response.status_code == 404:
                    msg = f"Calendar not found at: {settings['calendarPath']}"
                    logger.error(msg)
                    self.client = None
                    return False, msg
                elif response.status_code == 401:
                    msg = "Authentication failed for calendar access"
                    logger.error(msg)
                    self.client = None
                    return False, msg
                elif response.status_code >= 400:
                    msg = f"Error accessing calendar: HTTP {response.status_code}"
                    logger.error(msg)
                    self.client = None
                    return False, msg
                    
                logger.debug("Calendar access verified")
                logger.debug("All paths verified successfully")
                
                return True, None
                
            except Exception as e:
                msg = f"Error accessing calendar: {str(e)}"
                logger.error(msg)
                self.client = None
                return False, msg
                
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
        """Get the current client or create a new one"""
        if self.client:
            return True, self.client
        return False, "Client not initialized" 