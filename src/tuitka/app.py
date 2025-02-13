from pathlib import Path
import asyncio

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widgets import Header, Footer, Button, Label, Collapsible

from tuitka.widgets.script_input import ScriptInput
from tuitka.widgets.flag_widgets import ListFlag, BoolFlag, StringFlag
from tuitka.widgets.output_logger import OutputLogger
from tuitka.constants import OPTION_TREE, ENTRY_POINT_DICT
from tuitka.utils import get_entrypoint


class NuitkaTUI(App):
    CSS_PATH = Path("assets/style.tcss")
    BINDINGS = [Binding("space", "float_preview", "Preview", priority=True)]
    entrypoint: reactive[str] = reactive("", init=False)
    options: reactive[dict] = reactive({}, init=False)
    script: reactive[str] = reactive("script.py", init=False)

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Header()
            yield Label("Nuitka Executable Builder", classes="title")
            yield ScriptInput(
                value="", placeholder="Enter your Python script path", id="script_path"
            )

            for category, flag_list in OPTION_TREE.items():
                with Collapsible(title=category):
                    for flag_dict in flag_list:
                        match flag_dict["type"]:
                            case "bool":
                                yield BoolFlag(
                                    flag_dict=flag_dict, id=flag_dict["flag"]
                                )
                            case "string":
                                yield StringFlag(
                                    flag_dict=flag_dict, id=flag_dict["flag"]
                                )
                            case "list":
                                yield ListFlag(
                                    flag_dict=flag_dict, id=flag_dict["flag"]
                                )

            with Collapsible(
                title="Show Command Preview",
                id="collaps-preview",
                collapsed=False,
                expanded_symbol=":eye:",
            ):
                yield Label(
                    self.entrypoint, id="label-entrypoint", classes="command-label"
                )
                option_label = Label("", id="label-options", classes="command-label")
                option_label.display = False
                yield option_label
                yield Label(self.script, id="label-script", classes="command-label")

            yield Button("Build", id="build", variant="success")
            yield OutputLogger()
            yield Footer()

    def on_mount(self):
        self.look_for_entrypoint()

    def look_for_entrypoint(self):
        executable = get_entrypoint()
        if executable is None:
            return

        self.entrypoint = ENTRY_POINT_DICT.get(executable)

    def update_bool_flags(self, flag: str, default: bool) -> None:
        if not default:
            self.options[flag] = None
        else:
            self.options.pop(flag)
        self.mutate_reactive(NuitkaTUI.options)

    def update_string_flags(self, flag: str, new_value: str, default: bool) -> None:
        if not default:
            self.options[flag] = new_value
        else:
            self.options.pop(flag)
        self.mutate_reactive(NuitkaTUI.options)

    def watch_entrypoint(self):
        self.query_one("#label-entrypoint", Label).update(self.entrypoint)
        self.notify(
            title="Entrypoint detected",
            message=f"Using {self.entrypoint.split()[0]} to build your executable",
        )

    def watch_script(self):
        self.query_one("#label-script", Label).update(self.script)

    def watch_options(self):
        # write options to preview
        option_string_list = []
        for flag, flag_values in self.options.items():
            # Bool Flags
            if flag_values is None:
                option_string_list.append(flag)
            # String Flags
            if isinstance(flag_values, str):
                option_string_list.append(f"{flag}={flag_values}")

        self.query_one("#label-options", Label).update(
            "\n".join(f"{option} \\" for option in option_string_list)
        )

        # hide option-label if no options selected
        if not self.options:
            self.query_one("#label-options", Label).display = False
        else:
            self.query_one("#label-options", Label).display = True

    def get_command(self):
        command = "\n".join(
            [
                label.renderable
                for label in self.query(".command-label")
                if label.renderable
            ]
        )
        return command

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "build":
            command = "\n".join(
                [
                    label.renderable
                    for label in self.query(".command-label")
                    if label.renderable
                ]
            )
            command = command.replace("\\\n", "")
            self.run_command(command=command)

    def action_float_preview(self):
        self.query_one("#collaps-preview").toggle_class("preview")
        self.query_one(Button).toggle_class("preview")

    @work(thread=True, exclusive=True)
    async def run_command(self, command: str):
        executer = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        while True:
            if executer.stdout is None:
                break
            output_line = await executer.stdout.readline()

            self.query_one(OutputLogger).write_line(output_line.decode().strip())
        # executer.wait()


if __name__ == "__main__":
    NuitkaTUI().run()
