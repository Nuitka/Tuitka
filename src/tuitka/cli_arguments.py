from dataclasses import dataclass


@dataclass
class CompilationSettings:
    onefile: bool = False
    standalone: bool = False
    run_after_compilation: bool = False
    assume_yes_for_downloads: bool = False
    remove_output: bool = True
    show_progress: bool = False
    show_memory: bool = False
    disable_console: bool = False
    python_version: str = "3.11"

    def to_nuitka_args(self) -> list[str]:
        args = []

        if self.onefile:
            args.append("--onefile")
        elif self.standalone:
            args.append("--standalone")

        flag_mapping = {
            "run_after_compilation": "--run",
            "assume_yes_for_downloads": "--assume-yes-for-downloads",
            "remove_output": "--remove-output",
            "show_progress": "--show-progress",
            "show_memory": "--show-memory",
            "disable_console": "--disable-console",
        }

        for field_name, nuitka_arg in flag_mapping.items():
            if getattr(self, field_name):
                args.append(nuitka_arg)

        return args


presets = {
    "onefile_preset": CompilationSettings(
        onefile=True,
    ),
    "standalone_preset": CompilationSettings(
        standalone=True,
    ),
}


def get_compilation_settings(preset_name: str) -> CompilationSettings:
    return presets.get(preset_name, CompilationSettings())
