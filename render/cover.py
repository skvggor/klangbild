from PIL import Image, ImageDraw, ImageFont
from config.constants import WIDTH, HEIGHT
from utils.colors import hex_to_rgba
from utils.fonts import load_font_bold, load_font_regular


def render_cover(
    bg: Image.Image,
    title: str,
    artist: str,
    album: str,
    color: str,
    font_path: str | None = None,
    font_bold_path: str | None = None,
) -> Image.Image:
    font_title = load_font_bold(160, font_bold_path)
    font_artist = load_font_regular(120, font_path)
    font_album = load_font_regular(96, font_path)

    cover = bg.copy().convert("RGBA")
    draw = ImageDraw.Draw(cover, "RGBA")

    text_color = hex_to_rgba(color, 255)
    shadow_color = (0, 0, 0, 180)
    div_color = hex_to_rgba(color, 80)

    cx = WIDTH // 2

    def text_size(text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
        bb = font.getbbox(text)
        return int(bb[2] - bb[0]), int(bb[3] - bb[1])

    tw, th = text_size(title, font_title)
    aw, ah = text_size(artist, font_artist)
    lw, lh = text_size(album, font_album)

    GAP_TITLE_DIV = 40
    DIV_HEIGHT = 4
    DIV_WIDTH = max(tw, aw, lw) + 160
    GAP_DIV_ARTIST = 40
    GAP_ARTIST_ALBUM = 32

    block_h = (
        th + GAP_TITLE_DIV + DIV_HEIGHT + GAP_DIV_ARTIST + ah + GAP_ARTIST_ALBUM + lh
    )

    y = (HEIGHT - block_h) // 2

    def draw_text_centred(text: str, font: ImageFont.FreeTypeFont, y_top: int) -> None:
        w, _ = text_size(text, font)
        x = cx - w // 2
        draw.text((x + 2, y_top + 2), text, font=font, fill=shadow_color)
        draw.text((x, y_top), text, font=font, fill=text_color)

    draw_text_centred(title, font_title, y)
    y += th + GAP_TITLE_DIV

    draw.rectangle(
        [cx - DIV_WIDTH // 2, y, cx + DIV_WIDTH // 2, y + DIV_HEIGHT],
        fill=div_color,
    )
    y += DIV_HEIGHT + GAP_DIV_ARTIST

    draw_text_centred(artist, font_artist, y)
    y += ah + GAP_ARTIST_ALBUM

    draw_text_centred(album, font_album, y)

    return cover.convert("RGB")
