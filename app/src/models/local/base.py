from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Table, Column, ForeignKey
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Base(db.Model):
    __abstract__ = True
    pass

metrage_genre_association = Table("metrage_genre_association", Base.metadata,
    Column('metrage_id', ForeignKey('metrage.id')),
    Column('genre_id', ForeignKey('genre.id'))
)
