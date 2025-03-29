import logging
import os
from .config import Config

def setup_logging(app):
    """Configure application logging"""
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Ensure log directory exists
    os.makedirs(Config.LOG_PATH, exist_ok=True)
    
    # Configure file handler
    file_handler = logging.FileHandler(os.path.join(Config.LOG_PATH, 'app.log'))
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Configure app logger
    app.logger.setLevel(log_level)
    app.logger.addHandler(file_handler)
    
    # Configure werkzeug logger
    logging.getLogger('werkzeug').setLevel(log_level)
    logging.getLogger('werkzeug').addHandler(file_handler) 