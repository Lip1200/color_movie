from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
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
import numpy as np
import chromadb
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from func import (
    get_user_ratings,
    get_vector,
    get_user_list_ids,
    get_user_details,
    find_similar_movies_by_id,
    find_similar_movies_by_list_id
)

# Configuration de la base de données MySQL
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# Configuration de ChromaDB
chroma_client = chromadb.PersistentClient(path="./vec_data")
collection = chroma_client.get_or_create_collection(name="movies", metadata={"hnsw:space": "cosine"})

# Création de l'application Flask
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

app = create_app()

@app.route('/')
def index():
    return "Welcome to the Movie API!"

@app.route('/movies', methods=['GET'])
def get_movies():
    movies = Metrage.query.all()
    return jsonify({'movies': [{'id': movie.id, 'title': movie.titre} for movie in movies]})

@app.route('/movies/<int:user_id>', methods=['GET'])
def get_user_movies(user_id):
    results = session.query(
        Liste.nom_liste.label('liste_titre'),
        Metrage.titre.label('film_titre'),
        Personne.nom.label('directeur_nom')
    ).join(
        EntreeListe, Liste.id == EntreeListe.id_liste
    ).join(
        Metrage, EntreeListe.id_metrage == Metrage.id
    ).join(
        Credit, (Metrage.id == Credit.id_metrage) & (Credit.fonction == 'Director')
    ).join(
        Personne, Credit.id_personne == Personne.id
    ).filter(
        Liste.id_utilisateur == user_id
    ).all()

    if not results:
        return jsonify({'error': 'List not found'}), 404

    # Préparation des données pour la réponse
    data = {
        'list_title': results[0].liste_titre,
        'movies': [{'title': result.film_titre, 'director': result.directeur_nom} for result in results]
    }

    return jsonify(data)

@app.route('/user/<int:user_id>/similar_movies', methods=['GET'])
def get_similar_movies(user_id):
    user_ratings = get_user_ratings(user_id)
    if not user_ratings:
        return jsonify({"message": "No ratings found for this user."}), 404

    average_vector = calculate_weighted_average_vectors(user_ratings)
    similar_movie_ids, similar_movie_distances = find_similar_movies(average_vector)

    return jsonify({
        "user_id": user_id,
        "similar_movies": [
            {"movie_id": movie_id, "distance": distance}
            for movie_id, distance in zip(similar_movie_ids, similar_movie_distances)
        ]
    })

@app.route('/list/<int:list_id>/similar_movies', methods=['GET'])
def get_similar_movies_by_list(list_id):
    similar_movie_ids, similar_movie_distances = find_similar_movies_by_list_id(list_id, top_n=5)
    if not similar_movie_ids:
        return jsonify({"message": "No similar movies found."}), 404

    return jsonify({
        "list_id": list_id,
        "similar_movies": [
            {"movie_id": movie_id, "distance": distance}
            for movie_id, distance in zip(similar_movie_ids, similar_movie_distances)
        ]
    })


@app.route('/user/<int:user_id>/ratings', methods=['GET'])
def get_ratings(user_id):
    ratings = get_user_ratings(user_id)
    ratings_list = [{"movie_id": rating.id_metrage, "note": rating.note, "comment": rating.commentaire} for rating in ratings]
    return jsonify({"user_id": user_id, "ratings": ratings_list})

@app.route('/user/<int:user_id>/lists', methods=['GET'])
def get_lists(user_id):
    list_ids = get_user_list_ids(user_id)
    return jsonify({"user_id": user_id, "list_ids": list_ids})

@app.route('/similar_movies/<int:movie_id>', methods=['GET'])
def similar_movies(movie_id):
    try:
        similar_movie_ids, similar_movie_similarities = find_similar_movies_by_id(movie_id, top_n=5)
        return jsonify({"similar_movie_ids": similar_movie_ids, "similar_movie_similarities": similar_movie_similarities})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/similar_movies_by_list/<int:list_id>', methods=['GET'])
def similar_movies_by_list(list_id):
    try:
        similar_movie_ids, similar_movie_similarities = find_similar_movies_by_list_id(list_id, top_n=5)
        return jsonify({"similar_movie_ids": similar_movie_ids, "similar_movie_similarities": similar_movie_similarities})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/user_lists/<int:user_id>', methods=['GET'])
def user_lists(user_id):
    list_ids = get_user_list_ids(user_id)
    return jsonify({"list_ids": list_ids})

@app.route('/user/<int:user_id>/details', methods=['GET'])
def user_details(user_id):
    user_data = get_user_details(user_id)
    if user_data:
        return jsonify(user_data)
    else:
        return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)
