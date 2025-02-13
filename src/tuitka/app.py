from pathlib import Path
import asyncio

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widgets import Header, Footer, Label

from tuitka.widgets.script_input import ScriptInput
from tuitka.widgets.flag_widgets import ListFlag, BoolFlag, StringFlag, FlagCollapsible
from tuitka.widgets.command_preview import CommandPreviewer
from tuitka.widgets.output_logger import OutputLogger
from tuitka.constants import OPTION_TREE, ENTRY_POINT_DICT
from tuitka.utils import get_entrypoint


class NuitkaTUI(App):
    CSS_PATH = Path("assets/style.tcss")
    BINDINGS = [
        Binding("ctrl+l", "float_preview", "Pin Preview", priority=True),
        Binding("ctrl+j", "focus_next_flag", "Next Flag", priority=True),
        Binding("ctrl+k", "focus_previous_flag", "Previous Flag", priority=True),
    ]

    entrypoint: reactive[str] = reactive("", init=False)
    options: reactive[dict] = reactive({}, init=False)
    script: reactive[str] = reactive("script.py", init=False)

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Header()
            yield Label("Nuitka Executable Builder", classes="title")
            yield ScriptInput()

            for category, flag_list in OPTION_TREE.items():
                with FlagCollapsible(title=category):
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

            yield CommandPreviewer()
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

    def watch_options(self):
        # write options to preview label
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

    def watch_script(self):
        self.query_one("#label-script", Label).update(self.script)

    def action_float_preview(self):
        self.query_one(CommandPreviewer).toggle_class("preview")

    def action_focus_previous_flag(self):
        # Handle movement from first to last category
        if self.focused.parent.has_class("flagwidget"):
            first_focused = self.focused.parent.parent.parent._contents_list.index(
                self.focused.parent
            )
            if first_focused == 0:
                self.action_focus_previous()

        self.action_focus_previous()
        if isinstance(self.focused.parent, FlagCollapsible):
            # focus the last flag widget
            try:
                self.focused.parent._contents_list[-1].children[-1].focus()
            except AttributeError:
                self.action_focus_previous_flag()
            return
        if not self.focused.parent.has_class("flagwidget"):
            self.action_focus_previous_flag()

    def action_focus_next_flag(self):
        self.action_focus_next()
        if isinstance(self.focused.parent, FlagCollapsible):
            # focus the first flag widget
            self.focused.parent._contents_list[0].children[-1].focus()
            return
        if not self.focused.parent.has_class("flagwidget"):
            self.action_focus_next_flag()

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
