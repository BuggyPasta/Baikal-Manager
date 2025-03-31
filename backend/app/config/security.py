from flask import Flask, session
from .config import Config
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def configure_security(app: Flask):
    """Configure security settings for the application"""
    # Session security
    app.config.update(
        SESSION_COOKIE_SECURE=False,  # Set to True if using HTTPS
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        SESSION_TYPE='filesystem',
        SESSION_FILE_DIR=Config.get_path('flask_session'),
        SESSION_FILE_THRESHOLD=500  # Maximum number of sessions stored on disk
    )

    # CORS configuration
    app.config.update(
        CORS_SUPPORTS_CREDENTIALS=True,
        CORS_EXPOSE_HEADERS=['Content-Type', 'Authorization'],
        CORS_METHODS=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        CORS_ALLOW_HEADERS=['Content-Type', 'Authorization']
    )

    # Basic security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    # Session activity monitoring
    @app.before_request
    def check_session_expiry():
        if 'user_id' in session:
            session.permanent = True  # Make the session permanent but with expiry
            session.modified = True   # Mark the session as modified to ensure updates

    # Additional security settings
    app.config.update(
        SECRET_KEY=Config.APP_SECRET_KEY,
        JSON_SORT_KEYS=False,  # Preserve key order in JSON responses
        MAX_CONTENT_LENGTH=10 * 1024 * 1024  # 10MB max file size
    ) 