from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tuitka.app import NuitkaTUI


from textual.reactive import reactive
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Label, Switch, Select, Input, Collapsible, Rule

from textual.widgets._collapsible import CollapsibleTitle


class FlagCollapsible(Collapsible):
    def on_descendant_focus(self):
        self.collapsed = False

    def on_descendant_blur(self):
        if not self.has_focus_within:
            self.collapsed = True

    def _on_collapsible_title_toggle(self, event: CollapsibleTitle.Toggle) -> None:
        event.stop()
        self.collapsed = not self.collapsed


class BoolFlag(Vertical):
    app: "NuitkaTUI"

    def __init__(self, flag_dict: dict[str, str | bool], *args, **kwargs) -> None:
        self.flag_dict = flag_dict
        super().__init__(*args, **kwargs)
        self.classes = "flagwidget"
        self.id = flag_dict["flag"]

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(self.flag_dict["flag"])
            yield Switch(value=self.flag_dict.get("default"))
        yield Rule()
        return super().compose()

    def on_switch_changed(self, event: Switch.Changed):
        flag = self.id
        new_value = event.switch.value
        is_default = new_value == self.flag_dict.get("default")

        if not is_default:
            self.app.options[flag] = None
        else:
            self.app.options.pop(flag)
        self.app.update_options()


class StringFlag(Vertical):
    app: "NuitkaTUI"

    def __init__(self, flag_dict: dict[str, str], *args, **kwargs) -> None:
        self.flag_dict = flag_dict
        super().__init__(*args, **kwargs)
        self.classes = "flagwidget"
        self.id = flag_dict["flag"]

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(self.flag_dict["flag"])
            yield Input(placeholder=f"default: {self.flag_dict['default']}")
        yield Rule()
        return super().compose()

    def on_input_changed(self, event: Input.Changed):
        flag = self.id
        new_value = event.input.value
        is_default = new_value == self.flag_dict["default"]

        if not is_default:
            self.app.options[flag] = new_value
        else:
            self.app.options.pop(flag)
        self.app.update_options()


class SelectionFlag(Vertical):
    app: "NuitkaTUI"

    def __init__(self, flag_dict: dict[str, list], *args, **kwargs) -> None:
        self.flag_dict = flag_dict
        super().__init__(*args, **kwargs)
        self.classes = "flagwidget"
        self.id = flag_dict["flag"]

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(self.flag_dict["flag"])
            with self.prevent(Select.Changed):
                yield Select(
                    value=self.flag_dict["default"],
                    options=((choice, choice) for choice in self.flag_dict["choices"]),
                    allow_blank=False,
                )
        yield Rule()
        return super().compose()

    def on_select_changed(self, event: Select.Changed):
        flag = self.id
        new_value = event.select.value
        is_default = new_value == self.flag_dict["default"]

        if not is_default:
            self.app.options[flag] = new_value
        else:
            self.app.options.pop(flag)
        self.app.update_options()


class ListFlag(Vertical):
    app: "NuitkaTUI"
    flag: reactive[str] = reactive("")
    flag_value: reactive[str] = reactive("")
    complete_flag: reactive[str] = reactive("")

    def __init__(self, flag_dict: dict[str, list], *args, **kwargs) -> None:
        self.flag_dict = flag_dict
        super().__init__(*args, **kwargs)
        self.classes = "flagwidget"
        self.flag = flag_dict["flag"]
        self.flag_value = flag_dict["default"]

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(self.flag_dict["flag"])
            yield Select(
                (choice, choice) for choice in self.flag_dict.get("choices", [])
            )
        yield Rule()
        return super().compose()

    def watch_flag_value(self, new_flag_value): ...
