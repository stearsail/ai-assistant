import questionary
from assistant.settings.google import modify_oauth_credentials

MENU = {"Change Google OAuth credentials": modify_oauth_credentials}


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
