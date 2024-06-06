preferred_genres = {
    "Sci-Fi": 40,
    "Action": 5,
    "Adventure": 30,
    "Fantasy": 20,
    "Comedy": 3,
    "Drama": 10,
    "Thriller": 20,
}

star_wars = ["Sci-Fi", "Action", "Adventure"]
lotr = ["Fantasy", "Action", "Adventure"]
matrix = ["Sci-Fi", "Action"]
interstellar = ["Sci-Fi", "Adventure", "Drama"]
avengers = ["Action", "Adventure"]
harry_potter = ["Fantasy", "Adventure"]
inception = ["Sci-Fi", "Thriller"]


def get_pref_rate(movie_genres):
    pref_rate = 0
    for genre in movie_genres:
        pref_rate += preferred_genres.get(genre, 0)
    return pref_rate


movies = [
    ("star wars", star_wars),
    ("LOTR", lotr),
    ("Matrix", matrix),
    ("Interstellar", interstellar),
    ("Avengers", avengers),
    ("Harry Potter", harry_potter),
    ("Inception", inception),
]

# Sort Movie by preference rate
movies.sort(key=lambda x: get_pref_rate(x[1]), reverse=True)
for movie in movies:
    print(movie[0], movie[1], get_pref_rate(movie[1]))
