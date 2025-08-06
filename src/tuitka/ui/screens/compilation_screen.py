from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button

from tuitka.utils.platform import PYTHON_VERSION
from tuitka.compilation.runners import create_runner
from tuitka.assets import STYLE_MODAL_COMPILATION
from tuitka.ui.components.compilation_view import CompilationView


class CompilationScreen(ModalScreen):
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
        self.runner = create_runner()
        self.compilation_view = None

    def compose(self) -> ComposeResult:
        with Vertical():
            self.compilation_view = CompilationView()
            yield self.compilation_view
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

            close_btn.disabled = False
            cancel_btn.disabled = True

            self.compilation_view.compilation_success = self.compilation_success
            self.compilation_view.compilation_finished = True

    def on_mount(self) -> None:
        self.runner.set_output_callback(self._handle_output)
        self.runner.set_completion_callback(self._handle_completion)
        self.set_timer(0.5, self.run_compilation)

    def _handle_output(self, line: str) -> None:
        if self.compilation_view:
            self.compilation_view.write_output(line)

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
