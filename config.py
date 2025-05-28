import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get("SESSION_SECRET", "ohada_comptabilit_secret_key")
    # Nouvelle configuration pour Neon PostgreSQL
    database_url = os.environ.get("DATABASE_URL", "postgresql://neondb_owner:npg_kOmlE4KW5tJw@ep-twilight-boat-a89ewfq2-pooler.eastus2.azure.neon.tech/neondb?sslmode=require")
    
    # Ajouter des paramètres de connexion optimisés si nécessaire
    if "?" not in database_url:
        database_url += "?sslmode=require"
    if "connect_timeout" not in database_url:
        database_url += "&connect_timeout=10&application_name=smartohada&keepalives=1&keepalives_idle=30&keepalives_interval=10&keepalives_count=3"

    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 2,
        "pool_recycle": 55,
        "pool_pre_ping": True,
        "max_overflow": 3,
        "pool_timeout": 10,
        "connect_args": {
            "connect_timeout": 20,
            "keepalives": 1,
            "keepalives_idle": 60,
            "keepalives_interval": 10,
            "keepalives_count": 3
        }
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    

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

    # Optimisation de la base de données pour la production
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 280,
        "pool_pre_ping": True,
        "max_overflow": 20,
        "pool_timeout": 20,
        "connect_args": {"connect_timeout": 10}
    }

    # Configuration de sécurité
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=14)

    # Configuration pour le déploiement
    PREFERRED_URL_SCHEME = 'https'

# Config dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}