import pandas as pd

# Définition de la fonction read_tsv pour lire des fichiers TSV compressés
def read_tsv(filename):
    return pd.read_csv(filename, compression='gzip', sep='\t', header=0, low_memory=False)

# Lecture du fichier 'title.basics.tsv.gz' et stockage dans un DataFrame
df_basics = read_tsv('title.basics.tsv.gz')
# Création d'un ensemble des identifiants des titres pour adultes (isAdult == 1)
ids_to_delete = set(df_basics[df_basics.isAdult == 1].tconst.unique())

# Définition de la fonction filter_sql pour filtrer les fichiers selon les ids à supprimer
def filter_tsv(in_file, out_file):
    # Lecture du fichier d'entrée
    df = read_tsv(in_file)
    # Filtrage du DataFrame pour exclure les enregistrements dont les identifiants sont dans ids_to_delete
    df_filtered = df[~df['tconst'].isin(ids_to_delete)]
    df_filtered.to_csv(out_file, sep='\t')

# Lecture et filtrage des informations des personnes
df_people = read_tsv('name.basics.tsv.gz')
df_people = df_people[['nconst', 'primaryName', 'birthYear', 'deathYear']]

# Liste des fichiers d'entrée à traiter
in_files = ['title.basics.tsv.gz', 'title.crew.tsv.gz', 'title.episode.tsv.gz', 'title.principals.tsv.gz', 'title.ratings.tsv.gz']
# Création des noms de fichiers de sortie
out_files = map(lambda x: x.replace('.tsv.gz', '.filtered.tsv.gz'), in_files)


# Boucle sur chaque trio de fichier d'entrée, de sortie et de colonne d'identifiant
for in_file, out_file in zip(in_files, out_files):
    # Appel de filter_sql pour filtrer chaque fichier selon les identifiants à supprimer
    filter_tsv(in_file, out_file)
