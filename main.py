from fastapi import FastAPI, Request
import requests
import json
import base64
import os
import secrets
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
SELLAUTH_SECRET = os.getenv("SELLAUTH_SECRET")

KEYS_PATH = "keys.json"

SCRIPT_MAP = {
    "pls_donate": "pls_donate",
    "avatar": "avatar",
    "sab": "SAB",
    "catalog": "Catalog_Gifter"
}


def generate_key():
    return "Lumen-" + secrets.token_urlsafe(8)


def github_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }


def get_keys():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{KEYS_PATH}"

    r = requests.get(url, headers=github_headers())
    data = r.json()

    decoded = base64.b64decode(data["content"]).decode()

    return json.loads(decoded), data["sha"]


def save_keys(keys, sha):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{KEYS_PATH}"

    encoded = base64.b64encode(
        json.dumps(keys, indent=2).encode()
    ).decode()

    payload = {
        "message": "SellAuth key delivery",
        "content": encoded,
        "sha": sha
    }

    requests.put(url, headers=github_headers(), json=payload)


@app.get("/")
async def home():
    return {"status": "online"}


@app.post("/deliver")
async def deliver(request: Request):

    secret = request.query_params.get("secret")

    if secret != SELLAUTH_SECRET:
        return {"success": False}

    data = await request.json()

    script = request.query_params.get("script", "pls_donate")

    script_type = SCRIPT_MAP.get(script)

    if not script_type:
        return {"success": False}

    keys, sha = get_keys()

    key = generate_key()

    keys[key] = {
        "discord_id": None,
        "hwid": None,
        "script_type": script_type,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_hwid_set": None,
        "expires_at": None
    }

    save_keys(keys, sha)

    return {
        "success": True,
        "delivery": key
    }