# assistant

A personal assistant that runs in your terminal and works with your Google Workspace
(Calendar, Gmail, Tasks, Docs, …) through the [workspace-mcp](https://github.com/taylorwilsdon/google_workspace_mcp)
server, keeps notes in your Obsidian vault, and can search the web. It runs on a local model
through Ollama, or on Claude with an Anthropic API key.

## Requirements

- [uv](https://docs.astral.sh/uv/) and Python 3.13
- [Ollama](https://ollama.com) with a model that supports tools, or an Anthropic API key
- A Google Cloud OAuth client (Desktop app) and the Gmail address you sign in with

## Run

```bash
uv run assistant          # resume the last conversation
uv run assistant --new    # start a new one
```

The first run asks for your Google OAuth client ID, secret and Gmail address, and
optionally an Anthropic API key. The first Google tool call opens a browser to sign in.

## Chat commands

| Command     | Does                                  |
|-------------|---------------------------------------|
| `/help`     | list the commands                     |
| `/new`      | start a new conversation              |
| `/clear`    | clear the screen                      |
| `/settings` | open the settings menu                |
| `/exit`     | quit (`exit` and `quit` work as well) |

Tools that create, change or delete something ask before they run. When you decline,
you can tell the assistant why.

## Notes

The assistant can list, read, create, append to, edit and delete notes in an Obsidian vault.
Deleted notes are moved to the vault's `.trash` folder, so they can be restored.

It uses the vault Obsidian has open (from `~/.config/obsidian/obsidian.json`), or `~/Notes`
when there is none. To use a different vault, set it in `~/.config/assistant/preferences.json`:

```json
"notes": {"vault": "~/path/to/vault"}
```

## Configuration

```bash
assistant settings                  # interactive menu
assistant config show               # provider, model and masked credentials
assistant config api-key            # Anthropic API key (hidden prompt)
assistant config google             # Google OAuth credentials
assistant config provider ollama    # or anthropic
assistant config model qwen3.5:4b   # model for the current provider
assistant config timezone system    # or a zone such as Europe/Chisinau
```

Google services, their access level and how many tools are loaded are chosen in
`assistant settings` → Change Google Workspace access.

`GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `USER_GOOGLE_EMAIL` and
`ANTHROPIC_API_KEY` in the environment take precedence over the saved values.

## Files

| Path                                  | Holds                                   |
|---------------------------------------|-----------------------------------------|
| `~/.config/assistant/credentials.json` | OAuth client and API key (mode 0600)    |
| `~/.config/assistant/preferences.json` | provider, model, timezone, Google access, notes vault |
| `~/.config/assistant/sessions.db`      | conversation history                    |
| `~/.local/state/assistant/agno.log`    | agent logs                              |
| `~/.google_workspace_mcp/credentials/` | Google sign-in tokens                   |
