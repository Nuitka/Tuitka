from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual_tty.widgets import TextualTerminal
from tuitka.constants import PYTHON_VERSION
from textual import on

from tuitka.compilation_base import CompilationMixin
from tuitka.assets import STYLE_INLINE_APP
from tuitka.widgets.nuitka_header import NuitkaHeader


class InlineCompilationApp(CompilationMixin, App):
    CSS_PATH = STYLE_INLINE_APP

    compilation_finished: reactive[bool] = reactive(False, init=False)

    def __init__(
        self, python_file: Path, python_version: str = PYTHON_VERSION, **nuitka_options
    ):
        super().__init__()
        self.python_file = python_file
        self.python_version = python_version
        self.nuitka_options = nuitka_options
        self.terminal = None

    def compose(self) -> ComposeResult:
        with Vertical(id="terminal-container"):
            yield NuitkaHeader()
            yield TextualTerminal(id="compilation_terminal")

    def on_mount(self) -> None:
        self.terminal = self.query_one("#compilation_terminal", TextualTerminal)
        self.set_timer(0.1, self._start_compilation)

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
        self.set_timer(5.0, self.exit)
