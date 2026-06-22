import requests

song = "Believer"

r = requests.get(
    f"https://api.deezer.com/search?q={song}"
).json()

track = r["data"][0]

print("Song:", track["title"])
print("Artist:", track["artist"]["name"])
print("Artist Image:", track["artist"]["picture_xl"])
print("Album Cover:", track["album"]["cover_xl"])