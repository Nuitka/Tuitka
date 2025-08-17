from tuitka.utils import DependencyParser


def test_dependency_parser_no_deps(tmp_path):
    p = tmp_path / "script.py"
    p.write_text("import os\nimport sys\n")
    parser = DependencyParser(p)
    deps = parser.parse()
    assert deps.dependencies == []


def test_dependency_parser_with_pep723_deps(tmp_path):
    p = tmp_path / "script.py"
    p.write_text("# /// script\n# dependencies = [\"requests\", \"textual\"]\n# ///\n\nimport os\nimport sys\nimport requests\nimport textual\n")
    parser = DependencyParser(p)
    deps = parser.parse()
    assert sorted(deps.dependencies) == ["requests", "textual"]


def test_dependency_parser_with_requirements_txt(tmp_path):
    p = tmp_path / "script.py"
    p.write_text("import os\nimport sys\nimport requests\nimport textual\n")
    r = tmp_path / "requirements.txt"
    r.write_text("requests\ntextual\n")
    parser = DependencyParser(p)
    deps = parser.parse()
    assert sorted(deps.dependencies) == ["requests", "textual"]


def test_dependency_parser_with_pyproject_toml(tmp_path):
    p = tmp_path / "script.py"
    p.write_text("import os\nimport sys\nimport requests\nimport textual\n")
    t = tmp_path / "pyproject.toml"
    t.write_text("[project]\n    dependencies = [\"requests\", \"textual\"]\n")
    parser = DependencyParser(p)
    deps = parser.parse()
    assert sorted(deps.dependencies) == ["requests", "textual"]
