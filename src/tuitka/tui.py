from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Footer, Header

from tuitka.assets import STYLE_MAIN
from tuitka.widgets.modals import SplashScreen, SupportNuitkaModal
from tuitka.widgets.script_input import ScriptInputWidget


class NuitkaTUI(App):
    CSS_PATH = STYLE_MAIN
    TITLE = "Tuitka - Nuitka Terminal UI"
    script: reactive[str] = reactive("", init=False)

    BINDINGS = [
        ("ctrl+s", "show_support", "Support Nuitka"),
    ]

    def on_mount(self) -> None:
        self.push_screen(SplashScreen())

    def action_show_support(self) -> None:
        self.push_screen(SupportNuitkaModal())

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ScriptInputWidget()
        yield Footer()
