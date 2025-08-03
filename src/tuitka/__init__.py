import sys
from tuitka.tui import NuitkaTUI
from pathlib import Path


def main() -> None:
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        if not path.is_file() or not path.suffix == ".py":
            from rich import print
            from rich.panel import Panel

            print(
                Panel.fit(
                    f"{path} is not a valid Python file. Please provide a valid Python file or if you want to run the TUI, just run `tuitka` without arguments.",
                    title="Error",
                    subtitle="Usage: tuitka <file.py>",
                    border_style="red",
                )
            )
            return

        from tuitka.inline_app import InlineCompilationApp

        default_options = {
            "--onefile": True,
            "--assume-yes-for-downloads": True,
            "--remove-output": True,
        }

        inline_app = InlineCompilationApp(path, **default_options)
        inline_app.run(inline=True)
        return

    app = NuitkaTUI()
    app.run()
