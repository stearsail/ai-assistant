import json
import os
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


def save_credentials(
    client_id: str, client_secret: str, user_gmail: str = None
) -> None:
    data = _read_all()
    data["google"] = {
        "client_id": client_id,
        "client_secret": client_secret,
        "user_gmail": user_gmail,
    }
    _write_all(data)


def update_credential(field: str, value: str) -> None:
    data = _read_all()
    data.setdefault("google", {})[field] = value
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
            "user_gmail": os.environ["USER_GOOGLE_EMAIL"],
        }
    google = _read_all().get("google", {})
    client_id, client_secret, user_gmail = (
        google.get("client_id"),
        google.get("client_secret"),
        google.get("user_gmail"),
    )
    if not (client_id and client_secret):
        raise MissingCredentials("No Google OAuth credentials found")
    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "user_gmail": user_gmail,
    }


def load_anthropic_api_key() -> dict:
    if "ANTHROPIC_API_KEY" in os.environ:
        return {"anthropic_api_key": os.environ["ANTHROPIC_API_KEY"]}

    api_key = _read_all().get("anthropic", {}).get("api_key")
    if not api_key:
        raise MissingAPIKey("No Anthropic API key found.")
    return {"anthropic_api_key": api_key}


def _mask(value: str, keep_prefix: int = 7, keep_suffix: int = 4) -> str:
    if len(value) < keep_prefix + keep_suffix + 8:
        return "•" * 12
    return f"{value[:keep_prefix]}{'•' * 8}{value[-keep_suffix:]}"


def config_status() -> list[dict]:
    data = _read_all()
    google_from_env = (
        "GOOGLE_OAUTH_CLIENT_ID" in os.environ
        and "GOOGLE_OAUTH_CLIENT_SECRET" in os.environ
    )
    gmail_from_env = "USER_GOOGLE_EMAIL" in os.environ
    google = os.environ if google_from_env else data.get("google", {})
    anthropic_from_env = "ANTHROPIC_API_KEY" in os.environ
    entries = [
        (
            "Anthropic API key",
            os.environ["ANTHROPIC_API_KEY"]
            if anthropic_from_env
            else data.get("anthropic", {}).get("api_key"),
            anthropic_from_env,
            True,
        ),
        (
            "Google client ID",
            google.get("GOOGLE_OAUTH_CLIENT_ID" if google_from_env else "client_id"),
            google_from_env,
            False,
        ),
        (
            "Google client secret",
            google.get(
                "GOOGLE_OAUTH_CLIENT_SECRET" if google_from_env else "client_secret"
            ),
            google_from_env,
            True,
        ),
        (
            "Google account email",
            os.environ.get("USER_GOOGLE_EMAIL")
            or data.get("google", {}).get("user_gmail"),
            gmail_from_env,
            False,
        ),
    ]

    return [
        {
            "label": label,
            "configured": bool(value),
            "source": ("environment" if from_env else "config file") if value else "-",
            "display": (
                "(not set)" if not value else _mask(value) if is_secret else value
            ),
        }
        for label, value, from_env, is_secret in entries
    ]
