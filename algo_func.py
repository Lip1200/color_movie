import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
from src.models.local.metrage import Metrage
from src.models.local.critique import Critique
from src.models.local.liste import Liste
from src.models.local.entree_liste import EntreeListe
import chromadb
from flask import Flask, request, jsonify

# Configuration de la base de données MySQL
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# Configuration de ChromaDB
chroma_client = chromadb.PersistentClient(path="./vec_data")
collection = chroma_client.get_or_create_collection(name="movies", metadata={"hnsw:space": "cosine"})

# Fonction pour trouver les 5 vecteurs les plus proches
def find_top_n_similar_vectors(query_vector, vectors, top_n=5):
    similarities = cosine_similarity([query_vector], vectors)[0]
    top_n_indices = np.argsort(similarities)[-top_n:][::-1]
    top_n_similarities = similarities[top_n_indices]
    return top_n_indices, top_n_similarities

# Fonction pour trouver les films similaires à partir de l'ID du film
def find_similar_movies_by_id(movie_id, top_n=5):
    movie_id = str(movie_id)
    all_ids = collection.get(ids=None)["ids"]
    if movie_id not in all_ids:
        raise ValueError(f"Movie ID {movie_id} not found in the collection.")

    movie_index = all_ids.index(movie_id)
    vectors = np.array(collection.get(ids=all_ids)["embeddings"])
    query_vector = vectors[movie_index]

    indices, similarities = find_top_n_similar_vectors(query_vector, vectors, top_n + 1)
    indices = [idx for idx in indices if idx != movie_index][:top_n]
    similarities = [similarities[i] for i in range(len(similarities)) if indices[i] != movie_index][:top_n]

    most_similar_ids = [all_ids[i] for i in indices]
    return most_similar_ids, similarities

# Fonction pour trouver les films similaires à partir de l'ID d'une liste
def find_similar_movies_by_list_id(list_id, top_n=5):
    with Session() as session:
        list_entries = session.query(EntreeListe).filter(EntreeListe.id_liste == list_id).all()

    if not list_entries:
        print("No entries found for this list.")
        return []

    rated_movie_ids = [entry.id_metrage for entry in list_entries]
    user_ratings = session.query(Critique).filter(Critique.id_metrage.in_(rated_movie_ids)).all()

    if not user_ratings:
        print("No ratings found for these movies.")
        return []

    ratings_dict = {rating.id_metrage: rating.note for rating in user_ratings}
    ratings = np.array([ratings_dict[movie_id] for movie_id in rated_movie_ids if movie_id in ratings_dict])

    results = collection.get(ids=[str(movie_id) for movie_id in rated_movie_ids if movie_id in ratings_dict])
    rated_vectors = results['embeddings']

    if len(rated_vectors) == 0:
        print("No vectors found for the rated movies.")
        return []

    weighted_vectors = np.array([rating * vector for rating, vector in zip(ratings, rated_vectors)])
    average_vector = np.sum(weighted_vectors, axis=0) / np.sum(ratings)

    query_results = collection.query(
        query_embeddings=[average_vector.tolist()],
        n_results=top_n,
        include=["ids", "distances"]
    )

    if query_results['ids']:
        similar_movie_ids = query_results['ids'][0]
        similar_movie_distances = query_results['distances'][0]

        for idx, result_id in enumerate(similar_movie_ids):
            print(f"ID du Document {idx+1}: {result_id}")
            print(f"Distance: {similar_movie_distances[idx]}")
            print("-----")

        return similar_movie_ids, similar_movie_distances
    else:
        print("No similar movies found.")
        return []

# Fonction pour calculer la moyenne pondérée des vecteurs
def calculate_weighted_average_vectors(user_ratings):
    rated_movie_ids = [rating.id_metrage for rating in user_ratings]
    ratings = np.array([rating.note for rating in user_ratings])
    rated_vectors = get_movie_vectors(rated_movie_ids)
    weighted_vectors = np.array([rating * vector for rating, vector in zip(ratings, rated_vectors)])
    average_vector = np.sum(weighted_vectors, axis=0) / np.sum(ratings)
    return average_vector

# Fonction pour trouver des films similaires
def find_similar_movies(embedding, top_n=5):
    query_results = collection.query(
        query_embeddings=[embedding],
        n_results=top_n,
        include=["ids", "distances"]
    )
    if query_results['ids']:
        similar_movie_ids = query_results['ids'][0]
        similar_movie_distances = query_results['distances'][0]
        return similar_movie_ids, similar_movie_distances
    else:
        return [], []

# Fonction pour obtenir les vecteurs des films
def get_movie_vectors(movie_ids):
    results = collection.get(ids=[str(movie_id) for movie_id in movie_ids])
    return results['embeddings']

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

