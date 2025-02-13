from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tuitka.app import NuitkaTUI

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Label, Button


class EntrypointLabel(Label):
    app: "NuitkaTUI"

    def on_mount(self) -> None:
        self.update(self.app.entrypoint)
        self.id = "label-entrypoint"
        self.classes = "command-label"


class OptionsLabel(Label):
    app: "NuitkaTUI"

    def on_mount(self) -> None:
        self.id = "label-options"
        self.classes = "command-label"
        self.display = False


class ScriptLabel(Label):
    app: "NuitkaTUI"

    def on_mount(self) -> None:
        self.update(self.app.script)
        self.id = "label-script"
        self.classes = "command-label"


class CommandPreviewer(Vertical):
    app: "NuitkaTUI"

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield EntrypointLabel()
            yield OptionsLabel()
            yield ScriptLabel()

        yield Button("Build", id="build", variant="success")

        return super().compose()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "build":
            command = "\n".join(
                [
                    label.renderable
                    for label in self.query(".command-label")
                    if label.renderable
                ]
            )
            command = command.replace("\\\n", "")
            self.app.run_command(command=command)
