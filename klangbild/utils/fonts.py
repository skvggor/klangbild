import os
from PIL import ImageFont


def load_font_bold(size: int, custom_path: str | None = None) -> ImageFont.FreeTypeFont:
    if custom_path:
        if not os.path.exists(custom_path):
            raise RuntimeError(f"Font file not found: {custom_path}")
        return ImageFont.truetype(custom_path, size)
    candidates = [
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    raise RuntimeError(
        "No suitable bold font found. Install dejavu-fonts or liberation-fonts."
    )


def load_font_regular(
    size: int, custom_path: str | None = None
) -> ImageFont.FreeTypeFont:
    if custom_path:
        if not os.path.exists(custom_path):
            raise RuntimeError(f"Font file not found: {custom_path}")
        return ImageFont.truetype(custom_path, size)
    candidates = [
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    raise RuntimeError(
        "No suitable font found. Install dejavu-fonts or liberation-fonts."
    )
