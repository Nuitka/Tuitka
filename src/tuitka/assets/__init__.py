from pathlib import Path


def get_asset_path(asset_name: str) -> Path:
    assets_dir = Path(__file__).parent
    return assets_dir / asset_name


STYLE_MAIN = get_asset_path("style.tcss")
STYLE_MODAL_FILEDIALOG = get_asset_path("style_modal_filedialog.tcss")
STYLE_MODAL_COMPILATION = get_asset_path("style_modal_compilation.tcss")
STYLE_MODAL_SETTINGS = get_asset_path("style_modal_settings.tcss")
STYLE_MODAL_SPLASHSCREEN = get_asset_path("style_modal_splashscreen.tcss")
STYLE_MODAL_SUPPORT = get_asset_path("style_modal_support.tcss")

CONTENT_SUPPORT_NUITKA = get_asset_path("content/support_nuitka.md").read_text()
CONTENT_COMMERCIAL = get_asset_path("content/commercial.md").read_text()

__all__ = [
    "get_asset_path",
    "STYLE_MAIN",
    "STYLE_MODAL_FILEDIALOG",
    "STYLE_MODAL_COMPILATION",
    "STYLE_MODAL_SETTINGS",
    "STYLE_MODAL_SPLASHSCREEN",
    "STYLE_MODAL_SUPPORT",
    "CONTENT_SUPPORT_NUITKA",
    "CONTENT_COMMERCIAL",
]
