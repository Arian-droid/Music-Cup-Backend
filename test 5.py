from spotdl import Spotdl

# Initialize Spotdl with your Spotify credentials
# spotify_client_id = "3404161675204c95beb26f8ed32e4424"
# spotify_client_secret = "87fe2d25f8ef4919a2a0e131102806dd"
from SpotiFLAC import SpotiFLAC


SpotiFLAC(
    url="https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT",
    output_dir="./downloads",
    services=["deezer", "qobuz", "youtube", "soundcloud"]
)