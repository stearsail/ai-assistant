import questionary
from assistant.settings.anthropic import modify_api_key
from assistant.settings.google import modify_oauth_credentials
from assistant.settings.view import view_configuration

MENU = {
    "View current configuration": view_configuration,
    "Change Google OAuth credentials": modify_oauth_credentials,
    "Change Anthropic API Key": modify_api_key,
}


async def settings_menu() -> None:
    choices = [questionary.Choice(title=label, value=fn) for label, fn in MENU.items()]
    choices.append(questionary.Choice("Back", value=None))
    while True:
        action = await questionary.select(
            "Settings",
            choices=choices,
        ).ask_async()
        if action is None or action == "Back":
            return
        await action()

        # choices=[
        #     "View current configuration",
        #     "Change API key",
        #     "Change Google OAuth credentials",
        #     "Re-authenticate Google Account",
        #     "Choose enabled services",
        #     "Back",
        # ],
