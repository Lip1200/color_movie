import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://movienotes:filipe@db/MovieDb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("FLASK_SK", "")
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key_here')