from .base import Base
from .metrage import Metrage
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class EntreeListe(Base):
    __tablename__ = "entree_liste"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_liste: Mapped[int] = mapped_column(ForeignKey("liste.id"))
    id_metrage: Mapped[int] = mapped_column(ForeignKey("metrage.id"))

    metrage: Mapped["Metrage"] = relationship()
