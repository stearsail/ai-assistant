import os

from agno.tools.mcp import MCPTools

from assistant import config


def _get_servers() -> dict:
    creds = config.load_credentials()
    return {
        "google_workspace": {
            "command": "uvx workspace-mcp --tools calendar tasks gmail docs --tool-tier core",
            "env": {
                "GOOGLE_OAUTH_CLIENT_ID": creds["client_id"],
                "GOOGLE_OAUTH_CLIENT_SECRET": creds["client_secret"],
                **{
                    k: os.environ[k]
                    for k in ("DISPLAY", "XDG_RUNTIME_DIR")
                    if k in os.environ
                },
            },
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
