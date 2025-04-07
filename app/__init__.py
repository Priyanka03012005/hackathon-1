from flask import Flask
import os

def create_app():
    app = Flask(__name__, 
                static_folder='../static',
                template_folder='../templates')
    
    # Configure secret key for session management
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # Register blueprints
    from app.routes import main_bp
    from app.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    
    return app 