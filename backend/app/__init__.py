from flask import Flask, send_from_directory
from flask_cors import CORS
from .routes.health import health_bp
from .routes.auth import bp as auth_bp
from .routes.settings import bp as settings_bp
from .config.config import Config
from .config.logging import setup_logging
from .config.security import configure_security
import os

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, static_folder='/app/backend/app/static')
    CORS(app)
    
    # Basic setup
    os.makedirs(Config.DATA_PATH, exist_ok=True)
    os.makedirs(Config.LOG_PATH, exist_ok=True)
    app.config['SECRET_KEY'] = Config.APP_SECRET_KEY
    
    # Configure app
    setup_logging(app)
    configure_security(app)
    
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
    
    return app

app = create_app() 