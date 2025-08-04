from pathlib import Path


def get_asset_path(asset_name: str) -> Path:
    assets_dir = Path(__file__).parent
    return assets_dir / asset_name


STYLE_MAIN = get_asset_path("style.tcss")
STYLE_INLINE_APP = get_asset_path("style_inline_app.tcss")
STYLE_MODAL_FILEDIALOG = get_asset_path("style_modal_filedialog.tcss")
STYLE_MODAL_COMPILATION = get_asset_path("style_modal_compilation.tcss")
STYLE_MODAL_SETTINGS = get_asset_path("style_modal_settings.tcss")
STYLE_MODAL_SPLASHSCREEN = get_asset_path("style_modal_splashscreen.tcss")
STYLE_MODAL_SUPPORT = get_asset_path("style_modal_support.tcss")

NUITKA_LOGO = get_asset_path("logo/nuitka.png")

CONTENT_SUPPORT_NUITKA = get_asset_path("content/support_nuitka.md").read_text(
    encoding="utf-8"
)
CONTENT_COMMERCIAL = get_asset_path("content/commercial.md").read_text(encoding="utf-8")

__all__ = [
    "get_asset_path",
    "STYLE_MAIN",
    "STYLE_INLINE_APP",
    "STYLE_MODAL_FILEDIALOG",
    "STYLE_MODAL_COMPILATION",
    "STYLE_MODAL_SETTINGS",
    "STYLE_MODAL_SPLASHSCREEN",
    "STYLE_MODAL_SUPPORT",
    "NUITKA_LOGO",
    "CONTENT_SUPPORT_NUITKA",
    "CONTENT_COMMERCIAL",
]
