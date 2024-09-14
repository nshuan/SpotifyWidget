from dotenv import load_dotenv
import os
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify
from classes import Track
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image, ImageTk
from flask import Flask, request, redirect
import threading

auth_complete_event = threading.Event()

class SpotifyTrack:
    def __init__(self, auth_complete_event: threading.Event) -> None:
        self.auth_complete_event = auth_complete_event
        self.sp_oauth = self.authenticate() 
        self.spotify = Spotify(auth_manager=self.sp_oauth)

    # Authentication
    def authenticate(self):
        load_dotenv()
        CLIENT_ID = os.getenv("CLIENT_ID")
        CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        REDIRECT_URI = "http://localhost:8888/callback"
        SCOPE = "user-read-playback-state user-read-currently-playing"
        # SCOPE = "user-library-read"

        sp_oauth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)  
        # sp = Spotify(auth_manager=sp_oauth)

        auth_url = sp_oauth.get_authorize_url()
        print(f"Please go to the following URL to authorize your app: {auth_url}")

        app = Flask(__name__)
        # Route for Spotify redirect to local server
        @app.route('/callback')
        def callback():
            code = request.args.get('code')
            token_info = sp_oauth.get_access_token(code)
            
            Spotify(auth=token_info['access_token'])
            print("Token received and authentication successful!")

            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            func()

            self.auth_complete_event.set()

            return "Authentication complete! You can close this window."
        
        def start_local_server():
            # Open the URL automatically in the browser
            import webbrowser
            webbrowser.open(auth_url)

            # Run Flask server
            app.run(port=8888)


        server_thread = threading.Thread(target=start_local_server)
        server_thread.start()

        return sp_oauth

    # Get playing track
    def currently_playing_track(self):
        playing_track = self.spotify.currently_playing()
        current_playback = self.spotify.current_playback()

        if playing_track is None:
            return None
        if playing_track['currently_playing_type'] == 'ad':
            track = Track("Advertisement", ["Advertisement"])
            track.duration_in_ms = 30000
            track.progress_in_ms = int(playing_track['progress_ms'])
            track.is_playing = True
            return track
        
        playing_item = playing_track['item']
        track_name = playing_item['name']
        track_artists = playing_item['artists']
        track_artists_name = []
        for artist in track_artists:
            track_artists_name.append(artist['name'])

        track = Track(track_name, track_artists_name)
        track.duration_in_ms = int(playing_item['duration_ms'])
        track.progress_in_ms = int(playing_track['progress_ms'])
        track.is_playing = playing_track['is_playing']
        track.image_url = playing_item['album']['images'][2]['url']

        if current_playback is not None:
            track.is_shuffle = current_playback['shuffle_state']
            track.repeat_state = current_playback['repeat_state']
            
        return track
    
    def play_current_track(self):
        self.spotify.start_playback()

    def pause_current_track(self):
        self.spotify.pause_playback()

    def next_track(self):
        self.spotify.next_track()

    def previous_track(self):
        self.spotify.previous_track()
    
    def download_image(self, image_url):
        # Fetch the webpage content
        response = requests.get(image_url)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the first (and only) image tag
        img_tag = soup.find('img')

        # Extract the image URL from the 'src' attribute
        if img_tag:
            img_url = img_tag['src']
            
            # If the src is a relative URL, convert it to an absolute URL
            if img_url.startswith('/'):
                # Build the absolute URL (assuming it's from the same domain)
                img_url = requests.compat.urljoin(image_url, img_url)

            # Download the image
            img_response = requests.get(img_url)
            print("\n\nstatus code: " + img_response.status_code)
            # Check if the request was successful
            if img_response.status_code == 200:
                image_path = os.path.join("./test_image.jpg")
                with open(image_path, 'wb') as img_file:
                    img_file.write(response.content)

                # Convert the response content to a Pillow Image
                image_data = BytesIO(response.content)
                return Image.open(image_data)
            return None
        return None
        

auth_complete_event = threading.Event()
spotify = SpotifyTrack(auth_complete_event)
auth_complete_event.wait()
playing_track = spotify.spotify.current_playback()
print(playing_track)
# print(playing_track.name + "\n" + ', '.join(playing_track.artists))
# print("\n")
# print(spotify.currently_playing_progress_ms())