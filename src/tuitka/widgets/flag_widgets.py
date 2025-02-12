from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from tuitka.app import NuitkaTUI


from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Label, Switch, Select, Input

class BoolFlag(Horizontal):
    app: 'NuitkaTUI'

    def __init__(self, flag_dict:dict[str, str|bool], *args, **kwargs) -> None:
        self.flag_dict = flag_dict
        super().__init__(*args, **kwargs)
        self.classes = 'flagwidget'

    def compose(self) -> ComposeResult:
        yield Label(self.flag_dict['flag'])
        yield Switch(value=self.flag_dict.get('default'))
        return super().compose()

    def on_switch_changed(self, event:Switch.Changed):
        new_value = event.switch.value
        is_default = new_value == self.flag_dict.get('default')
        self.app.update_bool_flags(flag=self.id, default=is_default)


class StringFlag(Horizontal):
    app: 'NuitkaTUI'

    def __init__(self, flag_dict:dict[str, str], *args, **kwargs) -> None:
        self.flag_dict = flag_dict
        super().__init__(*args, **kwargs)
        self.classes = 'flagwidget'

    def compose(self) -> ComposeResult:
        yield Label(self.flag_dict['flag'])
        yield Input(placeholder=f'default: {self.flag_dict['default']}')
        return super().compose()

    def on_input_changed(self, event:Input.Changed):
        new_value = event.input.value
        is_default = new_value == self.flag_dict['default']
        self.app.update_string_flags(flag=self.id, new_value=new_value, default=is_default)


class ListFlag(Horizontal):
    app: 'NuitkaTUI'

    def __init__(self, flag_dict:dict[str, str| list], *args, **kwargs) -> None:
        self.flag_dict = flag_dict
        super().__init__(*args, **kwargs)
        self.classes = 'flagwidget'

    def compose(self) -> ComposeResult:
        yield Label(self.flag_dict['flag'])
        yield Select(
                (choice, choice) for choice in self.flag_dict.get('choices', [])
            )
        return super().compose()
