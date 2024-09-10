from dotenv import load_dotenv
import os
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify

# Authentication
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "https://spotify.norman.com/widget"
# SCOPE = "user-read-currently-playing"
SCOPE = "user-library-read"

sp_oauth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)  

sp = Spotify(auth_manager=sp_oauth)

#

taylor_uri = 'spotify:artist:06HL4z0CvFAxyc27GXpf02'
results = sp.artist_albums(taylor_uri, album_type='album')
albums = results['items']
while results['next']:
    results = sp.next(results)
    albums.extend(results['items'])

for album in albums:
    print(album['name'])