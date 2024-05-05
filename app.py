from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config
from src.models.local import (
    db,
    Base,
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

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    return app

app = create_app()
db.init_app(app)

@app.route('/')
def index():
    return "Welcome to the Movie API!"

@app.route('/movies', methods=['GET'])
def get_movies():
    movies = Metrage.query.all()
    return {'movies': [{'id': movie.id, 'title': movie.titre} for movie in movies]}

@app.route('/movies/<int:user_id>', methods=['GET'])
def get_user_movies(user_id):
    results = db.session.query(
        Liste.titre.label('liste_titre'),
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


if __name__ == '__main__':
    app.run(debug=True, port=5001) #(mon port 5000 est encombré)
