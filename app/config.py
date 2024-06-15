import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'mysql+pymysql://movienotes:REDACTED@db/MovieDb' )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('FLASK_SK', "b'\xc6\x91)\xc3\x00\xeb\x06c:\xdc\xe0\xd6-\x1a7I<\x13aM\xe24l\xe8'")
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', "b'\xc6\x91)\xc3\x00\xeb\x06c:\xdc\xe0\xd6-\x1a7I<\x13aM\xe24l\xe8'")
