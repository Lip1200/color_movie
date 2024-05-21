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

# Transformation des synopsis et des titres en vecteurs TF-IDF
corpus = [f"{metrage.titre} {metrage.synopsis}" for metrage in metrages]
text_embeddings = model.encode(corpus)


# Transformation des acteurs
actors_list = [" ".join([actor.personne.nom for actor in metrage.credits]) for metrage in metrages]
actor_embeddings = model.encode(actors_list)

# Vérification des dimensions
print(f"Dimension des vecteurs multi-hot : {multi_hot_genres.shape[1]}")
print(f"Dimension des vecteurs d'embedding pour les synopsys: {text_embeddings.shape[1]}")
print(f"Dimension des vecteurs des acteurs : {actor_embeddings.shape[1]}")

# Augmenter la dimension des vecteurs multi-hot pour correspondre aux dimensions des embeddings
target_dim = text_embeddings.shape[1]
padded_multi_hot_genres = np.pad(multi_hot_genres, ((0, 0), (0, target_dim - multi_hot_genres.shape[1])), mode='constant')

# Vérification des dimensions après padding
print(f"Dimension des vecteurs multi-hot après padding : {padded_multi_hot_genres.shape[1]}")

# Moyenne pondérée pour combiner les vecteurs
genre_weight = 0.4
text_weight = 0.4
actor_weight = 0.2


combined_vectors = [(genre_weight * genre_vector + text_weight * text_vector + actor_weight * actor_vector).tolist()
                    for genre_vector, text_vector, actor_vector in zip(padded_multi_hot_genres, text_embeddings, actor_embeddings)]



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
    include=["data", "distances"]  # Inclure les ids et distances dans les résultats
)

# Vérification si les résultats contiennent des documents
if results['ids'] is not None:
    # Affichage des résultats de la requête
    for idx, result_id in enumerate(results['ids'][0]):
        print(f"ID du Document {idx+1}: {result_id}")
        print(f"Distance: {results['distances'][0][idx]}")
        print("-----")
else:
    print("Aucun document correspondant trouvé.")