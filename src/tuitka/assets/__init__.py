from pathlib import Path


def get_asset_path(asset_name: str) -> Path:
    assets_dir = Path(__file__).parent
    return assets_dir / asset_name


STYLE_MAIN = get_asset_path("style.tcss")
STYLE_MODAL_FILEDIALOG = get_asset_path("style_modal_filedialog.tcss")
STYLE_MODAL_COMPILATION = get_asset_path("style_modal_compilation.tcss")

__all__ = [
    "get_asset_path",
    "STYLE_MAIN",
    "STYLE_MODAL_FILEDIALOG",
    "STYLE_MODAL_COMPILATION",
]
