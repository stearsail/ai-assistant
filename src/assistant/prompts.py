from functools import partial

import questionary
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style, merge_styles
from questionary.constants import DEFAULT_STYLE

from assistant import ui

QMARK = "›"


def _prompt_toolkit_color(color: str) -> str:
    # rich names ("bright_black") -> prompt_toolkit names ("ansibrightblack"); hex is shared
    return color if color.startswith("#") else f"ansi{color.replace('_', '')}"


QMARK_STYLE = Style([("qmark", f"fg:{_prompt_toolkit_color(ui.USER_COLOR)}")])

text = partial(questionary.text, qmark=QMARK, style=QMARK_STYLE)
password = partial(questionary.password, qmark=QMARK, style=QMARK_STYLE)
confirm = partial(questionary.confirm, qmark=QMARK, style=QMARK_STYLE)
select = partial(questionary.select, qmark=QMARK, style=QMARK_STYLE)
autocomplete = partial(questionary.autocomplete, qmark=QMARK, style=QMARK_STYLE)

# chat input, styled to match questionary prompts
STYLE = merge_styles([DEFAULT_STYLE, QMARK_STYLE])
CHAT_MESSAGE = FormattedText([("class:qmark", QMARK), ("", " ")])
