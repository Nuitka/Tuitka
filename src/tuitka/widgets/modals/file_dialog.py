from pathlib import Path
from typing import Iterable

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, DirectoryTree, Input

from tuitka.assets import STYLE_MODAL_FILEDIALOG


class CustomDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        exclude_patterns = (".", "__pycache__")
        return [path for path in paths if not path.name.startswith(exclude_patterns)]


class FileDialogScreen(ModalScreen[str | None]):
    CSS_PATH = STYLE_MODAL_FILEDIALOG

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
