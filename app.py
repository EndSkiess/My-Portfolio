import os
import requests
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
import random
import string
import base64
import tempfile
from ravendb import DocumentStore

# Load environment variables
load_dotenv()

# Configuration
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID")
DISCORD_SERVER_INVITE = os.getenv("DISCORD_SERVER_INVITE", "#")
GOOGLE_ADSENSE_ID = os.getenv("GOOGLE_ADSENSE_ID")


CODES_DOC_ID = "easteregg/codes"

app = Flask(__name__)

# RavenDB setup (shared with bot)
def get_raven_store():
    urls = os.getenv('RAVEN_URL', 'http://localhost:8080').split(',')
    database = os.getenv('RAVEN_DATABASE', 'shizu_bot')
    cert_path = os.getenv('RAVEN_CERT_PATH')
    cert_base64 = os.getenv('RAVEN_CERT_CONTENT')

    if cert_base64:
        try:
            # Render/Cloud optimization: Write base64 cert to temporary file
            temp_cert = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")
            temp_cert.write(base64.b64decode(cert_base64))
            temp_cert.close()
            cert_path = temp_cert.name
            print(f"Loaded certificate from environment variable into {cert_path}")
        except Exception as e:
            print(f"Failed to decode RAVEN_CERT_CONTENT: {e}")

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
    """Pull a random unused code from RavenDB. Returns a fresh random one and seeds DB if all are used."""
    if not raven_store:
        # Fallback to local only generation if DB is offline
        def make_part():
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"SKIES-{make_part()}-{make_part()}-{make_part()}"

    try:
        with raven_store.open_session() as session:
            data = session.load(CODES_DOC_ID)
            
            # Extract codes list from session data
            if not data:
                codes = []
            elif isinstance(data, dict):
                codes = data.get("codes", [])
            elif hasattr(data, 'codes'):
                codes = data.codes or []
            else:
                codes = []

            # Filter for unused codes
            unused = []
            for entry in codes:
                is_dict = isinstance(entry, dict)
                used = entry.get("used", True) if is_dict else getattr(entry, "used", True)
                if not used:
                    unused.append(entry)

            print(f"[Codes] Total: {len(codes)}, Unused: {len(unused)}")
            
            # If we have unused codes, return a random one
            if unused:
                selected = random.choice(unused)
                return selected.get("code") if isinstance(selected, dict) else getattr(selected, "code", None)

            # If pool is empty, generate and seed a new batch of 20
            from ravendb import PatchOperation, PatchRequest
            
            new_batch = []
            def make_code():
                p = lambda: ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                return f"SKIES-{p()}-{p()}-{p()}"
            
            for _ in range(20):
                new_batch.append({"code": make_code(), "used": False})
            
            if not data:
                # Create the document if it's completely missing
                session.store({"codes": new_batch}, CODES_DOC_ID)
                session.save_changes()
            else:
                # Patch into the existing array for performance
                script = "for (var i = 0; i < $newCodes.length; i++) { this.codes.push($newCodes[i]); }"
                patch_req = PatchRequest(script=script, values={"newCodes": new_batch})
                raven_store.operations.send(PatchOperation(key=CODES_DOC_ID, change_vector=None, patch=patch_req))
            
            print(f"[Codes] Seeded 20 new codes to RavenDB.")
            return new_batch[0]["code"]

    except Exception as e:
        print(f"Error sync with RavenDB: {e}")
        # Always return a valid looking code as ultimate fallback
        p = lambda: ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"SKIES-{p()}-{p()}-{p()}"


@app.route("/")
def index():
    return render_template("index.html", server_invite=DISCORD_SERVER_INVITE)

@app.route("/secret")
def secret():
    # Sync with RavenDB so the Discord bot can recognize the codes
    code = get_random_unused_code()
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

@app.route("/ads.txt")
def ads_txt():
    return app.send_static_file("ads.txt")

@app.context_processor
def inject_adsense():
    return dict(adsense_id=GOOGLE_ADSENSE_ID)

@app.route("/api/health")

def health():
    status = {
        "ravendb_store": raven_store is not None,
        "cert_loaded": False,
        "cert_env_present": os.getenv('RAVEN_CERT_CONTENT') is not None,
        "database": os.getenv('RAVEN_DATABASE', 'shizu_bot'),
        "url": os.getenv('RAVEN_URL', 'http://localhost:8080')
    }
    
    if raven_store:
        try:
            with raven_store.open_session() as session:
                data = session.load(CODES_DOC_ID)
                status["db_reachable"] = True
                status["codes_count"] = len(data.get("codes", [])) if isinstance(data, dict) else 0
        except Exception as e:
            status["db_reachable"] = False
            status["error"] = str(e)
            
    return jsonify(status)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
