from pathlib import Path
import asyncio

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widgets import Header, Footer, Label, Button  # , TabbedContent, TabPane
from textual.worker import Worker, WorkerState
from textual.widgets._collapsible import CollapsibleTitle

from tuitka.widgets.script_input import ScriptInputCombi
from tuitka.widgets.flag_widgets import (
    ListFlag,
    BoolFlag,
    StringFlag,
    SelectionFlag,
    FlagCollapsible,
)
from tuitka.widgets.modals import SplashScreen
from tuitka.widgets.command_preview import CommandPreviewer
from tuitka.widgets.output_logger import OutputLogger
from tuitka.constants import OPTION_TREE, ENTRY_POINT_DICT, MODE_DICT
from tuitka.utils import get_entrypoint


class NuitkaTUI(App):
    CSS_PATH = Path("assets/style.tcss")
    BINDINGS = [
        Binding("ctrl+l", "float_preview", "Pin Preview", priority=True),
        Binding("ctrl+j", "focus_next_category", "Next category", priority=True),
        Binding(
            "ctrl+k", "focus_previous_category", "Previous category", priority=True
        ),
    ]

    entrypoint: reactive[str] = reactive("", init=False)
    options: reactive[dict] = reactive({}, init=False)
    script: reactive[str] = reactive("script.py", init=False)

    def on_mount(self):
        self.look_for_entrypoint()
        self.push_screen(SplashScreen())

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(can_focus=False, id="v-scroll-app"):
            yield Label(
                "Choose your python file and compilation mode", classes="header-label"
            )
            yield ScriptInputCombi()
            yield SelectionFlag(flag_dict=MODE_DICT)
            yield Label("Customize Options with feature flags", classes="header-label")

            for category, flag_list in OPTION_TREE.items():
                with FlagCollapsible(title=category):
                    for flag_dict in flag_list:
                        match flag_dict["type"]:
                            case "bool":
                                yield BoolFlag(flag_dict=flag_dict)
                            case "string":
                                yield StringFlag(flag_dict=flag_dict)
                            case "list":
                                yield ListFlag(flag_dict=flag_dict)
                            case "selection":
                                yield SelectionFlag(flag_dict=flag_dict)

            # with TabbedContent():
            #     for category, flag_list in OPTION_TREE.items():
            #         with TabPane(category):
            #             for flag_dict in flag_list:
            #                 match flag_dict["type"]:
            #                     case "bool":
            #                         yield BoolFlag(flag_dict=flag_dict)
            #                     case "string":
            #                         yield StringFlag(flag_dict=flag_dict)
            #                     case "list":
            #                         yield ListFlag(flag_dict=flag_dict)
            #                     case "selection":
            #                         yield SelectionFlag(flag_dict=flag_dict)

            yield CommandPreviewer()
            yield Label("Log Output", classes="header-label")
            yield OutputLogger(auto_scroll=True)
        yield Footer()

    def look_for_entrypoint(self):
        executable = get_entrypoint()
        if executable is None:
            return
        self.entrypoint = ENTRY_POINT_DICT.get(executable)

    def update_options(self):
        self.mutate_reactive(NuitkaTUI.options)

    def watch_entrypoint(self):
        self.query_one("#label-entrypoint", Label).update(self.entrypoint)
        self.notify(
            title="Entrypoint detected",
            message=f"Using [yellow]{self.entrypoint.split()[0]}[/] to build your executable",
            timeout=2,
        )

    def watch_options(self):
        # write options to preview label
        option_string_list = []
        for flag, complete_flag in self.options.items():
            # Bool Flags
            if complete_flag is None:
                continue
            # String Flags
            if isinstance(complete_flag, str):
                option_string_list.append(complete_flag)

        if option_string_list:
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

    def action_focus_previous_category(self):
        self.screen.focus_previous(CollapsibleTitle)
        self.focused.parent.collapsed = False

    def action_focus_next_category(self):
        self.screen.focus_next(CollapsibleTitle)
        self.focused.parent.collapsed = False

    @work(thread=True, exclusive=True)
    async def run_command(self, command: str):
        self.call_from_thread(self.query_one(OutputLogger).clear)
        self.executer = await asyncio.create_subprocess_shell(
            command,
            # 'zsh test.zsh',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        while True:
            if self.executer.returncode is not None:
                break
            if self.executer.stdout is None:
                break
            output_line = await self.executer.stdout.readline()

            self.call_from_thread(
                self.query_one(OutputLogger).write_line, output_line.decode().strip()
            )

            self.call_from_thread(
                self.query_one("#v-scroll-app", VerticalScroll).scroll_end
            )
        self.call_from_thread(self.query_one(OutputLogger).write_line, "COMPLETED")
        # self.executer.wait()

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when the worker state changes."""
        if event.state in [WorkerState.PENDING, WorkerState.RUNNING]:
            self.query_one("#btn-execute", Button).disabled = True
            self.query_one("#btn-abort", Button).disabled = False

        if event.state not in [WorkerState.PENDING, WorkerState.RUNNING]:
            self.query_one("#btn-execute", Button).disabled = False
            self.query_one("#btn-abort", Button).disabled = True
