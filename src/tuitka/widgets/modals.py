from pathlib import Path

from textual import on
from textual.events import Resize
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Label, Static
from rich_pixels import Pixels

from tuitka.constants import LOGO_PATH, SPLASHSCREEN_TEXT


class SplashScreen(ModalScreen):
    CSS_PATH = Path("../assets/style_modal.tcss")

    def compose(self) -> ComposeResult:
        yield Label("Nuitka")
        yield Static(id="static-image")
        yield Static(SPLASHSCREEN_TEXT)

        return super().compose()

    def on_key(self):
        self.dismiss()

    @on(Resize)
    def keep_image_size(self, event: Resize):
        new_width, new_height = event.size
        self.image = Pixels.from_image_path(
            LOGO_PATH,
            resize=(int(new_width**0.9), new_height),  # Power ole
        )
        self.query_one("#static-image", Static).update(self.image)
