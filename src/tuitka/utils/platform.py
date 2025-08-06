import sys
import platform


def is_windows() -> bool:
    return platform.system() == "Windows"


def is_unix() -> bool:
    return not is_windows()


def get_default_python_version() -> str:
    """Get the appropriate Python version for compilation."""
    if is_windows():  # Nuitka does not support 3.13 too well yet
        if (sys.version_info.major, sys.version_info.minor) > (3, 12):
            return "3.12"
        else:
            return f"{sys.version_info.major}.{sys.version_info.minor}"
    else:
        return f"{sys.version_info.major}.{sys.version_info.minor}"


PYTHON_VERSION = get_default_python_version()
