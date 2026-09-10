import asyncio
import sys
import questionary
from assistant import config
from assistant.agent import run_agent
from assistant.settings.google import prompt_all_fields
from assistant.settings.validators import validate_anthropic_api_key


async def setup_oauth() -> None:
    try:
        config.load_credentials()
        questionary.print(
            "\nLoaded Google OAuth credentials\n", style="fg:#87ae73 bold italic"
        )
        return
    except config.MissingCredentials as e:
        questionary.print(f"\n{e}", style="fg:#ff0000 bold italic")
        questionary.print(
            "Please enter your google OAuth credentials (Cloud Console → APIs & Services → Credentials)"
        )
        values = await prompt_all_fields()
        if values is None:
            return
        config.save_credentials(**values)
        questionary.print(
            "\nSaved Google OAuth credentials in configuration\n",
            style="fg:#87ae73 bold italic",
        )


async def setup_api() -> None:
    try:
        config.load_anthropic_api_key()
        print("Loaded API Key.")
    except config.MissingAPIKey as e:
        api_key = await questionary.password(
            f"{e}\n Please enter your Anthropic API key:",
            validate=validate_anthropic_api_key,
        ).ask_async()
        if api_key is None:
            return
        config.save_anthropic_api_key(api_key.strip())
        questionary.print(
            "\nSaved Anthropic API key in configuration\n",
            style="fg:#87ae73 bold italic",
        )


async def _run() -> int:
    # load_dotenv()
    await setup_oauth()
    await setup_api()
    try:
        api_key = config.load_anthropic_api_key()["anthropic_api_key"]
    except (config.MissingAPIKey, config.MissingCredentials) as e:
        print(e, file=sys.stderr)
        return 1
    await run_agent(api_key)
    return 0


def main() -> int:
    return asyncio.run(_run())
