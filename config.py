# config.py — Konfigurasi RoadDetection

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'roadscan-secret-key-ganti-ini'

    # Database
    MYSQL_HOST     = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER     = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DB       = os.environ.get('MYSQL_DB') or 'roaddetection'
    MYSQL_PORT     = int(os.environ.get('MYSQL_PORT') or 3306)
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload
    UPLOAD_FOLDER      = os.path.join('static', 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

    # Model
    MODEL_PATH = os.path.join('model', 'model_kerusakan_jalan.keras')

    # Threshold confidence
    CONFIDENCE_THRESHOLD = 0.20