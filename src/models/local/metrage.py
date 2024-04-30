from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from typing import Optional
from .credit import Credit
from .base import Base
from .critique import Critique


class Metrage(Base):
    __tablename__ = "metrage"

    id: Mapped[int] = mapped_column(primary_key=True)
    titre: Mapped[str] = mapped_column(String(50))
    annee: Mapped[int]
    type: Mapped[str] = mapped_column(String(10))
    credits: Mapped[list["Credit"]] = relationship(
        back_populates="metrage", cascade="all, delete-orphan"
    )
    critiques: Mapped[list["Critique"]] = relationship(
        back_populates="metrage", cascade="all, delete-orphan"
    )
    genres: Mapped[list["Genre"]] = relationship(back_populates="metrage", cascade="all, delete-orphan")
    # note_moyenne: Mapped[float]
    synopsis: Mapped[Optional[str]] = mapped_column(String(500))

    def __repr__(self):
        return f"Metrage(id={self.id}, titre={self.titre}, annee={self.annee}, type={self.type})"
