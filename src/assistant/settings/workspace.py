from pathlib import Path

import questionary

from assistant import prompts, ui
from assistant.config.credentials import load_credentials
from assistant.config.preferences import (
    SERVICE_LEVELS,
    TIERS,
    load_workspace,
    update_workspace,
)

TOKENS_DIR = Path.home() / ".google_workspace_mcp" / "credentials"


def _forget_token() -> bool:
    # levels decide the OAuth scopes, so a wider one needs a new sign-in
    email = load_credentials().get("user_gmail")
    token = TOKENS_DIR / f"{email}.json"
    if not email or not token.exists():
        return False
    token.unlink()
    return True


def _title(option: str, current: str | None) -> str:
    return f"{option}  (current)" if option == current else option


async def _choose_services(current: dict) -> dict | None:
    services = await questionary.checkbox(
        "Google services:",
        choices=[
            questionary.Choice(title=service, value=service, checked=service in current)
            for service in SERVICE_LEVELS
        ],
        qmark=prompts.QMARK,
        style=prompts.QMARK_STYLE,
    ).ask_async()
    if not services:
        return None
    permissions = {}
    for service in services:
        level = await prompts.select(
            f"{service} access:",
            choices=[
                questionary.Choice(title=_title(level, current.get(service)), value=level)
                for level in SERVICE_LEVELS[service]
            ],
        ).ask_async()
        if level is None:
            return None
        permissions[service] = level
    return permissions


async def modify_workspace_access() -> bool:
    workspace = load_workspace()
    permissions = await _choose_services(workspace["permissions"])
    if permissions is None:
        ui.muted("Workspace access unchanged", before=1, after=1)
        return False

    tier = await prompts.select(
        "Tools per service:",
        choices=[
            questionary.Choice(title=_title(tier, workspace["tier"]), value=tier)
            for tier in TIERS
        ],
    ).ask_async()
    if tier is None:
        return False

    summary = ", ".join(f"{s}:{level}" for s, level in sorted(permissions.items()))
    ui.show(f"{summary}  ({tier} tools)", "notice", before=1)
    if not await prompts.confirm("Save this access?").ask_async():
        ui.muted("Workspace access unchanged", before=1, after=1)
        return False

    update_workspace(permissions=permissions, tier=tier)
    if permissions != workspace["permissions"] and _forget_token():
        ui.notice("Google will ask you to sign in again on the next tool call")
    ui.success("Workspace access updated", before=1, after=1)
    return True
