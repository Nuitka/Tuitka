from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Vertical, Horizontal
from textual.widgets import Button, Input, Static, Select
from textual.widgets import RadioButton, RadioSet

from tuitka.widgets.modals import (
    CompilationScreen,
    FileDialogScreen,
    NuitkaSettingsScreen,
)

from tuitka.cli_arguments import get_compilation_settings, CompilationSettings


class ScriptInput(Input):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            placeholder="Enter path to Python script to compile", *args, **kwargs
        )

    def on_mount(self) -> None:
        """Focus on mount."""
        self.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Update app script when input changes."""
        self.app.script = self.value.strip()


class ScriptInputWidget(Vertical):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.custom_settings = None  # Store custom settings when configured
    
    DEFAULT_CSS = """
    ScriptInputWidget {
        align: center middle;
        height: 100%;
    }
    
    .input-container {
        margin: 1 0;
        width: 100%;
        align: center middle;
    }
    
    .input-container Input {
        width: 60%;
        max-width: 80;
    }
    
    .button-container {
        margin: 1 0;
    }
    
    .version-label {
        text-align: center;
        margin: 0 0 1 0;
    }
    
    #python_version_select {
        width: 20%;
        max-width: 25;
    }
    
    #settings_options {
        height: auto;
        width: auto;
        margin: 1 0;
        max-width: 50%;
    }
    
    #settings_radioset {
        height: auto;
        width: auto;
        padding: 0;
        layout: horizontal;
        background: transparent;
        border: none;
    }
    
    RadioButton {
        width: auto;
        margin: 0 2;
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
    
    Static {
        text-align: center;
        color: $text-muted;
        margin: 2 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("Select a Python script to compile with Nuitka")

        with Center(classes="input-container"):
            yield ScriptInput(id="script_input")

        with Center(classes="button-container"):
            yield Button("Browse Files", variant="primary", id="browse_button")

        with Center():
            with Horizontal(id="settings_options"):
                with RadioSet(id="settings_radioset"):
                    yield RadioButton("Onefile Preset", id="onefile_preset")
                    yield RadioButton("Standalone Preset", id="standalone_preset")
                    yield RadioButton("Custom Settings", id="custom_settings")
                yield Select(
                    [
                        ("Py 3.8", "3.8"),
                        ("Py 3.9", "3.9"),
                        ("Py 3.10", "3.10"),
                        ("Py 3.11", "3.11"),
                        ("Py 3.12", "3.12"),
                    ],
                    value="3.11",
                    id="python_version_select",
                )
        
        with Center(classes="button-container"):
            yield Button("Compile", variant="success", id="compile_button")

    def on_mount(self) -> None:
        script_input = self.query_one("#script_input", ScriptInput)
        if not script_input.value.strip():
            self.query_one("#compile_button").display = False
            self.query_one("#settings_radioset").display = False

    @on(Input.Changed, "#script_input")
    def on_script_input_changed(self, event: Input.Changed) -> None:
        settings_radioset = self.query_one("#settings_radioset")
        if event.value.strip():
            settings_radioset.display = True
        else:
            self.query_one("#compile_button").display = False
            settings_radioset.display = False

    @on(Input.Submitted, "#script_input")
    def on_script_input_submitted(self, event: Input.Submitted) -> None:
        settings_radioset = self.query_one("#settings_radioset")
        if event.value.strip():
            settings_radioset.display = True

    @on(RadioSet.Changed, "#settings_radioset")
    def on_radio_changed(self, event: RadioSet.Changed) -> None:
        selected_button = event.radio_set.pressed_button
        if selected_button and selected_button.id == "custom_settings":
            self.app.push_screen(NuitkaSettingsScreen(self.custom_settings), self._handle_custom_settings)
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

            if selected_preset.id == "custom_settings" and self.custom_settings:
                settings = self.custom_settings
            else:
                settings = get_compilation_settings(selected_preset.id)

            # Get the selected Python version
            python_version_select = self.query_one("#python_version_select", Select)
            settings.python_version = python_version_select.value

            self.app.push_screen(CompilationScreen(settings))

    def _handle_file_selection(self, selected_file: str | None) -> None:
        if selected_file:
            self.query_one("#script_input", ScriptInput).value = selected_file
            self.app.script = selected_file
            self.query_one("#settings_radioset").display = True
    
    def _handle_custom_settings(self, settings: CompilationSettings | None) -> None:
        if settings:
            self.custom_settings = settings
            self.query_one("#compile_button").display = True
