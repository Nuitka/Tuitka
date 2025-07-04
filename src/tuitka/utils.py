import re
import toml
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import sys
import platform

platform_name = platform.system().lower()


@dataclass
class DependenciesMetadata:
    dependencies: list[str]
    requirements_path: Optional[Path] = (
        None  # Path to the source file where dependencies were parsed from
    )

    def to_pep_723(self) -> str:
        script_metadata = {"dependencies": self.dependencies}
        toml_content = toml.dumps(script_metadata)
        lines = ["# /// script"]
        lines.extend(f"# {line}" for line in toml_content.strip().splitlines())
        lines.append("# ///")
        return "\n".join(lines)

    @contextmanager
    def temp_pep_723_file(self, file_path: Path):
        original_content = file_path.read_text(encoding="utf-8")
        try:
            pep_723_block = self.to_pep_723()
            new_content = f"{pep_723_block}\n\n{original_content}"
            file_path.write_text(new_content, encoding="utf-8")
            yield file_path
        finally:
            file_path.write_text(original_content, encoding="utf-8")


def _extract_dependencies_from_table(dep_table: dict) -> list[str]:
    deps = []
    for name, value in dep_table.items():
        if name == "python":
            continue
        if isinstance(value, str):
            deps.append(
                f"{name}{value if value.startswith('[') else '==' + value.lstrip('=<>!~ ')}"
            )
        elif isinstance(value, dict):
            version = value.get("version")
            extras = value.get("extras")
            dep_str = name
            if extras and isinstance(extras, list):
                dep_str += "[{}]".format(",".join(extras))
            if version:
                dep_str += f"=={version.lstrip('=<>!~ ')}"
            deps.append(dep_str)
        else:
            deps.append(str(name))
    return deps


class DependencyParser:
    # All credit due to https://github.com/ftnext/pep723
    # ref: https://peps.python.org/pep-0723/#specification
    PEP_723_REGEX = (
        r"(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$"
    )

    def __init__(self, path: Path):
        self.path = path

    def _parse_pep_723(self, script: str) -> list[str]:
        name = "script"
        matches = list(
            filter(
                lambda m: m.group("type") == name,
                re.finditer(self.PEP_723_REGEX, script),
            )
        )
        if not matches:
            return []
        if len(matches) > 1:
            raise ValueError(f"Multiple {name} blocks found. You can write only one")
        group = matches[0].groupdict()
        content = "".join(
            line[2:] for line in group["content"].splitlines(keepends=True)
        )
        return toml.loads(content).get("dependencies", [])

    def _parse_requirements_txt(self, requirements_path: Path) -> list[str]:
        lines = requirements_path.read_text(encoding="utf-8").splitlines()
        return [
            line.strip() for line in lines if line.strip() and not line.startswith("#")
        ]

    def _parse_pyproject_toml(self, pyproject_path: Path) -> list[str]:
        content = pyproject_path.read_text(encoding="utf-8")
        pyproject_dict = toml.loads(content)
        deps = []
        tool = pyproject_dict.get("tool", {})

        # Poetry dependencies
        poetry_deps = tool.get("poetry", {}).get("dependencies", {})
        if poetry_deps:
            deps += _extract_dependencies_from_table(poetry_deps)

        # Hatch dependencies
        hatch_deps = tool.get("hatch", {}).get("metadata", {}).get("dependencies", [])
        if hatch_deps:
            deps += [d for d in hatch_deps if isinstance(d, str)]

        # PEP 621 project dependencies
        project_deps = pyproject_dict.get("project", {}).get("dependencies", [])
        if project_deps:
            deps += [d for d in project_deps if isinstance(d, str)]

        return list(set(deps))

    def _find_project_root(self) -> Optional[Path]:
        start_dir = self.path.parent if self.path.is_file() else self.path
        current_path = start_dir.resolve()
        root = Path(current_path.anchor)

        temp_path = current_path
        while True:
            if (
                (temp_path / "pyproject.toml").exists()
                or (temp_path / ".git").exists()
                or (temp_path / "requirements.txt").exists()
            ):
                return temp_path
            if temp_path == root:
                break
            temp_path = temp_path.parent
        return None

    def parse(self) -> DependenciesMetadata:
        if not self.path or not self.path.exists():
            return DependenciesMetadata(dependencies=[], requirements_path=None)

        # Check for PEP 723 dependencies in Python scripts
        if self.path.is_file() and self.path.suffix == ".py":
            script = self.path.read_text(encoding="utf-8")
            dependencies = self._parse_pep_723(script)
            if dependencies:
                return DependenciesMetadata(
                    dependencies=dependencies, requirements_path=self.path
                )

        # Find project root and search for dependency files
        project_root = self._find_project_root()
        search_dir = project_root or (
            self.path.parent if self.path.is_file() else self.path
        )

        # Try pyproject.toml first
        pyproject_candidate = search_dir / "pyproject.toml"
        if pyproject_candidate.exists():
            dependencies = self._parse_pyproject_toml(pyproject_candidate)
            return DependenciesMetadata(
                dependencies=dependencies, requirements_path=pyproject_candidate
            )

        # Fallback to requirements.txt
        requirements_candidate = search_dir / "requirements.txt"
        if requirements_candidate.exists():
            dependencies = self._parse_requirements_txt(requirements_candidate)
            return DependenciesMetadata(
                dependencies=dependencies, requirements_path=requirements_candidate
            )

        return DependenciesMetadata(dependencies=[], requirements_path=None)


