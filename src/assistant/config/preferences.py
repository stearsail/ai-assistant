import copy

from assistant.config.utils import CONFIG_DIR, read_all, write_all

PREFERENCES_FILE = CONFIG_DIR / "preferences.json"

PROVIDERS = ("anthropic", "ollama")

DEFAULTS = {
    "model": {
        "provider": "ollama",
        "anthropic": {"id": "claude-haiku-4-5-20251001"},
        "ollama": {
            "id": "qwen3.5:4b",
            "host": "http://localhost:11434",
            "num_ctx": 16384,
        },
    }
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


def update_provider(provider: str) -> None:
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider: {provider}")
    data = _load_all()
    data["model"]["provider"] = provider
    _write_preferences(data)
