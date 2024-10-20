import os
import logging
from flask import Flask, jsonify, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required
from flask_login import LoginManager
from flask_admin import Admin
from datetime import datetime, timedelta
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
    create_app,
    get_user_ratings,
    get_vector,
    get_user_list_ids,
    get_user_details,
    find_similar_movies_by_id,
    find_similar_movies_by_list_id,
    search_movie_by_title,
    jsonify_movies
)
import admin_setup
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from contextlib import contextmanager


# Configuration de la base de données MySQL
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

# Configuration de ChromaDB
chroma_client = chromadb.HttpClient(host=os.getenv("CHROMADB_URI"), port=8000)
collection = chroma_client.get_or_create_collection(name="Movie", metadata={"hnsw:space": "cosine"})

# Création de l'application app
app = create_app()

# Configuration de la journalisation
app.config['DEBUG'] = True
app.logger.setLevel(logging.DEBUG)

# Création du gestionnaire de journalisation
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

# Format des messages de journalisation
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
handler.setFormatter(formatter)

# Ajout du gestionnaire à l'application
app.logger.addHandler(handler)

admin = Admin(app, template_mode='bootstrap3')
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
admin.add_view(admin_setup.AdminModelView(Utilisateur, db.session))


@contextmanager
def session_scope():
    session = db.session
    try:
        yield session
        session.commit()
    except Exception as e:
        current_app.logger.error(f"Error during session scope: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = Utilisateur.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.mot_de_passe, password):
        access_token = create_access_token(identity={'user_id': user.id, 'is_admin': user.is_admin},
                                           expires_delta=timedelta(hours=24))
        return jsonify({'token': access_token, 'user_id': user.id})

    return jsonify({'message': 'Invalid credentials'}), 401


@app.route('/')
@jwt_required()
def index():
    return jsonify(message="Hello from Flask for Movie!")


@app.route('/endpoints', methods=['GET'])
def list_endpoints():
    endpoints = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            endpoints.append({
                "endpoint": rule.endpoint,
                "methods": list(rule.methods),
                "url": str(rule)
            })
    return jsonify(endpoints)


@app.route('/movies', methods=['GET'])
@jwt_required()
def get_movies():
    movies = Metrage.query.all()
    return jsonify({'Movie': [{'id': movie.id, 'title': movie.titre, 'director': movie.credits.directeur_nom} for movie
                              in movies]})


@app.route('/list/<int:list_id>', methods=['GET'])
@jwt_required()
def get_list_details(list_id):
    with session_scope() as session:
        liste = session.query(Liste).filter(Liste.id == list_id).one_or_none()
        if not liste:
            return jsonify({'message': 'List not found'}), 404

        list_details = session.query(
            Metrage.id.label('movie_id'),
            Metrage.titre.label('movie_title'),
            Metrage.annee.label('release_date'),
            Personne.nom.label('director_name'),
            Critique.note.label('note'),
            Critique.commentaire.label('comment')
        ).join(
            EntreeListe, EntreeListe.id_metrage == Metrage.id
        ).join(
            Credit, (Metrage.id == Credit.id_metrage) & (Credit.fonction == 'Director')
        ).join(
            Personne, Credit.id_personne == Personne.id
        ).outerjoin(
            Critique, (Metrage.id == Critique.id_metrage) & (EntreeListe.id_liste == list_id) & (Critique.id_utilisateur == liste.id_utilisateur)
        ).filter(
            EntreeListe.id_liste == list_id
        ).all()

        if not list_details:
            return jsonify({
                'list_name': liste.nom_liste,
                'movies': []
            })

        data = {
            'list_name': liste.nom_liste,
            'movies': [{'id': movie.movie_id, 'title': movie.movie_title, 'release_date': movie.release_date,
                        'director': movie.director_name, 'note': movie.note, 'comment': movie.comment} for movie in list_details]
        }

        return jsonify(data)



@app.route('/user/<int:user_id>/ratings', methods=['GET'])
@jwt_required()
def get_ratings(user_id):
    with session_scope() as session:
        ratings = get_user_ratings(session, user_id)
        ratings_list = [{"movie_id": rating.id_metrage, "note": rating.note, "comment": rating.commentaire} for rating
                        in ratings]
        return jsonify({"user_id": user_id, "ratings": ratings_list})


@app.route('/user/<int:user_id>/lists', methods=['GET'])
@jwt_required()
def get_lists(user_id):
    with session_scope() as session:
        try:
            lists = session.query(Liste).filter_by(id_utilisateur=user_id).all()
            if not lists:
                return jsonify([])

            lists_data = []
            for lst in lists:
                movie_count = session.query(EntreeListe).filter_by(id_liste=lst.id).count()
                lists_data.append({
                    'list_id': lst.id,
                    'list_name': lst.nom_liste,
                    'is_empty': movie_count == 0
                })

            current_app.logger.debug(f"User lists data: {lists_data}")
            return jsonify(lists_data)
        except Exception as e:
            current_app.logger.error(f"Error getting user lists: {str(e)}")
            return jsonify({"error": str(e)}), 500




@app.route('/similar_movies/<int:movie_id>', methods=['GET'])
@jwt_required()
def similar_movies(movie_id):
    current_app.logger.debug(f"Received request for similar movies to movie ID: {movie_id}")
    try:
        with session_scope() as session:
            similar_movie_ids, similar_movie_similarities = find_similar_movies_by_id(collection, movie_id, top_n=5)
            current_app.logger.debug(f"Found similar movies: {similar_movie_ids}")
            return jsonify_movies(session, similar_movie_ids)
    except ValueError as e:
        current_app.logger.error(f"ValueError: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Exception: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/list/<int:list_id>/similar_movies', methods=['GET'])
@jwt_required()
def similar_movies_by_list(list_id):
    try:
        with session_scope() as session:
            similar_movie_ids, similar_movie_similarities = find_similar_movies_by_list_id(session, collection, list_id,
                                                                                           top_n=5)
            return jsonify_movies(session, similar_movie_ids)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/user_lists', methods=['GET'])
@jwt_required()
def get_user_lists():
    user_id = get_jwt_identity()['user_id']
    lists = Liste.query.filter_by(id_utilisateur=user_id).all()
    lists_data = [{"id": lst.id, "nom_liste": lst.nom_liste} for lst in lists]
    return jsonify(lists_data)


@app.route('/user/<int:user_id>/details', methods=['GET'])
@jwt_required()
def user_details(user_id):
    with session_scope() as session:
        user_data = get_user_details(session, user_id)
        if user_data:
            return jsonify(user_data)
        else:
            return jsonify({"error": "User not found"}), 404


@app.route('/register_admin', methods=['POST'])
def register_admin():
    with session_scope() as session:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')

        if not email or not password or not name:
            return jsonify({'error': 'Missing email, password or name'}), 400

        existing_admin = session.query(Utilisateur).filter_by(is_admin=True).first()
        if existing_admin:
            return jsonify({'error': 'Admin already exists'}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_admin = Utilisateur(email=email, mot_de_passe=hashed_password, nom=name, is_admin=True)

        session.add(new_admin)
        session.commit()

        return jsonify({'message': 'Admin registered successfully'}), 201


@app.route('/register_user', methods=['POST'])
def register_user():
    with session_scope() as session:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not name or not email or not password:
            return jsonify({"message": "Missing data"}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = Utilisateur(nom=name, email=email, mot_de_passe=hashed_password)

        try:
            session.add(new_user)
            session.commit()
            return jsonify({"message": "User registered successfully"}), 200
        except Exception as e:
            session.rollback()
            return jsonify({"message": "Registration failed", "error": str(e)}), 500


@app.route('/lists', methods=['POST'])
@jwt_required()
def create_list():
    with session_scope() as session:
        data = request.get_json()
        list_name = data.get('name')

        if not list_name:
            return jsonify({'error': 'No Lists name provided'}), 400

        user_identity = get_jwt_identity()  # Récupérer l'identité utilisateur
        user_id = user_identity.get('user_id')  # Extraire l'ID utilisateur du dictionnaire
        new_list = Liste(id_utilisateur=user_id, nom_liste=list_name)
        session.add(new_list)
        session.commit()

        return jsonify({'message': 'Lists created', 'Lists': {'id': new_list.id, 'name': new_list.nom_liste}}), 201


@app.route('/list/<int:list_id>/add_movie', methods=['POST'])
@jwt_required()
def add_movie_to_list(list_id):
    data = request.get_json()
    current_app.logger.debug(f"Received data: {data}")
    user_identity = get_jwt_identity()
    user_id = user_identity['user_id']

    movie_id = data.get('movie_id')
    note = data.get('note')
    comment = data.get('comment')

    if not movie_id or note is None:
        current_app.logger.error(f"Missing movie_id or note: movie_id={movie_id}, note={note}")
        return jsonify({'error': 'Movie ID and rating are required.'}), 400

    with session_scope() as session:
        movie = session.get(Metrage, movie_id)
        liste = session.get(Liste, list_id)
        if not movie or not liste:
            error_message = 'Movie not found.' if not movie else 'List not found.'
            current_app.logger.error(f"{error_message} ID: {movie_id if not movie else list_id}")
            return jsonify({'error': error_strings}), 404

        critique = session.query(Critique).filter_by(id_metrage=movie_id, id_utilisateur=user_id).first()
        if critique:
            critique.note = note
            critique.commentaire = comment
        else:
            critique = Critique(id_utilisateur=user_id, id_metrage=movie_id, note=note, commentaire=comment)
            session.add(critique)
            list_entry = EntreeListe(id_liste=list_id, id_metrage=movie_id)
            session.add(list_entry)

        session.commit()
        current_app.logger.debug(f"Movie {movie_id} added to list {list_id} with new/updated critique.")
        return jsonify({'message': 'Movie added to list with new/updated critique.'}), 201


@app.route('/search_movies', methods=['GET'])
@jwt_required()
def search_movies():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])

    with session_scope() as session:
        try:
            movies = session.query(Metrage).filter(Metrage.titre.ilike(f'%{query}%')).all()
            movies_data = [{'id': movie.id, 'title': movie.titre, 'release_year': movie.annee} for movie in movies]
            return jsonify(movies_data)
        except Exception as e:
            logcurrent_app.logger.error(f"Error searching movies: {str(e)}")
            return jsonify({"error": str(e)}), 500


@app.route('/list/<int:list_id>', methods=['DELETE'])
@jwt_required()
def delete_list(list_id):
    with session_scope() as session:
        liste = session.get(Liste, list_id)
        if not liste:
            return jsonify({'error': 'Lists not found'}), 404

        try:
            session.delete(liste)
            session.commit()
            return jsonify({'message': 'Lists deleted successfully'}), 200
        except Exception as e:
            current_app.logger.error(f'Error deleting Lists: {e}')
            return jsonify({'error': 'Failed to delete Lists'}), 500


CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)


@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization,Cache-Control"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.route('/list/<int:list_id>/remove_movie', methods=['DELETE', 'OPTIONS'])
@jwt_required()
def remove_movie_from_list(list_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    with session_scope() as session:
        data = request.get_json()
        current_app.logger.debug(f'Received data: {data}')

        if not data:
            current_app.logger.error('No data provided')
            return jsonify({'error': 'No data provided'}), 400

        movie_id = data.get('movie_id')
        current_app.logger.debug(f'Movie ID: {movie_id}')

        if not movie_id:
            current_app.logger.error('No movie ID provided')
            return jsonify({'error': 'No movie ID provided'}), 400

        list_entry = session.query(EntreeListe).filter_by(id_liste=list_id, id_metrage=movie_id).first()
        if not list_entry:
            current_app.logger.error('Movie not found in the Lists')
            return jsonify({'error': 'Movie not found in the Lists'}), 404

        try:
            session.delete(list_entry)
            session.commit()
            current_app.logger.info(f'Movie {movie_id} removed from Lists {list_id}')
        except Exception as e:
            current_app.logger.error(f'Error removing movie from Lists: {e}')
            return jsonify({'error': 'Failed to remove movie from Lists'}), 500

        # Fetch updated Lists details
        return get_list_details(list_id)


@app.route('/movies/<int:movie_id>', methods=['GET'])
@jwt_required()
def get_movie_details(movie_id):
    with session_scope() as session:
        movie = session.get(Metrage, movie_id)
        if not movie:
            return jsonify({"error": "Movie not found"}), 404

        directors = [credit.personne.nom for credit in movie.credits if credit.fonction == 'Director']
        actors = [credit.personne.nom for credit in movie.credits if credit.fonction == 'Actor']

        movie_data = {
            "id": movie.id,
            "titre": movie.titre,
            "réalisateur": directors,
            "annee": movie.annee,
            "casting": actors,
            "synopsis": movie.synopsis,
            "note_moyenne": movie.note_moyenne
        }
        return jsonify(movie_data)


if __name__ == '__main__':
    app.run(host='flask', debug=True, port=5001)
