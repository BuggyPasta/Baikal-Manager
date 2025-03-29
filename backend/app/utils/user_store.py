import json
import time
from typing import Dict, Optional, List
from . import encryption
from ..config.config import Config

def _load_users() -> List[Dict]:
    try:
        with open(Config.get_path('users.json'), 'r') as f:
            return json.load(f)['users']
    except:
        return []

def _save_users(users: List[Dict]) -> None:
    with open(Config.get_path('users.json'), 'w') as f:
        json.dump({'users': users}, f)

def get_users() -> List[Dict]:
    return [{
        'username': u['username'],
        'fullName': u['fullName'],
        'last_login': u['last_login']
    } for u in _load_users()]

def get_user(username: str) -> Optional[Dict]:
    if user := next((u for u in _load_users() if u['username'] == username), None):
        if creds := user.get('baikal_credentials'):
            creds['password'] = encryption.decrypt(creds['password'])
        return user
    return None

def create_user(username: str, password: str, full_name: str) -> Dict:
    if get_user(username):
        raise ValueError('Username already exists')
    
    user = {
        'username': username,
        'password': password,
        'fullName': full_name,
        'created_at': time.time(),
        'last_login': None,
        'baikal_credentials': None
    }
    
    users = _load_users()
    users.append(user)
    _save_users(users)
    return user

def update_user(username: str, data: Dict) -> Dict:
    users = _load_users()
    if not (user := next((u for u in users if u['username'] == username), None)):
        raise ValueError('User not found')
    
    user.update(data)
    if creds := user.get('baikal_credentials'):
        if 'password' in creds:
            creds['password'] = encryption.encrypt(creds['password'])
    
    _save_users(users)
    return get_user(username)

def delete_user(username: str) -> bool:
    users = _load_users()
    new_users = [u for u in users if u['username'] != username]
    if len(new_users) < len(users):
        _save_users(new_users)
        return True
    return False

def update_last_login(username: str) -> None:
    update_user(username, {'last_login': time.time()})

_store = None

def get_user_store() -> UserStore:
    global _store
    if _store is None:
        _store = UserStore()
    return _store 