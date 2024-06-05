import os
import numpy as np
from sqlalchemy.orm import joinedload
from src.models.local import (
    Credit,
    Critique,
    EntreeListe,
    Liste,
    Metrage,
    Utilisateur
)
from flask import Flask, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from config import Config
import chromadb

chroma_client = chromadb.PersistentClient(os.getenv("CHROMADB_STORAGE_DIR"))
collection = chroma_client.get_or_create_collection(name="Movie", metadata={"hnsw:space": "cosine"})

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    return app


def find_similar_movies_by_vec(collection, query_vector, top_n=5):
    current_app.logger.debug(f"Querying collection with vector: {query_vector}")
    # Effectue une requête pour trouver les films les plus similaires
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_n,
        include=["embeddings", "distances"]
    )
    current_app.logger.debug(f"Query results: {results}")

    if not results['ids']:
        current_app.logger.error(f"No similar Movie found for the given vector.")
        raise ValueError(f"No similar Movie found for the given vector.")

    similar_movie_ids = results['ids'][0]
    similar_movie_distances = results['distances'][0]

    # Retourne les IDs et les distances des films similaires
    return similar_movie_ids, similar_movie_distances


# Fonction pour trouver les films similaires à partir de l'ID du film
def find_similar_movies_by_id(collection, movie_id, top_n=5):
    current_app.logger.debug(f"Finding similar movies for movie ID: {movie_id}")
    # Récupère le vecteur d'embedding du film donné dans ChromaDB
    result = get_vector(collection, movie_id)
    current_app.logger.debug(f"Embedding result for movie ID {movie_id}: {result}")

    # Vérifie si le film a été trouvé dans la collection
    if not result or 'embeddings' not in result or not result['embeddings']:
        current_app.logger.error(f"Movie ID {movie_id} not found in the collection.")
        raise ValueError(f"Movie ID {movie_id} not found in the collection.")

    # Récupère le vecteur d'embedding du film
    query_vector = result['embeddings'][0]
    current_app.logger.debug(f"Query vector for movie ID {movie_id}: {query_vector}")

    # Effectue une requête pour trouver les films les plus similaires
    similar_movie_ids, similar_movie_distances = find_similar_movies_by_vec(collection, query_vector, top_n)
    current_app.logger.debug(f"Similar movie IDs: {similar_movie_ids}, distances: {similar_movie_distances}")

    # Retourne les IDs et les distances des films similaires
    return similar_movie_ids, similar_movie_distances


def find_similar_movies_by_list_id(session, collection, list_id, top_n=5):
    list_entries = session.query(EntreeListe).filter(EntreeListe.id_liste == list_id).all()

    if not list_entries:
        print("No entries found for this Lists.")
        return [], []

    rated_movie_ids = [entry.id_metrage for entry in list_entries]
    print(f"Rated movie IDs: {rated_movie_ids}")

    user_ratings = session.query(Critique).filter(Critique.id_metrage.in_(rated_movie_ids)).all()
    print(f"User ratings: {user_ratings}")

    if not user_ratings:
        print("No ratings found for these Movie.")
        return [], []

    ratings_dict = {rating.id_metrage: rating.note for rating in user_ratings}
    ratings = np.array([ratings_dict[movie_id] for movie_id in rated_movie_ids if movie_id in ratings_dict])
    print(f"Ratings array: {ratings}")
    # Divise les notes par 10 pour que la pondération ne change pas le shape
    ratings = ratings / 10
    print(f"Normalized ratings array: {ratings}")

    chroma_ids = [str(movie_id) for movie_id in rated_movie_ids if movie_id in ratings_dict]
    print(f"ChromaDB IDs to query: {chroma_ids}")

    rated_vectors = []
    for movie_id in rated_movie_ids:
        vector_result = get_vector(collection, movie_id)
        if vector_result and 'embeddings' in vector_result:
            rated_vectors.append(np.array(vector_result['embeddings'][0]))
        else:
            print(f"No vector found for movie ID {movie_id}")
            return [], []

    weighted_vectors = np.array([rating * vector for rating, vector in zip(ratings, rated_vectors)])
    average_vector = np.mean(weighted_vectors, axis=0)
    print(f"Average vector: {average_vector}")

    # Convertir average_vector en liste
    average_vector = average_vector.tolist()
    similar_movie_ids, similar_movie_distances = find_similar_movies_by_vec(collection, average_vector,
                                                                            top_n + len(rated_movie_ids))

    # Exclure les films déjà présents dans la liste de favoris
    filtered_similar_movie_ids = [movie_id for movie_id in similar_movie_ids if int(movie_id) not in rated_movie_ids]
    filtered_similar_movie_distances = [similar_movie_distances[i] for i in range(len(similar_movie_ids)) if
                                        int(similar_movie_ids[i]) not in rated_movie_ids]

    return filtered_similar_movie_ids[:top_n], filtered_similar_movie_distances[:top_n]


