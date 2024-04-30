from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from .base import Base
from .personne import Personne


class Credit(Base):
    __tablename__ = "credit"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_metrage: Mapped[int] = mapped_column(ForeignKey("metrage.id"))
    id_personne: Mapped[int] = mapped_column(ForeignKey("personne.id"))

    metrage: Mapped["Metrage"] = relationship(back_populates="credits")
    personne: Mapped["Personne"] = relationship()
    fonction: Mapped[str] = mapped_column(String(50))

    def __repr__(self):
        return f"Credit(id={self.id}, metrage={self.metrage}, personne={self.personne}, fonction={self.fonction})"
