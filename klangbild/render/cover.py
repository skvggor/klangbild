from PIL import Image, ImageDraw, ImageFont
from ..config.constants import WIDTH, HEIGHT
from ..utils.colors import hex_to_rgba, parse_gradient_colors
from ..utils.fonts import load_font_bold, load_font_regular
from .frame import draw_gradient_text, fit_text, _apply_grain


def render_cover(
    bg: Image.Image,
    title: str,
    artist: str,
    album: str,
    color: str,
    font_path: str | None = None,
    font_bold_path: str | None = None,
    text_gradient: str | None = None,
    text_gradient_dir: str = "horizontal",
    grain: float = 0.0,
) -> Image.Image:
    """Render a 4K cover image: same background, text centred and larger.

    Layout (top -> bottom, all centred horizontally):
        title  (bold, 160px)
        artist (regular, 120px)
        album  (regular, 96px)
    """
    font_title = load_font_bold(160, font_bold_path)
    font_artist = load_font_regular(120, font_path)
    font_album = load_font_regular(96, font_path)

    _cover_margin = 200
    _cover_max_w = WIDTH - 2 * _cover_margin

    # Truncate texts that would exceed the available width
    title = fit_text(title, font_title, _cover_max_w)
    artist = fit_text(artist, font_artist, _cover_max_w)
    album = fit_text(album, font_album, _cover_max_w)

    cover = bg.copy().convert("RGBA")
    draw = ImageDraw.Draw(cover, "RGBA")

    text_color = hex_to_rgba(color, 255)

    cx = WIDTH // 2

    def text_size(text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
        bb = font.getbbox(text)
        return int(bb[2] - bb[0]), int(bb[3] - bb[1])

    tw, th = text_size(title, font_title)
    _aw, ah = text_size(artist, font_artist)
    _lw, lh = text_size(album, font_album)

    GAP_TITLE_ARTIST = 80
    GAP_ARTIST_ALBUM = 60

    block_h = th + GAP_TITLE_ARTIST + ah + GAP_ARTIST_ALBUM + lh

    y = (HEIGHT - block_h) // 2

    text_gradient_colors: list[tuple[int, ...]] | None = None
    if text_gradient:
        text_gradient_colors = parse_gradient_colors(text_gradient)

    if text_gradient_colors:
        for txt, font, y_pos in [
            (title, font_title, y),
            (artist, font_artist, y + th + GAP_TITLE_ARTIST),
            (album, font_album, y + th + GAP_TITLE_ARTIST + ah + GAP_ARTIST_ALBUM),
        ]:
            w, _ = text_size(txt, font)
            x = cx - w // 2
            draw_gradient_text(
                cover,
                txt,
                font,
                x,
                y_pos,
                text_gradient_colors,
                anchor=None,
                direction=text_gradient_dir,
            )
    else:

        def draw_text_centred(
            text: str, font: ImageFont.FreeTypeFont, y_top: int
        ) -> None:
            w, _ = text_size(text, font)
            x = cx - w // 2
            draw.text((x, y_top), text, font=font, fill=text_color)

        draw_text_centred(title, font_title, y)
        y += th + GAP_TITLE_ARTIST
        draw_text_centred(artist, font_artist, y)
        y += ah + GAP_ARTIST_ALBUM
        draw_text_centred(album, font_album, y)

    result = cover.convert("RGB")
    if grain > 0.0:
        result = _apply_grain(result, grain, 0)

    return result
