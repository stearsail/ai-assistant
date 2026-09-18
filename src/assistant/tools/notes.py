from pathlib import Path
from agno.tools import Toolkit

MAX_CHARS = 20_000

class NotesTools(Toolkit):
    def __init__(self, vault: str | Path):
        self.vault = Path(vault).expanduser()
        super().__init__(name="notes", tools=[self.list_notes, self.read_note])

    def list_notes(self) -> str:
        """List all notes in the user's Obsidian vault.

        Returns:
            One note path per line, relative to the vault. Pass a path to read_note to open it.
        """
        paths = sorted(
            str(p.relative_to(self.vault))
            for p in self.vault.rglob("*.md")
            if ".obsidian" not in p.parts
        )
        return "\n".join(paths) or "The vault has no notes yet."

    def read_note(self, path: str) -> str:
        """Read a note from the user's Obsidian vault.

        Args:
            path: The note's path relative to the vault, as listed by list_notes, e.g. "Projects/ideas.md".

        Returns:
            The note's Markdown content.
        """
        note = self._resolve(path)
        if note is None:
            return f"'{path}' is outside the vault. Use a path from list_notes."
        if not note.is_file():
            return f"No note at '{path}'. Call list_notes to see the available paths."
        text = note.read_text(encoding="utf-8", errors="replace")
        if len(text) > MAX_CHARS:
            return (
                text[:MAX_CHARS]
                + f"\n\n[Truncated: the note is {len(text)} characters long]"
            )
        return text

    def _resolve(self, path: str) -> Path | None:
        # the model picks the path, so it must not be able to leave the vault
        if not path.endswith(".md"):
            path += ".md"
        note = (self.vault / path).resolve()
        return note if note.is_relative_to(self.vault.resolve()) else None
