from functools import partial

import questionary
from prompt_toolkit.formatted_text import FormattedText
from questionary.constants import DEFAULT_STYLE

QMARK = "›"

text = partial(questionary.text, qmark=QMARK)
password = partial(questionary.password, qmark=QMARK)
confirm = partial(questionary.confirm, qmark=QMARK)
select = partial(questionary.select, qmark=QMARK)

# chat input, styled to match questionary prompts
STYLE = DEFAULT_STYLE
CHAT_MESSAGE = FormattedText([("class:qmark", QMARK), ("", " ")])
