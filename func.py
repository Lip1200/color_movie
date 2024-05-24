import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
from src.models.local import (
    db,
    Credit,
    Critique,
    EntreeListe,
    Genre,
    Liste,
    Metrage,
    Personne,
    Utilisateur,
    metrage_genre_association
)
import chromadb
from flask import Flask, request, jsonify

# Configuration de la base de données MySQL
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# Configuration de ChromaDB
chroma_client = chromadb.PersistentClient(path="./vec_data")
collection = chroma_client.get_or_create_collection(name="movies", metadata={"hnsw:space": "cosine"})

# Obtenir tous les identifiants dans la collection
all_ids = collection.get(ids=None)["ids"]
print(f"Total IDs in ChromaDB: {len(all_ids)}")


def find_similar_movies_by_vec(query_vector, top_n=5):
    # Effectue une requête pour trouver les films les plus similaires
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_n,
        include=["embeddings", "distances"]
    )
    if not results['ids']:
        raise ValueError(f"No similar movies found for the given vector.")

    similar_movie_ids = results['ids'][0]
    similar_movie_distances = results['distances'][0]

    # Retourne les IDs et les distances des films similaires
    return similar_movie_ids, similar_movie_distances


# Fonction pour trouver les films similaires à partir de l'ID du film
def find_similar_movies_by_id(movie_id, top_n=5):
    # Récupère le vecteur d'embedding du film donné dans ChromaDB
    result = get_vector(movie_id)

    # Vérifie si le film a été trouvé dans la collection
    if not result or 'embeddings' not in result or not result['embeddings']:
        raise ValueError(f"Movie ID {movie_id} not found in the collection.")

    # Récupère le vecteur d'embedding du film
    query_vector = result['embeddings'][0]
    #on transforme en list
    query_vector = query_vector.tolist()

    # Effectue une requête pour trouver les films les plus similaires
    similar_movie_ids, similar_movie_distances = find_similar_movies_by_vec(query_vector, top_n)

    # Retourne les IDs et les distances des films similaires
    return similar_movie_ids, similar_movie_distances



def find_similar_movies_by_list_id(list_id, top_n=5):
    list_entries = session.query(EntreeListe).filter(EntreeListe.id_liste == list_id).all()

    if not list_entries:
        print("No entries found for this list.")
        return [], []

    rated_movie_ids = [entry.id_metrage for entry in list_entries]
    print(f"Rated movie IDs: {rated_movie_ids}")

    user_ratings = session.query(Critique).filter(Critique.id_metrage.in_(rated_movie_ids)).all()
    print(f"User ratings: {user_ratings}")

    if not user_ratings:
        print("No ratings found for these movies.")
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
        vector_result = get_vector(movie_id)
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
    similar_movie_ids, similar_movie_distances = find_similar_movies_by_vec(average_vector, top_n)

    return similar_movie_ids, similar_movie_distances


# Fonction pour obtenir le vecteur d'un film
def get_vector(movie_id):
    results = collection.get(ids=[str(movie_id)], include=['embeddings'])
    if 'embeddings' in results and results['embeddings']:
        return results
    else:
        return None

# Fonction pour obtenir les critiques d'un utilisateur
def get_user_ratings(user_id):
    with Session() as session:
        user_ratings = session.query(Critique).filter(Critique.id_utilisateur == user_id).all()
    return user_ratings

# Fonction pour obtenir les IDs des listes d'un utilisateur
def get_user_list_ids(user_id):
    with Session() as session:
        user_lists = session.query(Liste.id).filter(Liste.id_utilisateur == user_id).all()
        list_ids = [list_id[0] for list_id in user_lists]
    return list_ids

# Fonction pour obtenir les détails complets d'un utilisateur
def get_user_details(user_id):
    with Session() as session:
        user = session.query(Utilisateur).get(user_id)
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
            lists_data.append({"list_id": lst.id, "list_name": lst.nom_liste, "movies": movies})

        # Obtenir les critiques de l'utilisateur
        user_ratings = session.query(Critique).filter(Critique.id_utilisateur == user_id).all()
        ratings_data = [{"movie_id": rating.id_metrage, "note": rating.note, "comment": rating.commentaire} for rating in user_ratings]

        user_data = {
            "user_id": user.id,
            "user_name": user.nom,
            "lists": lists_data,
            "ratings": ratings_data
        }

        return user_data