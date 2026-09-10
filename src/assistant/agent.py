# ACTUAL AGENT WIRING
from contextlib import AsyncExitStack

from agno.agent import Agent
from agno.db.in_memory import InMemoryDb
from agno.models.anthropic import Claude
from prompt_toolkit import PromptSession
import questionary

from assistant.config import load_anthropic_api_key
from assistant.settings.menu import settings_menu
from assistant.tools.servers import build_toolkits


def _setup_agent(api_key, toolkits, db, session_id) -> Agent:
    agent = Agent(
        db=db,
        id="personal-assistant-agent",
        session_id=session_id,
        name="Personal Assistant",
        model=Claude(id="claude-sonnet-5", api_key=api_key),
        tools=toolkits,
        add_history_to_context=True,
        num_history_runs=3,
        markdown=True,
    )
    return agent

async def _chat(agent: Agent, session: PromptSession) -> bool:
    while True:
        try:
            message = (await session.prompt_async("> ")).strip()
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
        api_key = load_anthropic_api_key()["anthropic_api_key"]
        async with AsyncExitStack() as stack:
            toolkits = [await stack.enter_async_context(t) for t in build_toolkits()]
            agent = _setup_agent(api_key, toolkits, db, session_id)
            reload = await _chat(agent, session)
        if not reload:
            return
        questionary.print("\nRestarting with new configuration\n", style='fg:#effd5f bold italic')

