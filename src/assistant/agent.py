# ACTUAL AGENT WIRING
from contextlib import AsyncExitStack

from agno.agent import Agent
from agno.db.in_memory import InMemoryDb
from agno.models.anthropic import Claude
from prompt_toolkit import PromptSession

from assistant.settings.menu import settings_menu
from assistant.tools.servers import build_toolkits


def setup_agent(api_key: str, toolkits: list) -> Agent:
    agent = Agent(
        db=InMemoryDb(),
        id="personal-assistant-agent",
        name="Personal Assistant",
        model=Claude(id="claude-sonnet-5", api_key=api_key),
        tools=toolkits,
        add_history_to_context=True,
        num_history_runs=3,
        markdown=True,
    )
    return agent


async def run_agent(api_key: str) -> None:
    async with AsyncExitStack() as stack:
        toolkits = [await stack.enter_async_context(t) for t in build_toolkits()]
        agent = setup_agent(api_key, toolkits)
        session = PromptSession()
        while True:
            try:
                message = (await session.prompt_async("> ")).strip()
            except (EOFError, KeyboardInterrupt):
                break
            if message in ("exit", "quit"):
                break
            if message == "/settings":
                await settings_menu()
                continue
            if message:
                await agent.aprint_response(input=message, stream=True)
    # async with build_toolkits() as agno_mcp_server:
    #     agent = setup_agent(api_key, agno_mcp_server)
    #     await agent.aprint_response(input=message, stream=True)
