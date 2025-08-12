from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from tuitka.widgets.terminal import TuitkaTerminal
from tuitka.constants import PYTHON_VERSION
from textual import on

from tuitka.compilation_base import CompilationMixin
from tuitka.assets import STYLE_INLINE_APP
from tuitka.widgets.nuitka_header import NuitkaHeader
from tuitka.utils import get_default_shell


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
            yield TuitkaTerminal(id="compilation_terminal", command=get_default_shell())

    def on_mount(self) -> None:
            self.terminal = self.query_one("#compilation_terminal", TuitkaTerminal)
            self.set_timer(0.1, self._start_compilation)

    def _start_compilation(self) -> None:
        self.start_compilation(
            self.terminal, self.python_file, self.python_version, **self.nuitka_options
        )

    @on(TuitkaTerminal.ProcessExited)
    def on_process_exited(self, event: TuitkaTerminal.ProcessExited) -> None:
        self.handle_process_exited(event.exit_code)

    def watch_compilation_finished(self, finished: bool) -> None:
        if not finished:
            return
        self.set_timer(5.0, self.exit)
