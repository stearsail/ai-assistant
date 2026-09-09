import questionary

from assistant.config import save_anthropic_api_key
from assistant.settings.validators import validate_anthropic_api_key


async def modify_api_key() -> None:
    api_key = await questionary.password(
        "New API key:", validate=validate_anthropic_api_key
    ).ask_async()
    if not api_key or not api_key.strip():
        return
    confirm = await questionary.confirm(
        "Are you sure you want to change your API key?"
    ).ask_async()
    if not confirm:
        questionary.print("\nAPI key modification cancelled\n", style="italic")
        return
    save_anthropic_api_key(api_key=api_key.strip())
    questionary.print("\nAnthropic API key modified successfully\n", style="italic")
