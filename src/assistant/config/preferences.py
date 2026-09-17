import copy
import os
import zoneinfo
from pathlib import Path

from assistant.config.utils import CONFIG_DIR, read_all, write_all

PREFERENCES_FILE = CONFIG_DIR / "preferences.json"

PROVIDERS = ("anthropic", "ollama")

TIERS = ("core", "extended", "complete")

# workspace-mcp access levels per service, cumulative and in order
SERVICE_LEVELS = {
    "calendar": ("readonly", "full"),
    "gmail": ("readonly", "organize", "drafts", "send", "full"),
    "tasks": ("readonly", "manage", "full"),
    "drive": ("readonly", "full"),
    "docs": ("readonly", "full"),
    "sheets": ("readonly", "full"),
    "slides": ("readonly", "full"),
    "forms": ("readonly", "full"),
    "chat": ("readonly", "full"),
    "contacts": ("readonly", "full"),
    "appscript": ("readonly", "full"),
}

DEFAULTS = {
    "model": {
        "provider": "ollama",
        "anthropic": {"id": "claude-haiku-4-5-20251001"},
        "ollama": {
            "id": "qwen3.5:4b",
            "host": "http://localhost:11434",
            "num_ctx": 16384,
        },
    },
    # None follows the system timezone
    "timezone": None,
    "workspace": {
        "tier": "core",
        "permissions": {
            "calendar": "full",
            "tasks": "full",
            "gmail": "readonly",
            "docs": "readonly",
        },
    },
}


class DefaultPreferences(Exception):
    pass


def _read_preferences() -> dict:
    return read_all(PREFERENCES_FILE)


def _write_preferences(data: dict) -> None:
    write_all(PREFERENCES_FILE, data, private=False)


def _deep_merge(base: dict, overlay: dict) -> dict:
    # deepcopy so the result never shares nested dicts with DEFAULTS
    merged = copy.deepcopy(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_all() -> dict:
    return _deep_merge(DEFAULTS, _read_preferences())


def load_preferences() -> dict:
    if not PREFERENCES_FILE.exists():
        _write_preferences(DEFAULTS)
        raise DefaultPreferences("Default preferences set")
    return _load_all()["model"]


def load_workspace() -> dict:
    return _load_all()["workspace"]


def update_provider(provider: str) -> None:
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider: {provider}")
    data = _load_all()
    data["model"]["provider"] = provider
    _write_preferences(data)


def update_model(provider: str, model_id: str) -> None:
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider: {provider}")
    data = _load_all()
    data["model"][provider]["id"] = model_id
    _write_preferences(data)


def system_timezone() -> str:
    # TZ wins, then the zone /etc/localtime links to, then /etc/timezone
    candidates = [os.environ.get("TZ", "").lstrip(":")]
    localtime = Path("/etc/localtime").resolve()
    if "zoneinfo" in localtime.parts:
        start = localtime.parts.index("zoneinfo") + 1
        candidates.append("/".join(localtime.parts[start:]))
    try:
        candidates.append(Path("/etc/timezone").read_text().strip())
    except OSError:
        pass
    zones = zoneinfo.available_timezones()
    return next((name for name in candidates if name in zones), "UTC")


def load_timezone() -> str | None:
    return _load_all()["timezone"]


def update_timezone(name: str | None) -> None:
    if name is not None and name not in zoneinfo.available_timezones():
        raise ValueError(f"Unknown timezone: {name}")
    data = _load_all()
    data["timezone"] = name
    _write_preferences(data)


def update_workspace(
    permissions: dict | None = None,
    tier: str | None = None,
) -> None:
    if permissions is not None:
        for service, level in permissions.items():
            levels = SERVICE_LEVELS.get(service)
            if levels is None:
                raise ValueError(f"Unknown service: {service}")
            if level not in levels:
                raise ValueError(f"Unknown {service} level: {level}")
    if tier is not None and tier not in TIERS:
        raise ValueError(f"Unknown tier: {tier}")
    data = _load_all()
    workspace = data["workspace"]
    if permissions is not None:
        workspace["permissions"] = permissions
    if tier is not None:
        workspace["tier"] = tier
    _write_preferences(data)
