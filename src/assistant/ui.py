from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

# shared with prompts.py so the qmark matches the user box border
USER_COLOR = "cyan"

console = Console(
    theme=Theme(
        {
            "success": "#87ae73 bold italic",
            "error": "#ff0000 bold italic",
            "notice": "#e5de00 italic",
            "muted": "bright_black",
            "heading": "bold",
            "ok": "green",
            "missing": "red",
            "tool": "dim cyan",
            "user_border": USER_COLOR,
            "assistant_border": "bright_black",
        }
    )
)


def show(message: str, style: str = "", *, before: int = 0, after: int = 0) -> None:
    # Text, not a markup string, so brackets in messages are printed as-is
    for _ in range(before):
        console.print()
    console.print(Text(message, style=style))
    for _ in range(after):
        console.print()


def success(message: str, *, before: int = 0, after: int = 0) -> None:
    show(message, "success", before=before, after=after)


def error(message: str, *, before: int = 0, after: int = 0) -> None:
    show(message, "error", before=before, after=after)


def notice(message: str, *, before: int = 0, after: int = 0) -> None:
    show(message, "notice", before=before, after=after)


def muted(message: str, *, before: int = 0, after: int = 0) -> None:
    show(message, "muted", before=before, after=after)


def user_panel(message: str) -> Panel:
    return Panel(
        Text(message),
        title="You",
        title_align="left",
        border_style="user_border",
        expand=False,
    )


def assistant_panel(markdown: str) -> Panel:
    return Panel(
        Markdown(markdown),
        title="Assistant",
        title_align="left",
        border_style="assistant_border",
    )
