import random
from config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.local.critique import Critique
from src.models.local.entree_liste import EntreeListe
from src.models.local.liste import Liste

# Configuration de la base de données MySQL
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# Utilisateurs cibles
user_ids = list(range(1, 17))

# Récupérer les listes de films favoris des utilisateurs cibles
favorite_lists = session.query(Liste).filter(Liste.id_utilisateur.in_(user_ids)).all()

# Vérifier que nous récupérons bien les listes
print(f"Nombre de listes récupérées : {len(favorite_lists)}")

for favorite_list in favorite_lists:
    print(f"Liste ID : {favorite_list.id}, Utilisateur ID : {favorite_list.id_utilisateur}, Nom de la liste : {favorite_list.nom_liste}")

    # Récupérer les entrées de liste pour chaque liste
    entries = session.query(EntreeListe).filter(EntreeListe.id_liste == favorite_list.id).all()

    # Vérifier que nous récupérons bien les entrées de liste
    print(f"Nombre d'entrées pour la liste ID {favorite_list.id} : {len(entries)}")

    for entry in entries:
        # Vérifier si une critique existe déjà pour éviter les doublons
        existing_critique = session.query(Critique).filter(
            Critique.id_utilisateur == favorite_list.id_utilisateur,
            Critique.id_metrage == entry.id_metrage
        ).first()

        if existing_critique:
            print(f"Critique existante trouvée pour Utilisateur ID : {favorite_list.id_utilisateur}, Metrage ID : {entry.id_metrage}")
            continue

        # Donner une note aléatoire entre 6 et 10 à chaque film dans les listes de films favoris
        random_note = random.randint(6, 10)
        critique = Critique(
            id_utilisateur=favorite_list.id_utilisateur,
            id_metrage=entry.id_metrage,
            note=random_note,
            commentaire=""  # Attribuer un commentaire vide au lieu de None
        )
        session.add(critique)

session.commit()
print("Notes aléatoires attribuées avec succès.")
