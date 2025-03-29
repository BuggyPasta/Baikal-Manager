from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """Simple health check endpoint for container monitoring"""
    return jsonify({'status': 'healthy'}), 200 