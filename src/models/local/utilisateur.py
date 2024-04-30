from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Utilisateur(Base):
    __tablename__ = "utilisateur"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str]
    email: Mapped[str]
    critiques: Mapped[list["Critique"]] = relationship(
        back_populates="utilisateur", cascade="all, delete-orphan"
    )
    listes: Mapped[list["Liste"]] = relationship(
        back_populates="utilisateur", cascade="all, delete-orphan"
    )
    mot_de_passe: Mapped[str]

    def __repr__(self):
        return f"Utilisateur(id={self.id}, nom={self.nom}, email={self.email}, mot_de_passe={self.mot_de_passe})"
