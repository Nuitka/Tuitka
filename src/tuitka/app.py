from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Header, Footer, Button, Label, Collapsible

from tuitka.widgets.script_input import ScriptInput
from tuitka.widgets.flag_widgets import ListFlag, BoolFlag, StringFlag
from tuitka.widgets.output_logger import OutputLogger
from tuitka.constants import OPTION_TREE

class NuitkaTUI(App):
    CSS_PATH = Path('assets/style.tcss')
    # entrypoint: reactive[str] = reactive('uvx --from nuitka nuitka \\')
    entrypoint: reactive[str] = reactive('uvx --from nuitka --with cowsay nuitka \\')
    options: reactive[dict] = reactive({}, init=False)
    script: reactive[str] = reactive('script.py', init=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Nuitka Executable Builder", classes="title")
        yield ScriptInput(value='', placeholder="Enter your Python script path", id="script_path")

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

        
        
        with Collapsible(title='Show Command Preview', collapsed=False, expanded_symbol=':eye:'):
            yield Label(self.entrypoint, id='label-entrypoint', classes='command-label')
            yield Label('', id='label-options', classes='command-label')
            yield Label(self.script, id='label-script', classes='command-label')

        yield Horizontal(Button("Build", id="build"))
        yield OutputLogger()
        yield Footer()
    


    def update_bool_flags(self, flag: str, default: bool) -> None:
        if not default:
            self.options[flag] = None
        else:
            self.options.pop(flag)
        self.mutate_reactive(NuitkaTUI.options)


    def update_string_flags(self, flag: str, new_value: str, default: bool ) -> None:
        if  not default:
            self.options[flag] = new_value
        else:
            self.options.pop(flag)
        self.mutate_reactive(NuitkaTUI.options)


    def watch_script(self):
        self.query_one('#label-script',Label).update(self.script) 


    def watch_options(self):

        # write options to preview
        option_string_list = []
        for flag, flag_values in self.options.items():
            # Bool Flags
            if flag_values is None:
                option_string_list.append(flag)
            # String Flags
            if isinstance(flag_values, str):
                option_string_list.append(f'{flag}={flag_values}')


        self.query_one('#label-options',Label).update('\n'.join(f'{option} \\' for option in  option_string_list))



    def get_command(self):
        command = '\n'.join([label.renderable for label in self.query('.command-label') if label.renderable ]) 
        return command

        # self.notify(repr(command))

    
    
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "build":
            command = '\n'.join([label.renderable for label in self.query('.command-label') if label.renderable ]) 
            command = command.replace('\\\n', '')
            self.run_command(command=command)
        
    
    def run_command(self, command: str):
        import subprocess
        executer = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE,  text=True)
        for output_line in iter(executer.stdout.readline, ''):
            self.query_one(OutputLogger).write_line(output_line)
        executer.stdout.close()
        return_code = executer.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, command)

if __name__ == "__main__":
    NuitkaTUI().run()
