import os
from dotenv import load_dotenv

class Config:
    load_dotenv()
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + os.environ.get("MOVIE_DB_USER", "movienotes") + ':' + os.environ.get("MOVIE_DB_PASSWORD","filipe") + '@localhost/MovieDb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("FLASK_SK", "")
