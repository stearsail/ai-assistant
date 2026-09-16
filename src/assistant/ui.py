from rich.console import Console
from rich.text import Text
from rich.theme import Theme

# shared with prompts.py so the qmark matches the echoed message
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
            "user": USER_COLOR,
        }
    )
)


STREAM_INDENT = 2


class StreamPrinter:
    # wraps as it prints so every line keeps the margin, the terminal would wrap to column 0
    def __init__(self, indent: int = STREAM_INDENT):
        self.indent = indent
        self.col = 0
        self.word = ""
        self.fresh = True

    def _out(self, text: str) -> None:
        console.print(text, end="", markup=False, highlight=False, soft_wrap=True)

    def _width(self) -> int:
        return max(20, console.width - 2 * self.indent)

    def _start_line(self) -> None:
        if self.fresh:
            self._out(" " * self.indent)
            self.fresh = False

    def _newline(self) -> None:
        self._out("\n")
        self.col = 0
        self.fresh = True

    def _flush_word(self) -> None:
        if not self.word:
            return
        if self.col and self.col + len(self.word) > self._width():
            self._newline()
        self._start_line()
        self._out(self.word)
        self.col += len(self.word)
        self.word = ""

    def write(self, chunk: str) -> None:
        for char in chunk:
            if char == "\n":
                self._flush_word()
                self._newline()
            elif char.isspace():
                self._flush_word()
                if self.col >= self._width():
                    self._newline()
                else:
                    self._start_line()
                    self._out(char)
                    self.col += 1
            else:
                self.word += char
                if len(self.word) >= self._width():
                    self._flush_word()

    def break_line(self) -> None:
        # anything else printed mid-reply ends the line, so finish it here first
        self._flush_word()
        if not self.fresh:
            self._newline()

    def close(self) -> None:
        self._flush_word()


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
