from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
KEYS_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/lumen-keys/main/keys.json"

@app.route("/")
def home():
    return "Lumen API online"

@app.route("/check")
def check_key():
    key = request.args.get("key", "")

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.raw"
    }

    r = requests.get(KEYS_URL, headers=headers)

    if r.status_code != 200:
        return jsonify({"valid": False, "error": "key database unavailable"})

    data = r.json()
    info = data.get("keys", {}).get(key)

    if not info or info.get("active") != True:
        return jsonify({"valid": False})

    return jsonify({"valid": True, "owner": info.get("owner", "")})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
