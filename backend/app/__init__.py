from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_session import Session
from .routes.health import health_bp
from .routes.auth import bp as auth_bp
from .routes.settings import bp as settings_bp
from .config.config import Config
from .config.logging import setup_logging
from .config.security import configure_security
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, static_folder='/app/backend/app/static')
    
    # Basic setup
    os.makedirs(Config.DATA_PATH, exist_ok=True)
    os.makedirs(Config.LOG_PATH, exist_ok=True)
    os.makedirs(Config.get_path('flask_session'), exist_ok=True)
    
    # Configure security first
    app.config['SECRET_KEY'] = Config.APP_SECRET_KEY
    configure_security(app)
    
    # Initialize CORS after security config
    CORS(app, supports_credentials=True)
    
    # Initialize session after CORS
    Session(app)
    
    # Configure app
    setup_logging(app)
    
    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(settings_bp)
    
    # Serve frontend
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')
    
    # Error handling
    @app.errorhandler(500)
    def handle_error(error):
        logger.error(f"Internal error: {str(error)}")
        return {'error': 'Internal server error'}, 500
    
    return app

app = create_app() 