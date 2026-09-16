import os

from agno.tools.mcp import MCPTools

from assistant.config.credentials import load_credentials
from assistant.config.preferences import SERVICE_LEVELS, load_workspace

# core tools that create, change or delete, with the level that registers them
WRITE_TOOLS = {
    "calendar": {"manage_event": "full"},
    "gmail": {"send_gmail_message": "send"},
    "tasks": {"manage_task": "manage"},
    "drive": {
        "create_drive_file": "full",
        "create_drive_folder": "full",
        "import_to_google_doc": "full",
        "import_to_google_slides": "full",
        "import_to_google_sheets": "full",
    },
    "docs": {"create_doc": "full", "modify_doc_text": "full"},
    "sheets": {"create_spreadsheet": "full", "modify_sheet_values": "full"},
    "slides": {"create_presentation": "full"},
    "forms": {"create_form": "full"},
    "chat": {"send_message": "full", "create_reaction": "full"},
    "contacts": {"manage_contact": "full"},
    "appscript": {
        "create_script_project": "full",
        "update_script_content": "full",
        "run_script_function": "full",
    },
}


def _command(workspace: dict) -> str:
    permissions = " ".join(
        f"{service}:{level}" for service, level in sorted(workspace["permissions"].items())
    )
    command = (
        f"uvx workspace-mcp --permissions {permissions} --tool-tier {workspace['tier']}"
    )
    if workspace["disabled_tools"]:
        command += " --disabled-tools " + " ".join(workspace["disabled_tools"])
    return command


def _confirm_tools(workspace: dict) -> list[str]:
    # a name the server never registers is only warned about, so keep to what the level enables
    disabled = set(workspace["disabled_tools"])
    tools = []
    for service, level in workspace["permissions"].items():
        levels = SERVICE_LEVELS.get(service, ())
        if level not in levels:
            continue
        for tool, needed in WRITE_TOOLS.get(service, {}).items():
            if levels.index(level) >= levels.index(needed) and tool not in disabled:
                tools.append(tool)
    return tools


def _get_servers() -> dict:
    creds = load_credentials()
    workspace = load_workspace()
    env = {
        "GOOGLE_OAUTH_CLIENT_ID": creds["client_id"],
        "GOOGLE_OAUTH_CLIENT_SECRET": creds["client_secret"],
        "WORKSPACE_MCP_LOG_LEVEL": "ERROR", #SET TO INFO TO DEBUG
        **{k: os.environ[k] for k in ("DISPLAY", "XDG_RUNTIME_DIR") if k in os.environ},
    }
    if creds.get("user_gmail"):
        env["USER_GOOGLE_EMAIL"] = creds["user_gmail"]

    return {
        "google_workspace": {
            "command": _command(workspace),
            "env": env,
            "confirm": _confirm_tools(workspace),
        },
    }


def build_toolkits() -> list[MCPTools]:
    server = _get_servers()
    toolkits = []
    google_workspace = MCPTools(
        command=server["google_workspace"]["command"],
        env=server["google_workspace"]["env"],
        requires_confirmation_tools=server["google_workspace"]["confirm"],
    )
    toolkits.append(google_workspace)
    return toolkits
