import pandas as pd

def read_tsv(filename):
    """Lit un fichier TSV compressé en format gzip."""
    return pd.read_csv(filename, compression='gzip', sep='\t', header=0, na_values='\\N', keep_default_na=False, low_memory=False)

# Lecture des données
df_basics = read_tsv('title.basics.tsv.gz')
df_crew = read_tsv('title.crew.tsv.gz')
df_episode = read_tsv('title.episode.tsv.gz')
df_people = read_tsv('name.basics.tsv.gz')
df_principals = read_tsv('title.principals.tsv.gz')
df_ratings = read_tsv('title.ratings.tsv.gz')

# Table Metrage
df_metrage = df_basics[df_basics['titleType'].isin(['movie', 'tvSeries'])]
df_metrage = df_metrage[['tconst', 'primaryTitle', 'startYear', 'genres']]
df_metrage.columns = ['ID_Metrage', 'Titre', 'Annee', 'Categorie']
df_metrage.to_csv('metrage.csv.gz', index=False, compression='gzip')

# Tables Film et Serie avec note moyenne
df_film_series = pd.merge(df_basics[['tconst', 'titleType']], df_crew[['tconst', 'directors']], on='tconst')
df_film_series = pd.merge(df_film_series, df_ratings[['tconst', 'averageRating']], on='tconst')

df_film = df_film_series[df_film_series['titleType'] == 'movie']
df_film = df_film[['tconst', 'directors', 'averageRating']]
df_film.columns = ['ID_Film', 'Realisateur', 'note_moyenne']
df_film.to_csv('film.csv.gz', index=False, compression='gzip')

df_serie = df_film_series[df_film_series['titleType'] == 'tvSeries']
df_serie = df_serie[['tconst', 'directors', 'averageRating']]
df_serie.columns = ['ID_Serie', 'Realisateur', 'note_moyenne']
df_serie.to_csv('serie.csv.gz', index=False, compression='gzip')

# Table Episode
df_episode_export = pd.merge(df_episode, df_basics[['tconst', 'primaryTitle']], on='tconst')
df_episode_export = df_episode_export[['tconst', 'parentTconst', 'seasonNumber', 'episodeNumber', 'primaryTitle']]
df_episode_export.columns = ['ID_Episode', 'ID_Serie', 'NumeroSaison', 'NumeroEpisode', 'TitreEpisode']
df_episode_export.to_csv('episode.csv.gz', index=False, compression='gzip')

# Table Personne
df_people_export = df_people[['nconst', 'primaryName', 'birthYear', 'deathYear']]
df_people_export.columns = ['ID_Personne', 'Nom', 'DateNaissance', 'DateMort']
df_people_export.to_csv('personne.csv.gz', index=False, compression='gzip')

# Préparation des tables Distribution et Distribution_Personne
df_distribution = df_principals[['tconst', 'nconst', 'category']].drop_duplicates()
df_distribution['ID_Distribution'] = pd.factorize(df_distribution['tconst'])[0] + 1  # Création d'un ID unique simplifié
df_distribution.to_csv('distribution.csv.gz', index=False, compression='gzip')

df_distribution_personne = df_distribution[['ID_Distribution', 'nconst', 'category']]
df_distribution_personne.columns = ['ID_Distribution', 'ID_personne', 'Role']
df_distribution_personne.to_csv('distribution_personne.csv.gz', index=False, compression='gzip')
