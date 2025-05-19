import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get("SESSION_SECRET", "ohada_comptabilit_secret_key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "postgresql://neondb_owner:npg_Crwao4WUkt5f@ep-spring-pond-a5upovj4-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 1800
    }
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Ollama configuration (for AI analysis)
    OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api")
    OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral:7b")
    
    # Tesseract configuration (for OCR)
    TESSERACT_CMD = os.environ.get("TESSERACT_CMD", "tesseract")
    TESSERACT_LANG = os.environ.get("TESSERACT_LANG", "fra")
    
    # Application settings
    APP_NAME = "SmartOHADA"
    COMPANY_NAME = "SmartOHADA Technologies"
    ADMIN_EMAIL = "admin@smartohada.com"
    
    # Feature flags
    ENABLE_OCR = True
    ENABLE_NLP = True
    ENABLE_AI_ANALYSIS = True
    ENABLE_DOCUMENT_GENERATION = True
    
    # Locale settings
    DEFAULT_LANGUAGE = "fr"
    DEFAULT_CURRENCY = "XOF"  # CFA Franc BCEAO
    DEFAULT_TIMEZONE = "Africa/Dakar"
    DATE_FORMAT = "%d/%m/%Y"
    DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
# Config dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
