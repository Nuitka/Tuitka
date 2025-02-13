DEFAULT_SCRIPT_NAME = "script.py"
ENTRY_POINT_DICT = {
    "nuitka": "nuitka \\",
    "uvx": "uvx --from nuitka nuitka \\",
}

OPTION_TREE: dict[str, list[dict]] = {
    "Control the inclusion of modules and packages in result": [
        {
            "flag": "--include-package",
            "type": "string",
            "default": "",
            # 'type': 'list',
            # 'default': [],
        },
        {
            "flag": "--include-modules",
            "type": "list",
            "default": [],
        },
        {
            "flag": "--prefer-source-code",
            "type": "bool",
            "default": False,
        },
        #
        {
            "flag": "--onefile",
            "type": "bool",
            "default": False,
        },
        {
            "flag": "--run",
            "type": "bool",
            "default": False,
        },
    ],
    "Compilation choices": [
        {
            "flag": "--file-reference-choice",
            "type": "selection",
            "default": "runtime",
            "choices": ["original", "runtime", "frozen"],
        },
    ],
    "Output choices": [
        {
            "flag": "--output-filename",
            "type": "string",
            "default": "",
        },
        {
            "flag": "--output-dir",
            "type": "path",
            "default": "",
        },
        {
            "flag": "--remove-output",
            "type": "bool",
            "default": False,
        },
    ],
}
