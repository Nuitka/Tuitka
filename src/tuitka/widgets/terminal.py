"""
Custom terminal widget built on textual-tty's TextualTerminal.

Adds:
- Sensible defaults (uses default shell when no command is provided).
- Optional mouse cursor/reporting support for recordings.
- Small cleanup to disable mouse reporting on unmount to avoid leaking state.

Usage examples:

	from tuitka.widgets.terminal import TuitkaTerminal

	# As a child widget
	yield TuitkaTerminal(id="compilation_terminal")

	# With an explicit command
	yield TuitkaTerminal(command=["/bin/bash", "-l"])  # or command="/bin/bash -l"

This widget is a drop-in replacement for TextualTerminal in our app.
"""

from __future__ import annotations

from typing import Sequence

import sys

from textual_tty.widgets import TextualTerminal

from tuitka.utils import get_default_shell


class TuitkaTerminal(TextualTerminal):
	# Keep CSS minimal to let parent containers control size; users can style via IDs
	DEFAULT_CSS = """
	TuitkaTerminal {
		border: none;
	}
	"""

	def __init__(
		self,
		*,
		command: str | Sequence[str] | None = None,
		show_mouse: bool = True,
		**kwargs,
	) -> None:
		# If no command is provided, use the best-effort default shell
		if command is None:
			command = get_default_shell()

		super().__init__(command=command, **kwargs)
		self.show_mouse = bool(show_mouse)
		self._mouse_enabled = bool(show_mouse)

	def on_unmount(self) -> None:  # type: ignore[override]
		"""Disable mouse reporting on teardown to avoid leaving the TTY dirty."""
		if self._mouse_enabled:
			try:
				sys.stdout.write("\033[?1003l\033[?1000l\033[?1015l\033[?1006l")
				sys.stdout.flush()
			except Exception:
				pass


__all__ = ["TuitkaTerminal"]

