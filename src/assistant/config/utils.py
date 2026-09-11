import sys
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "assistant"


def read_all(path: Path) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        print(
            f"Warning: {path} is not valid JSON ({e}). Treating it as empty.",
            file=sys.stderr,
        )
        return {}


def write_all(path: Path, data: dict, private: bool) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    if private:
        path.chmod(0o600)
