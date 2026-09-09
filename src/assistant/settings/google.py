import questionary
from assistant.config import update_credential

FIELDS = {
    "client_id": ("Client ID", questionary.text),
    "client_secret": ("Client Secret", questionary.password),
}


async def _modify_selected_credential(selected_cred: str) -> None:
    label, prompt_fn = FIELDS[selected_cred]
    value = await prompt_fn(f"New {label}:").ask_async()
    if not value or not value.strip():
        return
    update_credential(selected_cred, value.strip())
    return None


async def modify_oauth_credentials() -> None:
    choices = [
        questionary.Choice(title=label, value=field)
        for field, (label, _) in FIELDS.items()
    ]
    choices.append(questionary.Choice("Cancel", value=None))
    while True:
        choice = await questionary.select("Modify:", choices=choices).ask_async()

        if choice is None or choice == "Cancel":
            return
        await _modify_selected_credential(choice)
