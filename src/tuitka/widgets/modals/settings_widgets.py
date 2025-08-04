from textual.app import ComposeResult
from textual.containers import Grid, Vertical
from textual.widgets import Input, RadioButton, RadioSet, Select, Static, Switch


class ModalBoolFlag(Grid):
    def __init__(
        self,
        flag: str,
        help_text: str,
        default: bool = False,
        action: str = "store_true",
        nuitka_default: bool | None = None,
    ):
        super().__init__()
        self.flag = flag
        self.help_text = help_text
        self.default = default
        self.action = action
        self.nuitka_default = nuitka_default
        self.initial_value = default

    def compose(self) -> ComposeResult:
        yield Static(self.flag)
        yield Switch(value=self.initial_value, id=f"switch_{self.flag}")

    def get_value(self):
        switch = self.query_one(f"#switch_{self.flag}", Switch)
        if self.action == "store_false":
            return not switch.value if switch.value != self.default else None
        else:
            return switch.value if switch.value != self.default else None

    def is_changed(self) -> bool:
        return self.query_one(Switch).value != self.initial_value

    def reset(self) -> None:
        self.query_one(Switch).value = self.initial_value


class ModalStringFlag(Grid):
    def __init__(self, flag: str, help_text: str, default: str = "", metavar: str = ""):
        super().__init__()
        self.flag = flag
        self.help_text = help_text
        self.default = default
        self.initial_value = default
        self.metavar = metavar

    def compose(self) -> ComposeResult:
        yield Static(self.flag)
        yield Input(
            value=str(self.initial_value) if self.initial_value else "",
            placeholder=self.metavar or self.flag.upper(),
            id=f"input_{self.flag}",
        )

    def get_value(self):
        input_widget = self.query_one(f"#input_{self.flag}", Input)
        value = input_widget.value.strip()
        return value if value and value != str(self.default) else None

    def is_changed(self) -> bool:
        return self.query_one(Input).value != self.initial_value

    def reset(self) -> None:
        self.query_one(Input).value = self.initial_value


class ModalSelectionFlag(Grid):
    def __init__(self, flag: str, help_text: str, choices: list, default=None):
        super().__init__()
        self.flag = flag
        self.help_text = help_text
        self.choices = choices
        self.default = default
        self.initial_value = default

    def compose(self) -> ComposeResult:
        yield Static(self.flag)
        options = [(choice, choice) for choice in self.choices]
        if self.initial_value:
            initial_option = self.initial_value
        else:
            initial_option = Select.BLANK
        yield Select(options, value=initial_option, id=f"select_{self.flag}")

    def get_value(self):
        select = self.query_one(f"#select_{self.flag}", Select)
        return (
            select.value
            if select.value != Select.BLANK and select.value != self.default
            else None
        )

    def is_changed(self) -> bool:
        return self.query_one(Select).value != self.initial_value

    def reset(self) -> None:
        self.query_one(Select).value = self.initial_value


class ModalRadioFlag(Grid):
    def __init__(self, flag: str, help_text: str, choices: list, default=None):
        super().__init__()
        self.flag = flag
        self.help_text = help_text
        self.choices = choices
        self.default = default
        self.initial_value = default

    def compose(self) -> ComposeResult:
        yield Static(self.flag)
        with Vertical():
            with RadioSet(id=f"radio_{self.flag}"):
                for choice in self.choices:
                    yield RadioButton(
                        choice,
                        value=(choice == self.initial_value),
                        id=f"radio_{self.flag}_{choice}",
                    )

    def get_value(self):
        radio_set = self.query_one(f"#radio_{self.flag}", RadioSet)
        if radio_set.pressed_button and radio_set.pressed_button.label:
            selected_value = str(radio_set.pressed_button.label)
            return selected_value if selected_value != self.default else None
        return None

    def is_changed(self) -> bool:
        radio_set = self.query_one(RadioSet)
        if radio_set.pressed_button:
            return str(radio_set.pressed_button.label) != self.initial_value
        return self.initial_value is not None

    def reset(self) -> None:
        radio_set = self.query_one(RadioSet)
        for button in radio_set.query(RadioButton):
            button.value = str(button.label) == self.initial_value
