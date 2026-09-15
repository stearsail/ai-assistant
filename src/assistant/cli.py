import argparse
import asyncio
import sys
import questionary
from assistant.config.credentials import (
    load_anthropic_api_key,
    load_credentials,
    save_anthropic_api_key,
    save_credentials,
    MissingCredentials,
    MissingAPIKey,
)
from assistant import prompts
from assistant.agent import run_agent
from assistant.config.preferences import DefaultPreferences, load_preferences
from assistant.settings.google import prompt_all_fields
from assistant.settings.validators import validate_anthropic_api_key


async def setup_oauth() -> None:
    try:
        load_credentials()
        questionary.print(
            "Loaded Google OAuth credentials", style="fg:#87ae73 bold italic"
        )
        return
    except MissingCredentials as e:
        questionary.print(f"\n{e}", style="fg:#ff0000 bold italic")
        questionary.print(
            "Please enter your google OAuth credentials (Cloud Console → APIs & Services → Credentials)"
        )
        values = await prompt_all_fields()
        if values is None:
            return
        save_credentials(**values)
        questionary.print(
            "\nSaved Google OAuth credentials in configuration\n",
            style="fg:#87ae73 bold italic",
        )


async def setup_api() -> None:
    try:
        load_anthropic_api_key()
        questionary.print("Loaded Anthropic API key\n", style="fg:#87ae73 bold italic")
    except MissingAPIKey as e:
        answer = await prompts.confirm(
            f"{e}\nWould you like to set an API key now?"
        ).ask_async()
        if answer:
            api_key = await prompts.password(
                "Please enter your Anthropic API key:",
                validate=validate_anthropic_api_key,
            ).ask_async()
            if api_key is None:
                questionary.print(
                    "Skipped adding API key",
                    style="fg:#ff0000 bold italic",
                )
                return
            save_anthropic_api_key(api_key.strip())
            questionary.print(
                "\nSaved Anthropic API key in configuration",
                style="fg:#87ae73 bold italic",
            )
            questionary.print(
                "To use Anthropic as model provider, change Preferences in Settings",
                style="fg:ansibrightblack",
            )
        return


async def setup_preferences() -> None:
    try:
        load_preferences()
        questionary.print("Loaded preferences", style="fg:#87ae73 bold italic")
    except DefaultPreferences as e:
        questionary.print(f"{e}", style="fg:#87ae73 bold italic")


async def _run(resume: bool) -> int:
    await setup_preferences()
    await setup_oauth()
    await setup_api()
    try:
        load_credentials()
    except MissingCredentials as e:
        print(e, file=sys.stderr)
        return 1
    await run_agent(resume=resume)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="assistant")
    parser.add_argument(
        "--new",
        action="store_true",
        help="start a new conversation instead of resuming the last one",
    )
    args = parser.parse_args()
    return asyncio.run(_run(resume=not args.new))
