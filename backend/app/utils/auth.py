from functools import wraps
from flask import session, jsonify, request
import os
import json
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from ..config.config import Config

def login_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def guest_only(f):
    """Decorator to restrict routes to unauthenticated users only"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in session:
            return jsonify({'error': 'Already authenticated'}), 403
        return f(*args, **kwargs)
    return decorated_function

def get_user_file(username):
    """Get path to user's credentials file"""
    users_dir = os.path.join(Config.DATA_PATH, 'users')
    os.makedirs(users_dir, exist_ok=True)
    return os.path.join(users_dir, f"{username}.json")

def get_encryption_key():
    """Get or create master encryption key"""
    key_path = Config.ENCRYPTION_KEY_PATH
    if os.path.exists(key_path):
        with open(key_path, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        os.makedirs(os.path.dirname(key_path), exist_ok=True)
        with open(key_path, 'wb') as f:
            f.write(key)
        return key

def hash_password(password, salt=None):
    """Hash password using PBKDF2"""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    key = base64.b64encode(kdf.derive(password.encode()))
    return salt, key

def verify_password(password, salt, key):
    """Verify password against stored hash"""
    _, new_key = hash_password(password, salt)
    return new_key == key

def create_user(username, password):
    """Create a new user"""
    user_file = get_user_file(username)
    
    if os.path.exists(user_file):
        return False, "Username already exists"
    
    # Hash password
    salt, key = hash_password(password)
    
    # Create user data
    user_data = {
        'username': username,
        'salt': base64.b64encode(salt).decode(),
        'key': key.decode(),
        'created_at': datetime.utcnow().isoformat()
    }
    
    # Encrypt user data
    fernet = Fernet(get_encryption_key())
    encrypted_data = fernet.encrypt(json.dumps(user_data).encode())
    
    # Save to file
    with open(user_file, 'wb') as f:
        f.write(encrypted_data)
    
    return True, None

def verify_user(username, password):
    """Verify user credentials"""
    user_file = get_user_file(username)
    
    if not os.path.exists(user_file):
        return False
    
    try:
        # Read and decrypt user data
        with open(user_file, 'rb') as f:
            encrypted_data = f.read()
        
        fernet = Fernet(get_encryption_key())
        decrypted_data = fernet.decrypt(encrypted_data)
        user_data = json.loads(decrypted_data)
        
        # Verify password
        salt = base64.b64decode(user_data['salt'])
        stored_key = user_data['key'].encode()
        
        return verify_password(password, salt, stored_key)
    
    except Exception:
        return False

def delete_user(username):
    """Delete a user account"""
    user_file = get_user_file(username)
    
    if os.path.exists(user_file):
        os.remove(user_file)
        
        # Delete user data directory
        data_dir = os.path.join(Config.DATA_PATH, username)
        if os.path.exists(data_dir):
            import shutil
            shutil.rmtree(data_dir)
        
        return True
    
    return False 