# Julian Getz, Noah Rosenthal, Ari Latimer
import requests

TMDB_API_KEY = 'c9f38a087f579feb4174d8e353fe773f'
OMDB_API_KEY = '431128c6'

def fetch_tmdb_genres():
    """
    Fetches the list of movie genres from the TMDb API and returns a dictionary
    mapping genre IDs to genre names.
    """
    url = f'https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US'
    response = requests.get(url)
    genres_data = response.json()
    return {genre['id']: genre['name'] for genre in genres_data['genres']}

def fetch_tmdb_movies():
    """
    Fetches a list of popular movies from the TMDb API and maps the genre IDs
    to their respective genre names.
    """
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page=1'
    response = requests.get(url)
    movies_data = response.json()

    # Get the genre mapping (genre ID to genre name)
    genres_mapping = fetch_tmdb_genres()

    movies = []
    for movie in movies_data['results']:
        # Map genre IDs to genre names
        movie_genres = [genres_mapping.get(genre_id) for genre_id in movie['genre_ids']]
        movie_info = {
            'title': movie['title'],
            'genre': ', '.join(movie_genres),  # Join genre names into a single string
            'release_date': movie.get('release_date', 'Unknown'),
            'overview': movie['overview'],
            'tmdb_id': movie['id']  # Store TMDb ID for fetching additional details
        }
        movies.append(movie_info)

    return movies

def fetch_omdb_details(title):
    """
    Fetches additional movie details from the OMDb API based on the movie title.
    """
    url = f'http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        omdb_data = response.json()
        return {
            'imdb_rating': omdb_data.get('imdbRating', 'N/A'),
            'runtime': omdb_data.get('Runtime', 'N/A'),
            'director': omdb_data.get('Director', 'N/A')
        }
    return {
        'imdb_rating': 'N/A',
        'runtime': 'N/A',
        'director': 'N/A'
    }

def display_movies(movies):
    """
    Displays a list of movie details, including additional details from the OMDb API.
    """
    for movie in movies:
        omdb_details = fetch_omdb_details(movie['title'])
        print(f"Title: {movie['title']}")
        print(f"Genre: {movie['genre']}")
        print(f"Release Date: {movie['release_date']}")
        print(f"Overview: {movie['overview']}")
        print(f"IMDB Rating: {omdb_details['imdb_rating']}")
        print(f"Runtime: {omdb_details['runtime']}")
        print(f"Director: {omdb_details['director']}")
        print('-' * 40)

def save_movies_to_file(movies, filename):
    """
    Saves the movie details, including additional OMDb details, to a file.
    """
    with open(filename, 'w') as file:
        for movie in movies:
            omdb_details = fetch_omdb_details(movie['title'])
            file.write(f"Title: {movie['title']}\n")
            file.write(f"Genre: {movie['genre']}\n")
            file.write(f"Release Date: {movie['release_date']}\n")
            file.write(f"Overview: {movie['overview']}\n")
            file.write(f"IMDB Rating: {omdb_details['imdb_rating']}\n")
            file.write(f"Runtime: {omdb_details['runtime']}\n")
            file.write(f"Director: {omdb_details['director']}\n")
            file.write('-' * 40 + '\n')

def main():
    """
    Main function to fetch, display, and save movie details.
    """
    print("Fetching TMDb Movies...")
    tmdb_movies = fetch_tmdb_movies()

    # Display the movies
    display_movies(tmdb_movies)

    # Optionally, save the movie details to a file
    save_movies_to_file(tmdb_movies, 'movies_with_details.txt')
    print("Movies have been saved to 'movies_with_details.txt'.")

if __name__ == '__main__':
    main()