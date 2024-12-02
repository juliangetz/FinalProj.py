import requests
import sqlite3
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns

# Your API Keys (Replace with your actual keys)
TMDB_API_KEY = 'your_tmdb_api_key'
OMDB_API_KEY = 'your_omdb_api_key'
BASE_URL_TMDB = 'https://api.themoviedb.org/3'
BASE_URL_OMDB = 'http://www.omdbapi.com/'

# Database setup
def create_database():
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tmdb_movies (
            movie_id INTEGER PRIMARY KEY,
            title TEXT,
            release_date TEXT,
            genre TEXT,
            average_rating REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS omdb_movies (
            movie_id INTEGER PRIMARY KEY,
            title TEXT,
            plot TEXT,
            director TEXT,
            imdb_rating REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS imdb_movies (
            movie_id INTEGER PRIMARY KEY,
            title TEXT,
            year TEXT,
            imdb_rank INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Fetch data from TMDb API
def fetch_tmdb_data():
    url = f"{BASE_URL_TMDB}/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page=1"
    response = requests.get(url)
    data = response.json()
    
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()

    for movie in data['results']:
        title = movie['title']
        release_date = movie['release_date']
        genre = ', '.join(map(str, movie['genre_ids']))  # Mapping genre IDs (could be refined)
        rating = movie['vote_average']

        cursor.execute("INSERT OR IGNORE INTO tmdb_movies (title, release_date, genre, average_rating) VALUES (?, ?, ?, ?)",
                       (title, release_date, genre, rating))

    conn.commit()
    conn.close()

# Fetch data from OMDb API
def fetch_omdb_data(movie_title):
    url = f"{BASE_URL_OMDB}?t={movie_title}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    data = response.json()

    return {
        'plot': data.get('Plot'),
        'director': data.get('Director'),
        'imdb_rating': data.get('imdbRating')
    }

def store_omdb_data():
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()

    cursor.execute("SELECT title FROM tmdb_movies")
    movies = cursor.fetchall()

    for movie in movies:
        movie_title = movie[0]
        omdb_data = fetch_omdb_data(movie_title)

        cursor.execute("INSERT OR IGNORE INTO omdb_movies (title, plot, director, imdb_rating) VALUES (?, ?, ?, ?)",
                       (movie_title, omdb_data['plot'], omdb_data['director'], omdb_data['imdb_rating']))

    conn.commit()
    conn.close()

# Web Scraping from IMDb Top Movies
def fetch_imdb_data():
    url = "https://www.imdb.com/chart/top"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    movies = soup.select('td.titleColumn')
    movie_list = []

    for movie in movies:
        title = movie.a.text
        year = movie.span.text.strip('()')
        imdb_rank = int(movie.contents[0].strip())

        movie_list.append({
            'title': title,
            'year': year,
            'rank': imdb_rank
        })

    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()

    for movie in movie_list:
        cursor.execute("INSERT OR IGNORE INTO imdb_movies (title, year, imdb_rank) VALUES (?, ?, ?)",
                       (movie['title'], movie['year'], movie['rank']))

    conn.commit()
    conn.close()

# Calculating Average Rating by Genre
def average_rating_by_genre():
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT genre, AVG(average_rating) FROM tmdb_movies GROUP BY genre")
    result = cursor.fetchall()
    
    conn.close()
    return result

# Plotting Genre Rating Comparison
def plot_genre_ratings():
    avg_ratings = average_rating_by_genre()
    genres = [item[0] for item in avg_ratings]
    ratings = [item[1] for item in avg_ratings]

    plt.figure(figsize=(10,6))
    sns.barplot(x=genres, y=ratings)
    plt.title('Average Movie Ratings by Genre')
    plt.xlabel('Genre')
    plt.ylabel('Average Rating')
    plt.xticks(rotation=45, ha="right")
    plt.show()

# IMDb vs. TMDb vs. OMDb Ratings Comparison
def imdb_vs_api_ratings():
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT tmdb_movies.title, tmdb_movies.average_rating, omdb_movies.imdb_rating, imdb_movies.imdb_rank
        FROM tmdb_movies
        LEFT JOIN omdb_movies ON tmdb_movies.title = omdb_movies.title
        LEFT JOIN imdb_movies ON tmdb_movies.title = imdb_movies.title
    ''')
    movies = cursor.fetchall()

    tmdb_ratings = []
    omdb_ratings = []
    imdb_ranks = []

    for movie in movies:
        tmdb_ratings.append(movie[1])
        omdb_ratings.append(float(movie[2]) if movie[2] else 0)
        imdb_ranks.append(movie[3])

    # Line Chart for Ratings Comparison
    plt.figure(figsize=(10,6))
    plt.plot(tmdb_ratings, label="TMDb Ratings")
    plt.plot(omdb_ratings, label="OMDb Ratings")
    plt.plot(imdb_ranks, label="IMDb Rank (Inverse)", linestyle='--')
    plt.legend()
    plt.title('Ratings Comparison: IMDb vs TMDb vs OMDb')
    plt.xlabel('Movies')
    plt.ylabel('Ratings / IMDb Rank')
    plt.show()

# Main function to run the entire process
def main():
    create_database()
    fetch_tmdb_data()
    store_omdb_data()
    fetch_imdb_data()
    
    plot_genre_ratings()
    imdb_vs_api_ratings()

if __name__ == "__main__":
    main()


##Final Proj
print("hello")