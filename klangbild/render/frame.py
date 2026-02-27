import numpy as np
from PIL import Image, ImageDraw, ImageFont
from ..config.constants import (
    WIDTH,
    HEIGHT,
    FPS,
    WAVE_WIDTH,
    WAVE_HEIGHT,
    WAVE_CENTER_Y,
    WAVE_X_START,
    SEEK_BAR_W,
    SEEK_BAR_H,
    SEEK_BAR_X,
    SEEK_BAR_Y,
    TEXT_X,
    TEXT_Y_TIME,
    TEXT_Y_TITLE,
    TEXT_Y_ARTIST,
    TEXT_Y_ALBUM,
    WAVE_FADE_WIDTH,
)
from ..utils.colors import hex_to_rgba
from ..utils.time import compute_fade_alphas, format_time


def render_frame(
    bg: Image.Image,
    samples: np.ndarray,
    frame_idx: int,
    n_frames: int,
    duration: float,
    title: str,
    artist: str,
    album: str,
    color: str,
    font_title: ImageFont.FreeTypeFont,
    font_artist: ImageFont.FreeTypeFont,
    font_album: ImageFont.FreeTypeFont,
    font_time: ImageFont.FreeTypeFont,
) -> Image.Image:
    alpha_bg, alpha_wave, alpha_ui = compute_fade_alphas(frame_idx, n_frames, FPS)

    black = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    if alpha_bg >= 1.0:
        frame = bg.copy().convert("RGBA")
    else:
        frame = Image.blend(black, bg.convert("RGB"), alpha_bg).convert("RGBA")

    wave_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    wave_draw = ImageDraw.Draw(wave_layer, "RGBA")

    def wa(base: int) -> int:
        return int(base * alpha_wave)

    wave_color = hex_to_rgba(color, wa(204))
    wave_fill = hex_to_rgba(color, wa(50))
    centre_color = hex_to_rgba(color, wa(40))

    n_cols = len(samples)
    xs = np.linspace(WAVE_X_START, WAVE_X_START + WAVE_WIDTH, n_cols, dtype=int)
    amplitudes = np.clip(samples, -1.0, 1.0)

    peak = np.percentile(np.abs(amplitudes), 99)
    if peak > 0:
        amplitudes = amplitudes / peak * 0.80

    ys = (amplitudes * WAVE_HEIGHT).astype(int)

    poly_top = [(xs[i], WAVE_CENTER_Y - ys[i]) for i in range(n_cols)]
    poly_bot = [(xs[i], WAVE_CENTER_Y + ys[i]) for i in range(n_cols - 1, -1, -1)]
    wave_draw.polygon(poly_top + poly_bot, fill=wave_fill)

    top_points = [(xs[i], WAVE_CENTER_Y - ys[i]) for i in range(n_cols)]
    bot_points = [(xs[i], WAVE_CENTER_Y + ys[i]) for i in range(n_cols)]
    if len(top_points) > 1:
        wave_draw.line(top_points, fill=wave_color, width=3)
        wave_draw.line(bot_points, fill=wave_color, width=3)

    wave_draw.line(
        [(WAVE_X_START, WAVE_CENTER_Y), (WAVE_X_START + WAVE_WIDTH, WAVE_CENTER_Y)],
        fill=centre_color,
        width=1,
    )

    wave_arr = np.array(wave_layer, dtype=np.float32)
    fade = np.ones(WIDTH, dtype=np.float32)
    x0, x1 = WAVE_X_START, WAVE_X_START + WAVE_WIDTH
    fade[x0 : x0 + WAVE_FADE_WIDTH] = np.linspace(0.0, 1.0, WAVE_FADE_WIDTH)
    fade[x1 - WAVE_FADE_WIDTH : x1] = np.linspace(1.0, 0.0, WAVE_FADE_WIDTH)
    fade[:x0] = 0.0
    fade[x1:] = 0.0
    wave_arr[:, :, 3] *= fade[np.newaxis, :]
    wave_layer = Image.fromarray(np.clip(wave_arr, 0, 255).astype(np.uint8), "RGBA")

    frame = Image.alpha_composite(frame, wave_layer)

    ui_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(ui_layer, "RGBA")

    def ua(base: int) -> int:
        return int(base * alpha_ui)

    text_color = hex_to_rgba(color, ua(255))
    shadow_color = (0, 0, 0, ua(160))
    seek_bg_color = hex_to_rgba(color, ua(50))
    seek_fg_color = hex_to_rgba(color, ua(220))
    dot_color = hex_to_rgba(color, ua(255))

    progress = frame_idx / max(n_frames - 1, 1)
    filled_w = int(SEEK_BAR_W * progress)

    draw.rectangle(
        [SEEK_BAR_X, SEEK_BAR_Y, SEEK_BAR_X + SEEK_BAR_W, SEEK_BAR_Y + SEEK_BAR_H],
        fill=seek_bg_color,
    )
    if filled_w > 0:
        draw.rectangle(
            [SEEK_BAR_X, SEEK_BAR_Y, SEEK_BAR_X + filled_w, SEEK_BAR_Y + SEEK_BAR_H],
            fill=seek_fg_color,
        )
    dot_r = 10
    dot_x = SEEK_BAR_X + filled_w
    dot_y = SEEK_BAR_Y + SEEK_BAR_H // 2
    draw.ellipse(
        [dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r],
        fill=dot_color,
    )

    elapsed = frame_idx / FPS
    time_str = f"{format_time(elapsed)} / {format_time(duration)}"
    draw.text(
        (TEXT_X + 2, TEXT_Y_TIME + 2), time_str, font=font_time, fill=shadow_color
    )
    draw.text((TEXT_X, TEXT_Y_TIME), time_str, font=font_time, fill=text_color)

    for text, font, y in [
        (title, font_title, TEXT_Y_TITLE),
        (artist, font_artist, TEXT_Y_ARTIST),
        (album, font_album, TEXT_Y_ALBUM),
    ]:
        draw.text((TEXT_X + 2, y + 2), text, font=font, fill=shadow_color)
        draw.text((TEXT_X, y), text, font=font, fill=text_color)

    frame = Image.alpha_composite(frame, ui_layer)

    return frame.convert("RGB")
