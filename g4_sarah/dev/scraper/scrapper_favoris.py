import requests
from bs4 import BeautifulSoup
import csv

def fetch_movie_data(session, url: str) ->list[str]:
    response = session.get(url)
    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        print("Failed to retrieve the webpage")
        return []

    # Parser le contenu HTML avec BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Sélectionner tous les éléments de la liste de films
    films = soup.find_all('li', class_='item')

    # Liste pour stocker les données des films
    film_list = []

    # Extraire les données de chaque film
    for film in films:
        title_element = film.find('h3', class_='title')
        original_title_element = title_element.find('span', class_='original')
        director_element = film.find('span', class_='director')
        year_element = film.find('span', class_='year')

        title = original_title_element.get_text(strip=True) if original_title_element else title_element.get_text(strip=True) if title_element else "N/A"
        director = director_element.get_text(strip=True) if director_element else "Unknown"
        year = year_element.get_text(strip=True) if year_element else "Unknown"

        # Ajouter les données à la liste
        film_list.append({
            'Title': title,
            'Director': director,
            'Year': year
        })

    return film_list

def write_to_csv(movie_data: list[str], filename: str) -> None:
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Director', 'Year'])  # Header
        for data in movie_data:
            writer.writerow([data['Title'], data['Director'], data['Year']])  # Data

def main():
    session = requests.Session()

    while True:
        url = input("tapez l'URL de lacinetek.com ou 'exit' pour quitter:  ")
        if url.lower() == 'exit':
            break

        movie_data = fetch_movie_data(session, url)
        if movie_data:
            filename = url.split('/')[-1] + '.csv' if '/' in url else 'output.csv'
            write_to_csv(movie_data, filename)
            print(f"Data written to {filename}")
        else:
            print("No movie data found.")

    session.close()


if __name__ == "__main__":
    main()
