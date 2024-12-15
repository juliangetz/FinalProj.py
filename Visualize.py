import sqlite3
import matplotlib.pyplot as plt
import csv
from datetime import datetime

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

    years = [row[0] for row in rows]
    counts = [row[1] for row in rows]

    # Convert years to integers if possible, to ensure sorting is correct
    try:
        years = [int(y) for y in years]
    except ValueError:
        # If conversion fails, just leave them as strings
        pass

    print("OMDb Movies per Year:")
    for y, c in zip(years, counts):
        print(f"Year: {y}, Count: {c}")

    # Write calculated data to CSV
    with open("omdb_movies_per_year.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Year", "Count"])
        for y, c in zip(years, counts):
            writer.writerow([y, c])

    plt.figure(figsize=(12, 6))
    plt.bar(years, counts, color='blue')
    plt.xlabel('Year')
    plt.ylabel('Number of Movies')
    plt.title('Number of Movies Released Each Year (OMDb Data)')

    # Reduce the number of x-ticks if there are many years
    if len(years) > 20:
        # Show every 5th year as a tick
        tick_positions = range(0, len(years), 5)
        tick_labels = [years[i] for i in tick_positions]
        plt.xticks(tick_labels, rotation=45, ha='right')
    else:
        # If there are not many years, show them all, just rotate for clarity
        plt.xticks(years, rotation=45, ha='right')

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

    print("\nTMDB Movies per Language:")
    for row in rows:
        print(f"Language: {row[0]}, Count: {row[1]}")

    language_codes = [r[0] for r in rows]
    counts = [r[1] for r in rows]

    # Write calculated data to CSV
    with open("tmdb_movies_per_language.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Language Code", "Count"])
        for lang, cnt in zip(language_codes, counts):
            writer.writerow([lang, cnt])

    plt.figure(figsize=(12, 6))
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

    print("\nTMDB Movies per Genre:")
    for row in rows:
        print(f"Genre: {row[0]}, Count: {row[1]}")

    genres = [r[0] for r in rows]
    counts = [r[1] for r in rows]

    # Write calculated data to CSV
    with open("tmdb_movies_per_genre.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Genre", "Count"])
        for genre, cnt in zip(genres, counts):
            writer.writerow([genre, cnt])

    plt.figure(figsize=(12, 6))
    plt.bar(genres, counts, color='purple')
    plt.xlabel('Genre')
    plt.ylabel('Number of Movies')
    plt.title('Number of Movies Per Genre (TMDB Data)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def visualize_tmdb_months():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Extract month from release_date and count movies per month
    cur.execute("""
        SELECT 
            strftime('%m', release_date) AS Month, 
            COUNT(*) AS CountPerMonth
        FROM movies_tmdb
        WHERE release_date IS NOT NULL AND release_date != ''
        GROUP BY Month
        ORDER BY Month;
    """)

    rows = cur.fetchall()
    conn.close()

    # Convert month numbers to month names
    month_numbers = [row[0] for row in rows]
    counts = [row[1] for row in rows]
    month_names = [datetime.strptime(m, "%m").strftime("%B") for m in month_numbers]

    print("\nTMDB Movies per Month:")
    for month, count in zip(month_names, counts):
        print(f"Month: {month}, Count: {count}")

    # Write calculated data to CSV
    with open("tmdb_movies_per_month.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Month", "Count"])
        for month, count in zip(month_names, counts):
            writer.writerow([month, count])

    # Create a pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(counts, labels=month_names, autopct='%1.1f%%', startangle=140, colors=plt.cm.tab20.colors)
    plt.title('Distribution of Movie Releases by Month (TMDB Data)')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.tight_layout()
    plt.show()


def visualize_omdb_ratings():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Fetch IMDb ratings from OMDb data, excluding 'N/A' ratings
    cur.execute("""
        SELECT imdbRating
        FROM movies
        WHERE imdbRating != 'N/A' AND imdbRating IS NOT NULL;
    """)

    rows = cur.fetchall()
    conn.close()

    ratings = [float(row[0]) for row in rows if row[0] != 'N/A']

    print("\nOMDb Movies by IMDb Rating:")
    print(f"Total Ratings Available: {len(ratings)}")

    # Write calculated data to CSV
    with open("omdb_movies_ratings.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["IMDb Rating"])
        for rating in ratings:
            writer.writerow([rating])

    # Create a histogram
    plt.figure(figsize=(12, 6))
    plt.hist(ratings, bins=10, color='gold', edgecolor='black')
    plt.xlabel('IMDb Rating')
    plt.ylabel('Number of Movies')
    plt.title('Distribution of IMDb Ratings (OMDb Data)')
    plt.xticks(range(0, 11))  # Ratings typically range from 0 to 10
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    visualize_omdb()
    visualize_tmdb_languages()
    visualize_tmdb_genres()
    visualize_tmdb_months()
    visualize_omdb_ratings()
