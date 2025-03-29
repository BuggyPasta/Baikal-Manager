import os

class Config:
    """Application configuration"""
    APP_NAME = os.getenv('APP_NAME', 'Baikal-Manager')
    APP_SECRET_KEY = os.getenv('APP_SECRET_KEY', 'change_this_in_production')
    DATA_PATH = os.getenv('DATA_DIR', '/data')
    LOG_PATH = os.getenv('LOG_PATH', '/data/logs')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    DEFAULT_INACTIVITY_TIMEOUT = int(os.getenv('DEFAULT_INACTIVITY_TIMEOUT', '10'))
    DEFAULT_MODE = os.getenv('DEFAULT_MODE', 'light')
    ENCRYPTION_KEY_PATH = os.getenv('ENCRYPTION_KEY_PATH', '/data/encryption.key')

    @classmethod
    def get_path(cls, *paths):
        """Get a path within the data directory"""
        path = os.path.join(cls.DATA_PATH, *paths)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return path 