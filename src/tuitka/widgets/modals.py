import asyncio
from pathlib import Path
from typing import Iterable

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, ScrollableContainer, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.message import Message
from textual.widgets import (
    Button,
    DirectoryTree,
    Input,
    Log,
    RadioButton,
    RadioSet,
    Select,
    Static,
    Switch,
    Collapsible,
)

from tuitka.constants import SNAKE_ART, SPLASHSCREEN_LINKS
from tuitka.utils import prepare_nuitka_command, create_nuitka_options_dict
from tuitka.cli_arguments import CompilationSettings
from tuitka.assets import (
    STYLE_MODAL_FILEDIALOG,
    STYLE_MODAL_COMPILATION,
    STYLE_MODAL_SETTINGS,
    STYLE_MODAL_SPLASHSCREEN,
)


class OutputLogger(Log):
    can_focus = False


class SplashScreen(ModalScreen):
    CSS_PATH = STYLE_MODAL_SPLASHSCREEN

    class Dismiss(Message):
        pass

    def compose(self) -> ComposeResult:
        with Vertical(id="splash-dialog"):
            with Vertical(id="splash-content"):
                yield Static(SNAKE_ART, id="splash-art")
                yield Static(SPLASHSCREEN_LINKS, id="splash-links")
            yield Static("Press any key to skip...", classes="continue-text")

    def on_mount(self) -> None:
        self.set_timer(3, self._on_timer)

    def _on_timer(self) -> None:
        self.post_message(self.Dismiss())

    def on_key(self) -> None:
        self.post_message(self.Dismiss())

    def on_splash_screen_dismiss(self, _: "SplashScreen.Dismiss") -> None:
        self.dismiss()


class CustomDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        exclude_patterns = (".", "__pycache__")
        return [path for path in paths if not path.name.startswith(exclude_patterns)]


