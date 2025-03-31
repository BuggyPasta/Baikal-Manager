import json
import time
import os
import fcntl
import logging
from typing import Dict, Optional, List
from ..config.config import Config

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class UserStore:
    def __init__(self):
        self.file_path = Config.get_path('users.json')
        self.backup_path = Config.get_path('users.json.bak')
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def _load_users(self) -> List[Dict]:
        try:
            with open(self.file_path, 'r') as f:
                # Get an exclusive lock for reading
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    data = json.load(f)
                    return data.get('users', [])
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error reading users.json: {str(e)}")
            # Try to recover from backup
            if os.path.exists(self.backup_path):
                logger.info("Attempting to recover from backup")
                with open(self.backup_path, 'r') as f:
                    try:
                        return json.load(f).get('users', [])
                    except:
                        logger.error("Backup recovery failed")
            return []

    def _save_users(self, users: List[Dict]) -> None:
        # Create a backup of the current file if it exists
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as src, open(self.backup_path, 'w') as dst:
                    dst.write(src.read())
            except Exception as e:
                logger.error(f"Failed to create backup: {str(e)}")

        # Save the new data with locking
        with open(self.file_path, 'w') as f:
            # Get an exclusive lock for writing
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump({'users': users}, f, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def get_users(self) -> List[Dict]:
        return [{
            'username': u['username'],
            'fullName': u['fullName'],
            'last_login': u['last_login']
        } for u in self._load_users()]

    def get_user(self, username: str) -> Optional[Dict]:
        if user := next((u for u in self._load_users() if u['username'] == username), None):
            # Create a copy of the user data to avoid modifying the original
            return user.copy()
        return None

    def create_user(self, username: str, password: str, full_name: str) -> Dict:
        if self.get_user(username):
            raise ValueError('Username already exists')
        
        user = {
            'username': username,
            'password': password,
            'fullName': full_name,
            'created_at': time.time(),
            'last_login': None,
            'baikal_credentials': None
        }
        
        users = self._load_users()
        users.append(user)
        self._save_users(users)
        return user

    def update_user(self, username: str, data: Dict) -> Dict:
        users = self._load_users()
        if not (user := next((u for u in users if u['username'] == username), None)):
            raise ValueError('User not found')
        
        # Create a copy of the user data to avoid modifying the original
        updated_user = user.copy()
        updated_user.update(data)
        
        # Update the user in the list
        users = [updated_user if u['username'] == username else u for u in users]
        self._save_users(users)
        
        return self.get_user(username)

    def delete_user(self, username: str) -> bool:
        users = self._load_users()
        new_users = [u for u in users if u['username'] != username]
        if len(new_users) < len(users):
            self._save_users(new_users)
            return True
        return False

    def update_last_login(self, username: str) -> None:
        self.update_user(username, {'last_login': time.time()})

_store = None

def get_user_store() -> UserStore:
    global _store
    if _store is None:
        _store = UserStore()
    return _store 