import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Optional
from asyncio.subprocess import Process
from textual_tty.widgets import TextualTerminal
from tuitka.utils.platform import PYTHON_VERSION
from tuitka.utils.nuitka import prepare_nuitka_command
from tuitka.utils.platform import is_windows


class CompilationRunner(ABC):
    def __init__(self):
        self.output_callback: Optional[Callable[[str], None]] = None
        self.completion_callback: Optional[Callable[[int], None]] = None

    def set_output_callback(self, callback: Callable[[str], None]) -> None:
        self.output_callback = callback

    def set_completion_callback(self, callback: Callable[[int], None]) -> None:
        self.completion_callback = callback

    @abstractmethod
    async def run_compilation(
        self, python_file: Path, python_version: str = PYTHON_VERSION, **nuitka_options
    ) -> int:
        pass

    @abstractmethod
    async def stop_compilation(self) -> None:
        pass

    def _emit_output(self, line: str) -> None:
        if self.output_callback:
            self.output_callback(line)

    def _emit_completion(self, exit_code: int) -> None:
        if self.completion_callback:
            self.completion_callback(exit_code)


class ProcessRunner(CompilationRunner):
    def __init__(self):
        super().__init__()
        self.process: Optional[Process] = None

    async def run_compilation(
        self, python_file: Path, python_version: str = PYTHON_VERSION, **nuitka_options
    ) -> int:
        try:
            cmd, deps_metadata = prepare_nuitka_command(
                python_file, python_version, **nuitka_options
            )

            self._emit_output(f"Starting compilation of {python_file.name}...")
            self._emit_output(f"Command: {' '.join(cmd)}")
            self._emit_output("=" * 60)
            return await self._execute_command(cmd)

        except Exception as e:
            self._emit_output(f"ERROR: {e}")
            return 1

    async def _execute_command(self, cmd: list[str]) -> int:
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=Path.cwd(),
            )
            self.process = process

            while True:
                output = await process.stdout.readline()
                if not output:
                    break
                line = output.decode().strip()
                self._emit_output(line)

            exit_code = await process.wait()

            if exit_code == 0:
                self._emit_output("=" * 60)
                self._emit_output("✓ Compilation completed successfully!")
            else:
                self._emit_output("=" * 60)
                self._emit_output(f"✗ Compilation failed with exit code: {exit_code}")

            self._emit_completion(exit_code)
            return exit_code

        except Exception as e:
            self._emit_output(f"EXECUTION ERROR: {e}")
            self._emit_completion(1)
            return 1
        finally:
            self.process = None

    async def stop_compilation(self):
        if self.process:
            try:
                self.process.terminate()
                try:
                    await asyncio.wait_for(self.process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    self.process.kill()
                    await self.process.wait()
            finally:
                self.process = None


class TerminalRunner(CompilationRunner):
    def __init__(self, terminal: TextualTerminal):
        super().__init__()
        self.terminal = terminal

    async def run_compilation(
        self, python_file: Path, python_version: str = PYTHON_VERSION, **nuitka_options
    ) -> int:
        try:
            cmd, deps_metadata = prepare_nuitka_command(
                python_file, python_version, **nuitka_options
            )

            command_to_run = " ".join(cmd) + "; exit"
            self.terminal.input("clear\n")

            self.terminal.input(command_to_run + "\n")

            return 0

        except Exception as e:
            self._emit_output(f"ERROR: {e}")
            self._emit_completion(1)
            return 1

    async def stop_compilation(self) -> None:
        pass


def create_runner(terminal: Optional[TextualTerminal] = None) -> CompilationRunner:
    """Create the appropriate compilation runner based on platform and terminal availability."""
    if is_windows() or terminal is None:
        return ProcessRunner()
    else:
        return TerminalRunner(terminal)
