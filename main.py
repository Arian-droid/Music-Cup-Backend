from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import yt_dlp
import requests
import tempfile
import os
import urllib.parse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AUDD_TOKEN = "c5528448035fc86c7fc1d02e8b508b4a"
AUDD_TOKEN = os.getenv("AUDD_TOKEN")


# =========================
# HTTP (your original API)
# =========================
@app.post("/recognize")
async def recognize(file: UploadFile = File(...)):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
        temp_file.write(await file.read())
        temp_path = temp_file.name

    try:
        with open(temp_path, "rb") as audio:
            response = requests.post(
                "https://api.audd.io/",
                data={
                    "api_token": AUDD_TOKEN,
                    "return": "spotify,apple_music"
                },
                files={"file": audio}
            )

        data = response.json()

        if not data.get("result"):
            return {"success": False, "message": "Song not found"}

        result = data["result"]

        spotify_data = result.get("spotify", {})
        spotify_url = spotify_data.get("external_urls", {}).get("spotify")

        spotify_album_image = None
        if spotify_data.get("album", {}).get("images"):
            spotify_album_image = spotify_data["album"]["images"][0]["url"]

        title = result.get("title")
        artist = result.get("artist")

        # lyrics
        lyrics = None
        try:
            lyrics_response = requests.get(
                "https://lrclib.net/api/get",
                params={
                    "artist_name": artist,
                    "track_name": title,
                },
                timeout=5
            )

            if lyrics_response.status_code == 200:
                lyrics_data = lyrics_response.json()
                lyrics = lyrics_data.get("plainLyrics") or lyrics_data.get("syncedLyrics")

        except Exception as e:
            print("Lyrics API Error:", e)



    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# =========================
# WEB SOCKET (LIVE STREAM)
# =========================
@app.websocket("/ws/recognize")
async def ws_recognize(websocket: WebSocket):
    await websocket.accept()

    buffer = bytearray()

    try:
        while True:
            chunk = await websocket.receive_bytes()

            buffer.extend(chunk)

            # ⚡ process every ~3–4 seconds of audio
            if len(buffer) > 100_000:

                with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
                    temp_file.write(buffer)
                    temp_path = temp_file.name

                buffer = bytearray()

                try:
                    with open(temp_path, "rb") as audio:
                        response = requests.post(
                            "https://api.audd.io/",
                            data={
                                "api_token": AUDD_TOKEN,
                                "return": "spotify,apple_music"
                            },
                            files={"file": audio}
                        )

                    data = response.json()



                    # =========================
                    # SONG FOUND
                    # =========================
                    if data.get("result"):
                        result = data["result"]

                        spotify_data = result.get("spotify", {})

                        cover = None

                        if spotify_data.get("album", {}).get("images"):
                            cover = spotify_data["album"]["images"][0]["url"]

                        # title = result.get("title")
                        # artist = result.get("artist")
                        title = str(result.get("title") or "")
                        artist = str(result.get("artist") or "")

                        artist_img = None
                        artist_bio = None

                        try:
                            artist_res = requests.get(
                                "https://www.theaudiodb.com/api/v1/json/2/search.php",
                                params={"s": artist},
                                timeout=15
                            )

                            artist_data = artist_res.json()

                            if artist_data.get("artists"):
                                artist_info = artist_data["artists"][0]

                                artist_img = (
                                        artist_info.get("strArtistThumb")
                                        or artist_info.get("strArtistFanart")
                                )

                                artist_bio = artist_info.get("strBiographyEN")

                        except Exception as e:
                            print("Artist API Error:", e)

                        lyrics = None

                        try:
                            title_clean = str(title or "")
                            artist_clean = str(artist or "")

                            lyrics_response = requests.get(
                                "https://lrclib.net/api/get",
                                params={
                                    "artist_name": artist_clean,
                                    "track_name": title_clean,
                                },
                                timeout=15
                            )

                            print("LRCLIB STATUS:", lyrics_response.status_code)
                            print("LRCLIB TEXT:", lyrics_response.text)

                            if lyrics_response.status_code == 200:
                                lyrics_data = lyrics_response.json()
                                lyrics = lyrics_data.get("plainLyrics") or lyrics_data.get("syncedLyrics")
                                print("lyricsssssssss:", lyrics)

                        except requests.exceptions.Timeout:
                            print("LRCLIB timeout")

                        except Exception as e:
                            print("Lyrics error:", e)




                        print("COVER:", cover)

                        print("LYRICS:", lyrics)

                        await websocket.send_json({
                            "type": "FOUND",
                            "data": {
                                "title": title,
                                "artist": artist,
                                "album": result.get("album"),
                                "cover": cover,
                                "artist_image": artist_img,
                                "artist_bio": artist_bio,
                                "lyrics": lyrics,
                            }
                        })

                        break

                    # =========================
                    # STILL SEARCHING
                    # =========================
                    else:
                        await websocket.send_json({
                            "type": "SEARCHING"
                        })

                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

    except WebSocketDisconnect:
        print("Client disconnected")

    finally:
        await websocket.close()


# =========================
# DOWNLOAD API (UNCHANGED)
# =========================
