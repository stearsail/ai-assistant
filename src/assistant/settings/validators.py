import re

_CLIENT_ID_RE = re.compile(r"^\d+-[A-Za-z0-9_-]+\.apps\.googleusercontent\.com$")
_CLIENT_ID_SUFFIX = ".apps.googleusercontent.com"
_CLIENT_SECRET_PREFIX = "GOCSPX-"
_API_KEY_PREFIX = "sk-ant-"
_GOOGLE_MAIL_DOMAINS = ("gmail.com", "googlemail.com")
_GMAIL_LOCAL_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9.+_-]*[A-Za-z0-9])?$")


def _blank_or_spaced(value: str, noun: str) -> str | None:
    if not value.strip():
        return f"{noun} cannot be empty."
    if any(char.isspace() for char in value.strip()):
        return f"{noun} cannot contain spaces."
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
        return "Client secret is too short."
    return True


def validate_user_gmail(value: str) -> bool | str:
    value = value.strip()
    if any(char.isspace() for char in value):
        return "Email cannot contain spaces."
    if value.count("@") != 1:
        return "Enter a full address, e.g. you@gmail.com"
    local, _, domain = value.partition("@")
    if domain.lower() not in _GOOGLE_MAIL_DOMAINS:
        return f"Expected a {_GOOGLE_MAIL_DOMAINS[0]} address."
    if not _GMAIL_LOCAL_RE.match(local):
        return "Invalid characters before @."
    return True


def validate_anthropic_api_key(value: str) -> bool | str:
    value = value.strip()
    if error := _blank_or_spaced(value, "API key"):
        return error
    if not value.startswith(_API_KEY_PREFIX):
        return f"Anthropic API keys start with {_API_KEY_PREFIX!r}."
    if len(value) < 40:
        return "API key is too short."
    return True
