from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tuitka.app import NuitkaTUI

from textual.app import ComposeResult
from textual.widgets import Input, Button
from textual.containers import Horizontal

from tuitka.widgets.modals import FileDialogScreen
from tuitka.constants import DEFAULT_SCRIPT_NAME


class ScriptInput(Input):
    app: "NuitkaTUI"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.value = ""
        self.placeholder = "Enter your Python script path"

    def on_mount(self):
        self.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        self.app.script = self.value.strip()
        if not self.value:
            self.app.script = DEFAULT_SCRIPT_NAME


class ScriptInputCombi(Horizontal):
    app: "NuitkaTUI"

    def compose(self) -> ComposeResult:
        yield ScriptInput()
        yield Button("Select File")

        return super().compose()

    def on_button_pressed(self):
        self.app.push_screen(FileDialogScreen(), callback=self.update_script_input)

    def update_script_input(self, selected_file: str | None):
        if selected_file is not None:
            self.query_one(ScriptInput).value = selected_file
