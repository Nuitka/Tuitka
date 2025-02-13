from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tuitka.app import NuitkaTUI

from textual.widgets import Input


class ScriptInput(Input):
    app: "NuitkaTUI"

    ...

    def on_input_changed(self, event: Input.Changed) -> None:
        self.app.script = self.value.strip()
        if not self.value:
            self.app.script = "script.py"
