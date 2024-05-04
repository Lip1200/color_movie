import csv
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, joinedload
from src.models.local import (
    Liste,
    Metrage,
    Personne,
    Utilisateur,
    EntreeListe,
    Credit
)

def read_movies_from_csv(file_path: str) -> list[str]:
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        return [(row[0], row[1]) for row in reader]

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


def create_favorite_list(session: Session, user_id: int, movies: list[str]) -> None:
    user = session.get(Utilisateur, user_id)
    if not user:
        print("User not found")
        return

    new_list = Liste(utilisateur=user, titre="Favorite Movies")
    session.add(new_list)
    session.commit()

    for title, director in movies:
        movie_id = get_movie_id(session, title, director)
        if movie_id:
            entry = EntreeListe(id_liste=new_list.id, id_metrage=movie_id)
            session.add(entry)
        else:
            print(f"Movie '{title}' directed by {director} not found in the database.")

    session.commit()


def main():
    load_dotenv()
    engine = create_engine("mysql+mysqldb://" + os.environ.get("MOVIE_DB_USER", "") + ":" + os.environ.get("MOVIE_DB_PASSWORD", "") + "@localhost/MovieDb", echo=True)
    Session = sessionmaker(engine)
    with Session() as session:
        user_id = 18  # ids users de 1 à 500
        file_path = './scraper/18-xavier-dolan.csv'  #

        # Read movie titles and directors from CSV
        movies = read_movies_from_csv(file_path)

        # Create a favorite list with the movies found in the database
        create_favorite_list(session, user_id, movies)

if __name__ == "__main__":
    main()