def parse_dependencies(_path: str | Path) -> DependenciesMetadata:
    path = Path(_path) if isinstance(_path, str) else _path
    parser = DependencyParser(path)
    return parser.parse()


def prepare_nuitka_command(
    script_path: Path, python_version: str = "3.11", **nuitka_options
) -> tuple[list[str], DependenciesMetadata]:
    dependencies_metadata = parse_dependencies(script_path)

    cmd = [
        "uv",
        "--python-preference",
        "system",
        "run",
        "--python",
        python_version,
        "--isolated",
        "--with",
        "nuitka",
        "nuitka",
    ]

    for flag, value in nuitka_options.items():
        if value is None:
            continue
        if isinstance(value, bool) and value:
            cmd.append(flag)
        elif isinstance(value, str) and value.strip():
            cmd.append(f"{flag}={value.strip()}")
        elif isinstance(value, (list, tuple)) and value:
            for item in value:
                if isinstance(item, str) and item.strip():
                    cmd.append(f"{flag}={item.strip()}")

    cmd.append(script_path.as_posix())

    return cmd, dependencies_metadata


def create_nuitka_options_dict() -> dict[str, dict[str, dict]]:
    from collections import OrderedDict

    sys.argv.append("--help-all")
    from nuitka.OptionParsing import parser
    from nuitka.plugins.Plugins import addStandardPluginCommandLineOptions

    addStandardPluginCommandLineOptions(parser=parser, plugin_help_mode=True)
    del sys.argv[-1]

    options_dict = OrderedDict()

    if hasattr(parser, "option_list") and parser.option_list:
        general_options = OrderedDict()
        for option in parser.option_list:
            option_names = option._short_opts + option._long_opts
            option_data = {
                "names": option_names,
                "help": option.help,
                "default": getattr(option, "default", None),
                "type": getattr(option, "type", None),
                "choices": getattr(option, "choices", None),
                "dest": getattr(option, "dest", None),
                "action": getattr(option, "action", None),
                "metavar": getattr(option, "metavar", None),
            }

            primary_name = next(
                (name for name in option_names if name.startswith("--")),
                option_names[0] if option_names else str(option),
            )
            general_options[primary_name] = option_data

        if general_options:
            options_dict["General Options"] = general_options

    for group in parser.option_groups:
        group_name = group.title
        group_options = OrderedDict()

        for option in group.option_list:
            option_names = option._short_opts + option._long_opts
            option_data = {
                "names": option_names,
                "help": option.help,
                "default": getattr(option, "default", None),
                "type": getattr(option, "type", None),
                "choices": getattr(option, "choices", None),
                "dest": getattr(option, "dest", None),
                "action": getattr(option, "action", None),
                "metavar": getattr(option, "metavar", None),
            }

            primary_name = next(
                (name for name in option_names if name.startswith("--")),
                option_names[0] if option_names else str(option),
            )
            group_options[primary_name] = option_data

        options_dict[group_name] = group_options

    return options_dict


__all__ = [
    "prepare_nuitka_command",
    "create_nuitka_options_dict",
    "DependenciesMetadata",
]


if __name__ == "__main__":
    import json
    from rich import print

    options_dict = create_nuitka_options_dict()
    print(json.dumps(options_dict, indent=4, default=str))
