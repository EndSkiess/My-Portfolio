import os
import requests
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID")
DISCORD_SERVER_INVITE = os.getenv("DISCORD_SERVER_INVITE", "#")

@app.route("/")
def index():
    return render_template("index.html", server_invite=DISCORD_SERVER_INVITE)

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
