import questionary

from assistant.config import update_credential
from assistant.settings.validators import (
    validate_google_client_id,
    validate_google_client_secret,
)

FIELDS = {
    "client_id": ("Client ID", questionary.text, validate_google_client_id),
    "client_secret": (
        "Client Secret",
        questionary.password,
        validate_google_client_secret,
    ),
}


async def _modify_selected_credential(selected_cred: str) -> None:
    label, prompt_fn, validator = FIELDS[selected_cred]
    value = await prompt_fn(f"New {label}:", validate=validator).ask_async()
    if not value or not value.strip():
        return
    confirm = await questionary.confirm(
        f"Are you sure you want to modify your {label}?"
    ).ask_async()
    if confirm:
        update_credential(selected_cred, value.strip())
        questionary.print(f"\n{label} modified successfully\n", style="italic")
        return
    questionary.print(f"\n{label} modification cancelled\n", style="italic")


async def modify_oauth_credentials() -> None:
    choices = [
        questionary.Choice(title=label, value=field)
        for field, (label, *_) in FIELDS.items()
    ]
    choices.append(questionary.Choice("Cancel", value=None))
    while True:
        choice = await questionary.select("Modify:", choices=choices).ask_async()

        if choice is None or choice == "Cancel":
            return
        await _modify_selected_credential(choice)
