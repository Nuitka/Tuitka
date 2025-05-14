from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Footer, Header

from tuitka.assets import STYLE_MAIN
from tuitka.widgets.modals import SplashScreen
from tuitka.widgets.script_input import ScriptInputWidget


class NuitkaTUI(App):
    CSS_PATH = STYLE_MAIN
    TITLE = "Tuitka - Nuitka TUI"
    script: reactive[str] = reactive("", init=False)

    def on_mount(self) -> None:
        self.push_screen(SplashScreen())

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ScriptInputWidget()
        yield Footer()
