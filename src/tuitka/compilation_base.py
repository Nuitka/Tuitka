from pathlib import Path
from tuitka.constants import PYTHON_VERSION
from textual_tty.widgets import TextualTerminal

from tuitka.utils import prepare_nuitka_command


class CompilationMixin:
    def start_compilation(
        self,
        terminal: TextualTerminal,
        python_file: Path,
        python_version: str = PYTHON_VERSION,
        **nuitka_options,
    ) -> None:
        try:
            cmd, deps_metadata = prepare_nuitka_command(
                python_file, python_version, **nuitka_options
            )

            command_to_run = " ".join(cmd) + "; exit"

            terminal.input("clear\n")
            terminal.input(f"echo 'Executing: {command_to_run}'\n")

            if (
                deps_metadata.dependencies
                and deps_metadata.requirements_path != python_file
            ):
                with deps_metadata.temp_pep_723_file(python_file):
                    terminal.input(command_to_run + "\n")
            else:
                terminal.input(command_to_run + "\n")

        except Exception as e:
            self.handle_compilation_error(str(e))

    def handle_compilation_error(self, error_message: str) -> None:
        self.compilation_finished = True
        self.compilation_success = False

    def handle_process_exited(self, exit_code: int) -> None:
        self.compilation_success = exit_code == 0
        self.compilation_finished = True
