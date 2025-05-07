import subprocess
import sys
from functools import partial
from pathlib import Path
from time import sleep

from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.syntax import Syntax
from rich.text import Text

from tuitka.constants import SPLASHSCREEN_TEXT
from tuitka.utils import prepare_nuitka_command

console = Console()

ConsoleSyntax = partial(Syntax, lexer="console")


def prepare_layout() -> Layout:
    layout = Layout()
    layout.split_column(Layout(name="upper", ratio=1), Layout(name="lower", ratio=3))
    return layout


def run_compilation(script_path: Path) -> int:
    cmd, requirements_txt = prepare_nuitka_command(script_path)
    layout = prepare_layout()

    layout["upper"].update(
        Align.center(
            Text.from_markup(
                f"[bold blue]command:[/bold blue] {' '.join(cmd[cmd.index('nuitka') :])}\n\n"
            ),
            vertical="bottom",
        )
    )
    output = ""

    syntax = ConsoleSyntax(output)
    layout["lower"].update(syntax)

    process = subprocess.Popen(
        " ".join(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        text=True,
        bufsize=1,
    )

    with Live(layout, refresh_per_second=1, console=console) as live:
        for line in iter(process.stdout.readline, ""):
            output += line
            syntax = ConsoleSyntax(output)
            layout["lower"].update(syntax)
            live.update(layout)

    process.communicate()
    requirements_txt.unlink(missing_ok=True)
    return process.returncode or 0


def cli(script_path: str) -> None:
    console.print(
        Align.center(
            Text.from_markup(SPLASHSCREEN_TEXT),
            vertical="middle",
        )
    )

    sleep(3)

    if len(sys.argv) == 2:
        path = Path(script_path).resolve()
        if path.exists() and path.suffix == ".py":
            try:
                run_compilation(path)
            except Exception as e:
                console.print(f"[bold red]Error during compilation:[/bold red] {e}")
        else:
            console.print(
                f"[bold red]Error:[/bold red] '{script_path}' is not a valid Python file"
            )
    else:
        console.print(
            "[bold red]Error:[/bold red] Please provide a single Python script as an argument"
        )
