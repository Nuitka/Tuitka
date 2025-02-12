from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Header, Footer, Button, Label, TextArea, Collapsible, Checkbox, Input, Switch

from tuitka.widgets.script_input import ScriptInput
from tuitka.widgets.command_preview import CommandPreviewer
from tuitka.widgets.flag_widgets import ListFlag, BoolFlag, StringFlag
from tuitka.constants import OPTION_TREE

class NuitkaTUI(App):
    CSS_PATH = Path('assets/style.tcss')
    options: reactive[dict] = reactive({})
    command: reactive[str] = reactive('nuitka')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Nuitka Executable Builder", classes="title")
        yield ScriptInput(placeholder="Enter your Python script path", id="script_path")

        # import subprocess
        # out =subprocess.run(['uvx', '--refresh', '--from','nuitka','nuitka', '--help'], text=True, capture_output=True)
        # lines = out.stdout.splitlines()
        # tmp_cat = ''
        # tmp_flags = []
        # for i, line in enumerate(lines):
        #     if line == '':
        #         if tmp_cat:
        #             with Collapsible(title=tmp_cat):
        #                 for flag in tmp_flags:
        #                     yield Label(flag)
        #             tmp_cat=''
        #             tmp_flags=[]
        #         else:
        #             tmp_cat=lines[i+1]
        #
        #     if line.strip().startswith('--'):
        #         tmp_flags.append(line.strip().split(' ')[0])

        for category, flag_list in OPTION_TREE.items():
            with Collapsible(title=category):
                for flag_dict in flag_list:
                    match flag_dict['type']:
                        case 'bool':
                            yield BoolFlag(flag_dict=flag_dict, id=flag_dict['flag'])
                        case 'string':
                            yield StringFlag(flag_dict=flag_dict, id=flag_dict['flag'])
                        case 'list':
                            yield ListFlag(flag_dict=flag_dict, id=flag_dict['flag'])

        
        
        yield Label('Command Preview')
        yield CommandPreviewer("", id="preview")
        yield Horizontal(Button("Build", id="build"))
        yield Footer()
    


    @on(Switch.Changed)
    def update_bool_flags(self, event: Switch.Changed) -> None:
        flag = event.switch.parent.id
        if event.switch.value:
            self.options[flag] = None
        else:
            if flag in self.options:
                self.options.pop(flag)

        self.mutate_reactive(NuitkaTUI.options)

    @on(Input.Changed)
    def update_sting_flags(self, event: Input.Changed) -> None:
        flag = event.input.parent.id
        value = event.input.value

        if event.input.value:
            self.options[flag] = value
        else:
            if flag in self.options:
                self.options.pop(flag)

        self.mutate_reactive(NuitkaTUI.options)

    def watch_options(self):
        script = self.query_one(ScriptInput).value.strip()
        if not script:
            script = "script.py"

        option_string_list = []
        for flag, flag_values in self.options.items():
            if flag_values is None:
                option_string_list.append(flag)
            if isinstance(flag_values, str):
                option_string_list.append(f'{flag}={flag_values}')


        self.command = f"nuitka {' '.join(option_string_list)} {script}"

    def watch_command(self):
        self.query_one(CommandPreviewer).load_text(self.command)
    
    
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "build":
            command = self.query_one("#preview", TextArea).text
            self.run_command(command)
    
    def run_command(self, command: str):
        import subprocess
        subprocess.run(command, shell=True)

if __name__ == "__main__":
    NuitkaTUI().run()
