from typing import Optional
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from .base import Base


class Personne(Base):
    __tablename__ = "personne"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(50))
    date_naissance: Mapped[Optional[date]]
    date_deces: Mapped[Optional[date]]

    def __repr__(self):
        return f"Personne(id={self.id}, nom={self.nom}, date_naissance={self.date_naissance}, date_deces={self.date_deces})"
