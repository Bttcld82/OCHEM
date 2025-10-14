import os

class Config:
    # Chiave segreta per Flask-WTF e sessioni
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'ochem.sqlite3')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-WTF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour in seconds
    
    # Upload files
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size