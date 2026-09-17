import zoneinfo

from assistant import prompts, ui
from assistant.config.preferences import load_timezone, system_timezone, update_timezone


def describe_timezone(name: str | None) -> str:
    return name or f"{system_timezone()} (from the system)"


async def modify_timezone() -> bool:
    stored = load_timezone()
    ui.muted(f"Current: {describe_timezone(stored)}", before=1)
    zones = sorted(zoneinfo.available_timezones())
    valid = set(zones)
    answer = await prompts.autocomplete(
        "Timezone, leave empty to follow the system:",
        choices=zones,
        validate=lambda value: not value.strip()
        or value.strip() in valid
        or "Unknown timezone",
    ).ask_async()
    if answer is None:
        return False
    name = answer.strip() or None
    if name == stored:
        return False
    update_timezone(name)
    ui.success(f"Timezone set to {describe_timezone(name)}", before=1, after=1)
    return True
