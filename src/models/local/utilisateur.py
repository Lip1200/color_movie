from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, String


class Utilisateur(Base):
    __tablename__ = "utilisateur"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom = Column(String(50), nullable=False)
    email: Mapped[str] = Column(String(50))
    mot_de_passe: Mapped[str] = Column(String(50))
    critiques: Mapped[list["Critique"]] = relationship(
        back_populates="utilisateur", cascade="all, delete-orphan"
    )
    listes: Mapped[list["Liste"]] = relationship(
        back_populates="utilisateur", cascade="all, delete-orphan"
    )
    mot_de_passe: Mapped[str]

    def __repr__(self):
        return f"Utilisateur(id={self.id}, nom={self.nom}, email={self.email}, mot_de_passe={self.mot_de_passe})"
