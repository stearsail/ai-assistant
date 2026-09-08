import os

SERVERS = {
    "google_workspace": {
        "command": "uvx workspace-mcp --tools calendar tasks gmail docs",
        "env": {
            "GOOGLE_OAUTH_CLIENT_ID": os.environ["GOOGLE_OAUTH_CLIENT_ID"],
            "GOOGLE_OAUTH_CLIENT_SECRET": os.environ["GOOGLE_OAUTH_CLIENT_SECRET"],
        },
    },
}
