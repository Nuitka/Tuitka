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
    flag: reactive[str] = reactive("", init=False)
    flag_value: reactive[str] = reactive("", init=False)
    complete_flag: reactive[str | None] = reactive(None, init=False)

    def __init__(self, flag_dict: dict[str, str | bool], *args, **kwargs) -> None:
        self.flag_dict = flag_dict
        super().__init__(*args, **kwargs)
        self.classes = "flagwidget"
        self.flag = flag_dict["flag"]
        self.flag_value = flag_dict["default"]

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(self.flag_dict["flag"])
            yield Switch(value=self.flag_dict["default"])
        yield Rule()
        return super().compose()

    def on_switch_changed(self, event: Switch.Changed):
        self.flag_value = event.switch.value

    def watch_flag_value(self):
        if self.flag_value == self.flag_dict["default"]:
            self.complete_flag = None
        else:
            self.complete_flag = f"{self.flag}"

    def watch_complete_flag(self):
        if self.complete_flag is None:
            self.app.options.pop(self.flag)
        else:
            self.app.options[self.flag] = self.complete_flag
        self.app.update_options()


class StringFlag(Vertical):
    app: "NuitkaTUI"
    flag: reactive[str] = reactive("", init=False)
    flag_value: reactive[str] = reactive("", init=False)
    complete_flag: reactive[str | None] = reactive(None, init=False)

    def __init__(self, flag_dict: dict[str, str], *args, **kwargs) -> None:
        self.flag_dict = flag_dict
        super().__init__(*args, **kwargs)
        self.classes = "flagwidget"
        self.flag = flag_dict["flag"]
        self.flag_value = flag_dict["default"]

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(self.flag_dict["flag"])
            yield Input(placeholder=f"default: {self.flag_dict['default']}")
        yield Rule()
        return super().compose()

    def on_input_changed(self, event: Input.Changed):
        self.flag_value = event.input.value

    def watch_flag_value(self):
        if self.flag_value == self.flag_dict["default"]:
            self.complete_flag = None
        else:
            self.complete_flag = f"{self.flag}={self.flag_value}"

    def watch_complete_flag(self):
        if self.complete_flag is None:
            self.app.options.pop(self.flag)
        else:
            self.app.options[self.flag] = self.complete_flag
        self.app.update_options()


class SelectionFlag(Vertical):
    app: "NuitkaTUI"
    flag: reactive[str] = reactive("", init=False)
    flag_value: reactive[str] = reactive("", init=False)
    complete_flag: reactive[str | None] = reactive(None, init=False)

    def __init__(self, flag_dict: dict[str, list], *args, **kwargs) -> None:
        self.flag_dict = flag_dict
        super().__init__(*args, **kwargs)
        self.classes = "flagwidget"
        self.flag = flag_dict["flag"]
        self.flag_value = flag_dict["default"]

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
        self.flag_value = event.select.value

    def watch_flag_value(self):
        if self.flag_value == self.flag_dict["default"]:
            self.complete_flag = None
        else:
            self.complete_flag = f"{self.flag}={self.flag_value}"

    def watch_complete_flag(self):
        if self.complete_flag is None:
            self.app.options.pop(self.flag)
        else:
            self.app.options[self.flag] = self.complete_flag
        self.app.update_options()


class ListFlag(Vertical):
    app: "NuitkaTUI"
    flag: reactive[str] = reactive("", init=False)
    flag_value: reactive[str] = reactive("", init=False)
    complete_flag: reactive[str | None] = reactive(None, init=False)

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
