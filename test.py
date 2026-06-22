import requests
import os

# =========================
# 🚨 FORCE DISABLE PROXIES
# =========================
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""

# =========================
# 🔑 YOUR AUDD TOKEN
# =========================
AUDD_TOKEN = "c5528448035fc86c7fc1d02e8b508b4a"

# =========================
# 🎵 AUDIO FILE PATH
# =========================
FILE_PATH = "song.mp3"


def test_audd():
    try:
        print("📤 Sending audio to AudD...")

        with open(FILE_PATH, "rb") as f:
            response = requests.post(
                "https://api.audd.io/",
                data={
                    "api_token": AUDD_TOKEN,
                    "return": "spotify,apple_music"
                },
                files={
                    "file": f
                },
                timeout=30,
                proxies={"http": None, "https": None}  # 🔥 IMPORTANT FIX
            )

        print("\n📥 STATUS CODE:", response.status_code)

        # Try to parse JSON
        try:
            data = response.json()
        except Exception:
            print("❌ Invalid JSON response:")
            print(response.text)
            return

        print("\n📦 FULL RESPONSE:")
        print(data)

        # Check result
        if data.get("result"):
            result = data["result"]

            print("\n✅ SONG FOUND!")
            print("🎵 Title:", result.get("title"))
            print("👤 Artist:", result.get("artist"))
            print("💿 Album:", result.get("album"))



        else:
            print("\n❌ No song detected")
            print("Reason:", data)

    except Exception as e:
        print("\n💥 ERROR OCCURRED:")
        print(e)


if __name__ == "__main__":
    test_audd()