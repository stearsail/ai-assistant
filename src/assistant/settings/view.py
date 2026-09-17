import questionary

from assistant import ui
from assistant.config.credentials import CREDENTIALS_FILE, config_status


async def view_configuration(pause: bool = True) -> bool:
    rows = config_status()
    width = max(len(row["label"]) for row in rows)

    ui.show("  Current configuration", "heading", before=1, after=1)

    for row in rows:
        mark = "✓" if row["configured"] else "✗"
        ui.show(
            f"  {mark} {row['label']:<{width}}  {row['display']}",
            "ok" if row["configured"] else "missing",
        )
        ui.muted(f"    {'':<{width}}  from {row['source']}")

    ui.muted(f"  Stored in {CREDENTIALS_FILE}", before=1)

    if any(row["source"] == "environment" for row in rows):
        ui.notice(
            "  Some values come from environment variables, which take\n"
            "  precedence over this file. Changing them here will have no\n"
            "  effect until those variables are unset.",
            before=1,
        )
    ui.console.print()
    if pause:
        await questionary.press_any_key_to_continue().ask_async()
    return False
