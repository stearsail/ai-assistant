# ACTUAL AGENT WIRING
from contextlib import AsyncExitStack

from assistant.tools.servers import build_toolkits
from agno.agent import Agent
from agno.models.anthropic import Claude


def setup_agent(api_key: str, toolkits: list) -> Agent:
    agent = Agent(
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
        while True:
            try:
                message = input("> ").strip()
            except(EOFError, KeyboardInterrupt):
                break
            if message in ("exit", "quit"):
                break
            if message:
                await agent.aprint_response(input=message, stream=True)
    # async with build_toolkits() as agno_mcp_server:
    #     agent = setup_agent(api_key, agno_mcp_server)
    #     await agent.aprint_response(input=message, stream=True)
