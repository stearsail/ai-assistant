import questionary

from assistant.config.credentials import CREDENTIALS_FILE, config_status

_OK = "fg:ansigreen"
_MISSING = "fg:ansired"
_MUTED = "fg:ansibrightblack"


async def view_configuration() -> bool:
    rows = config_status()
    width = max(len(row["label"]) for row in rows)

    questionary.print("\n  Current configuration\n", style="bold")

    for row in rows:
        mark = "✓" if row["configured"] else "✗"
        questionary.print(
            f"  {mark} {row['label']:<{width}}  {row['display']}",
            style=_OK if row["configured"] else _MISSING,
        )
        questionary.print(f"    {'':<{width}}  from {row['source']}", style=_MUTED)

    questionary.print(f"\n  Stored in {CREDENTIALS_FILE}", style=_MUTED)

    if any(row["source"] == "environment" for row in rows):
        questionary.print(
            "\n  Some values come from environment variables, which take\n"
            "  precedence over this file. Changing them here will have no\n"
            "  effect until those variables are unset.",
            style="fg:ansiyellow",
        )
    questionary.print("")
    await questionary.press_any_key_to_continue().ask_async()
    return False
