from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static
from rich_pixels import Pixels
from tuitka.assets import NUITKA_LOGO


class NuitkaHeader(Vertical):
    DEFAULT_CSS = """
    NuitkaHeader {
        height: auto;
        width: 1fr;
    }
    
    NuitkaHeader #image {
        text-align: center;
        content-align: center middle;
        margin-bottom: 1;
    }
    
    NuitkaHeader #website-link {
        text-align: center;
        margin: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static(Pixels.from_image_path(NUITKA_LOGO, (20, 20)), id="image")
        yield Static("[dim]https://nuitka.net[/dim]", id="website-link")
