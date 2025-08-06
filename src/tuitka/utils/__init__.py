# Re-export for backward compatibility
from tuitka.utils.platform import is_windows  # noqa
from tuitka.utils.nuitka import (  # noqa
    prepare_nuitka_command,
    create_nuitka_options_dict,
    DependenciesMetadata,
)

__all__ = [
    "prepare_nuitka_command",
    "create_nuitka_options_dict",
    "DependenciesMetadata",
    "is_windows",
]
