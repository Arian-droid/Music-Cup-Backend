import requests

def get_similar_tracks(track_id):
    url = f"https://api.deezer.com/track/{track_id}/related"

    res = requests.get(url).json()

    # SAFETY CHECK 👇
    if "data" not in res:
        print("No similar tracks found or API error:", res)
        return []

    similar = []

    for t in res["data"]:
        similar.append({
            "title": t["title"],
            "artist": t["artist"]["name"],
            "preview": t["preview"],
            "cover": t["album"]["cover_xl"]
        })

    return similar



song_name = "Hero"

def search_track(song_name):
    url = f"https://api.deezer.com/search"
    params = {"q": song_name}

    res = requests.get(url, params=params).json()

    if res["data"]:
        track = res["data"][0]
        return track["id"], track

    return None, None



track_id, track = search_track(song_name)

if track_id:
    print("Found:", track["title"], "-", track["artist"]["name"])
    print("Album Cover:", track["album"]["cover_xl"])

    similar = get_similar_tracks(track_id)

    print("\nSimilar songs:")
    for s in similar[:10]:
        print(f"{s['title']} - {s['artist']}")
        print("Cover:", s["cover"])
        print("Preview:", s["preview"])
        print("---")