from flask import Flask
from .config import Config
from datetime import timedelta

def configure_security(app: Flask):
    """Configure basic security settings for LAN application"""
    # Session security
    app.config.update(
        SESSION_COOKIE_SECURE=False,  # Set to True if using HTTPS
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(days=7)
    )

    # Basic security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        return response

    # Additional security settings
    app.config.update(
        SECRET_KEY=Config.APP_SECRET_KEY
    ) 