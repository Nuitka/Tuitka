from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Button, Collapsible, Input, Static

from tuitka.utils import create_nuitka_options_dict
from tuitka.assets import STYLE_MODAL_SETTINGS
from .settings_widgets import (
    ModalBoolFlag,
    ModalStringFlag,
    ModalSelectionFlag,
    ModalRadioFlag,
)


class NuitkaSettingsScreen(ModalScreen[dict | None]):
    CSS_PATH = STYLE_MODAL_SETTINGS

    def __init__(self, initial_settings: dict | None = None):
        super().__init__()
        self.current_settings = initial_settings or {}
        self.flag_widgets: list[
            ModalBoolFlag | ModalStringFlag | ModalSelectionFlag | ModalRadioFlag
        ] = []

        self.nuitka_options = create_nuitka_options_dict()

    def compose(self) -> ComposeResult:
        yield Static("Nuitka Settings", classes="settings-header")
        with Horizontal(id="filter-controls"):
            yield Input(
                placeholder="Search settings...",
                id="search_input",
                classes="filter-input",
            )
        with ScrollableContainer(id="settings-container"):
            for category, options in self.nuitka_options.items():
                with Collapsible(title=category):
                    for flag, config in options.items():
                        if self.should_skip_flag(flag, config):
                            continue

                        widget = self._create_flag_widget(flag, config)
                        if widget:
                            self.flag_widgets.append(widget)
                            yield widget

        with Horizontal(classes="settings-controls"):
            yield Button("Save", variant="success", id="save_button")
            yield Button("Cancel", variant="error", id="cancel_button")

    def should_skip_flag(self, flag: str, config: dict) -> bool:
        skip_flags = {
            "--help",
            "-h",
            "--module",
            "--version",
            "--standalone",
            "--onefile",
        }

        if flag in skip_flags:
            return True

        if config.get("action") == "help":
            return True

        if config.get("help") == "SUPPRESSHELP":
            return True

        return False

    def _create_flag_widget(self, flag: str, config: dict):
        action = config.get("action", "store")
        flag_type = config.get("type")
        choices = config.get("choices")
        default = config.get("default")
        help_text = config.get("help", "")
        metavar = config.get("metavar", "")

        current_value = self.current_settings.get(flag)

        if action in ["store_true", "store_false"]:
            widget_default = (
                current_value
                if current_value is not None
                else (default if isinstance(default, bool) else False)
            )
            widget = ModalBoolFlag(
                flag, help_text, widget_default, action=action, nuitka_default=default
            )
            widget.tooltip = help_text
            return widget

        elif choices:
            if "mode" in flag.lower() or flag in ["--mode"]:
                widget_default = current_value if current_value is not None else default
                widget = ModalRadioFlag(flag, help_text, choices, widget_default)
                widget.tooltip = help_text
                return widget
            else:
                widget_default = current_value if current_value is not None else default
                widget = ModalSelectionFlag(flag, help_text, choices, widget_default)
                widget.tooltip = help_text
                return widget

        elif action in ["store", "append"] and flag_type == "string":
            widget_default = (
                current_value
                if current_value is not None
                else (default if isinstance(default, str) else "")
            )
            widget = ModalStringFlag(flag, help_text, widget_default, metavar)
            widget.tooltip = help_text
            return widget

        return None

    @on(Input.Changed, "#search_input")
    def on_search_changed(self, event: Input.Changed) -> None:
        search_term = event.value.lower().strip()
        self.filter_settings(search_term)

    def filter_settings(self, search_term: str) -> None:
        query_selector = (
            "ModalBoolFlag, ModalStringFlag, ModalSelectionFlag, ModalRadioFlag"
        )
        all_widgets = self.query(query_selector)
        all_collapsibles = self.query(Collapsible)

        if not search_term:
            for widget in all_widgets:
                widget.display = True
            for collapsible in all_collapsibles:
                collapsible.display = True
                collapsible.collapsed = True
            self.query_one("#settings-container", ScrollableContainer).scroll_home(
                animate=False
            )
            return

        for collapsible in all_collapsibles:
            collapsible.display = False

        for widget in all_widgets:
            match = (
                search_term in widget.flag.lower()
                or search_term in widget.help_text.lower()
            )
            widget.display = match
            if match:
                parent = widget.parent
                while parent is not None and not isinstance(parent, Collapsible):
                    parent = parent.parent
                if parent is not None:
                    parent.display = True
                    parent.collapsed = False
        self.query_one("#settings-container", ScrollableContainer).scroll_home(
            animate=False
        )

    @on(Button.Pressed, "#save_button")
    def on_save_pressed(self) -> None:
        settings = {}

        for widget in self.flag_widgets:
            value = widget.get_value()
            if value is not None:
                settings[widget.flag] = value

        self.dismiss(settings)

    @on(Button.Pressed, "#cancel_button")
    def on_cancel_pressed(self) -> None:
        self.dismiss(None)
