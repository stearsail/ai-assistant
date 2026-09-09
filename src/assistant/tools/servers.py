import assistant.config as config
from agno.tools.mcp import MCPTools

def _get_servers() -> dict:
    creds = config.load_credentials()
    return {
        "google_workspace": {
            "command": "uvx workspace-mcp --tools calendar tasks gmail docs",
            "env": {
                "GOOGLE_OAUTH_CLIENT_ID": creds["client_id"],
                "GOOGLE_OAUTH_CLIENT_SECRET": creds["client_secret"],
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