class FileDialogScreen(ModalScreen[str | None]):
    CSS_PATH = STYLE_MODAL_FILEDIALOG

    DEFAULT_CSS = """
    Input {
        width: 1fr;
    }
    """

    dir_root: reactive[Path] = reactive(Path.cwd(), init=False)
    selected_py_file: reactive[str] = reactive("", init=False)

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal(classes="path-controls"):
                yield Input(
                    value=self.dir_root.as_posix(),
                    placeholder="Enter directory path",
                    id="path_input",
                )
                yield Button("🏠", variant="default", id="btn_home", tooltip="Home")
                yield Button(
                    "📁", variant="default", id="btn_cwd", tooltip="Current Dir"
                )

            yield CustomDirectoryTree(path=self.dir_root, id="file_tree")

            with Horizontal(id="horizontal-navigation"):
                yield Button(
                    "Select", variant="success", id="btn_select", disabled=True
                )
                yield Button("Cancel", variant="default", id="btn_cancel")

    @on(Button.Pressed)
    def handle_button_press(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "btn_home":
            self._set_directory(Path.home())
        elif button_id == "btn_cwd":
            self._set_directory(Path.cwd())
        elif button_id == "btn_select":
            self.dismiss(result=self.selected_py_file)
        elif button_id == "btn_cancel":
            self.dismiss()

    @on(Input.Changed, "#path_input")
    def handle_path_change(self, event: Input.Changed) -> None:
        try:
            path = Path(event.value)
            if path.exists() and path.is_dir():
                self.dir_root = path
        except (OSError, ValueError):
            pass

    @on(DirectoryTree.FileSelected)
    def handle_file_selection(self, event: DirectoryTree.FileSelected) -> None:
        if event.path.suffix == ".py":
            self.selected_py_file = event.path.as_posix()
            self.query_one("#btn_select").disabled = False
        else:
            self.selected_py_file = ""
            self.query_one("#btn_select").disabled = True

    def watch_dir_root(self) -> None:
        if self.dir_root.exists() and self.dir_root.is_dir():
            self.query_one("#file_tree", CustomDirectoryTree).path = self.dir_root
            self.query_one("#path_input", Input).value = self.dir_root.as_posix()

    def _set_directory(self, path: Path) -> None:
        self.dir_root = path


class CompilationScreen(ModalScreen):
    CSS_PATH = STYLE_MODAL_COMPILATION

    compilation_finished: reactive[bool] = reactive(False, init=False)
    compilation_success: reactive[bool] = reactive(False, init=False)

    def __init__(self, settings: CompilationSettings) -> None:
        super().__init__()
        self.settings = settings

    def compose(self) -> ComposeResult:
        with Vertical():
            yield OutputLogger(id="output_log")
            yield Static(
                "Compilation in progress...",
                id="status_label",
                classes="compilation-status in-progress",
            )
            with Horizontal(classes="compilation-controls"):
                yield Button("Close", variant="default", id="btn_close", disabled=True)
                yield Button("Cancel", variant="error", id="btn_cancel")

    @on(Button.Pressed)
    def handle_button_press(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_close":
            self.dismiss()
        elif event.button.id == "btn_cancel":
            # TODO: Implement process cancellation
            self.dismiss()

    def watch_compilation_finished(self, finished: bool) -> None:
        if finished:
            close_btn = self.query_one("#btn_close", Button)
            cancel_btn = self.query_one("#btn_cancel", Button)
            status_label = self.query_one("#status_label", Static)

            close_btn.disabled = False
            cancel_btn.disabled = True

            if self.compilation_success:
                status_label.update("✓ Compilation completed successfully!")
                status_label.set_class(True, "success")
                status_label.set_class(False, "in-progress")
            else:
                status_label.update("✗ Compilation failed!")
                status_label.set_class(True, "error")
                status_label.set_class(False, "in-progress")

    def on_mount(self) -> None:
        self.run_compilation()

    @work(thread=True, exclusive=True)
    async def run_compilation(self) -> None:
        log = self.query_one("#output_log", OutputLogger)

        self.app.call_from_thread(log.clear)
        cmd, requirements_txt = prepare_nuitka_command(
            Path(self.app.script), self.settings
        )

        try:
            nuitka_index = cmd.index("nuitka")
            cmd_display = " ".join(cmd[nuitka_index:])
        except ValueError:
            cmd_display = " ".join(cmd)

        self.app.call_from_thread(log.write_line, cmd_display)
        self.app.call_from_thread(log.write_line, "")

        process = await asyncio.create_subprocess_shell(
            " ".join(cmd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        while True:
            if process.returncode is not None:
                break
            if process.stdout is None:
                break

            line = await process.stdout.readline()
            if not line:
                break

            self.app.call_from_thread(log.write_line, line.decode().rstrip())

        await process.wait()

        self.app.call_from_thread(
            setattr, self, "compilation_success", process.returncode == 0
        )
        self.app.call_from_thread(setattr, self, "compilation_finished", True)

        if requirements_txt and requirements_txt.exists():
            requirements_txt.unlink()


class ModalBoolFlag(Grid):
    def __init__(self, flag: str, help_text: str, default: bool = False):
        super().__init__()
        self.flag = flag
        self.help_text = help_text
        self.default = default
        self.initial_value = default

    def compose(self) -> ComposeResult:
        yield Static(self.flag)
        yield Switch(value=self.initial_value, id=f"switch_{self.flag}")

    def get_value(self):
        switch = self.query_one(f"#switch_{self.flag}", Switch)
        return switch.value if switch.value != self.default else None

    def is_changed(self) -> bool:
        return self.query_one(Switch).value != self.initial_value

    def reset(self) -> None:
        self.query_one(Switch).value = self.initial_value


class ModalStringFlag(Grid):
    def __init__(self, flag: str, help_text: str, default: str = "", metavar: str = ""):
        super().__init__()
        self.flag = flag
        self.help_text = help_text
        self.default = default
        self.initial_value = default
        self.metavar = metavar

    def compose(self) -> ComposeResult:
        yield Static(self.flag)
        yield Input(
            value=str(self.initial_value) if self.initial_value else "",
            placeholder=self.metavar or self.flag.upper(),
            id=f"input_{self.flag}",
        )

    def get_value(self):
        input_widget = self.query_one(f"#input_{self.flag}", Input)
        value = input_widget.value.strip()
        return value if value and value != str(self.default) else None

    def is_changed(self) -> bool:
        return self.query_one(Input).value != self.initial_value

    def reset(self) -> None:
        self.query_one(Input).value = self.initial_value


class ModalSelectionFlag(Grid):
    def __init__(self, flag: str, help_text: str, choices: list, default=None):
        super().__init__()
        self.flag = flag
        self.help_text = help_text
        self.choices = choices
        self.default = default
        self.initial_value = default

    def compose(self) -> ComposeResult:
        yield Static(self.flag)
        options = [(choice, choice) for choice in self.choices]
        if self.initial_value:
            initial_option = self.initial_value
        else:
            initial_option = Select.BLANK
        yield Select(options, value=initial_option, id=f"select_{self.flag}")

    def get_value(self):
        select = self.query_one(f"#select_{self.flag}", Select)
        return (
            select.value
            if select.value != Select.BLANK and select.value != self.default
            else None
        )

    def is_changed(self) -> bool:
        return self.query_one(Select).value != self.initial_value

    def reset(self) -> None:
        self.query_one(Select).value = self.initial_value


class ModalRadioFlag(Grid):
    def __init__(self, flag: str, help_text: str, choices: list, default=None):
        super().__init__()
        self.flag = flag
        self.help_text = help_text
        self.choices = choices
        self.default = default
        self.initial_value = default

    def compose(self) -> ComposeResult:
        yield Static(self.flag)
        with Vertical():
            with RadioSet(id=f"radio_{self.flag}"):
                for choice in self.choices:
                    yield RadioButton(
                        choice,
                        value=(choice == self.initial_value),
                        id=f"radio_{self.flag}_{choice}",
                    )

    def get_value(self):
        radio_set = self.query_one(f"#radio_{self.flag}", RadioSet)
        if radio_set.pressed_button and radio_set.pressed_button.label:
            selected_value = str(radio_set.pressed_button.label)
            return selected_value if selected_value != self.default else None
        return None

    def is_changed(self) -> bool:
        radio_set = self.query_one(RadioSet)
        if radio_set.pressed_button:
            return str(radio_set.pressed_button.label) != self.initial_value
        return self.initial_value is not None

    def reset(self) -> None:
        radio_set = self.query_one(RadioSet)
        for button in radio_set.query(RadioButton):
            button.value = str(button.label) == self.initial_value


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
            "--standalone",
            "--onefile",
            "--module",
            "--version",
            "--gdb",
            "--github-workflow-options",
            "--must-not-re-execute",
            "--edit-module-code",
            "--list-package-data",
            "--list-distribution-metadata",
            "--list-package-dlls",
            "--list-package-exe",
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
            widget = ModalBoolFlag(flag, help_text, widget_default)
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
        """Filter settings based on search input."""
        search_term = event.value.lower().strip()
        self.filter_settings(search_term)

    def filter_settings(self, search_term: str) -> None:
        """Filter settings based on search term."""
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
        """Collect all settings from flag widgets and return as dict."""
        settings = {}

        for widget in self.flag_widgets:
            value = widget.get_value()
            if value is not None:
                settings[widget.flag] = value

        self.dismiss(settings)

    @on(Button.Pressed, "#cancel_button")
    def on_cancel_pressed(self) -> None:
        self.dismiss(None)
