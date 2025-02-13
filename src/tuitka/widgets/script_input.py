from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tuitka.app import NuitkaTUI

from textual.widgets import Input

from tuitka.constants import DEFAULT_SCRIPT_NAME


class ScriptInput(Input):
    app: "NuitkaTUI"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.value = ""
        self.placeholder = "Enter your Python script path"

    def on_input_changed(self, event: Input.Changed) -> None:
        self.app.script = self.value.strip()
        if not self.value:
            self.app.script = DEFAULT_SCRIPT_NAME
