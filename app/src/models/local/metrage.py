from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text
from .credit import Credit
from .base import Base, metrage_genre_association
from .critique import Critique
from typing import Optional


class Metrage(Base):
    __tablename__ = "metrage"

    id: Mapped[int] = mapped_column(primary_key=True)
    titre: Mapped[str] = mapped_column(String(255))
    annee: Mapped[int]
    type: Mapped[str] = mapped_column(String(50))
    synopsis: Mapped[Optional[Text]] = mapped_column(Text)
    note_moyenne: Mapped[float] = mapped_column(nullable=True)
    credits: Mapped[list["Credit"]] = relationship(
        back_populates="metrage", cascade="all, delete-orphan"
    )
    critiques: Mapped[list["Critique"]] = relationship(
        back_populates="metrage", cascade="all, delete-orphan"
    )

    genres: Mapped[list['Genre']] = relationship(
        'Genre',
        secondary=metrage_genre_association,
        back_populates='metrages'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'titre': self.titre,
            'annee': self.annee,
            'type': self.type,
            'synopsis': self.synopsis,
            'note_moyenne': self.note_moyenne,
        }
    def __repr__(self):
        return f"Metrage(id={self.id}, titre={self.titre}, annee={self.annee}, type={self.type})"
