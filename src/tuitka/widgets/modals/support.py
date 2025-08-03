from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Markdown, TabbedContent, TabPane

from tuitka.assets import (
    STYLE_MODAL_SUPPORT,
    CONTENT_SUPPORT_NUITKA,
    CONTENT_COMMERCIAL,
)


class SupportNuitkaModal(ModalScreen):
    CSS_PATH = STYLE_MODAL_SUPPORT

    BINDINGS = [
        ("s", "show_tab('support')", "Support Nuitka"),
        ("c", "show_tab('commercial')", "Commercial"),
        ("escape", "dismiss", "Close"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="support-dialog"):
            with TabbedContent(initial="support"):
                with TabPane("Support Nuitka", id="support"):
                    yield Markdown(CONTENT_SUPPORT_NUITKA)

                with TabPane("Commercial", id="commercial"):
                    yield Markdown(CONTENT_COMMERCIAL)

            with Horizontal(classes="support-controls"):
                yield Button("Close", variant="primary", id="close_button")

    @on(Button.Pressed, "#close_button")
    def on_close_pressed(self) -> None:
        self.dismiss()

    def action_show_tab(self, tab: str) -> None:
        tabbed_content = self.query_one(TabbedContent)
        tabbed_content.active = tab

    def action_dismiss(self) -> None:
        self.dismiss()
