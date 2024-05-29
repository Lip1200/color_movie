import random
from sklearn.ensemble import RandomForestClassifier
import csv 
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, joinedload
from src.models.local import (
    Liste,
    Metrage,
    Personne,
    Utilisateur,
    EntreeListe,
    Credit
)

def read_movies_from_csv(file_path: str) -> list[str]:
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        return [(row[0], row[1]) for row in reader]
    
# def suggestion_genre(genre):
#     propositions = []
#     for film in read_movies_from_csv:
#         if film["genre"].lower() == genre.lower():
#             propositions.append(film["titre"])
#     if len(propositions) < 20:
#         print("Il n'y a pas assez de films dans ce genre dans la base de données.")
#     else:
#         random.shuffle(propositions)
#         return propositions[:20]

