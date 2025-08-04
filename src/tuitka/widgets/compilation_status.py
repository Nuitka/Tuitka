from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static, LoadingIndicator


class CompilationStatusWidget(Vertical):
    DEFAULT_CSS = """
    CompilationStatusWidget {
        height: auto;
        width: 1fr;
    }
    
    .status-container {
        height: auto;
        margin: 1 2;
        align: center middle;
    }
    
    .status-loading {
        height: 4;
    }
    
    .status-message {
        text-align: center;
        margin: 0 2;
        height: 1;
    }
    
    .status-success {
        color: $success;
    }
    
    .status-error {
        color: $error;
    }
    
    .status-in-progress {
        color: $text-muted;
    }
    """

    def __init__(self, initial_message: str = "Initializing compilation..."):
        super().__init__()
        self.initial_message = initial_message

    def compose(self) -> ComposeResult:
        with Vertical(classes="status-container status-loading"):
            yield LoadingIndicator(id="status_loading")
            yield Static(
                self.initial_message, id="status_message", classes="status-message"
            )

    def update_status(self, message: str, state: str = "in-progress") -> None:
        status = self.query_one("#status_message", Static)
        status.update(message)

        status.remove_class("status-in-progress", "status-success", "status-error")

        if state == "success":
            status.add_class("status-success")
        elif state == "error":
            status.add_class("status-error")
        else:
            status.add_class("status-in-progress")

    def hide_loading(self) -> None:
        self.query_one("#status_loading", LoadingIndicator).display = False
