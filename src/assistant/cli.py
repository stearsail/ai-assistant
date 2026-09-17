import argparse
import asyncio
import sys
from assistant.config.credentials import (
    load_anthropic_api_key,
    load_credentials,
    save_anthropic_api_key,
    save_credentials,
    MissingCredentials,
    MissingAPIKey,
)
from assistant import prompts, ui
from assistant.agent import run_agent
from assistant.config.logs import route_agno_logs
from assistant.config.preferences import (
    PROVIDERS,
    DefaultPreferences,
    load_preferences,
    update_model,
    update_provider,
    update_timezone,
)
from assistant.settings.anthropic import modify_api_key
from assistant.settings.google import modify_oauth_credentials, prompt_all_fields
from assistant.settings.menu import settings_menu
from assistant.settings.provider import ollama_model_error
from assistant.settings.timezone import describe_timezone
from assistant.settings.validators import validate_anthropic_api_key
from assistant.settings.view import view_configuration


async def setup_oauth() -> None:
    try:
        load_credentials()
        ui.success("Loaded Google OAuth credentials")
        return
    except MissingCredentials as e:
        ui.error(str(e), before=1)
        ui.show(
            "Please enter your google OAuth credentials (Cloud Console → APIs & Services → Credentials)"
        )
        values = await prompt_all_fields()
        if values is None:
            return
        save_credentials(**values)
        ui.success("Saved Google OAuth credentials in configuration", before=1, after=1)


async def setup_api() -> None:
    try:
        load_anthropic_api_key()
        ui.success("Loaded Anthropic API key", after=1)
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
                ui.error("Skipped adding API key")
                return
            save_anthropic_api_key(api_key.strip())
            ui.success("Saved Anthropic API key in configuration", before=1)
            ui.muted("To use Anthropic as model provider, change Preferences in Settings")
        return


async def setup_preferences() -> None:
    try:
        load_preferences()
        ui.success("Loaded preferences")
    except DefaultPreferences as e:
        ui.success(str(e))


def _preferences() -> dict:
    try:
        return load_preferences()
    except DefaultPreferences:
        return load_preferences()


def _error(message: str) -> int:
    ui.error(message)
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
    ui.show(f"  Provider: {provider} ({prefs[provider]['id']})", "heading", before=1)
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
    ui.success(f"Provider set to {args.name}")
    return 0


async def _model_command(args: argparse.Namespace) -> int:
    prefs = _preferences()
    provider = prefs["provider"]
    if provider == "ollama":
        error = await ollama_model_error(prefs["ollama"]["host"], args.id)
        if error:
            return _error(error)
    update_model(provider, args.id)
    ui.success(f"{provider} model set to {args.id}")
    return 0


async def _timezone_command(args: argparse.Namespace) -> int:
    name = None if args.name == "system" else args.name
    try:
        update_timezone(name)
    except ValueError as e:
        return _error(str(e))
    ui.success(f"Timezone set to {describe_timezone(name)}")
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

    timezone = keys.add_parser("timezone", help="set the timezone the assistant uses")
    timezone.add_argument("name", help="e.g. Europe/Chisinau, or 'system' to follow the system")
    timezone.set_defaults(func=_timezone_command)

    args = parser.parse_args()
    route_agno_logs()
    return asyncio.run(args.func(args))
