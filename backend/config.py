import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root:jinchun123@localhost:3306/energy_station')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Server Port
    PORT = int(os.getenv('PORT', 5001))
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://:123456@localhost:6379/0')
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')
    
    # Pagination
    PER_PAGE = int(os.getenv('PER_PAGE', 20))
    
    # Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    
    # MiniMax
    MINIMAX_API_KEY = os.getenv('MINIMAX_API_KEY', '')
    MINIMAX_GROUP_ID = os.getenv('MINIMAX_GROUP_ID', '')
    MINIMAX_API_URL = 'https://api.minimax.chat/v1/text/chatcompletion_v2'
    
    # OCR
    OCR_PROVIDER = os.getenv('OCR_PROVIDER', 'baidu')  # 'baidu' or 'tencent'
    BAIDU_OCR_API_KEY = os.getenv('BAIDU_OCR_API_KEY', '')
    BAIDU_OCR_SECRET_KEY = os.getenv('BAIDU_OCR_SECRET_KEY', '')
    TENCENT_OCR_SECRET_ID = os.getenv('TENCENT_OCR_SECRET_ID', '')
    TENCENT_OCR_SECRET_KEY = os.getenv('TENCENT_OCR_SECRET_KEY', '')
    
    # 企业微信推送
    WECHAT_WORK_CORPID = os.getenv('WECHAT_WORK_CORPID', '')
    WECHAT_WORK_CORPSECRET = os.getenv('WECHAT_WORK_CORPSECRET', '')
    WECHAT_WORK_AGENTID = os.getenv('WECHAT_WORK_AGENTID', '')
    
    # API
    API_TITLE = '蒙小碳能源站 API'
    API_VERSION = 'v1'
    OPENAPI_VERSION = '3.0.2'
    OPENAPI_URL_PREFIX = '/'
    OPENAPI_SWAGGER_UI_PATH = '/swagger-ui'
    OPENAPI_SWAGGER_UI_URL = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    
    # Scheduler
    ENABLE_SCHEDULER = os.getenv('ENABLE_SCHEDULER', 'true').lower() == 'true'
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'
    
    # Email Alert
    SMTP_SERVER = os.getenv('SMTP_SERVER', '')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    ALERT_EMAILS = os.getenv('ALERT_EMAILS', '').split(',') if os.getenv('ALERT_EMAILS') else []

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
