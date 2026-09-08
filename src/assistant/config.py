import os
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "assistant"
CONFIG_FILE = CONFIG_DIR / "credentials.json"

class MissingCredentials(Exception):
    pass

def save_credentials(client_id, client_secret) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    data = {"GOOGLE_OAUTH_CLIENT_ID": client_id, "GOOGLE_OAUTH_CLIENT_SECRET": client_secret}
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    CONFIG_FILE.chmod(0o600)
    

def load_credentials() -> dict:
    result = {}
    try:
        if "GOOGLE_OAUTH_CLIENT_ID" in os.environ and "GOOGLE_OAUTH_CLIENT_SECRET" in os.environ:
            result["google_client_id"] = os.environ["GOOGLE_OAUTH_CLIENT_ID"]
            result["google_client_secret"] = os.environ["GOOGLE_OAUTH_CLIENT_SECRET"]
            return result
        with open(CONFIG_FILE, "r", encoding='utf-8') as f:
            data = json.load(f)
            result["google_client_id"] = data["GOOGLE_OAUTH_CLIENT_ID"]
            result["google_client_secret"] = data["GOOGLE_OAUTH_CLIENT_SECRET"]
    except FileNotFoundError as e:
        raise MissingCredentials("No credentials found. Run: assistant setup") from e
    except json.JSONDecodeError as e:
        raise MissingCredentials(f"Credentials file is corrupt: {CONFIG_FILE}") from e
    return result