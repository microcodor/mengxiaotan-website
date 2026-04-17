from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_smorest import Api
from redis import Redis
from config import config
import os

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
redis_client = None

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Initialize Redis
    global redis_client
    from urllib.parse import urlparse
    redis_url = app.config['REDIS_URL']
    parsed = urlparse(redis_url)
    
    redis_client = Redis(
        host=parsed.hostname or 'localhost',
        port=parsed.port or 6379,
        db=int(parsed.path[1:]) if parsed.path and len(parsed.path) > 1 else 0,
        password=parsed.password,
        decode_responses=True
    )
    
    # Initialize API
    api = Api(app)
    
    # Register blueprints
    from app.api import (
        auth_bp, articles_bp, users_bp, subscriptions_bp, permissions_bp,
        admin_bp, push_bp, push_settings_bp, crawler_bp, categories_bp, 
        company_bp, scheduler_bp, monitor_bp, briefs_bp, company_profile_bp,
        simulation_bp, reports_bp, monitoring_bp
    )
    api.register_blueprint(auth_bp)
    api.register_blueprint(articles_bp)
    api.register_blueprint(users_bp)
    api.register_blueprint(subscriptions_bp)
    api.register_blueprint(permissions_bp)
    api.register_blueprint(admin_bp)
    api.register_blueprint(push_bp)
    api.register_blueprint(push_settings_bp)
    api.register_blueprint(crawler_bp)
    api.register_blueprint(categories_bp)
    api.register_blueprint(company_bp)
    api.register_blueprint(scheduler_bp)
    api.register_blueprint(monitor_bp)
    api.register_blueprint(briefs_bp)
    api.register_blueprint(company_profile_bp)
    api.register_blueprint(simulation_bp)
    api.register_blueprint(reports_bp)
    api.register_blueprint(monitoring_bp)
    
    # Initialize push services
    from app.services.push_service import init_push_services
    init_push_services(app)
    
    # Initialize scheduler
    from app.scheduler import init_scheduler
    init_scheduler(app)
    
    # Create upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app
