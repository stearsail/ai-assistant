import re

_CLIENT_ID_RE = re.compile(r"^\d+-[A-Za-z0-9_-]+\.apps\.googleusercontent\.com$")
_CLIENT_ID_SUFFIX = ".apps.googleusercontent.com"
_CLIENT_SECRET_PREFIX = "GOCSPX-"
_API_KEY_PREFIX = "sk-ant-"
_GOOGLE_MAIL_DOMAINS = ("gmail.com", "googlemail.com")
_GMAIL_LOCAL_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9.+_-]*[A-Za-z0-9])?$")


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


def validate_user_gmail(value: str) -> bool | str:
    """Validate the Google account address.
    This field is optional - an empty value is accepted so the user can skip
    it during setup. Without it the agent supplies the address per tool call
    instead of the server reading USER_GOOGLE_EMAIL.
    """
    value = value.strip()
    if not value:
        return True
    if any(char.isspace() for char in value):
        return "Email cannot contain spaces - check for a broken paste."
    if value.count("@") != 1:
        return "Enter a full address, for example you@gmail.com"
    local, _, domain = value.partition("@")
    if domain.lower() not in _GOOGLE_MAIL_DOMAINS:
        return f"Expected a {_GOOGLE_MAIL_DOMAINS[0]} address."
    if not _GMAIL_LOCAL_RE.match(local):
        return "The part before @ contains characters Gmail does not allow."
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
