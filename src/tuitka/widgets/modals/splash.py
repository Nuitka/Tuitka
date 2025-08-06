from random import randint, uniform

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.geometry import Offset
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Static

from tuitka.ui.constants import SNAKE_ARTS, SPLASHSCREEN_LINKS
from tuitka.assets import STYLE_MODAL_SPLASHSCREEN


class SplashScreen(ModalScreen):
    CSS_PATH = STYLE_MODAL_SPLASHSCREEN

    class Dismiss(Message):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.snake_arts = SNAKE_ARTS
        self.current_snake_index = randint(0, len(self.snake_arts) - 1)
        self.snake_timer = None
        self._is_screen_mounted = False

    def compose(self) -> ComposeResult:
        with Vertical(id="splash-dialog"):
            with Vertical(id="splash-content"):
                yield Static(self.snake_arts[self.current_snake_index], id="splash-art")
                yield Static(SPLASHSCREEN_LINKS, id="splash-links")
            yield Static(
                "Press any key to skip...",
                classes="continue-text",
            )

    def on_mount(self) -> None:
        self._is_screen_mounted = True
        self.set_timer(8, self._on_timer)
        self.snake_timer = self.set_interval(4.0, self._cycle_snake)
        initial_offset = self._get_random_offset()
        self.query_one("#splash-art", Static).animate(
            "offset",
            initial_offset,
            duration=2.0,
        )

    def _get_random_offset(self, magnitude: float = 25.0) -> Offset:
        x_offset = uniform(-magnitude, magnitude)
        y_offset = uniform(-magnitude * 0.6, magnitude * 0.6)
        return Offset(x_offset, y_offset)

    def _on_timer(self) -> None:
        self.post_message(self.Dismiss())

    def _cycle_snake(self) -> None:
        if not self._is_screen_mounted:
            return
        self.current_snake_index = (self.current_snake_index + 1) % len(self.snake_arts)
        self._update_snake_art()

    def _update_snake_art(self) -> None:
        if not self._is_screen_mounted:
            return
        splash_art = self.query_one("#splash-art", Static)
        exit_offset = self._get_random_offset(magnitude=30)

        def on_exit_complete():
            self._snake_slide_in()
            splash_art.animate(
                "offset",
                Offset(0, 0),
                duration=0.5,
            )

        splash_art.animate(
            "offset", exit_offset, duration=0.8, on_complete=on_exit_complete
        )

    def _snake_slide_in(self) -> None:
        if not self._is_screen_mounted:
            return
        splash_art = self.query_one("#splash-art", Static)
        splash_art.update(self.snake_arts[self.current_snake_index])
        entry_start = self._get_random_offset(magnitude=35)
        splash_art.offset = entry_start
        entry_end = Offset(0, 0)
        splash_art.animate(
            "offset",
            entry_end,
            duration=0.8,
        )

    def on_key(self, event) -> None:
        self.post_message(self.Dismiss())

    def on_splash_screen_dismiss(self, _: "SplashScreen.Dismiss") -> None:
        self._is_screen_mounted = False
        if self.snake_timer:
            self.snake_timer.stop()
            self.snake_timer = None
        self.dismiss()
