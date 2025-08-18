from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, Center, Container
from textual.widgets import Button, Input, Static
from textual.widgets import RadioButton, RadioSet
from tuitka.constants import PYTHON_VERSION
from tuitka.widgets.nuitka_header import NuitkaHeader
from pathlib import Path

from tuitka.widgets.modals import (
    CompilationScreen,
    FileDialogScreen,
    NuitkaSettingsScreen,
)


class ScriptInput(Input):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            placeholder="Enter path to Python script to compile", *args, **kwargs
        )

    def on_mount(self) -> None:
        self.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Update app script when input changes."""
        self.app.script = Path(self.value.strip())


class ScriptInputWidget(Container):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.custom_settings = None

    DEFAULT_CSS = """
    ScriptInputWidget {
        width: 1fr;
        height: 1fr;
        align: center middle;
        padding: 1;
    }

    #main_container {
        width: 85%;
        max-width: 100;
        height: auto;
        align: center middle;
    }

    #title_label {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
        width: 1fr;
    }

    #input_section {
        width: 1fr;
        height: auto;
        margin-bottom: 1;
    }

    #script_input {
        width: 1fr;
        margin-bottom: 1;
    }

    #browse_button {
        width: auto;
    }

    #compilation_options_container {
        border: round $panel-lighten-2;
        width: 1fr;
        height: auto;
        padding: 1;
        margin-bottom: 1;
    }

    .group_title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
        width: 1fr;
    }

    .sub_title {
        margin-top: 0;
        margin-bottom: 0;
        color: $text-muted;
        width: 1fr;
    }

    /* disabled for now */
    #python_version_select {
        display: none;
        width: 1fr;
        margin-top: 0;
    }

    #settings_radioset {
        height: auto;
        width: 1fr;
        margin-top: 0;
        margin-bottom: 0;
        align: center middle;
        layout: horizontal;
    }

    RadioButton {
        width: auto;
        margin: 0 1;
        background: transparent;
        border: none;
        outline: none;
        text-style: none;
    }

    RadioButton:focus {
        background: transparent;
        border: none;
        outline: none;
    }

    #compile_button_container {
        width: 1fr;
        height: auto;
        align: center middle;
        margin-top: 0;
        margin-bottom: 0;
    }

    #compile_button {
        width: auto;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="main_container"):
            yield NuitkaHeader()
            yield Static(
                "Select a Python script to compile with Nuitka", id="title_label"
            )

            with Vertical(id="input_section"):
                yield ScriptInput(id="script_input")
                with Center():
                    yield Button("Browse Files", variant="primary", id="browse_button")

            with Vertical(id="compilation_options_container"):
                yield Static("Compilation Options", classes="group_title")

                yield Static("Presets", classes="sub_title")
                with RadioSet(id="settings_radioset"):
                    yield RadioButton("Onefile", id="onefile_preset", value=True)
                    yield RadioButton("Standalone", id="standalone_preset")
                    yield RadioButton("Custom", id="custom_settings")

                # Python version selection temporarily disabled - using current Python version
                # yield Static("Python Version", classes="sub_title")
                # yield Select(
                #     [
                #         ("3.8", "3.8"),
                #         ("3.9", "3.9"),
                #         ("3.10", "3.10"),
                #         ("3.11", "3.11"),
                #         ("3.12", "3.12"),
                #     ],
                #     value=PYTHON_VERSION,
                #     allow_blank=False,
                #     id="python_version_select",
                # )

            with Center(id="compile_button_container"):
                yield Button("Compile", variant="success", id="compile_button")

    def on_mount(self) -> None:
        script_input = self.query_one("#script_input", ScriptInput)
        if not script_input.value.strip():
            self.query_one("#compile_button", Button).display = False
            self.query_one("#compilation_options_container").display = False

    @on(Input.Changed, "#script_input")
    def on_script_input_changed(self, event: Input.Changed) -> None:
        # evaluate if options should show up
        should_be_visible = bool(event.value.strip())

        self.query_one("#compile_button", Button).display = should_be_visible
        self.query_one("#compilation_options_container").display = should_be_visible

    @on(Input.Submitted, "#script_input")
    def on_script_input_submitted(self, event: Input.Submitted) -> None:
        settings_radioset = self.query_one("#settings_radioset")
        if event.value.strip():
            settings_radioset.display = True

    @on(RadioSet.Changed, "#settings_radioset")
    def on_radio_changed(self, event: RadioSet.Changed) -> None:
        selected_button = event.radio_set.pressed_button
        if selected_button and selected_button.id == "custom_settings":
            self.app.push_screen(
                NuitkaSettingsScreen(self.custom_settings), self._handle_custom_settings
            )
        else:
            self.query_one("#compile_button").display = True

    @on(Button.Pressed, "#browse_button")
    def open_file_dialog(self) -> None:
        self.app.push_screen(FileDialogScreen(), callback=self._handle_file_selection)

    @on(Button.Pressed, "#compile_button")
    def start_compilation(self) -> None:
        script_input = self.query_one("#script_input", ScriptInput)
        if script_input.value.strip():
            radioset = self.query_one("#settings_radioset", RadioSet)
            selected_preset = radioset.pressed_button

            if selected_preset is None:
                return

            python_version = PYTHON_VERSION

            nuitka_options = {
                "--assume-yes-for-downloads": True,
                "--remove-output": True,
            }
            if selected_preset.id == "onefile_preset":
                nuitka_options["--onefile"] = True
            elif selected_preset.id == "standalone_preset":
                nuitka_options["--standalone"] = True
            elif selected_preset.id == "custom_settings" and self.custom_settings:
                nuitka_options = self.custom_settings

            self.app.push_screen(CompilationScreen(python_version, **nuitka_options))

    def _handle_file_selection(self, selected_file: str | None) -> None:
        if selected_file:
            self.query_one("#script_input", ScriptInput).value = selected_file
            self.app.script = selected_file
            self.query_one("#compilation_options_container").display = True

    def _handle_custom_settings(self, settings: dict | None) -> None:
        if settings:
            self.custom_settings = settings
            self.query_one("#compile_button").display = True
