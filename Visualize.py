import sqlite3
import matplotlib.pyplot as plt
import csv

DB_FILE = 'movies.db'

def visualize_omdb():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        SELECT Year, COUNT(*) AS CountPerYear
        FROM movies
        GROUP BY Year
        ORDER BY Year;
    """)

    rows = cur.fetchall()
    conn.close()

    # Separate the data into lists for plotting
    years = [row[0] for row in rows]
    counts = [row[1] for row in rows]

    # Print the results to verify
    print("OMDb Movies per Year:")
    for row in rows:
        print(f"Year: {row[0]}, Count: {row[1]}")

    # Create a bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(years, counts, color='blue')
    plt.xlabel('Year')
    plt.ylabel('Number of Movies')
    plt.title('Number of Movies Released Each Year (OMDb Data)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def visualize_tmdb_languages():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Movies per language from TMDB data
    cur.execute("""
        SELECT l.language_code, COUNT(m.tmdb_id) as movie_count
        FROM movies_tmdb m
        JOIN languages_tmdb l ON m.language_id = l.language_id
        GROUP BY l.language_code
        ORDER BY movie_count DESC;
    """)

    rows = cur.fetchall()
    conn.close()

    # Print results
    print("\nTMDB Movies per Language:")
    for row in rows:
        print(f"Language: {row[0]}, Count: {row[1]}")

    # Create a bar chart
    language_codes = [r[0] for r in rows]
    counts = [r[1] for r in rows]

    plt.figure(figsize=(10, 6))
    plt.bar(language_codes, counts, color='green')
    plt.xlabel('Language Code')
    plt.ylabel('Number of Movies')
    plt.title('Number of Movies Per Language (TMDB Data)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def visualize_tmdb_genres():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Frequency of different genres from the TMDB data
    cur.execute("""
        SELECT g.genre_name, COUNT(mg.tmdb_id) AS CountPerGenre
        FROM movie_genres_tmdb mg
        JOIN genres_tmdb g ON mg.genre_id = g.genre_id
        GROUP BY g.genre_id
        ORDER BY CountPerGenre DESC;
    """)

    rows = cur.fetchall()
    conn.close()

    # Print results
    print("\nTMDB Movies per Genre:")
    for row in rows:
        print(f"Genre: {row[0]}, Count: {row[1]}")

    # Create a bar chart for TMDB genres
    genres = [r[0] for r in rows]
    counts = [r[1] for r in rows]

    plt.figure(figsize=(10, 6))
    plt.bar(genres, counts, color='purple')
    plt.xlabel('Genre')
    plt.ylabel('Number of Movies')
    plt.title('Number of Movies Per Genre (TMDB Data)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    visualize_omdb()
    visualize_tmdb_languages()
    visualize_tmdb_genres()
