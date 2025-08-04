import asyncio
import subprocess
from pathlib import Path
from typing import Optional, Callable
from tuitka.constants import PYTHON_VERSION
from tuitka.utils import prepare_nuitka_command


class DirectCompilationRunner:
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.output_callback: Optional[Callable[[str], None]] = None
        self.completion_callback: Optional[Callable[[int], None]] = None

    def set_output_callback(self, callback: Callable[[str], None]):
        self.output_callback = callback

    def set_completion_callback(self, callback: Callable[[int], None]):
        self.completion_callback = callback

    async def run_compilation(
        self, python_file: Path, python_version: str = PYTHON_VERSION, **nuitka_options
    ) -> int:
        try:
            # Prepare the command
            cmd, deps_metadata = prepare_nuitka_command(
                python_file, python_version, **nuitka_options
            )

            if self.output_callback:
                self.output_callback(f"Starting compilation of {python_file.name}...")
                self.output_callback(f"Command: {' '.join(cmd)}")
                self.output_callback("=" * 60)

            if (
                deps_metadata.dependencies
                and deps_metadata.requirements_path != python_file
            ):
                if self.output_callback:
                    self.output_callback(
                        f"Dependencies: {', '.join(deps_metadata.dependencies)}"
                    )

                with deps_metadata.temp_pep_723_file(python_file):
                    return await self._execute_command(cmd)
            else:
                return await self._execute_command(cmd)

        except Exception as e:
            if self.output_callback:
                self.output_callback(f"ERROR: {e}")
            return 1

    async def _execute_command(self, cmd: list[str]) -> int:
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=Path.cwd(),
            )

            while True:
                output = self.process.stdout.readline()
                if output == "" and self.process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    if self.output_callback:
                        self.output_callback(line)

                await asyncio.sleep(0.01)

            exit_code = self.process.wait()

            if self.output_callback:
                if exit_code == 0:
                    self.output_callback("=" * 60)
                    self.output_callback("✓ Compilation completed successfully!")
                else:
                    self.output_callback("=" * 60)
                    self.output_callback(
                        f"✗ Compilation failed with exit code: {exit_code}"
                    )

            if self.completion_callback:
                self.completion_callback(exit_code)

            return exit_code

        except Exception as e:
            if self.output_callback:
                self.output_callback(f"EXECUTION ERROR: {e}")
            if self.completion_callback:
                self.completion_callback(1)
            return 1
        finally:
            self.process = None

    def stop_compilation(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
