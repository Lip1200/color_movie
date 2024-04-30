from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from .base import Base
from .entree_liste import EntreeListe
from .utilisateur import Utilisateur


class Liste(Base):
    __tablename__ = "liste"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_utilisateur: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"))

    utilisateur: Mapped[Utilisateur] = relationship(back_populates="listes")
    titre: Mapped[str] = mapped_column(String(50))
    entrees_metrages: Mapped[list[EntreeListe]] = relationship()

    def __repr__(self):
        return (
            f"Liste(id={self.id}, utilisateur={self.utilisateur}, titre={self.titre})"
        )
