import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Genel
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # Veritabanı
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # E-Posta Ayarları
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")


    # JWT Ayarları
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-jwt-secret')

    