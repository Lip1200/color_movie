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
    Genre,
    metrage_genre_association
)

personnes: dict[int, Personne] = {}
genres: dict[int, Genre] = {}
metrages: dict[int, Metrage] = {}


def get_metrages(tmdb: TMDB, dico_genres: dict, page=1) -> Metrage:
    top_rated_movies = tmdb.list_top_rated_movies(page=page)
    for movie in top_rated_movies["results"]:
        metrage_id = movie["id"]
        if metrage_id not in metrages:
            metrage = Metrage(
                id=movie["id"],
                titre=movie["title"],
                annee=date.fromisoformat(movie["release_date"]).year,
                type="film",
                synopsis=movie["overview"],
                note_moyenne=movie["vote_average"]
            )
            metrages[metrage_id] = metrage
            metrage.credits = get_credits(tmdb, metrage)
            metrage.genres = get_genres(tmdb, movie, dico_genres)
        metrage = metrages[metrage_id]
        yield metrage


def get_personne(tmdb: TMDB, personne_id: int) -> Personne:
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


def get_credits(tmdb: TMDB, metrage: Metrage) ->list[Credit]:
    print(f"Getting credits for {metrage.titre}")
    movie_credits = tmdb.get_movies_credits(metrage.id)
    credits: list[Credit] = []
    max_acteurs = 10
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

def get_genres(tmdb: TMDB, movie: dict, dico_genre: dict) -> list[Genre]:
    print(f"Getting genres for {movie['title']}")
    genres_list: list[Genre] = []
    for id in movie["genre_ids"]:
        genre_obj = Genre(
            id=id,
            nom_genre=dico_genre[id]
        )
        genres_list.append(genre_obj)
    return genres_list

def init_genres(tmdb: TMDB, session: Session) -> dict:
    dataframe = tmdb.get_genres()
    dico_genres = {}
    for data in dataframe["genres"]:
        genre = Genre(
            id=data["id"],
            nom_genre=data["name"]
        )
        session.merge(genre)
        dico_genres[data["id"]] = data["name"]
    return dico_genres


def initialize_metrages_cache(session: Session) -> None:
    all_metrages = session.query(Metrage).all()
    for metrage in all_metrages:
        metrages[metrage.id] = metrage


def main():
    load_dotenv()

    engine = create_engine("mysql+mysqldb://" + os.environ.get("MOVIE_DB_USER", "") + ":" + os.environ.get("MOVIE_DB_PASSWORD","") + "@localhost/MovieDb", echo=True)
    #engine = create_engine('sqlite:///Movie.db')
    tmdb = TMDB(os.environ.get("TMDB_API_KEY", ""))

    Base.metadata.create_all(engine)

    with Session(engine) as session:
       initialize_metrages_cache(session)
       #rempli genres
       dico_genres = init_genres(tmdb, session)
       session.commit()

       total_pages = 500  # max_page=500
       for i in range(1, total_pages+1):
           for metrage in get_metrages(tmdb, dico_genres,  page=i):
                session.merge(metrage)
           session.commit()


if __name__ == "__main__":
    main()
