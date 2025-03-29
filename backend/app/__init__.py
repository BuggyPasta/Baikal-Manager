from flask import Flask
from .routes.health import health_bp
from .config.config import Config
from .config.logging import setup_logging
from .config.security import configure_security
import os

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Basic setup
    os.makedirs(Config.DATA_PATH, exist_ok=True)
    app.config['SECRET_KEY'] = Config.APP_SECRET_KEY
    
    # Configure app
    setup_logging(app)
    configure_security(app)
    
    # Routes
    app.register_blueprint(health_bp)
    
    return app

app = create_app() 