# Fonction pour obtenir le vecteur d'un film
def get_vector(collection, movie_id):
    current_app.logger.debug(f"Getting vector for movie ID: {movie_id}")
    try:
        results = collection.get(ids=[str(movie_id)], include=["embeddings"])
        current_app.logger.debug(f"Results from collection.get: {results}")

        if 'embeddings' in results and results['embeddings']:
            return results
        else:
            current_app.logger.error(f"Embeddings not found in the results for movie ID {movie_id}")
            return None
    except Exception as e:
        current_app.logger.error(f"An error occurred while getting vector for movie ID {movie_id}: {str(e)}")
        return None


# Fonction pour obtenir les critiques d'un utilisateur
def get_user_ratings(session, user_id):
    user_ratings = session.query(Critique).filter(Critique.id_utilisateur == user_id).all()
    return user_ratings


# Fonction pour obtenir les IDs des listes d'un utilisateur
def get_user_list_ids(session, user_id):
    return session.query(Liste.id, Liste.nom_liste).filter(Liste.id_utilisateur == user_id).all()


# Fonction pour obtenir les détails complets d'un utilisateur
def get_user_details(session, user_id):
    user = session.get(Utilisateur, user_id)
    if not user:
        return None

    # Obtenir les listes de l'utilisateur
    user_lists = session.query(Liste).filter(Liste.id_utilisateur == user_id).all()

    # Préparer les données des listes
    lists_data = []
    for lst in user_lists:
        list_entries = session.query(EntreeListe).filter(EntreeListe.id_liste == lst.id).all()
        movies = []
        for entry in list_entries:
            movie = session.query(Metrage).get(entry.id_metrage)
            if movie:
                movies.append({"movie_id": movie.id, "title": movie.titre})
        lists_data.append({"list_id": lst.id, "list_name": lst.nom_liste, "Movie": movies})

    # Obtenir les critiques de l'utilisateur
    user_ratings = session.query(Critique).filter(Critique.id_utilisateur == user_id).all()
    ratings_data = [{"movie_id": rating.id_metrage, "note": rating.note, "comment": rating.commentaire} for rating in
                    user_ratings]

    user_data = {
        "user_id": user.id,
        "user_name": user.nom,
        "lists": lists_data,
        "ratings": ratings_data
    }

    return user_data


def search_movie_by_title(session, title):
    movies = session.query(Metrage).filter(Metrage.titre.ilike(f"%{title}%")).all()
    movie_details = []
    for movie in movies:
        directors = [credit.personne.nom for credit in movie.credits if credit.fonction == 'Director']
        actors = [credit.personne.nom for credit in movie.credits if credit.fonction == 'Actor']
        movie_details.append({"title": movie.titre, "year": movie.annee, "directors": directors, "actors": actors,
                              "synopsis": movie.synopsis})
    return movie_details


def jsonify_movies(session, similar_movie_ids):
    if not similar_movie_ids:
        return jsonify({"message": "No similar movies found."}), 404
    sim_movies = []
    for movie_id in similar_movie_ids:
        movie = session.get(Metrage, movie_id)
        if movie:
            sim_movies.append({
                'id': movie.id,
                'title': movie.titre,
                'release_year': movie.annee,
                'type': movie.type,
                'synopsis': movie.synopsis,
                'note_moyenne': movie.note_moyenne
            })
    return jsonify({"similar_movies": sim_movies})
