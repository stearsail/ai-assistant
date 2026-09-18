import re
from datetime import datetime
from pathlib import Path

from agno.tools import Toolkit

# keeps one long note from filling the model's context
MAX_CHARS = 20_000
# Obsidian rejects these in file names, or they break [[links]]
UNSAFE_CHARS = re.compile(r'[*"\\/<>:|?#^\[\]]')
# where Obsidian itself puts deleted notes when set to "Move to Obsidian trash"
TRASH = ".trash"


class NotesTools(Toolkit):
    def __init__(self, vault: str | Path):
        self.vault = Path(vault).expanduser()
        super().__init__(
            name="notes",
            tools=[
                self.list_notes,
                self.read_note,
                self.create_note,
                self.append_to_note,
                self.edit_note,
                self.delete_note,
            ],
            requires_confirmation_tools=[
                "create_note",
                "append_to_note",
                "edit_note",
                "delete_note",
            ],
        )

    def list_notes(self) -> str:
        """List all notes in the user's Obsidian vault.

        Returns:
            One note path per line, relative to the vault. Pass a path to read_note to open it.
        """
        paths = sorted(
            str(p.relative_to(self.vault))
            for p in self.vault.rglob("*.md")
            # hidden folders hold Obsidian's config and trash, not notes
            if not any(part.startswith(".") for part in p.relative_to(self.vault).parts)
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
            return f"'{path}' isn't a note in the vault. Use a path from list_notes."
        if not note.is_file():
            return f"No note at '{path}'. Call list_notes to see the available paths."
        text = note.read_text(encoding="utf-8", errors="replace")
        if len(text) > MAX_CHARS:
            return (
                text[:MAX_CHARS]
                + f"\n\n[Truncated: the note is {len(text)} characters long]"
            )
        return text

    def create_note(self, title: str, content: str, folder: str = "") -> str:
        """Create a new note in the user's Obsidian vault. Never overwrites an existing note.

        Args:
            title: The note's title, which becomes its file name, e.g. "Trip ideas".
            content: The note's Markdown content.
            folder: A folder inside the vault for the note, e.g. "Projects". Leave empty for the top of the vault.

        Returns:
            The new note's path relative to the vault.
        """
        name = UNSAFE_CHARS.sub("", title).strip().lstrip(".")
        if not name:
            return "The title has no usable characters. Pick a title with letters or numbers."
        folder = folder.strip().strip("/")
        note = self._resolve(f"{folder}/{name}" if folder else name)
        if note is None:
            return f"'{folder}' can't hold notes. Use a folder inside the vault, or leave it empty."
        if note.exists():
            return f"A note called '{name}' already exists. Use append_to_note, or pick another title."
        note.parent.mkdir(parents=True, exist_ok=True)
        note.write_text(content.rstrip() + "\n", encoding="utf-8")
        return f"Created {self._relative(note)}"

    def append_to_note(self, path: str, content: str) -> str:
        """Add text to the end of an existing note in the user's Obsidian vault.

        Args:
            path: The note's path relative to the vault, as listed by list_notes.
            content: The Markdown text to add.

        Returns:
            Which note the text was added to.
        """
        note = self._resolve(path)
        if note is None:
            return f"'{path}' isn't a note in the vault. Use a path from list_notes."
        if not note.is_file():
            return f"No note at '{path}'. Call list_notes to see the paths, or create_note to start one."
        existing = note.read_text(encoding="utf-8", errors="replace")
        # start on a new line so the text doesn't run into the note's last sentence
        separator = "\n" if existing and not existing.endswith("\n") else ""
        with note.open("a", encoding="utf-8") as f:
            f.write(separator + content.rstrip() + "\n")
        return f"Added to {self._relative(note)}"

    def edit_note(self, path: str, old_text: str, new_text: str = "") -> str:
        """Remove or replace a passage in an existing note in the user's Obsidian vault.

        Args:
            path: The note's path relative to the vault, as listed by list_notes.
            old_text: The exact text to change, copied from read_note. It must appear only once in the note.
            new_text: The text to put in its place. Leave empty to remove old_text.

        Returns:
            What was changed.
        """
        note = self._resolve(path)
        if note is None:
            return f"'{path}' isn't a note in the vault. Use a path from list_notes."
        if not note.is_file():
            return f"No note at '{path}'. Call list_notes to see the available paths."
        if not old_text:
            return "old_text is empty. Copy the exact text to change from read_note."
        try:
            text = note.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return f"{self._relative(note)} isn't plain UTF-8 text, so it can't be edited safely."
        count = text.count(old_text)
        if count == 0:
            return f"That text isn't in {self._relative(note)}. Call read_note and copy it exactly."
        if count > 1:
            return (
                f"That text appears {count} times in {self._relative(note)}. "
                "Include more of the surrounding text so it matches only once."
            )
        if new_text:
            updated = text.replace(old_text, new_text, 1)
        elif old_text + "\n" in text:
            # removing a whole line shouldn't leave an empty line behind
            updated = text.replace(old_text + "\n", "", 1)
        else:
            updated = text.replace(old_text, "", 1)
        note.write_text(updated, encoding="utf-8")
        action = "Updated" if new_text else "Removed the text from"
        return f"{action} {self._relative(note)}"

    def delete_note(self, path: str) -> str:
        """Delete a note from the user's Obsidian vault by moving it to the vault's trash, where it can be restored.

        Args:
            path: The note's path relative to the vault, as listed by list_notes.

        Returns:
            Where the note was moved.
        """
        note = self._resolve(path)
        if note is None:
            return f"'{path}' isn't a note in the vault. Use a path from list_notes."
        if not note.is_file():
            return f"No note at '{path}'. Call list_notes to see the available paths."
        relative = self._relative(note)
        trash = self.vault.resolve() / TRASH
        trash.mkdir(exist_ok=True)
        target = trash / note.name
        if target.exists():
            target = (
                trash / f"{note.stem} {datetime.now():%Y-%m-%d %H%M%S}{note.suffix}"
            )
        note.rename(target)
        return f"Moved {relative} to the vault's {TRASH} folder, it can be restored from there"

    def _resolve(self, path: str) -> Path | None:
        # the model picks the path, so it must not be able to leave the vault
        if not path.endswith(".md"):
            path += ".md"
        vault = self.vault.resolve()
        note = (self.vault / path).resolve()
        if not note.is_relative_to(vault):
            return None
        if any(part.startswith(".") for part in note.relative_to(vault).parts):
            return None
        return note

    def _relative(self, note: Path) -> str:
        return str(note.relative_to(self.vault.resolve()))
