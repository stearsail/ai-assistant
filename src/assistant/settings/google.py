import questionary

from assistant import prompts, ui
from assistant.config.credentials import (
    credential_status,
    update_credential,
)
from assistant.settings.validators import (
    validate_google_client_id,
    validate_google_client_secret,
    validate_user_gmail,
)

FIELDS = {
    "client_id": ("Client ID", prompts.text, validate_google_client_id),
    "client_secret": (
        "Client Secret",
        prompts.password,
        validate_google_client_secret,
    ),
    "user_gmail": ("Gmail Address", prompts.text, validate_user_gmail),
}


async def prompt_all_fields() -> dict | None:
    values = {}
    for field, (label, prompt_fn, validator) in FIELDS.items():
        value = await prompt_fn(f"{label}:", validate=validator).ask_async()
        if value is None:
            return None
        values[field] = value.strip() or None
    return values


async def _modify_selected_credential(selected_cred: str) -> bool:
    label, prompt_fn, validator = FIELDS[selected_cred]
    current = credential_status(f"google.{selected_cred}")
    if current:
        ui.muted(f"Current: {current['display']}", before=1)
    value = await prompt_fn(f"New {label}:", validate=validator).ask_async()
    if not value or not value.strip():
        return False
    confirm = await prompts.confirm(
        f"Are you sure you want to modify your {label}?"
    ).ask_async()
    if confirm:
        update_credential(selected_cred, value.strip())
        ui.success(f"{label} modified successfully", before=1, after=1)
        return True
    ui.muted(f"{label} modification cancelled", before=1, after=1)
    return False


async def modify_oauth_credentials() -> bool:
    choices = [
        questionary.Choice(title=label, value=field)
        for field, (label, *_) in FIELDS.items()
    ]
    choices.append(questionary.Choice("Cancel", value=None))
    changed = False
    while True:
        choice = await prompts.select("Modify:", choices=choices).ask_async()
        if choice is None or choice == "Cancel":
            return changed
        changed = await _modify_selected_credential(choice) or changed
