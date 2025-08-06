from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import RichLog, Static
from textual_tty.widgets import TextualTerminal
from tuitka.utils.platform import is_windows


class CompilationView(Vertical):
    compilation_finished: reactive[bool] = reactive(False, init=False)
    compilation_success: reactive[bool] = reactive(False, init=False)

    def __init__(self, use_terminal: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.use_terminal = use_terminal and not is_windows()
        self.log_widget = None
        self.terminal = None

    def compose(self) -> ComposeResult:
        if self.use_terminal:
            self.terminal = TextualTerminal(id="compilation_terminal")
            yield self.terminal
        else:
            self.log_widget = RichLog(id="compilation_log", highlight=True, markup=True)
            yield self.log_widget

        yield Static(
            "Compilation in progress...",
            id="status_label",
            classes="compilation-status in-progress",
        )

    def get_terminal(self) -> TextualTerminal:
        return self.terminal

    def get_log_widget(self) -> RichLog:
        return self.log_widget

    def write_output(self, line: str) -> None:
        if self.log_widget:
            self.log_widget.write(line)

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
