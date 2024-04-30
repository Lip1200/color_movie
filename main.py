from src.tmdb import TMDB
from dotenv import load_dotenv
import os
from datetime import date

from sqlalchemy import create_engine, select, insert, delete, update
from sqlalchemy.orm import Session

from src.models.local import (
    Base,
    Credit,
    Critique,
    Liste,
    Metrage,
    Personne,
    Utilisateur,
    EntreeListe,
    Genre
)

personnes: dict[int, Personne] = {}


def get_metrages(tmdb: TMDB):
    total_pages = 4     #max_page=500
    i = 0
    while i < total_pages:
        popular_movies = tmdb.list_popular_movies()
        total_pages = popular_movies["total_pages"]

        for movie in popular_movies["results"]:
            metrage = Metrage(
                id=movie["id"],
                titre=movie["title"],
                annee=date.fromisoformat(movie["release_date"]).year,
                type="film",
            )
            metrage.credits = get_credits(tmdb, metrage)
            yield metrage


def get_personne(tmdb: TMDB, personne_id: int):
    if personne_id in personnes:
        return personnes[personne_id]

    print(f"Getting person {personne_id}")
    person = tmdb.get_person(personne_id)
    personne = Personne(
        id=person["id"],
        nom=person["name"],
        date_naissance=(
            date.fromisoformat(person["birthday"])
            if person["birthday"] is not None
            else None
        ),
        date_deces=(
            date.fromisoformat(person["deathday"])
            if person["deathday"] is not None
            else None
        ),
    )
    personnes[personne.id] = personne

    return personne


def get_credits(tmdb: TMDB, metrage: Metrage):
    print(f"Getting credits for {metrage.titre}")
    movie_credits = tmdb.get_movies_credits(metrage.id)
    credits: list[Credit] = []
    max_acteurs = 20
    for cast in movie_credits["cast"]:
        personne = get_personne(tmdb, cast["id"])
        credit = Credit(
            id_metrage=metrage.id,
            id_personne=personne.id,
            metrage=metrage,
            personne=personne,
            fonction="actor",
        )
        credits.append(credit)
        max_acteurs -= 1
        if max_acteurs == 0:
            break

    for crew in movie_credits["crew"]:
        if crew["job"] == "Director":
            personne = get_personne(tmdb, crew["id"])
            credit = Credit(
                id_metrage=metrage.id,
                id_personne=personne.id,
                metrage=metrage,
                personne=personne,
                fonction="Director",
            )
            credits.append(credit)

    return credits

def get_genres(tmdb: TMDB, metrage: Metrage):
    print(f"Getting genres for {metrage.titre}")
    movies_details = tmdb.get_movie(metrage.id)
    genres: list[Genre] = []
    for detail in movies_details["genres"]:
        genre = Genre(
            id=detail("id"),
            id_metrage=metrage.id,
            nom_genre=detail("name"),
            metrage=metrage,
        )
        genres.append(genre)

def main():
    load_dotenv()

    engine = create_engine("mysql+mysqldb://" + os.environ.get("TMDB_DB_USER", "") + ":" + os.environ.get("TMDB_DB_PASSWORD","") + "@localhost/MovieDb", echo=True)

    tmdb = TMDB(os.environ.get("TMDB_API_KEY", ""))

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        for metrage in get_metrages(tmdb):
            if session.query(Metrage.id).filter_by(id=metrage.id).scalar() is None:
                session.add(metrage)
                session.commit()


if __name__ == "__main__":
    main()
