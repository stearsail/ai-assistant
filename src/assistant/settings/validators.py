import re

_CLIENT_ID_RE = re.compile(r"^\d+-[A-Za-z0-9_-]+\.apps\.googleusercontent\.com$")
_CLIENT_ID_SUFFIX = ".apps.googleusercontent.com"
_CLIENT_SECRET_PREFIX = "GOCSPX-"
_API_KEY_PREFIX = "sk-ant-"


def _blank_or_spaced(value: str, noun: str) -> str | None:
    """Checks every credential shares. Returns an error message, or None."""
    if not value.strip():
        return f"{noun} cannot be empty."
    if any(char.isspace() for char in value.strip()):
        return f"{noun} cannot contain spaces - check for a broken paste."
    return None


def validate_google_client_id(value: str) -> bool | str:
    value = value.strip()
    if error := _blank_or_spaced(value, "Client ID"):
        return error
    if value.startswith(_CLIENT_SECRET_PREFIX):
        return "That is a client secret, not a client ID."
    if not _CLIENT_ID_RE.match(value):
        return "Expected 123456789-abc123def456.apps.googleusercontent.com"
    return True


def validate_google_client_secret(value: str) -> bool | str:
    value = value.strip()
    if error := _blank_or_spaced(value, "Client secret"):
        return error
    if value.endswith(_CLIENT_ID_SUFFIX):
        return "That is a client ID, not a client secret."
    if len(value) < 15:
        return "That looks too short for a client secret."
    return True


def validate_anthropic_api_key(value: str) -> bool | str:
    value = value.strip()
    if error := _blank_or_spaced(value, "API key"):
        return error
    if not value.startswith(_API_KEY_PREFIX):
        return f"Anthropic API keys start with {_API_KEY_PREFIX!r}."
    if len(value) < 40:
        return "That looks too short for an Anthropic API key."
    return True
