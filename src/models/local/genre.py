from .base import Base
from .metrage import Metrage
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Genre(Base):

    __tablename__ = "genre"
    id: Mapped[int] = mapped_column(primary_key=True)
    id_metrage: Mapped[int] = mapped_column(ForeignKey("metrage.id"))
    nom_genre: Mapped[str] = mapped_column(String(50))

    metrage: Mapped["Metrage"] = relationship(back_populates="genres")

