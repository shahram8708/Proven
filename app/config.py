import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_FILE_SIZE_MB', 5)) * 1024 * 1024

    # Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.mailtrap.io')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ('true', '1')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@proven.work')

    # AWS S3 (production file storage)
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET', 'proven-evidence-files')
    AWS_S3_REGION = os.environ.get('AWS_S3_REGION', 'ap-south-1')

    # Google Gemini AI
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    # Razorpay
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID')
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET')
    RAZORPAY_WEBHOOK_SECRET = os.environ.get('RAZORPAY_WEBHOOK_SECRET')

    # App
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
    MAX_EVIDENCE_FILES = int(os.environ.get('MAX_EVIDENCE_FILES', 5))
    DAILY_EVIDENCE_LIMIT = int(os.environ.get('DAILY_EVIDENCE_LIMIT', 10))

    # File storage backend: 'local' or 's3'
    STORAGE_BACKEND = os.environ.get('STORAGE_BACKEND', 'local')
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')

    # Session / Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # Keep sessions/auth cookies valid for one year unless the user logs out.
    PERMANENT_SESSION_LIFETIME = timedelta(days=365)
    REMEMBER_COOKIE_DURATION = timedelta(days=365)
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST = False
    WTF_CSRF_ENABLED = True
    RATELIMIT_STORAGE_URI = 'memory://'

    # Default admin (created on first run)
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@proven.work')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'ProvenAdmin@2026')
    ADMIN_FIRST_NAME = os.environ.get('ADMIN_FIRST_NAME', 'Proven')
    ADMIN_LAST_NAME = os.environ.get('ADMIN_LAST_NAME', 'Admin')
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'provenadmin')


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'proven_dev.db')
    )
    SESSION_COOKIE_SECURE = False
    STORAGE_BACKEND = os.environ.get('STORAGE_BACKEND', 'local')


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'
    STORAGE_BACKEND = os.environ.get('STORAGE_BACKEND', 's3')


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    STORAGE_BACKEND = 'local'


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}
