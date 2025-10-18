"""Flask Application Factory"""

from flask import Flask
from flask_cors import CORS
from config import Config

def create_app():
    """Create Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app)
    
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.route('/')
    def health_check():
        return {
            'status': 'healthy',
            'message': 'Inventory Management API is running',
            'version': '1.0.0'
        }
    
    return app