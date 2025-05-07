import sys

from tuitka.cli import cli
from tuitka.tui import NuitkaTUI


def main() -> None:
    if len(sys.argv) == 2:
        cli(sys.argv[1])
    else:
        app = NuitkaTUI()
        app.run()
