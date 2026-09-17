import os

from agno.tools.mcp import MCPTools

from assistant.config.credentials import load_credentials
from assistant.config.preferences import load_workspace


class WorkspaceTools(MCPTools):
    # confirm by default: only tools the server itself marks read-only run without asking
    async def build_tools(self) -> None:
        if self.session is not None:
            listed = await self.session.list_tools()
            tools = listed if isinstance(listed, list) else listed.tools
            self.requires_confirmation_tools = [
                tool.name
                for tool in tools
                if not (tool.annotations and tool.annotations.read_only_hint)
            ]
        await super().build_tools()


def _command(workspace: dict) -> str:
    permissions = " ".join(
        f"{service}:{level}"
        for service, level in sorted(workspace["permissions"].items())
    )
    return (
        f"uvx workspace-mcp --permissions {permissions} --tool-tier {workspace['tier']}"
    )


def _get_servers() -> dict:
    creds = load_credentials()
    env = {
        "GOOGLE_OAUTH_CLIENT_ID": creds["client_id"],
        "GOOGLE_OAUTH_CLIENT_SECRET": creds["client_secret"],
        "WORKSPACE_MCP_LOG_LEVEL": "ERROR",  # SET TO INFO TO DEBUG
        **{k: os.environ[k] for k in ("DISPLAY", "XDG_RUNTIME_DIR") if k in os.environ},
    }
    if creds.get("user_gmail"):
        env["USER_GOOGLE_EMAIL"] = creds["user_gmail"]

    return {
        "google_workspace": {
            "command": _command(load_workspace()),
            "env": env,
        },
    }


def build_toolkits() -> list[MCPTools]:
    server = _get_servers()
    toolkits = []
    google_workspace = WorkspaceTools(
        command=server["google_workspace"]["command"],
        env=server["google_workspace"]["env"],
    )
    toolkits.append(google_workspace)
    return toolkits
