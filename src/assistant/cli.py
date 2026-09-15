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
from assistant.config.preferences import (
    PROVIDERS,
    DefaultPreferences,
    load_preferences,
    update_model,
    update_provider,
)
from assistant.settings.anthropic import modify_api_key
from assistant.settings.google import modify_oauth_credentials, prompt_all_fields
from assistant.settings.menu import settings_menu
from assistant.settings.provider import ollama_model_error
from assistant.settings.validators import validate_anthropic_api_key
from assistant.settings.view import view_configuration


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


def _preferences() -> dict:
    try:
        return load_preferences()
    except DefaultPreferences:
        return load_preferences()


def _error(message: str) -> int:
    questionary.print(message, style="fg:#ff0000 bold italic")
    return 1


async def _chat_command(args: argparse.Namespace) -> int:
    await setup_preferences()
    await setup_oauth()
    await setup_api()
    try:
        load_credentials()
    except MissingCredentials as e:
        print(e, file=sys.stderr)
        return 1
    await run_agent(resume=not args.new)
    return 0


async def _settings_command(args: argparse.Namespace) -> int:
    await settings_menu()
    return 0


async def _show_command(args: argparse.Namespace) -> int:
    prefs = _preferences()
    provider = prefs["provider"]
    questionary.print(
        f"\n  Provider: {provider} ({prefs[provider]['id']})", style="bold"
    )
    await view_configuration()
    return 0


async def _api_key_command(args: argparse.Namespace) -> int:
    await modify_api_key()
    return 0


async def _google_command(args: argparse.Namespace) -> int:
    await modify_oauth_credentials()
    return 0


async def _provider_command(args: argparse.Namespace) -> int:
    if args.name == "anthropic":
        try:
            load_anthropic_api_key()
        except MissingAPIKey:
            return _error(
                "No Anthropic API key set. Add one with: assistant config api-key"
            )
    update_provider(args.name)
    questionary.print(f"Provider set to {args.name}", style="fg:#87ae73 bold italic")
    return 0


async def _model_command(args: argparse.Namespace) -> int:
    prefs = _preferences()
    provider = prefs["provider"]
    if provider == "ollama":
        error = await ollama_model_error(prefs["ollama"]["host"], args.id)
        if error:
            return _error(error)
    update_model(provider, args.id)
    questionary.print(
        f"{provider} model set to {args.id}", style="fg:#87ae73 bold italic"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="assistant")
    parser.add_argument(
        "--new",
        action="store_true",
        help="start a new conversation instead of resuming the last one",
    )
    parser.set_defaults(func=_chat_command)
    commands = parser.add_subparsers(title="commands", metavar="<command>")

    commands.add_parser("settings", help="open the settings menu").set_defaults(
        func=_settings_command
    )

    config = commands.add_parser("config", help="view or change configuration")
    keys = config.add_subparsers(title="settings", metavar="<setting>", required=True)
    keys.add_parser(
        "show", help="show provider, model and masked credentials"
    ).set_defaults(func=_show_command)
    keys.add_parser(
        "api-key", help="set the Anthropic API key (hidden prompt)"
    ).set_defaults(func=_api_key_command)
    keys.add_parser(
        "google", help="set Google OAuth credentials (prompted)"
    ).set_defaults(func=_google_command)

    provider = keys.add_parser("provider", help="set the model provider")
    provider.add_argument("name", choices=PROVIDERS)
    provider.set_defaults(func=_provider_command)

    model = keys.add_parser("model", help="set the model for the current provider")
    model.add_argument("id", help="e.g. qwen3.5:4b or claude-sonnet-5")
    model.set_defaults(func=_model_command)

    args = parser.parse_args()
    return asyncio.run(args.func(args))
