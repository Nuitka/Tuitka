from pathlib import Path
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual import on
from textual_tty.widgets import TextualTerminal

from tuitka.utils.platform import PYTHON_VERSION
from tuitka.compilation.runners import create_runner
from tuitka.assets import STYLE_INLINE_APP
from tuitka.ui.components.header import NuitkaHeader
from tuitka.ui.components.compilation_view import CompilationView
from tuitka.utils.platform import is_windows


class InlineCompilationApp(App):
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
        self.compilation_view = None
        self.runner = None

    def compose(self) -> ComposeResult:
        yield NuitkaHeader()
        self.compilation_view = CompilationView(
            use_terminal=not is_windows(), id="terminal-container"
        )
        yield self.compilation_view

    def on_mount(self) -> None:
        terminal = self.compilation_view.get_terminal() if not is_windows() else None
        self.runner = create_runner(terminal)

        if is_windows():
            self.runner.set_output_callback(self._handle_output)
            self.runner.set_completion_callback(self._handle_completion)
            self.set_timer(0.5, self.run_compilation)
        else:
            # For Unix, we don't use callbacks since the terminal handles the process
            # The completion is handled via TextualTerminal.ProcessExited events
            self.set_timer(0.1, self._start_compilation)

    def _handle_output(self, line: str) -> None:
        if self.compilation_view:
            self.compilation_view.write_output(line)

    def _handle_completion(self, exit_code: int) -> None:
        self.compilation_success = exit_code == 0
        self.compilation_finished = True

    async def run_compilation(self) -> None:
        if self.runner:
            await self.runner.run_compilation(
                self.python_file, self.python_version, **self.nuitka_options
            )

    async def _start_compilation(self) -> None:
        if self.runner:
            await self.runner.run_compilation(
                self.python_file, self.python_version, **self.nuitka_options
            )

    @on(TextualTerminal.ProcessExited)
    def on_process_exited(self, event: TextualTerminal.ProcessExited) -> None:
        self.compilation_success = event.exit_code == 0
        self.compilation_finished = True

    def watch_compilation_finished(self, finished: bool) -> None:
        if not finished:
            return

        self.compilation_view.compilation_success = self.compilation_success
        self.compilation_view.compilation_finished = True

        # Exit after a delay
        self.set_timer(5.0, self.exit)
