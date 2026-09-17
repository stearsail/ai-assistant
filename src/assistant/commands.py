from prompt_toolkit.completion import Completer, Completion
from rich.text import Text

from assistant import ui

COMMANDS = {
    "/help": "list the available commands",
    "/new": "start a new conversation",
    "/clear": "clear the screen, the conversation carries on",
    "/settings": "open the settings menu",
    "/exit": "quit the assistant",
}


class SlashCompleter(Completer):
    # only a lone /command is completed, so normal messages never get suggestions
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if not text.startswith("/") or " " in text:
            return
        for name, description in COMMANDS.items():
            if name.startswith(text):
                yield Completion(
                    name, start_position=-len(text), display_meta=description
                )


def show_help() -> None:
    width = max(map(len, COMMANDS))
    ui.show("Commands", "heading", before=1)
    for name, description in COMMANDS.items():
        ui.console.print(
            Text.assemble(
                "  ", (f"{name:<{width}}", "user"), "  ", (description, "muted")
            )
        )
    ui.console.print()
