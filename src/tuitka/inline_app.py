from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import RichLog, Static
from textual_tty.widgets import TextualTerminal
from tuitka.constants import PYTHON_VERSION
from tuitka.utils import is_windows
from textual import on

from tuitka.compilation_base import CompilationMixin
from tuitka.assets import STYLE_INLINE_APP
from tuitka.widgets.nuitka_header import NuitkaHeader

if is_windows():
    from tuitka.direct_compilation import DirectCompilationRunner


class InlineCompilationApp(CompilationMixin, App):
    CSS_PATH = STYLE_INLINE_APP

    compilation_finished: reactive[bool] = reactive(False, init=False)
    compilation_success: reactive[bool] = reactive(False, init=False)

    def __init__(
        self, python_file: Path, python_version: str = PYTHON_VERSION, **nuitka_options
    ):
        super().__init__()
        self.python_file = python_file
        self.python_version = python_version
        self.nuitka_options = nuitka_options
        self.runner = None
        self.terminal = None
        self.log_widget = None

    def compose(self) -> ComposeResult:
        with Vertical(id="terminal-container"):
            yield NuitkaHeader()
            if is_windows():
                self.log_widget = RichLog(
                    id="compilation_log", highlight=True, markup=True
                )
                yield self.log_widget
            else:
                yield TextualTerminal(id="compilation_terminal")
            yield Static(
                "Compilation in progress...",
                id="status_label",
                classes="compilation-status in-progress",
            )

    def on_mount(self) -> None:
        if is_windows():
            self.runner = DirectCompilationRunner()
            self.runner.set_output_callback(self._handle_output)
            self.runner.set_completion_callback(self._handle_completion)
            self.set_timer(0.5, self.run_compilation_windows)
        else:
            self.terminal = self.query_one("#compilation_terminal", TextualTerminal)
            self.set_timer(0.1, self._start_compilation)

    def _handle_output(self, line: str) -> None:
        if self.log_widget:
            self.log_widget.write(line)

    def _handle_completion(self, exit_code: int) -> None:
        self.compilation_success = exit_code == 0
        self.compilation_finished = True

    async def run_compilation_windows(self) -> None:
        await self.runner.run_compilation(
            self.python_file, self.python_version, **self.nuitka_options
        )

    def _start_compilation(self) -> None:
        self.start_compilation(
            self.terminal, self.python_file, self.python_version, **self.nuitka_options
        )

    @on(TextualTerminal.ProcessExited)
    def on_process_exited(self, event: TextualTerminal.ProcessExited) -> None:
        self.handle_process_exited(event.exit_code)

    def watch_compilation_finished(self, finished: bool) -> None:
        if not finished:
            return

        status_label = self.query_one("#status_label", Static)
        if self.compilation_success:
            status_label.update("✓ Compilation completed successfully!")
            status_label.set_class(True, "success")
            status_label.set_class(False, "in-progress")
        else:
            status_label.update("✗ Compilation failed!")
            status_label.set_class(True, "error")
            status_label.set_class(False, "in-progress")

        # Exit after a delay
        self.set_timer(5.0, self.exit)
