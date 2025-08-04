from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Static, RichLog
from tuitka.constants import PYTHON_VERSION

from tuitka.direct_compilation import DirectCompilationRunner
from tuitka.assets import STYLE_MODAL_COMPILATION


class DirectCompilationScreen(ModalScreen):
    CSS_PATH = STYLE_MODAL_COMPILATION

    compilation_finished: reactive[bool] = reactive(False, init=False)
    compilation_success: reactive[bool] = reactive(False, init=False)

    def __init__(
        self, python_file: Path, python_version: str = PYTHON_VERSION, **nuitka_options
    ) -> None:
        super().__init__()
        self.python_file = python_file
        self.python_version = python_version
        self.nuitka_options = nuitka_options
        self.runner = DirectCompilationRunner()
        self.log_widget = None

    def compose(self) -> ComposeResult:
        with Vertical():
            self.log_widget = RichLog(id="compilation_log", highlight=True, markup=True)
            yield self.log_widget
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
        self.runner.set_output_callback(self._handle_output)
        self.runner.set_completion_callback(self._handle_completion)

        self.set_timer(0.5, self.run_compilation)

    def _handle_output(self, line: str) -> None:
        """Handle output from the compilation process."""
        if self.log_widget:
            self.log_widget.write(line)

    def _handle_completion(self, exit_code: int) -> None:
        self.compilation_success = exit_code == 0
        self.compilation_finished = True

    def cancel_compilation(self) -> None:
        if self.runner:
            self.runner.stop_compilation()

    async def run_compilation(self) -> None:
        await self.runner.run_compilation(
            self.python_file, self.python_version, **self.nuitka_options
        )
