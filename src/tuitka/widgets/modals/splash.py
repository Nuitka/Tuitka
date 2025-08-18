from random import randint, uniform, choice

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.geometry import Offset
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Static

from tuitka.constants import SNAKE_ARTS, SPLASHSCREEN_LINKS, SNAKE_FACTS
from tuitka.assets import STYLE_MODAL_SPLASHSCREEN


class SplashScreen(ModalScreen):
    CSS_PATH = STYLE_MODAL_SPLASHSCREEN

    class Dismiss(Message):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.snake_index = randint(0, len(SNAKE_ARTS) - 1)
        self.char_index = 0
        self.animation_timer = None

    def compose(self) -> ComposeResult:
        with Vertical(id="splash-dialog"):
            with Vertical(id="splash-content"):
                yield Static("", id="splash-art")
                yield Static("", id="splash-fact")
                yield Static(SPLASHSCREEN_LINKS, id="splash-links")
                yield Static(
                    "Press any key to skip...",
                    classes="continue-text",
                )

    def on_mount(self) -> None:
        self.set_timer(8, self.dismiss_splash)

        self.initialize_content()
        self.start_animations()

    def initialize_content(self) -> None:
        fact_widget = self.query_one("#splash-fact", Static)
        fact_widget.update(f"\n{choice(SNAKE_FACTS)}\n\n")
        self.char_index = 0

    def start_animations(self) -> None:
        art_widget = self.query_one("#splash-art", Static)
        initial_offset = self.get_random_offset(magnitude=6.0)
        art_widget.animate("offset", initial_offset, duration=5.0)
        self.set_timer(0.2, self.start_text_animation)

    def start_text_animation(self) -> None:
        if self.animation_timer:
            self.animation_timer.stop()

        self.animation_timer = self.set_interval(0.012, self.update_text)

    def update_text(self) -> None:
        target_text = SNAKE_ARTS[self.snake_index]

        if self.char_index >= len(target_text):
            if self.animation_timer:
                self.animation_timer.stop()
                self.animation_timer = None
            return

        current_text = target_text[: self.char_index + 1]
        art_widget = self.query_one("#splash-art", Static)
        art_widget.update(current_text)

        self.char_index += 1

    def get_random_offset(self, magnitude: float = 15.0) -> Offset:
        x_offset = uniform(-magnitude, magnitude)
        y_offset = uniform(-magnitude * 0.4, magnitude * 0.4)
        return Offset(x_offset, y_offset)

    def dismiss_splash(self) -> None:
        self.post_message(self.Dismiss())

    def on_key(self, event) -> None:
        self.dismiss_splash()

    def on_splash_screen_dismiss(self, _: "SplashScreen.Dismiss") -> None:
        if self.animation_timer:
            self.animation_timer.stop()
        self.dismiss()
