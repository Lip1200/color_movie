import random
from flask import Flask
from config import Config
from app import create_app
from src.models.local.base import db
from src.models.local.critique import Critique
from src.models.local.entree_liste import EntreeListe
from src.models.local.liste import Liste

app = create_app()
app.config.from_object(Config)
db.init_app(app)

# Utilisateurs cibles
user_ids = list(range(1, 17))

with app.app_context():
    db.create_all()

    # Récupérer les listes de films favoris des utilisateurs cibles
    favorite_lists = db.session.execute(
        db.select(Liste).filter(Liste.id_utilisateur.in_(user_ids))
    ).scalars().all()

    # Vérifier que nous récupérons bien les listes
    print(f"Nombre de listes récupérées : {len(favorite_lists)}")

    for favorite_list in favorite_lists:
        print(
            f"Liste ID : {favorite_list.id}, Utilisateur ID : {favorite_list.id_utilisateur}, Nom de la liste : {favorite_list.nom_liste}")

        # Récupérer les entrées de liste pour chaque liste
        entries = db.session.execute(
            db.select(EntreeListe).filter(EntreeListe.id_liste == favorite_list.id)
        ).scalars().all()

        # Vérifier que nous récupérons bien les entrées de liste
        print(f"Nombre d'entrées pour la liste ID {favorite_list.id} : {len(entries)}")

        for entry in entries:
            # Donner une note aléatoire entre 7 et 10 à chaque film dans les listes de films favoris
            random_note = random.randint(7, 10)
            critique = Critique(
                id_utilisateur=favorite_list.id_utilisateur,
                id_metrage=entry.id_metrage,
                note=random_note,
                commentaire=None
            )
            db.session.add(critique)

    db.session.commit()
    print("Notes aléatoires attribuées avec succès.")
