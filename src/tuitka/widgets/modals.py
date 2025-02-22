from pathlib import Path
from typing import Iterable

from textual import on
from textual.reactive import reactive
from textual.events import Resize
from textual.containers import Vertical, Horizontal
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Label, Static, Input, DirectoryTree, Button
from rich_pixels import Pixels

from tuitka.constants import LOGO_PATH, SPLASHSCREEN_TEXT


class SplashScreen(ModalScreen):
    CSS_PATH = Path("../assets/style_modal_splash.tcss")

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


class CustomDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        exclude_patterns = (".", "__pycache__")
        return [path for path in paths if not path.name.startswith(exclude_patterns)]


class FileDialogScreen(ModalScreen):
    CSS_PATH = Path("../assets/style_modal_filedialog.tcss")
    dir_root: reactive[Path] = reactive(Path.cwd(), init=False)
    selected_py_file: reactive[str] = reactive("", init=False)

    def on_mount(self):
        self.query_exactly_one(Input).focus()
        self.query_exactly_one(Input).border_title = "root path"
        self.query_exactly_one(Input).border_title = ""

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal(id="horizontal-root"):
                yield Input(self.dir_root.as_posix())
                yield Button(":house:", variant="warning", id="btn-home")
                yield Button("CWD", variant="error", id="btn-cwd")

            yield CustomDirectoryTree(path=self.dir_root)
            yield Label("File selected", classes="header-label")
            yield Label("No file selected yet", id="label-selected-file")
            with Horizontal(id="horizontal-navigation"):
                yield Button(
                    "Continue", variant="success", id="btn-continue", disabled=True
                )
                yield Button("Cancel", variant="error", id="btn-cancel")

    @on(Button.Pressed)
    def button_interactions(self, event: Button.Pressed):
        if "home" in event.button.id:
            self.query_exactly_one(Input).value = Path.home().as_posix()
            self.dir_root = Path.home()
        elif "cwd" in event.button.id:
            self.query_exactly_one(Input).value = Path.cwd().as_posix()
            self.dir_root = Path.cwd()
        elif "continue" in event.button.id:
            self.dismiss(result=self.selected_py_file)
        elif "cancel" in event.button.id:
            self.dismiss()

    def on_input_changed(self, event: Input.Changed):
        self.dir_root = Path(event.input.value)

    @on(DirectoryTree.FileSelected)
    def choose_a_file(self, event: DirectoryTree.FileSelected):
        if event.path.name.endswith(".py"):
            self.query_one("#btn-continue").disabled = False
            self.selected_py_file = event.path.as_posix()
        else:
            self.query_one("#btn-continue").disabled = True
            self.selected_py_file = "[red]not a valid python File[/]"

    def watch_selected_py_file(self, new_value: Input.Submitted):
        self.query_exactly_one("#label-selected-file", Label).update(new_value)

    def watch_dir_root(self):
        if self.dir_root.exists() and self.dir_root.is_dir():
            self.query_exactly_one(CustomDirectoryTree).path = self.dir_root
