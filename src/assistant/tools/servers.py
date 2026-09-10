import os

from agno.tools.mcp import MCPTools

from assistant import config


def _get_servers() -> dict:
    creds = config.load_credentials()
    env = {
        "GOOGLE_OAUTH_CLIENT_ID": creds["client_id"],
        "GOOGLE_OAUTH_CLIENT_SECRET": creds["client_secret"],
        **{k: os.environ[k] for k in ("DISPLAY", "XDG_RUNTIME_DIR") if k in os.environ},
    }
    if creds.get("user_gmail"):
        env["USER_GOOGLE_EMAIL"] = creds["user_gmail"]

    return {
        "google_workspace": {
            "command": "uvx workspace-mcp --permissions calendar:full tasks:manage gmail:readonly docs:readonly --tool-tier core",
            "env": env,
        },
    }


def build_toolkits() -> list[MCPTools]:
    server = _get_servers()
    toolkits = []
    google_workspace = MCPTools(
        command=server["google_workspace"]["command"],
        env=server["google_workspace"]["env"],
    )
    toolkits.append(google_workspace)
    return toolkits
