import os
import requests
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
import random
from ravendb import DocumentStore

# Load environment variables
load_dotenv()

# Configuration
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID")
DISCORD_SERVER_INVITE = os.getenv("DISCORD_SERVER_INVITE", "#")

CODES_DOC_ID = "easteregg/codes"

app = Flask(__name__)

# RavenDB setup (shared with bot)
def get_raven_store():
    urls = os.getenv('RAVEN_URL', 'http://localhost:8080').split(',')
    database = os.getenv('RAVEN_DATABASE', 'shizu_bot')
    cert_path = os.getenv('RAVEN_CERT_PATH')
    store = DocumentStore(urls=urls, database=database)
    if cert_path and os.path.exists(cert_path):
        if hasattr(store, 'certificate_pem_path'):
            store.certificate_pem_path = cert_path
        else:
            store.certificate = cert_path
    store.conventions.disable_topology_updates = True
    store.initialize()
    return store

try:
    raven_store = get_raven_store()
except Exception as e:
    print(f"RavenDB connection failed: {e}")
    raven_store = None


def get_random_unused_code():
    """Pull a random unused code from RavenDB. Returns None if all are used."""
    if not raven_store:
        return None
    try:
        with raven_store.open_session() as session:
            data = session.load(CODES_DOC_ID)
            if not data:
                return None
            codes = data.get("codes", []) if isinstance(data, dict) else []
            unused = [entry for entry in codes if isinstance(entry, dict) and not entry.get("used", True)]
            if not unused:
                return None
            return random.choice(unused)["code"]
    except Exception as e:
        print(f"Error fetching code from DB: {e}")
        return None


@app.route("/")
def index():
    return render_template("index.html", server_invite=DISCORD_SERVER_INVITE)

@app.route("/secret")
def secret():
    code = get_random_unused_code()
    if not code:
        # Fallback message when all codes are exhausted
        code = "ALL-CODES-USED"
    return render_template("secret.html", secret_code=code)

@app.route("/coming-soon")
def coming_soon():
    return render_template("coming_soon.html")

@app.route("/api/discord")
def discord_profile():
    if not DISCORD_BOT_TOKEN or not DISCORD_USER_ID:
        return jsonify({
            "error": "Discord token or user ID not configured",
            "dummy_data": {
                "display_name": "Retro User",
                "username": "retrouser",
                "avatar_url": "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png"
            }
        }), 200

    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}"
    }
    
    try:
        response = requests.get(f"https://discord.com/api/v10/users/{DISCORD_USER_ID}", headers=headers)
        response.raise_for_status()
        user_data = response.json()
        
        avatar_hash = user_data.get('avatar')
        discord_id = user_data.get('id')
        
        if avatar_hash:
            avatar_url = f"https://cdn.discordapp.com/avatars/{discord_id}/{avatar_hash}.png?size=256"
        else:
            discriminator = int(user_data.get('discriminator', '0'))
            default_avatar_index = discriminator % 5 if user_data.get('discriminator') != '0' else 0
            avatar_url = f"https://cdn.discordapp.com/embed/avatars/{default_avatar_index}.png"

        return jsonify({
            "display_name": user_data.get("global_name") or user_data.get("username"),
            "username": user_data.get("username"),
            "avatar_url": avatar_url
        })

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Discord user: {e}")
        return jsonify({"error": "Failed to fetch Discord profile"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
