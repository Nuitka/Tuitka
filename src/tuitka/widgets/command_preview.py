from typing import TYPE_CHECKING
# from signal import SIGINT

if TYPE_CHECKING:
    from tuitka.app import NuitkaTUI

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll, Horizontal
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
        yield Label("Command preview and Building Executeable", classes="header-label")
        with VerticalScroll(can_focus=False):
            yield EntrypointLabel()
            yield OptionsLabel()
            yield ScriptLabel()

        with Horizontal():
            yield Button("Build", variant="success", id="btn-execute")
            yield Button("Cancel", variant="error", id="btn-abort", disabled=True)

        return super().compose()

    @on(Button.Pressed, "#btn-execute")
    def action_execute_command(self):
        self.app.query_one(VerticalScroll).scroll_end(animate=False)
        command = "\n".join(
            [
                label.renderable
                for label in self.query(".command-label")
                if label.renderable
            ]
        )
        command = command.replace("\\\n", "")
        self.app.run_command(command=command)

    @on(Button.Pressed, "#btn-abort")
    def action_cancel_command(self):
        self.notify("Stopped", severity="error")
        # self.app.executer.send_signal(SIGINT)
        self.app.executer.terminate()
        self.app.workers.cancel_all()
        self.app.executer = None
