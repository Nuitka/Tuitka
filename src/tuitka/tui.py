from pathlib import Path

from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Footer, Header

from tuitka.widgets.modals import SplashScreen
from tuitka.widgets.script_input import ScriptInputCombi


class NuitkaTUI(App):
    CSS_PATH = Path("assets/style.tcss")
    entrypoint: reactive[str] = reactive("", init=False)
    options: reactive[dict] = reactive({}, init=False)
    script: reactive[str] = reactive("script.py", init=False)

    def on_mount(self):
        self.push_screen(SplashScreen())

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScriptInputCombi()
        yield Footer()
