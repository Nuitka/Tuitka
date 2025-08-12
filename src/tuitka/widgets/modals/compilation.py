from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Static
from tuitka.constants import PYTHON_VERSION
from tuitka.widgets.terminal import TuitkaTerminal

from tuitka.compilation_base import CompilationMixin
from tuitka.assets import STYLE_MODAL_COMPILATION


class CompilationScreen(CompilationMixin, ModalScreen):
    CSS_PATH = STYLE_MODAL_COMPILATION

    compilation_finished: reactive[bool] = reactive(False, init=False)
    compilation_success: reactive[bool] = reactive(False, init=False)

    def __init__(self, python_version: str = PYTHON_VERSION, **nuitka_options) -> None:
        super().__init__()
        self.python_version = python_version
        self.nuitka_options = nuitka_options
        self.terminal = None

    def compose(self) -> ComposeResult:
        with Vertical():
            yield TuitkaTerminal(id="compilation_terminal")
            yield Static(
                "Compilation in progress...",
                id="status_label",
                classes="compilation-status in-progress",
            )
            with Horizontal(classes="compilation-controls"):
                yield Button("Close", variant="default", id="btn_close", disabled=True)
                yield Button("Cancel", variant="error", id="btn_cancel")

    @on(Button.Pressed)
    def handle_button_press(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_close":
            self.dismiss()
        elif event.button.id == "btn_cancel":
            self.cancel_compilation()
            self.dismiss()

    def watch_compilation_finished(self, finished: bool) -> None:
        if finished:
            close_btn = self.query_one("#btn_close", Button)
            cancel_btn = self.query_one("#btn_cancel", Button)
            status_label = self.query_one("#status_label", Static)

            close_btn.disabled = False
            cancel_btn.disabled = True

            if self.compilation_success:
                status_label.update("✓ Compilation completed successfully!")
                status_label.set_class(True, "success")
                status_label.set_class(False, "in-progress")
            else:
                status_label.update("✗ Compilation failed!")
                status_label.set_class(True, "error")
                status_label.set_class(False, "in-progress")

    def on_mount(self) -> None:
        self.terminal = self.query_one("#compilation_terminal", TuitkaTerminal)
        self.set_timer(0.5, self.run_compilation)

    def cancel_compilation(self) -> None:
        if self.terminal:
            self.terminal.stop_process()

    def run_compilation(self) -> None:
        script_path = Path(self.app.script)
        self.start_compilation(
            self.terminal, script_path, self.python_version, **self.nuitka_options
        )

    @on(TuitkaTerminal.ProcessExited)
    def on_process_exited(self, event: TuitkaTerminal.ProcessExited) -> None:
        self.handle_process_exited(event.exit_code)
