import sqlite3
import requests

DB_FILE = 'movies.db'

# ----- OMDb API Details -----
OMDB_API_KEY = '431128c6'
OMDB_SEARCH_TERM = 'Comedy'
OMDB_BATCH_SIZE = 10

# ----- TMDB API Details -----
TMDB_API_KEY = 'c9f38a087f579feb4174d8e353fe773f'
TMDB_BATCH_SIZE = 25
TMDB_SEARCH_URL = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US"


# ----- OMDb Functions -----
def create_omdb_table(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS movies (
        imdbID TEXT PRIMARY KEY,
        Title TEXT,
        Year TEXT,
        Type TEXT,
        Poster TEXT
    )''')
    conn.commit()

def get_omdb_stored_count(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM movies")
    return cur.fetchone()[0]

def insert_omdb_movie(conn, movie):
    conn.execute("""
        INSERT OR IGNORE INTO movies (imdbID, Title, Year, Type, Poster)
        VALUES (?, ?, ?, ?, ?)""", (
            movie.get('imdbID'),
            movie.get('Title'),
            movie.get('Year'),
            movie.get('Type'),
            movie.get('Poster')
        )
    )
    conn.commit()

def fetch_omdb_movies(page):
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={OMDB_SEARCH_TERM}&page={page}"
    response = requests.get(url)
    data = response.json()
    if data.get('Response', 'False') == 'True' and 'Search' in data:
        return data['Search']
    return []

def gather_omdb_data():
    conn = sqlite3.connect(DB_FILE)
    create_omdb_table(conn)
    stored_count = get_omdb_stored_count(conn)

    # Determine next page
    next_page = (stored_count // 10) + 1
    movies = fetch_omdb_movies(next_page)

    if not movies:
        print(f"No OMDb movies returned for page {next_page}. Possibly out of results.")
        conn.close()
        return

    inserted = 0
    for movie in movies:
        if inserted >= OMDB_BATCH_SIZE:
            break
        insert_omdb_movie(conn, movie)
        inserted += 1

    new_count = get_omdb_stored_count(conn)
    print(f"[OMDb] Inserted {new_count - stored_count} new items. Total now: {new_count}.")
    conn.close()


# ----- TMDB Functions -----
def create_tmdb_tables(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS languages_tmdb (
            language_id INTEGER PRIMARY KEY AUTOINCREMENT,
            language_code TEXT UNIQUE
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS movies_tmdb (
            tmdb_id INTEGER PRIMARY KEY,
            title TEXT,
            release_date TEXT,
            language_id INTEGER,
            FOREIGN KEY(language_id) REFERENCES languages_tmdb(language_id)
        )
    ''')

    # Create a genres table and a junction table for TMDB movies and genres
    conn.execute('''
        CREATE TABLE IF NOT EXISTS genres_tmdb (
            genre_id INTEGER PRIMARY KEY,
            genre_name TEXT UNIQUE
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS movie_genres_tmdb (
            tmdb_id INTEGER,
            genre_id INTEGER,
            PRIMARY KEY (tmdb_id, genre_id),
            FOREIGN KEY(tmdb_id) REFERENCES movies_tmdb(tmdb_id),
            FOREIGN KEY(genre_id) REFERENCES genres_tmdb(genre_id)
        )
    ''')
    conn.commit()

def get_tmdb_stored_count(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM movies_tmdb")
    return cur.fetchone()[0]

def get_language_id(conn, language_code):
    cur = conn.cursor()
    cur.execute("SELECT language_id FROM languages_tmdb WHERE language_code = ?", (language_code,))
    row = cur.fetchone()
    if row:
        return row[0]
    else:
        cur.execute("INSERT INTO languages_tmdb (language_code) VALUES (?)", (language_code,))
        conn.commit()
        return cur.lastrowid

def get_genre_id(conn, genre_id, genre_name):
    # Insert the genre if not exists
    cur = conn.cursor()
    cur.execute("SELECT genre_id FROM genres_tmdb WHERE genre_id = ?", (genre_id,))
    row = cur.fetchone()
    if not row:
        cur.execute("INSERT OR IGNORE INTO genres_tmdb (genre_id, genre_name) VALUES (?, ?)", (genre_id, genre_name))
        conn.commit()
    return genre_id

def insert_tmdb_movie(conn, movie):
    tmdb_id = movie.get('id')
    title = movie.get('title')
    release_date = movie.get('release_date')
    original_language = movie.get('original_language')

    language_id = get_language_id(conn, original_language)

    conn.execute("""
        INSERT OR IGNORE INTO movies_tmdb (tmdb_id, title, release_date, language_id)
        VALUES (?, ?, ?, ?)
    """, (tmdb_id, title, release_date, language_id))
    conn.commit()

    # Insert genres
    genres = movie.get('genre_ids', [])
    for g_id in genres:
        # For simplicity, we must know genre names. TMDB API provides standard mappings, but here we hardcode or fetch them.
        # For best results, retrieve the genre list from TMDB API and store them once.
        # Below is a hardcoded genre map (commonly known TMDB genres):
        genre_map = {
            28: "Action",
            12: "Adventure",
            16: "Animation",
            35: "Comedy",
            80: "Crime",
            99: "Documentary",
            18: "Drama",
            10751: "Family",
            14: "Fantasy",
            36: "History",
            27: "Horror",
            10402: "Music",
            9648: "Mystery",
            10749: "Romance",
            878: "Science Fiction",
            10770: "TV Movie",
            53: "Thriller",
            10752: "War",
            37: "Western"
        }
        genre_name = genre_map.get(g_id, "Unknown")
        get_genre_id(conn, g_id, genre_name)

        conn.execute("""
            INSERT OR IGNORE INTO movie_genres_tmdb (tmdb_id, genre_id)
            VALUES (?, ?)
        """, (tmdb_id, g_id))
    conn.commit()

def fetch_tmdb_movies(page):
    url = f"{TMDB_SEARCH_URL}&page={page}"
    response = requests.get(url)
    data = response.json()
    if data.get('results'):
        return data['results']
    return []

def gather_tmdb_data():
    conn = sqlite3.connect(DB_FILE)
    create_tmdb_tables(conn)
    
    stored_count = get_tmdb_stored_count(conn)
    next_page = (stored_count // 20) + 1

    movies = fetch_tmdb_movies(next_page)
    if not movies:
        print(f"No TMDB movies returned for page {next_page}. Possibly out of results.")
        conn.close()
        return

    inserted = 0
    for movie in movies:
        if inserted >= TMDB_BATCH_SIZE:
            break
        insert_tmdb_movie(conn, movie)
        inserted += 1

    new_count = get_tmdb_stored_count(conn)
    print(f"[TMDB] Inserted {new_count - stored_count} new items. Total now: {new_count}.")
    conn.close()


if __name__ == "__main__":
    # Gather OMDb data
    gather_omdb_data()

    # Gather TMDB data
    gather_tmdb_data()
