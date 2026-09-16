import questionary

from assistant import prompts
from assistant.settings.anthropic import modify_api_key
from assistant.settings.google import modify_oauth_credentials
from assistant.settings.provider import modify_provider_settings
from assistant.settings.view import view_configuration
from assistant.settings.workspace import modify_workspace_access

MENU = {
    "View current configuration": view_configuration,
    "Change Google OAuth credentials": modify_oauth_credentials,
    "Change Anthropic API Key": modify_api_key,
    "Change provider settings": modify_provider_settings,
    "Change Google Workspace access": modify_workspace_access,
}


async def settings_menu() -> bool:
    changed = False
    choices = [questionary.Choice(title=label, value=fn) for label, fn in MENU.items()]
    choices.append(questionary.Choice("Back", value=None))
    while True:
        action = await prompts.select(
            "Settings",
            choices=choices,
        ).ask_async()
        if action is None or action == "Back":
            return changed
        changed = await action() or changed
