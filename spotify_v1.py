import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging
import time
from urllib.parse import urlparse, parse_qs

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def read_credentials(file_path):
    credentials = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            credentials[key] = value
    return credentials

cred_file = 'cred.txt'
credentials = read_credentials(cred_file)
SPOTIPY_CLIENT_ID = 'cdc8876c4e7543858bc7243f0fe6a965'
SPOTIPY_CLIENT_SECRET = credentials.get('SECRET')
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'  # Or your preferred redirect URI

# Spotify API setup
SCOPE = "playlist-modify-private playlist-modify-public"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=SCOPE))


def clean_spotify_url(url):
    """Extract album ID from Spotify URL."""
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.split('/')
    return path_segments[-1] if len(path_segments) > 2 else None

def get_album_tracks(album_id):
    """Retrieve tracks from an album, handling potential errors."""
    try:
        results = sp.album_tracks(album_id)
        return [track['id'] for track in results['items']]
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 404:
            logger.warning(f"Album not found: {album_id}")
        else:
            logger.error(f"Error fetching tracks for album {album_id}: {e}")
        return []

def add_tracks_to_playlist(playlist_id, tracks):
    """Add tracks to a playlist, handling potential errors."""
    try:
        sp.playlist_add_items(playlist_id, tracks)
        logger.info(f"Added {len(tracks)} tracks to playlist")
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Error adding tracks to playlist: {e}")

def process_album_links(file_path, playlist_id):
    """Process album links from a file and add tracks to a playlist."""
    with open(file_path, 'r') as file:
        for line in file:
            album_id = clean_spotify_url(line.strip())
            if album_id:
                tracks = get_album_tracks(album_id)
                if tracks:
                    add_tracks_to_playlist(playlist_id, tracks)
                time.sleep(1)  # Avoid rate limiting
            else:
                logger.warning(f"Invalid Spotify URL: {line.strip()}")

def main():
    file_path = 'spotify_links.txt'  # File containing Spotify album links
    playlist_id = '5FnBhI6UqIpj59hHKE5dWH'  # Replace with your playlist ID
    
    try:
        process_album_links(file_path, playlist_id)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
