from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Label, Switch, Select, Input

class BoolFlag(Horizontal):
    def __init__(self, flag_dict:dict[str, str|bool], *args, **kwargs) -> None:
        self.flag_dict = flag_dict
        super().__init__(*args, **kwargs)
        self.classes = 'flagwidget'

    def compose(self) -> ComposeResult:
        yield Label(self.flag_dict['flag'])
        yield Switch(value=self.flag_dict.get('default'))
        return super().compose()

class StringFlag(Horizontal):
    def __init__(self, flag_dict:dict[str, str], *args, **kwargs) -> None:
        self.flag_dict = flag_dict
        super().__init__(*args, **kwargs)
        self.classes = 'flagwidget'

    def compose(self) -> ComposeResult:
        yield Label(self.flag_dict['flag'])
        yield Input(placeholder=self.flag_dict.get('default', ''))
        return super().compose()

class ListFlag(Horizontal):
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
