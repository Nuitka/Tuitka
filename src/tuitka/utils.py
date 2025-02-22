import shutil


def is_nuitka_installed():
    if shutil.which("nuitka") is None:
        return False
    return True


def is_uvx_installed():
    if shutil.which("uvx") is None:
        return False
    return True


def get_entrypoint():
    if is_nuitka_installed():
        return "nuitka"
    if is_uvx_installed():
        return "uvx"
