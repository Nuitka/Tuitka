from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tuitka.tui import NuitkaTUI

from textual.app import ComposeResult
from textual.containers import Center, Horizontal, Vertical
from textual.widgets import Button, Input, Label

from tuitka.widgets.modals import CompilationScreen, FileDialogScreen


class ScriptInput(Input):
    app: "NuitkaTUI"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.value = ""
        self.placeholder = "Enter The Path to Python script you want to compile"

    def on_mount(self):
        self.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        self.app.script = self.value.strip()
        if not self.value:
            self.app.script = __file__


class ScriptInputCombi(Horizontal):
    app: "NuitkaTUI"

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(id="script_input_placeholder")
            with Center():
                yield ScriptInput(id="script_input")
            with Center():
                yield Button("Select File", id="select_file_button")

    def on_button_pressed(self):
        self.app.push_screen(FileDialogScreen(), callback=self.file_selected_callback)

    def file_selected_callback(self, selected_file: str | None):
        if selected_file is not None:
            self.query_one(ScriptInput).value = selected_file
            self.app.push_screen(CompilationScreen())
