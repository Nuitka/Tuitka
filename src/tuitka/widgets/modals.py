import asyncio
from pathlib import Path
from typing import Iterable

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, DirectoryTree, Input, Log, Static, Checkbox, Label
from textual.containers import ScrollableContainer

from tuitka.constants import SPLASHSCREEN_TEXT
from tuitka.utils import prepare_nuitka_command
from tuitka.cli_arguments import CompilationSettings
from tuitka.assets import (
    STYLE_MODAL_FILEDIALOG,
    STYLE_MODAL_COMPILATION,
    STYLE_MODAL_SETTINGS,
)


class OutputLogger(Log):
    can_focus = False


class SplashScreen(ModalScreen):
    DEFAULT_CSS = """
    SplashScreen {
        align: center middle;
    }
    
    #splash-dialog {
        width: 70;
        height: 20;
        padding: 2;
    }
    
    #splash-content {
        text-align: center;
        content-align: center middle;
        height: 1fr;
    }

    .continue-text {
        color: $text-muted;
        text-align: center;
        margin: 1 0 0 0;
    }

    """

    def compose(self) -> ComposeResult:
        with Vertical(id="splash-dialog"):
            yield Static(SPLASHSCREEN_TEXT, id="splash-content")
            yield Static("Press any key to continue...", classes="continue-text")

    def on_key(self) -> None:
        """Dismiss on any key press."""
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


class NuitkaSettingsScreen(ModalScreen[CompilationSettings | None]):
    """Settings screen for custom Nuitka configuration options."""

    CSS_PATH = STYLE_MODAL_SETTINGS

    def __init__(self, initial_settings: CompilationSettings | None = None):
        super().__init__()
        self.settings = initial_settings or CompilationSettings()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Nuitka Compilation Settings", classes="settings-header")

            with ScrollableContainer(classes="scrollable-content"):
                with Vertical(classes="settings-section"):
                    yield Label("Build Mode:")
                    with Horizontal(classes="option-row"):
                        yield Checkbox(
                            "Onefile", id="onefile_check", value=self.settings.onefile
                        )
                    with Horizontal(classes="option-row"):
                        yield Checkbox(
                            "Standalone",
                            id="standalone_check",
                            value=self.settings.standalone,
                        )

                with Vertical(classes="settings-section"):
                    yield Label("Runtime Options:")
                    with Horizontal(classes="option-row"):
                        yield Checkbox(
                            "Run after compilation",
                            id="run_after_check",
                            value=self.settings.run_after_compilation,
                        )
                    with Horizontal(classes="option-row"):
                        yield Checkbox(
                            "Disable console window",
                            id="disable_console_check",
                            value=self.settings.disable_console,
                        )

                with Vertical(classes="settings-section"):
                    yield Label("Build Process:")
                    with Horizontal(classes="option-row"):
                        yield Checkbox(
                            "Assume yes for downloads",
                            id="assume_yes_check",
                            value=self.settings.assume_yes_for_downloads,
                        )
                    with Horizontal(classes="option-row"):
                        yield Checkbox(
                            "Remove output directory",
                            id="remove_output_check",
                            value=self.settings.remove_output,
                        )
                    with Horizontal(classes="option-row"):
                        yield Checkbox(
                            "Show progress",
                            id="show_progress_check",
                            value=self.settings.show_progress,
                        )
                    with Horizontal(classes="option-row"):
                        yield Checkbox(
                            "Show memory usage",
                            id="show_memory_check",
                            value=self.settings.show_memory,
                        )

            with Horizontal(classes="settings-controls"):
                yield Button("Save Settings", variant="success", id="save_button")
                yield Button("Reset to Defaults", variant="default", id="reset_button")
                yield Button("Cancel", variant="default", id="cancel_button")

    @on(Checkbox.Changed, "#onefile_check")
    def on_onefile_changed(self, event: Checkbox.Changed) -> None:
        if event.value:
            standalone_check = self.query_one("#standalone_check", Checkbox)
            standalone_check.value = False

    @on(Checkbox.Changed, "#standalone_check")
    def on_standalone_changed(self, event: Checkbox.Changed) -> None:
        if event.value:
            onefile_check = self.query_one("#onefile_check", Checkbox)
            onefile_check.value = False

    @on(Button.Pressed, "#save_button")
    def on_save_pressed(self) -> None:
        settings = CompilationSettings(
            onefile=self.query_one("#onefile_check", Checkbox).value,
            standalone=self.query_one("#standalone_check", Checkbox).value,
            run_after_compilation=self.query_one("#run_after_check", Checkbox).value,
            assume_yes_for_downloads=self.query_one(
                "#assume_yes_check", Checkbox
            ).value,
            remove_output=self.query_one("#remove_output_check", Checkbox).value,
            show_progress=self.query_one("#show_progress_check", Checkbox).value,
            show_memory=self.query_one("#show_memory_check", Checkbox).value,
            disable_console=self.query_one("#disable_console_check", Checkbox).value,
            python_version=self.settings.python_version,  # Keep the existing Python version
        )
        self.dismiss(settings)

    @on(Button.Pressed, "#reset_button")
    def on_reset_pressed(self) -> None:
        default_settings = CompilationSettings()
        self.query_one("#onefile_check", Checkbox).value = default_settings.onefile
        self.query_one(
            "#standalone_check", Checkbox
        ).value = default_settings.standalone
        self.query_one(
            "#run_after_check", Checkbox
        ).value = default_settings.run_after_compilation
        self.query_one(
            "#assume_yes_check", Checkbox
        ).value = default_settings.assume_yes_for_downloads
        self.query_one(
            "#remove_output_check", Checkbox
        ).value = default_settings.remove_output
        self.query_one(
            "#show_progress_check", Checkbox
        ).value = default_settings.show_progress
        self.query_one(
            "#show_memory_check", Checkbox
        ).value = default_settings.show_memory
        self.query_one(
            "#disable_console_check", Checkbox
        ).value = default_settings.disable_console

    @on(Button.Pressed, "#cancel_button")
    def on_cancel_pressed(self) -> None:
        self.dismiss(None)
