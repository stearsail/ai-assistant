import asyncio

import questionary
import ollama
from assistant import prompts
from assistant.config.credentials import MissingAPIKey, load_anthropic_api_key
from assistant.config.preferences import PROVIDERS, load_preferences, update_model, update_provider


async def _switch_provider() -> bool:
    current = load_preferences()["provider"]
    other = next(p for p in PROVIDERS if p != current)
    switch = await prompts.confirm(
        f"Are you sure you want to change the provider to {other.capitalize()}?"
    ).ask_async()
    if switch:
        if other == "anthropic":
            try:
                load_anthropic_api_key()
            except MissingAPIKey:
                questionary.print(
                    "Could not switch provider to Anthropic, no API key is set",
                    style="fg:#ff0000 bold italic",
                )
                return False
        update_provider(other)
        return True
    return False


ANTHROPIC_MODELS = ("claude-haiku-4-5-20251001", "claude-sonnet-5", "claude-opus-5")


def _title(name: str, current: str, extra: str = "") -> str:
    return f"{name:24} {extra}" + ("  (current)" if name == current else "")


async def _ollama_choices(host: str, current: str) -> list[questionary.Choice] | None:
    client = ollama.AsyncClient(host=host)
    try:
        models = (await client.list()).models
        infos = await asyncio.gather(*(client.show(m.model) for m in models))
    except ConnectionError:
        questionary.print(f"Could not connect to Ollama at {host}", style="fg:#ff0000 bold italic")
        return None
    return [
        questionary.Choice(
            title=_title(m.model, current, f"{m.size / 1e9:.1f} GB"),
            value=m.model,
            disabled=None if "tools" in (info.capabilities or []) else "no tool support",
        )
        for m, info in zip(models, infos)
    ]


async def _switch_model() -> bool:
    prefs = load_preferences()
    provider = prefs["provider"]
    current = prefs[provider]["id"]

    if provider == "ollama":
        choices = await _ollama_choices(prefs["ollama"]["host"], current)
        if choices is None:
            return False
    else:
        choices = [questionary.Choice(title=_title(m, current), value=m) for m in ANTHROPIC_MODELS]

    if not any(c.disabled is None for c in choices):
        questionary.print(
            "No models with tool support installed. Pull one with: ollama pull <model>",
            style="fg:#ff0000 bold italic",
        )
        return False

    choices.append(questionary.Choice("Back", value=None))
    model = await prompts.select("Model:", choices=choices).ask_async()
    if model in (None, "Back") or model == current:
        return False

    update_model(provider, model)
    questionary.print(f"\nModel changed to {model}\n", style="italic")
    return True


async def modify_provider_settings() -> bool:
    changed = False
    while True:
        choice = await prompts.select(
            "Provider settings:",
            choices=[
                questionary.Choice(title="Switch provider", value="provider"),
                questionary.Choice(title="Select new model", value="id"),
                questionary.Choice(title="Back", value=None),
            ],
        ).ask_async()
        if choice in (None, "Back"):
            return changed
        if choice == "provider":
            changed = await _switch_provider() or changed
        if choice == "id":
            changed = await _switch_model() or changed
