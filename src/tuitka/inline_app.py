from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from tuitka.constants import PYTHON_VERSION
from textual import on

from tuitka.assets import STYLE_INLINE_APP
from tuitka.widgets.nuitka_header import NuitkaHeader
from tuitka.utils import prepare_nuitka_command
from textual_tty.widgets import TextualTerminal


class InlineCompilationApp(App):
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
        self.nuitka_command, self.deps_metadata = prepare_nuitka_command(
            python_file, python_version, **nuitka_options
        )

    def compose(self) -> ComposeResult:
        with Vertical(id="terminal-container"):
            yield NuitkaHeader()
            yield TextualTerminal(
                id="compilation_terminal", command=self.nuitka_command
            )

    def on_mount(self) -> None:
        self.terminal = self.query_one("#compilation_terminal", TextualTerminal)

    @on(TextualTerminal.ProcessExited)
    def on_process_exited(self, event: TextualTerminal.ProcessExited) -> None:
        self.compilation_finished = True
        if not self.compilation_finished:
            return
        self.set_timer(5.0, self.exit)
