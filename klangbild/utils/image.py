from PIL import Image
from ..config.constants import WIDTH, HEIGHT, BG_DARKEN_ALPHA


def prepare_background(image_path: str) -> Image.Image:
    print("Preparing background...")
    bg = Image.open(image_path).convert("RGB")

    bg_ratio = bg.width / bg.height
    target_ratio = WIDTH / HEIGHT

    if bg_ratio > target_ratio:
        new_h = HEIGHT
        new_w = int(HEIGHT * bg_ratio)
    else:
        new_w = WIDTH
        new_h = int(WIDTH / bg_ratio)

    bg = bg.resize((new_w, new_h), Image.Resampling.LANCZOS)

    left = (new_w - WIDTH) // 2
    top = (new_h - HEIGHT) // 2
    bg = bg.crop((left, top, left + WIDTH, top + HEIGHT))

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, BG_DARKEN_ALPHA))
    bg = bg.convert("RGBA")
    bg = Image.alpha_composite(bg, overlay).convert("RGB")

    return bg
