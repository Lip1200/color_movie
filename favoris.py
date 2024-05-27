import csv
import os
from config import Config
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, joinedload
from src.models.local import (
    Liste,
    Metrage,
    Personne,
    Utilisateur,
    EntreeListe,
    Credit,
    Critique  # Ajouté pour insérer les critiques
)

def read_movies_from_csv(file_path: str) -> list[tuple[str, str, int]]:
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        return [(row[0], row[1], int(row[3])) for row in reader]  # Inclure le titre, le réalisateur et la note

def get_movie_id(session: Session, title: str, director_name: str) -> int:
    movie = session.query(Metrage).options(joinedload(Metrage.credits)).join(
        Credit, Metrage.credits
    ).join(
        Personne, Credit.personne
    ).filter(
        Metrage.titre == title,
        Personne.nom == director_name,
        Credit.fonction == 'Director'
    ).first()
    return movie.id if movie else None

def create_favorite_list(session: Session, user_id: int, user_name: str, movies: list[tuple[str, str, int]]) -> None:
    user = session.get(Utilisateur, user_id)
    if not user:
        print("User not found")
        return

    # Mettre à jour le nom de l'utilisateur s'il est fourni
    if user_name:
        user.nom = user_name
        session.add(user)
        session.commit()

    # Vérifiez les noms de colonnes dans le modèle Liste
    print(f"Liste columns: {Liste.__table__.columns.keys()}")

    new_list = Liste(id_utilisateur=user.id, nom_liste="Favorite Movies")
    session.add(new_list)
    session.commit()

    for title, director, rating in movies:
        movie_id = get_movie_id(session, title, director)
        if movie_id:
            entry = EntreeListe(id_liste=new_list.id, id_metrage=movie_id)
            session.add(entry)
            critique = Critique(id_utilisateur=user_id, id_metrage=movie_id, note=rating, commentaire="")
            session.add(critique)
        else:
            print(f"Movie '{title}' directed by {director} not found in the database.")

    session.commit()

def main():
    load_dotenv()
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(engine)
    with Session() as session:
        user_id = 19  # ids users de 1 à 500
        user_name = "Lois Lane"  # Nom de l'utilisateur
        file_path = './scraper/19-fanDeSuperHero'  #

        # Read movie titles, directors, and ratings from CSV
        movies = read_movies_from_csv(file_path)

        # Create a favorite list with the movies found in the database
        create_favorite_list(session, user_id, user_name, movies)

if __name__ == "__main__":
    main()
