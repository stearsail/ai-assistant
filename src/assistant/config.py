import os
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "assistant"
CONFIG_FILE = CONFIG_DIR / "credentials.json"


class MissingCredentials(Exception):
    pass


class MissingAPIKey(Exception):
    pass


def _read_all() -> dict:
    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _write_all(data: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    CONFIG_FILE.chmod(0o600)


def save_credentials(client_id, client_secret) -> None:
    data = _read_all()
    data["google"] = {"client_id": client_id, "client_secret": client_secret}
    _write_all(data)


def save_anthropic_api_key(api_key: str) -> None:
    data = _read_all()
    data["anthropic"] = {"api_key": api_key}
    _write_all(data)


def load_credentials() -> dict:
    if (
        "GOOGLE_OAUTH_CLIENT_ID" in os.environ
        and "GOOGLE_OAUTH_CLIENT_SECRET" in os.environ
    ):
        return {
            "client_id": os.environ["GOOGLE_OAUTH_CLIENT_ID"],
            "client_secret": os.environ["GOOGLE_OAUTH_CLIENT_SECRET"],
        }
    google = _read_all().get("google", {})
    client_id, client_secret = google.get("client_id"), google.get("client_secret")
    if not (client_id and client_secret):
        raise MissingCredentials("No Google credentials found. Run: assistant setup")
    return {"client_id": client_id, "client_secret": client_secret}


def load_anthropic_api_key() -> dict:
    if "ANTHROPIC_API_KEY" in os.environ:
        return {"anthropic_api_key": os.environ["ANTHROPIC_API_KEY"]}

    api_key = _read_all().get("anthropic", {}).get("api_key")
    if not api_key:
        raise MissingAPIKey("No Anthropic API key found. Run: assistant setup")
    return {"anthropic_api_key": api_key}
