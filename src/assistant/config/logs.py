import logging
from pathlib import Path

LOG_FILE = Path.home() / ".local" / "state" / "assistant" / "agno.log"


def route_agno_logs() -> None:
    # agno resets its log level on every run, but never touches its handlers
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(LOG_FILE)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    agno = logging.getLogger("agno")
    agno.handlers.clear()
    agno.addHandler(handler)
