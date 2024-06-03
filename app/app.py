from flask import jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, login_user, UserMixin, LoginManager
from flask_admin import Admin
import jwt
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
    search_movie_by_title
)
import admin_setup
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import logging
from contextlib import contextmanager

# Configuration de la base de données MySQL
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

# Configuration de ChromaDB
chroma_client = chromadb.PersistentClient(path="../vec_data")
collection = chroma_client.get_or_create_collection(name="Movie", metadata={"hnsw:space": "cosine"})

# Création de l'application app
app = create_app()

login_manager = LoginManager()
login_manager.init_app(app)
admin = Admin(app, template_mode='bootstrap3')
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
# Ajouter des vues administratives
admin.add_view(admin_setup.AdminModelView(Utilisateur, db.session))




@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
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

@login_manager.user_loader
def load_user(user_id):
    return Utilisateur.query.get(int(user_id))

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = Utilisateur.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.mot_de_passe, password):
        access_token = create_access_token(identity={'user_id': user.id, 'is_admin': user.is_admin}, expires_delta=timedelta(hours=24))
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
    return jsonify({'Movie': [{'id': movie.id, 'title': movie.titre, 'director': movie.credits.directeur_nom} for movie in movies]})

@app.route('/list/<int:list_id>', methods=['GET'])
@jwt_required()
def get_list_details(list_id):
    with session_scope() as session:
        list_details = session.query(
            Liste.nom_liste.label('list_name'),
            Metrage.id.label('movie_id'),
            Metrage.titre.label('movie_title'),
            Metrage.annee.label('release_date'),
            Personne.nom.label('director_name')
        ).join(
            EntreeListe, Liste.id == EntreeListe.id_liste
        ).join(
            Metrage, EntreeListe.id_metrage == Metrage.id
        ).join(
            Credit, (Metrage.id == Credit.id_metrage) & (Credit.fonction == 'Director')
        ).join(
            Personne, Credit.id_personne == Personne.id
        ).filter(
            Liste.id == list_id
        ).all()

        if not list_details:
            return jsonify({
                'list_name': '',
                'Movie': []
            })

        data = {
            'list_name': list_details[0].list_name,
            'Movie': [{'id': result.movie_id, 'title': result.movie_title, 'release_date': result.release_date, 'director': result.director_name} for result in list_details]
        }

        return jsonify(data)



@app.route('/list/<int:list_id>/similar_movies', methods=['GET'])
@jwt_required()
def get_similar_movies_by_list(list_id):
    with session_scope() as session:
        similar_movie_ids, similar_movie_distances = find_similar_movies_by_list_id(session, list_id, top_n=5)
        if not similar_movie_ids:
            return jsonify({"message": "No similar Movie found."}), 404

        return jsonify({
            "list_id": list_id,
            "similar_movies": [
                {"movie_id": movie_id, "distance": distance}
                for movie_id, distance in zip(similar_movie_ids, similar_movie_distances)
            ]
        })

@app.route('/user/<int:user_id>/ratings', methods=['GET'])
@jwt_required()
def get_ratings(user_id):
    with session_scope() as session:
        ratings = get_user_ratings(session, user_id)
        ratings_list = [{"movie_id": rating.id_metrage, "note": rating.note, "comment": rating.commentaire} for rating in ratings]
        return jsonify({"user_id": user_id, "ratings": ratings_list})

@app.route('/user/<int:user_id>/lists', methods=['GET'])
@jwt_required()
def get_lists(user_id):
    with session_scope() as session:
        try:
            lists = get_user_list_ids(session, user_id)
            if not lists:
                return jsonify([])

            lists_data = [{'list_id': list_id, 'list_name': list_name} for list_id, list_name in lists]
            return jsonify(lists_data)
        except Exception as e:
            logging.error(f"Error getting user lists: {str(e)}")
            return jsonify({"error": str(e)}), 500



@app.route('/similar_movies/<int:movie_id>', methods=['GET'])
@jwt_required()
def similar_movies(movie_id):
    try:
        similar_movie_ids, similar_movie_similarities = find_similar_movies_by_id(collection, movie_id, top_n=5)
        return jsonify({"similar_movie_ids": similar_movie_ids, "similar_movie_similarities": similar_movie_similarities})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/similar_movies_by_list/<int:list_id>', methods=['GET'])
@jwt_required()
def similar_movies_by_list(list_id):
    try:
        with session_scope() as session:
            similar_movie_ids, similar_movie_similarities = find_similar_movies_by_list_id(session, collection, list_id, top_n=5)
            return jsonify({"similar_movie_ids": similar_movie_ids, "similar_movie_similarities": similar_movie_similarities})
    except ValueError as e:
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
    with session_scope() as session:
        data = request.get_json()
        movie_id = data.get('movie_id')
        note = data.get('note')
        comment = data.get('comment')

        if not movie_id or note is None:
            return jsonify({'error': 'No movie ID or rating provided'}), 400

        movie = session.query(Metrage).get(movie_id)
        if not movie:
            return jsonify({'error': 'Movie not found'}), 404

        list_entry = EntreeListe(id_liste=list_id, id_metrage=movie.id, note=note, comment=comment)
        session.add(list_entry)
        session.commit()

        # Fetch updated Lists details
        list_details = get_list_details(list_id).json

        return jsonify(list_details), 201

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
            logging.error(f"Error searching movies: {str(e)}")
            return jsonify({"error": str(e)}), 500

@app.route('/list/<int:list_id>', methods=['DELETE'])
@jwt_required()
def delete_list(list_id):
    with session_scope() as session:
        liste = session.query(Liste).get(list_id)
        if not liste:
            return jsonify({'error': 'Lists not found'}), 404

        try:
            session.delete(liste)
            session.commit()
            return jsonify({'message': 'Lists deleted successfully'}), 200
        except Exception as e:
            logging.error(f'Error deleting Lists: {e}')
            return jsonify({'error': 'Failed to delete Lists'}), 500


CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization,Cache-Control"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    return response



@app.route('/list/<int:list_id>/remove_movie', methods=['DELETE', 'OPTIONS'])
@jwt_required()
def remove_movie_from_list(list_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json()
    logging.debug(f'Received data: {data}')

    if not data:
        logging.error('No data provided')
        return jsonify({'error': 'No data provided'}), 400

    movie_id = data.get('movie_id')
    logging.debug(f'Movie ID: {movie_id}')

    if not movie_id:
        logging.error('No movie ID provided')
        return jsonify({'error': 'No movie ID provided'}), 400

    list_entry = EntreeListe.query.filter_by(id_liste=list_id, id_metrage=movie_id).first()
    if not list_entry:
        logging.error('Movie not found in the Lists')
        return jsonify({'error': 'Movie not found in the Lists'}), 404

    try:
        db.session.delete(list_entry)
        db.session.commit()
        logging.info(f'Movie {movie_id} removed from Lists {list_id}')
    except Exception as e:
        logging.error(f'Error removing movie from Lists: {e}')
        return jsonify({'error': 'Failed to remove movie from Lists'}), 500

    # Fetch updated Lists details
    return get_list_details(list_id)


@app.route('/movies/<int:movie_id>', methods=['GET'])
@jwt_required()
def get_movie_details(movie_id):
    movie = Metrage.query.get(movie_id)
    if not movie:
        return jsonify({"error": "Movie not found"}), 404

    movie_data = {
        "id": movie.id,
        "titre": movie.titre,
        "annee": movie.annee,
        "type": movie.type,
        "synopsis": movie.synopsis,
        "note_moyenne": movie.note_moyenne
    }
    return jsonify(movie_data)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5001)
