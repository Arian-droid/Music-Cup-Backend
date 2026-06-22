import requests

response = requests.get(
    "https://lrclib.net/api/get",
    params={
        "artist_name": "Coldplay",
        "track_name": "Yellow"
    },
    timeout=10
)

print(response.status_code)
print(response.text)