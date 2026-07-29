# config.py — Konfigurasi RoadScan

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'roadscan-secret-key-ganti-ini'
    
    # Database
    MYSQL_HOST     = 'mysql.railway.internal'
    MYSQL_USER     = 'root'
    MYSQL_PASSWORD = 'iDyxpWTHzkNzDAfEbEDjXDocPkPTvXOn'          # sesuaikan password MySQL
    MYSQL_DB       = 'railway'
    MYSQL_PORT     = 3306
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload
    UPLOAD_FOLDER     = os.path.join('static', 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    
    # Model
    MODEL_PATH = os.path.join('model', 'model_kerusakan.keras')
    
    # Threshold confidence
    CONFIDENCE_THRESHOLD = 0.70
