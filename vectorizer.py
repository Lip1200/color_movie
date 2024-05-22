import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.local.metrage import Metrage
from config import Config
import chromadb
from sentence_transformers import SentenceTransformer

# Configuration de la base de données MySQL
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# Configuration de ChromaDB
chroma_client = chromadb.PersistentClient(path="./vec_data")

# Récupération des métrages
metrages = session.query(Metrage).all()

# Transformation des genres
mlb = MultiLabelBinarizer()
genres_list = [[genre.nom_genre for genre in metrage.genres] for metrage in metrages]
multi_hot_genres = mlb.fit_transform(genres_list).astype(float)

# Chargement du modèle d'embedding
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

corpus = []
for metrage in metrages:
    actors = ", ".join([actor.personne.nom for actor in metrage.credits if actor.fonction == 'Actor'])
    director = ", ".join([director.personne.nom for director in metrage.credits if director.fonction == 'Director'])
    average_rating = metrage.note_moyenne if metrage.note_moyenne is not None else 0
    word_rating = ""

    if average_rating == 0:
        word_rating= "unknown"
    if average_rating < 3:
        word_rating = "very bad"
    if average_rating < 5:
        word_rating = "bad"
    if average_rating < 7:
        word_rating = "good"
    if average_rating < 9:
        word_rating = "great"
    if average_rating <= 10:
        word_rating = "excellent"

    corpus.append(f"title: {metrage.titre}\n"
                  f"synopsis: {metrage.synopsis}\n"
                  f"actor's list: {actors}\n"
                  f"director: {director}\n"
                  f"average rating: {average_rating} with the score: {word_rating} \n")

# Création des embeddings
text_embeddings = model.encode(corpus)

# Vérification des dimensions
print(f"Dimension des vecteurs multi-hot : {multi_hot_genres.shape[1]}")
print(f"Dimension des vecteurs d'embedding pour les synopsis + acteurs : {text_embeddings.shape[1]}")

# Augmenter la dimension des vecteurs multi-hot pour correspondre aux dimensions des embeddings
target_dim = text_embeddings.shape[1]
padded_multi_hot_genres = np.pad(multi_hot_genres, ((0, 0), (0, target_dim - multi_hot_genres.shape[1])), mode='constant')

# Vérification des dimensions après padding
print(f"Dimension des vecteurs multi-hot après padding : {padded_multi_hot_genres.shape[1]}")

# Moyenne pondérée pour combiner les vecteurs
genre_weight = 0.4
text_weight = 0.6

combined_vectors = [(genre_weight * genre_vector + text_weight * text_vector).tolist()
                    for genre_vector, text_vector in zip(padded_multi_hot_genres, text_embeddings)]

# Création ou récupération de la collection
collection_name = "movies"
collection = chroma_client.get_or_create_collection(name=collection_name)

# Préparation des données pour l'ajout
ids = [str(metrage.id) for metrage in metrages]

# Sauvegarde des vecteurs dans ChromaDB (sans documents et métadatas)
collection.upsert(
    ids=ids,
    embeddings=combined_vectors
)

print("Les vecteurs ont été créés et sauvegardés avec succès.")

# Interrogation de la collection
query_texts = ["An epic space adventure"]
query_embeddings = model.encode(query_texts)
results = collection.query(
    query_embeddings=query_embeddings.tolist(),
    n_results=5,  # Nombre de résultats à retourner
    include=["embeddings", "distances"]  # Inclure les embeddings et distances dans les résultats
)

# Vérification si les résultats contiennent des documents
if 'embeddings' in results and results['embeddings']:
    # Affichage des résultats de la requête
    for idx, result_id in enumerate(results['ids'][0]):
        print(f"ID du Document {idx+1}: {result_id}")
        print(f"Distance: {results['distances'][0][idx]}")
        print("-----")
else:
    print("Aucun document correspondant trouvé.")
