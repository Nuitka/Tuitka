import re
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DependenciesMetadata:
    dependencies: list[str]

    def temp_requirements(self) -> Path:
        path = Path("requirements.txt")
        with path.open("w") as f:
            f.writelines("\n".join(self.dependencies))
        return path


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


# All credit due to https://github.com/ftnext/pep723
# ref: https://peps.python.org/pep-0723/#specification
REGEX = r"(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$"


def parse_723(script: str) -> DependenciesMetadata:
    name = "script"
    matches = list(
        filter(lambda m: m.group("type") == name, re.finditer(REGEX, script))
    )
    if not matches:
        return DependenciesMetadata(dependencies=[])  # Changed this line
    if len(matches) > 1:
        raise ValueError(f"Multiple {name} blocks found. You can write only one")
    group = matches[0].groupdict()
    content = "".join(line[2:] for line in group["content"].splitlines(keepends=True))
    return DependenciesMetadata(
        dependencies=tomllib.loads(content).get("dependencies", [])
    )


def parse_requirements_text(requirements: str) -> DependenciesMetadata:
    with open(requirements, "r") as f:
        lines = f.readlines()
    return DependenciesMetadata(
        dependencies=[
            line.strip() for line in lines if line.strip() and not line.startswith("#")
        ]
    )


def parse_pyproject(pyproject: str) -> DependenciesMetadata:
    pyproject_dict = tomllib.loads(pyproject)
    deps = []
    tool = pyproject_dict.get("tool", {})
    poetry_deps = tool.get("poetry", {}).get("dependencies", {})
    if poetry_deps:
        deps += _extract_dependencies_from_table(poetry_deps)
    hatch_deps = tool.get("hatch", {}).get("metadata", {}).get("dependencies", [])
    if hatch_deps:
        deps += [d for d in hatch_deps if isinstance(d, str)]
    project_deps = pyproject_dict.get("project", {}).get("dependencies", [])
    if project_deps:
        deps += [d for d in project_deps if isinstance(d, str)]

    return DependenciesMetadata(dependencies=set(deps))


def parse_dependencies(_path: str | Path) -> DependenciesMetadata:
    path = Path(_path) if isinstance(_path, str) else _path
    if not path or not path.exists():
        return DependenciesMetadata(dependencies=[])
    if path.name == "pyproject.toml":
        with path.open("rb") as f:
            content = f.read()
        return parse_pyproject(content.decode())
    elif path.name == "requirements.txt":
        return parse_requirements_text(str(path))
    else:
        with path.open("r") as f:
            script = f.read()
        metadata = parse_723(script)
        if metadata.dependencies:
            return metadata
    return DependenciesMetadata(dependencies=[])


def prepare_nuitka_command(script_path: Path) -> tuple[list[str], Path]:
    requirements_txt = parse_dependencies(script_path).temp_requirements()
    cmd = [
        "uvx",
        "--isolated",
        "--with-requirements",
        requirements_txt.as_posix(),
        "nuitka",
        "--remove-output",
        "--onefile",
        "--run",
        script_path.as_posix(),
    ]
    return cmd, requirements_txt


__all__ = ["prepare_nuitka_command"]
