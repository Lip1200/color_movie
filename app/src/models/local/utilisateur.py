from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, String, Boolean
from .base import Base
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class Utilisateur(Base, UserMixin):
    __tablename__ = "utilisateur"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom = Column(String(50), nullable=False)
    email: Mapped[str] = Column(String(50))
    mot_de_passe = Column(String(255), nullable=False)
    is_admin: Mapped[bool] = Column(Boolean, default=False)
    critiques: Mapped[list["Critique"]] = relationship(
        back_populates="utilisateur", cascade="all, delete-orphan"
    )
    listes: Mapped[list["Liste"]] = relationship(
        back_populates="utilisateur", cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.mot_de_passe = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.mot_de_passe, password)

    def __repr__(self):
        return f"Utilisateur(id={self.id}, nom={self.nom}, email={self.email})"
