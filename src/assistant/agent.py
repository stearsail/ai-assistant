from contextlib import AsyncExitStack
from pathlib import Path
import uuid
from agno.agent import Agent, ToolCallStartedEvent, RunContentEvent
from agno.db.base import SessionType
from agno.db.sqlite import SqliteDb
from agno.models.ollama import Ollama
from agno.models.anthropic import Claude
from prompt_toolkit import PromptSession

from assistant import prompts, ui
from assistant.config.credentials import (
    MissingAPIKey,
    load_anthropic_api_key,
    load_credentials,
)
from assistant.config.preferences import load_preferences, update_provider
from assistant.config.utils import CONFIG_DIR
from assistant.settings.menu import settings_menu
from assistant.tools.servers import build_toolkits

AGENT_ID = "personal-assistant-agent"


def _latest_session_id(db: SqliteDb) -> str | None:
    sessions = db.get_sessions(
        session_type=SessionType.AGENT,
        component_id=AGENT_ID,
        sort_by="updated_at",
        sort_order="desc",
        limit=1,
        include_runs=False,
    )
    return sessions[0].session_id if sessions else None


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
        id=AGENT_ID,
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


async def _stream_reply(agent: Agent, message: str, session_id: str) -> None:
    status = ui.console.status("Thinking…")
    status.start()
    printer = ui.StreamPrinter()
    streaming = False
    try:
        async for event in agent.arun(
            input=message, stream=True, stream_events=True, session_id=session_id
        ):
            if isinstance(event, ToolCallStartedEvent):
                printer.break_line()
                ui.show(f"→ {event.tool.tool_name}", "tool")
            elif isinstance(event, RunContentEvent) and event.content:
                if not streaming:
                    status.stop()
                    streaming = True
                printer.write(event.content)
    finally:
        status.stop()
        printer.close()
    # end the reply's last line, then leave a blank line before the next prompt
    ui.console.print()
    ui.console.print()


async def _chat(
    agent: Agent, session: PromptSession, session_id: str
) -> tuple[bool, str]:
    while True:
        try:
            message = (
                await session.prompt_async(prompts.CHAT_MESSAGE, style=prompts.STYLE)
            ).strip()
        except (EOFError, KeyboardInterrupt):
            break
        if message in ("exit", "quit"):
            break
        if message == "/new":
            session_id = str(uuid.uuid4())
            ui.notice("Started a new conversation", before=1, after=1)
            continue
        if message == "/settings":
            if await settings_menu():
                return True, session_id
            continue
        if message:
            ui.show(f"› {message}", "user", after=1)
            await _stream_reply(agent, message, session_id)
    return False, session_id


async def run_agent(resume: bool = True) -> None:
    db = SqliteDb(db_file=str(CONFIG_DIR / "sessions.db"))
    session = PromptSession(erase_when_done=True)
    session_id = _latest_session_id(db) if resume else None
    if resume:
        ui.notice(
            "Resuming last conversation"
            if session_id
            else "No previous conversation found, starting a new one"
        )
    session_id = session_id or str(uuid.uuid4())
    while True:
        user_gmail = load_credentials().get("user_gmail")
        prefs = load_preferences()
        api_key = None
        if prefs["provider"] == "anthropic":
            try:
                api_key = load_anthropic_api_key()["anthropic_api_key"]
            except MissingAPIKey:
                ui.error("No Anthropic API key set, switched provider to Ollama")
                update_provider("ollama")
                prefs = load_preferences()
        model = _build_model(prefs, api_key)
        async with AsyncExitStack() as stack:
            toolkits = [await stack.enter_async_context(t) for t in build_toolkits()]
            agent = _setup_agent(model, user_gmail, toolkits, db, session_id)
            reload, session_id = await _chat(agent, session, session_id)
        if not reload:
            return
        ui.notice("Restarting with new configuration", before=1, after=1)
