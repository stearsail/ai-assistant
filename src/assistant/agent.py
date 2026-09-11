from contextlib import AsyncExitStack

import questionary
from agno.agent import Agent
from agno.db.in_memory import InMemoryDb
from agno.models.ollama import Ollama
from agno.models.anthropic import Claude
from prompt_toolkit import PromptSession

from assistant import prompts
from assistant.config.credentials import (
    MissingAPIKey,
    load_anthropic_api_key,
    load_credentials,
)
from assistant.config.preferences import load_preferences, update_provider
from assistant.settings.menu import settings_menu
from assistant.tools.servers import build_toolkits


def _build_model(prefs: dict, api_key: str | None) -> Claude | Ollama:
    provider = prefs["provider"]
    if provider == "ollama":
        o = prefs["ollama"]
        return Ollama(
            id=o["id"],
            host=o["host"],
            options={"num_ctx": o["num_ctx"]},
            api_key=None,
        )
    if provider == "anthropic":
        return Claude(id=prefs["anthropic"]["id"], api_key=api_key)
    raise ValueError(f"Unknown provider: {provider}")


def _setup_agent(model, user_gmail, toolkits, db, session_id) -> Agent:
    instructions = [
        "You are a personal assistant with access to various tools, including the user's Google Workspace. "
    ]
    if user_gmail:
        instructions.append(
            f"The user's Google account is {user_gmail}. "
            "Always use it for the user_google_email parameter."
        )
    agent = Agent(
        db=db,
        id="personal-assistant-agent",
        session_id=session_id,
        name="Personal Assistant",
        instructions=instructions,
        model=model,
        tools=toolkits,
        add_history_to_context=True,
        num_history_runs=3,
        add_datetime_to_context=True,
        timezone_identifier="Europe/Bucharest",
    )
    return agent


async def _chat(agent: Agent, session: PromptSession) -> bool:
    while True:
        try:
            message = (
                await session.prompt_async(prompts.CHAT_MESSAGE, style=prompts.STYLE)
            ).strip()
        except (EOFError, KeyboardInterrupt):
            break
        if message in ("exit", "quit"):
            break
        if message == "/settings":
            if await settings_menu():
                return True
            continue
        if message:
            await agent.aprint_response(input=message, stream=True)
    return False


async def run_agent() -> None:
    db = InMemoryDb()
    session = PromptSession()
    session_id = "cli"
    while True:
        user_gmail = load_credentials().get("user_gmail")
        prefs = load_preferences()
        api_key = None
        if prefs["provider"] == "anthropic":
            try:
                api_key = load_anthropic_api_key()["anthropic_api_key"]
            except MissingAPIKey:
                questionary.print(
                    "No Anthropic API key set, switched provider to Ollama",
                    style="fg:#ff0000 bold italic",
                )
                update_provider("ollama")
                prefs = load_preferences()
        model = _build_model(prefs, api_key)
        async with AsyncExitStack() as stack:
            toolkits = [await stack.enter_async_context(t) for t in build_toolkits()]
            agent = _setup_agent(model, user_gmail, toolkits, db, session_id)
            reload = await _chat(agent, session)
        if not reload:
            return
        questionary.print(
            "\nRestarting with new configuration\n", style="fg:#effd5f bold italic"
        )
