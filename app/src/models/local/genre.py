from .base import Base, metrage_genre_association
from .metrage import Metrage
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Genre(Base):
    __tablename__ = "genre"
    id: Mapped[int] = mapped_column(primary_key=True)
    nom_genre: Mapped[str] = mapped_column(String(50))

    metrages: Mapped[list['Metrage']] = relationship(
        'Metrage',
        secondary=metrage_genre_association,
        back_populates='genres'
    )