from cryptography.fernet import Fernet
from ..config.config import Config

def get_key():
    key_path = Config.get_path('encryption.key')
    try:
        with open(key_path, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open(key_path, 'wb') as f:
            f.write(key)
        return key

def encrypt(data: str) -> str:
    return Fernet(get_key()).encrypt(data.encode()).decode()

def decrypt(data: str) -> str:
    return Fernet(get_key()).decrypt(data.encode()).decode() if data else '' 