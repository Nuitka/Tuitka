DEFAULT_SCRIPT_NAME = "script.py"
ENTRY_POINT_DICT = {
    "nuitka": "nuitka \\",
    "uvx": "uvx --from nuitka nuitka \\",
}

INCLUDE_GROUP = {
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
            "flag": "--include-plugin-directory",
            "type": "list",
            "default": [],
        },
        {
            "flag": "--include-plugin-files",
            "type": "list",
            "default": [],
        },
        {
            "flag": "--prefer-source-code",
            "type": "bool",
            "default": False,
        },
    ]
}

FOLLOW_GROUP = {
    "Control the following into imported modules": [
        {
            "flag": "--follow-imports",
            "type": "bool",
            "default": True,  # in standalone
            # "default": False, # else
        },
        {
            "flag": "--follow-import-to",
            "type": "list",
            "default": [],
        },
        {
            "flag": "--nofollow-import-to",
            "type": "list",
            "default": [],
        },
        {
            "flag": "--nofollow-imports",
            "type": "bool",
            "default": False,  # not useable in standalone mode
        },
        {
            "flag": "--follow-stdlib",
            "type": "bool",
            "default": False,
        },
    ]
}

ONEFILE_GROUP = {
    "Onefile options": [
        {
            "flag": "--onefile-tempdir-spec",
            "type": "string",  # path
            "default": "",  # {TEMP}/onefile_{PID}_{TIME}
        },
        {
            "flag": "--onefile-child-grace-time",
            "type": "int",
            "default": 5000,  # ms
        },
        {
            "flag": "--onefile-no-compression",
            "type": "bool",
            "default": False,
        },
        {
            "flag": "--onefile-as-archive",
            "type": "bool",
            "default": False,
        },
    ]
}

DATA_GROUP = {
    "Data files": [
        {
            "flag": "--include-package-data",
            "type": "list",
            "default": [],
        },
        {
            "flag": "--include-data-files",  # --incluce-data-file for single file
            "type": "list",
            "default": [],
        },
        {
            "flag": "--include-data-dir",
            "type": "list",
            "default": [],
        },
        {
            "flag": "--noinclude-data-files",  # --incluce-data-file for single file
            "type": "list",
            "default": [],
        },
        {
            # makes only sense in --onefile
            "flag": "--include-onefile-external-data",  # --incluce-data-files-external
            "type": "list",
            "default": [],
        },
        {
            "flag": "--list-package-data",
            "type": "string",
            "default": "",
        },
        {
            "flag": "--include-raw-dir",
            "type": "list",
            "default": [],
        },
    ]
}

METADATA_GROUP = {
    "Metadata support": [
        {
            "flag": "--include-distribution-metadata",
            "type": "list",
            "default": [],
        },
    ]
}

DLL_GROUP = {
    "DLL files": [
        {
            "flag": "--noinclude-dlls",
            "type": "list",
            "default": [],
        },
        {
            "flag": "--list-package-dlls",
            "type": "list",
            "default": [],
        },
    ]
}

WARNINGS_GROUP = {
    "Control the warnings to be given by Nuitka": [
        {
            "flag": "--warn-implicit-exceptions",
            "type": "bool",
            "default": False,
        },
        {
            "flag": "--warn-unusual-code",
            "type": "bool",
            "default": False,
        },
        {
            "flag": "--assume-yes-for-downloads",
            "type": "bool",
            "default": False,  # will prompt
        },
        {
            "flag": "--nowarn-mnemonic",
            "type": "list",
            "default": [],
        },
    ]
}

EXECUTE_GROUP = {
    "Compilation choices": [
        {
            "flag": "--user-package-configuration-file",
            "type": "list",
            "default": [],
        },
        # Test Only: Should not be used
        # {
        #     "flag": "--full-compat",
        #     "type": "bool",
        #     "default": True,
        # },
        {
            "flag": "--file-reference-choice",
            "type": "selection",
            "default": "runtime",  # default for standalone binary and module mode
            "choices": ["original", "runtime", "frozen"],
        },
        {
            "flag": "--module-name-choice",
            "type": "selection",
            "default": "runtime",  # default for module mode, else runtime
            "choices": ["original", "runtime"],
        },
    ]
}

OUTPUT_GROUP = {
    "Output choices": [
        {
            "flag": "--output-filename",
            "type": "string",
            "default": "",  # programm_name.exe on win32orposixwindows else .bin
        },
        {
            "flag": "--output-dir",
            "type": "string",  # path
            "default": "",  # default CWD
        },
        {
            "flag": "--remove-output",
            "type": "bool",
            "default": False,
        },
        {
            "flag": "--no-pyi-file",
            "type": "bool",
            "default": True,
        },
        {
            "flag": "--no-pyi-stubs",
            "type": "bool",
            "default": True,
        },
    ]
}

DEPLOYMENT_GROUP = {
    "Deployment control": [
        {
            "flag": "--deployment",
            "type": "bool",
            "default": False,
        },
        {
            "flag": "--no-deployment-flag",
            "type": "list",
            "default": [],
        },
    ]
}

ENVIRONMENT_GROUP = {
    "Deployment control": [
        {
            "flag": "--force-runtime-environment-variable",
            "type": "list",
            "default": [],
        },
    ]
}

DEBUG_GROUP = {
    "Debug features": [
        {
            "flag": "--debug",
            "type": "bool",
            "default": False,
        },
        {
            "flag": "--no-debug-immortal-assumptions",
            "type": "bool",
            "default": True,
        },
        # {
        #     "flag": "--debug-immortal-assumption",
        #     "type": "bool",
        #     "default": False,
        # },
        {
            "flag": "--unstripped",
            "type": "bool",
            "default": False,
        },
        {
            "flag": "--profile",
            "type": "bool",
            "default": False,
        },
        {
            "flag": "--trace-execution",
            "type": "bool",
            "default": False,
        },
        {
            "flag": "--xml",
            "type": "string",
            "default": "",
        },
        {
            "flag": "--experimental",
            "type": "list",
            "default": [],
        },
        {
            "flag": "--explain-imports",
            "type": "bool",
            "default": False,
        },
        {
            "flag": "--low-memory",
            "type": "bool",
            "default": False,
        },
        {
            "flag": "--create-environment-from-report",
            "type": "string",
            "default": "",
        },
        {
            "flag": "--generate-c-only",
            "type": "bool",
            "default": False,
        },
    ]
}

DEVELOPMENT_GROUP = {
    "Nuitka development features": [
        {
            "flag": "--devel-missing-code-helpers",
            "type": "bool",
            "default": False,
        },
        {
            "flag": "--devel-missing-trust",
            "type": "bool",
            "default": False,
        },
        {
            "flag": "--devel-recompile-c-only",
            "type": "bool",
            "default": False,
        },
        {
            "flag": "--devel-internal-graph",
            "type": "bool",
            "default": False,
        },
        {
            "flag": "--devel-generate-ming64-header",
            "type": "bool",
            "default": False,
        },
    ]
}
# https://github.com/Nuitka/Nuitka/blob/develop/nuitka/OptionParsing.py#L1043

OPTION_TREE: dict[str, list] = (
    INCLUDE_GROUP
    | FOLLOW_GROUP
    | ONEFILE_GROUP
    | DATA_GROUP
    | METADATA_GROUP
    | DLL_GROUP
    | WARNINGS_GROUP
    | EXECUTE_GROUP
    | OUTPUT_GROUP
    | DEPLOYMENT_GROUP
    | ENVIRONMENT_GROUP
    | DEBUG_GROUP
    | DEVELOPMENT_GROUP
)
