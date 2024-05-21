import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.local.metrage import Metrage
from src.models.local.genre import Genre
from config import Config
import chromadb
from chromadb.utils import embedding_functions

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
multi_hot_genres = mlb.fit_transform(genres_list)

# Transformation des synopsis et des titres
corpus = [f"{metrage.titre} {metrage.synopsis}" for metrage in metrages]
vectorizer = TfidfVectorizer()
text_vectors = vectorizer.fit_transform(corpus).toarray()

# Combinaison des vecteurs
combined_vectors = [list(genre_vector) + list(text_vector)
                    for genre_vector, text_vector in zip(multi_hot_genres, text_vectors)]

# Convertir tous les embeddings en type float
combined_vectors = np.array(combined_vectors, dtype=float).tolist()

# Création ou récupération de la collection
collection_name = "movies"
collection = chroma_client.get_or_create_collection(name=collection_name)

# Préparation des données pour l'ajout
ids = [str(metrage.id) for metrage in metrages]
documents = [f"{metrage.titre} {metrage.synopsis}" for metrage in metrages]
metadatas = [{"titre": metrage.titre, "synopsis": metrage.synopsis} for metrage in metrages]

# Sauvegarde des vecteurs dans ChromaDB
collection.upsert(
    documents=documents,
    ids=ids,
    metadatas=metadatas,
    embeddings=combined_vectors
)

print("Les vecteurs ont été créés et sauvegardés avec succès.")

# Interrogation de la collection
query_texts = ["Une aventure épique dans l'espace"]
query_vectors = vectorizer.transform(query_texts).toarray()

# On n'a pas besoin des multi-hot genres pour les requêtes, donc on utilise directement les vecteurs de texte.
query_embeddings = np.array(query_vectors, dtype=float).tolist()

results = collection.query(
    query_embeddings=query_embeddings,
    n_results=5  # Nombre de résultats à retourner
)
print(results)
