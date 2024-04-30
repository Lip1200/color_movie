from .base import Base
from .utilisateur import Utilisateur
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Critique(Base):
    __tablename__ = "critique"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_utilisateur: Mapped[int] = mapped_column(ForeignKey("utilisateur.id"))
    id_metrage: Mapped[int] = mapped_column(ForeignKey("metrage.id"))

    utilisateur: Mapped["Utilisateur"] = relationship(back_populates="critiques")
    metrage: Mapped["Metrage"] = relationship(back_populates="critiques")
    note: Mapped[int]
    commentaire: Mapped[Text] = mapped_column(Text)

    def __repr__(self):
        return f"Critique(id={self.id}, utilisateur={self.utilisateur}, metrage={self.metrage}, note={self.note}, commentaire={self.commentaire})"
