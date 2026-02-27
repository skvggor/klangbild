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
from ..config.layouts import get_layout_config
from ..utils.colors import hex_to_rgba, parse_gradient_colors
from ..utils.time import compute_fade_alphas, format_time


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def _lc_int(lc: dict, key: str, default: int) -> int:  # type: ignore[type-arg]
    """Extract an integer value from the layout config dict."""
    val = lc.get(key, default)
    return int(val) if val is not None else default


def fit_text(
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
    ellipsis: str = "\u2026",
) -> str:
    """Truncate *text* so it fits within *max_width* pixels when rendered with *font*.

    If the text already fits, it is returned unchanged.  Otherwise characters
    are removed from the end and the Unicode ellipsis character (U+2026) is
    appended until the result fits.
    """
    bb = font.getbbox(text)
    if int(bb[2] - bb[0]) <= max_width:
        return text

    lo, hi = 0, len(text) - 1
    best = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        candidate = text[:mid] + ellipsis
        bb = font.getbbox(candidate)
        if int(bb[2] - bb[0]) <= max_width:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1

    return text[:best] + ellipsis if best > 0 else ellipsis


def _lerp_color(
    c0: tuple[int, ...], c1: tuple[int, ...], t: float
) -> tuple[int, int, int, int]:
    return (
        int(c0[0] + (c1[0] - c0[0]) * t),
        int(c0[1] + (c1[1] - c0[1]) * t),
        int(c0[2] + (c1[2] - c0[2]) * t),
        int(c0[3] + (c1[3] - c0[3]) * t),
    )


def _make_gradient_image(
    width: int,
    height: int,
    colors: list[tuple[int, ...]],
    direction: str = "horizontal",
) -> Image.Image:
    """Build an RGBA image filled with a linear gradient."""
    img = Image.new("RGBA", (width, height))
    draw = ImageDraw.Draw(img)
    n = len(colors)
    steps = height if direction == "vertical" else width

    for i in range(steps):
        t = i / max(steps - 1, 1)
        if n == 1:
            c = colors[0]
        else:
            seg_size = 1.0 / (n - 1)
            idx = min(int(t / seg_size), n - 2)
            t_local = (t - idx * seg_size) / seg_size
            c = _lerp_color(colors[idx], colors[idx + 1], t_local)
        if direction == "vertical":
            draw.line([(0, i), (width, i)], fill=c)
        else:
            draw.line([(i, 0), (i, height)], fill=c)

    return img


def draw_gradient_text(
    canvas: Image.Image,
    text: str,
    font: ImageFont.FreeTypeFont,
    x: int,
    y: int,
    gradient_colors: list[tuple[int, ...]],
    anchor: str | None = None,
    direction: str = "horizontal",
) -> None:
    """Draw *text* onto *canvas* (RGBA) filled with a gradient.

    The technique:
      1. Render text in white on a transparent RGBA scratch image.
      2. Build a same-size gradient image.
      3. Use the text mask's alpha channel to composite the gradient onto
         the canvas.
    """
    if not gradient_colors:
        return

    bb = font.getbbox(text)
    tw = int(bb[2] - bb[0])
    th = int(bb[3] - bb[1])
    if tw <= 0 or th <= 0:
        return

    if anchor == "center":
        tx = int(x - tw // 2)
        ty = int(y - th // 2)
    elif anchor == "right":
        tx = int(x - tw)
        ty = int(y)
    else:
        tx = int(x)
        ty = int(y)

    # 1. Render white text -> get glyph alpha mask
    text_img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_img)
    text_draw.text((-bb[0], -bb[1]), text, font=font, fill=(255, 255, 255, 255))

    # 2. Build gradient image
    grad_img = _make_gradient_image(tw, th, gradient_colors, direction=direction)

    # 3. Multiply glyph alpha with gradient alpha so fade works correctly.
    #    text_alpha is 0 outside glyphs, 255 inside (from white text render).
    #    grad_alpha carries the fade value from ua().
    #    Final alpha = (glyph_alpha * grad_alpha) / 255
    text_alpha = text_img.split()[3]
    grad_alpha = grad_img.split()[3]
    ta = np.array(text_alpha, dtype=np.uint16)
    ga = np.array(grad_alpha, dtype=np.uint16)
    combined = ((ta * ga + 127) // 255).astype(np.uint8)
    grad_img.putalpha(Image.fromarray(combined, "L"))

    # 4. Paste onto canvas
    canvas.alpha_composite(grad_img, dest=(tx, ty))


# ---------------------------------------------------------------------------
# Waveform drawing: line style
# ---------------------------------------------------------------------------


def _draw_wave_line(
    wave_draw: ImageDraw.ImageDraw,
    samples: np.ndarray,
    lc: dict,  # type: ignore[type-arg]
    wave_color: tuple[int, int, int, int],
    wave_fill: tuple[int, int, int, int],
    centre_color: tuple[int, int, int, int],
    wave_gradient_colors: list[tuple[int, ...]] | None = None,
) -> None:
    """Draw a mirrored-line waveform (the original / classic style)."""
    w_x0 = _lc_int(lc, "wave_x_start", WAVE_X_START)
    w_width = _lc_int(lc, "wave_width", WAVE_WIDTH)
    w_height = _lc_int(lc, "wave_height", WAVE_HEIGHT)
    w_cy = _lc_int(lc, "wave_center_y", WAVE_CENTER_Y)

    n_cols = len(samples)
    xs = np.linspace(w_x0, w_x0 + w_width, n_cols, dtype=int)
    amplitudes = np.clip(samples, -1.0, 1.0)

    peak = np.percentile(np.abs(amplitudes), 99)
    if peak > 0:
        amplitudes = amplitudes / peak * 0.80

    ys = (amplitudes * w_height).astype(int)

    # Filled polygon
    poly_top = [(int(xs[i]), int(w_cy - ys[i])) for i in range(n_cols)]
    poly_bot = [(int(xs[i]), int(w_cy + ys[i])) for i in range(n_cols - 1, -1, -1)]
    wave_draw.polygon(poly_top + poly_bot, fill=wave_fill)

    # Lines
    top_points = [(int(xs[i]), int(w_cy - ys[i])) for i in range(n_cols)]
    bot_points = [(int(xs[i]), int(w_cy + ys[i])) for i in range(n_cols)]
    if len(top_points) > 1:
        wave_draw.line(top_points, fill=wave_color, width=3)
        wave_draw.line(bot_points, fill=wave_color, width=3)


# ---------------------------------------------------------------------------
# Waveform drawing: circular style
# ---------------------------------------------------------------------------


def _draw_wave_circular(
    wave_draw: ImageDraw.ImageDraw,
    samples: np.ndarray,
    lc: dict,  # type: ignore[type-arg]
    wave_color: tuple[int, int, int, int],
    wave_fill: tuple[int, int, int, int],
    centre_color: tuple[int, int, int, int],
    wave_gradient_colors: list[tuple[int, ...]] | None = None,
) -> None:
    """Draw a radial/circular waveform -- bars project outward from a ring.

    When wave_gradient_colors is provided, each bar is coloured according to
    its angular position around the circle.
    """
    cx = _lc_int(lc, "wave_center_x", WIDTH // 2)
    cy = _lc_int(lc, "wave_center_y", WAVE_CENTER_Y)
    max_radius = _lc_int(lc, "circular_radius", 400)
    inner_r = max_radius * 0.35
    max_bar = max_radius * 0.55

    n_bars = min(len(samples), 240)

    indices = np.linspace(0, len(samples) - 1, n_bars, dtype=int)
    bar_amps = np.abs(np.clip(samples[indices], -1.0, 1.0))

    peak = np.percentile(bar_amps, 99)
    if peak > 0:
        bar_amps = bar_amps / peak * 0.90

    # Draw subtle inner circle
    r_int = int(inner_r)
    wave_draw.ellipse(
        [cx - r_int, cy - r_int, cx + r_int, cy + r_int],
        outline=centre_color,
        width=2,
    )

    base_r, base_g, base_b, base_alpha = wave_color

    for i in range(n_bars):
        angle = 2.0 * np.pi * i / n_bars - np.pi / 2
        amp = float(bar_amps[i])
        bar_len = max_bar * amp + 8

        # If gradient: pick bar colour by angular position
        if wave_gradient_colors and len(wave_gradient_colors) >= 2:
            t_bar = i / n_bars
            seg_size = 1.0 / (len(wave_gradient_colors) - 1)
            idx = min(int(t_bar / seg_size), len(wave_gradient_colors) - 2)
            t_local = (t_bar - idx * seg_size) / seg_size
            c0 = wave_gradient_colors[idx]
            c1 = wave_gradient_colors[idx + 1]
            bar_r = int(c0[0] + (c1[0] - c0[0]) * t_local)
            bar_g = int(c0[1] + (c1[1] - c0[1]) * t_local)
            bar_b = int(c0[2] + (c1[2] - c0[2]) * t_local)
        else:
            bar_r, bar_g, bar_b = base_r, base_g, base_b

        n_segments = max(4, int(bar_len / 6))
        for seg in range(n_segments):
            seg_start = inner_r + (bar_len * seg / n_segments)
            seg_end = inner_r + (bar_len * (seg + 1) / n_segments)

            x1 = cx + np.cos(angle) * seg_start
            y1 = cy + np.sin(angle) * seg_start
            x2 = cx + np.cos(angle) * seg_end
            y2 = cy + np.sin(angle) * seg_end

            t = seg / n_segments
            gradient_factor = 1.0 - t * 0.5
            amp_factor = 0.6 + 0.4 * amp
            seg_alpha = int(base_alpha * gradient_factor * amp_factor)
            seg_col = (bar_r, bar_g, bar_b, seg_alpha)

            wave_draw.line(
                [(int(x1), int(y1)), (int(x2), int(y2))],
                fill=seg_col,
                width=5,
            )

        # Dot at tip
        x_outer = cx + np.cos(angle) * (inner_r + bar_len)
        y_outer = cy + np.sin(angle) * (inner_r + bar_len)
        dot_alpha = int(base_alpha * 0.7 * amp)
        dot_col = (bar_r, bar_g, bar_b, dot_alpha)
        dot_r = 4
        ix, iy = int(x_outer), int(y_outer)
        wave_draw.ellipse(
            [ix - dot_r, iy - dot_r, ix + dot_r, iy + dot_r],
            fill=dot_col,
        )


# ---------------------------------------------------------------------------
# Film grain
# ---------------------------------------------------------------------------


def _apply_grain(img: Image.Image, intensity: float, frame_idx: int) -> Image.Image:
    """Overlay film-grain noise on *img* (RGB).

    Uses centred noise (±amplitude) so the overall brightness is preserved.
    Each frame uses a different RNG seed so the grain animates naturally.
    """
    if intensity <= 0:
        return img

    rng = np.random.default_rng(frame_idx)
    arr = np.array(img, dtype=np.int16)

    amplitude = int(round(intensity * 128))
    noise = rng.integers(-amplitude, amplitude + 1, size=arr.shape, dtype=np.int16)

    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


# ---------------------------------------------------------------------------
# Main frame renderer
# ---------------------------------------------------------------------------


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
    text_gradient: str | None = None,
    text_gradient_dir: str = "horizontal",
    wave_gradient: str | None = None,
    wave_gradient_dir: str = "horizontal",
    grain: float = 0.0,
    layout: str = "classic",
    wave_style: str = "line",
    font_title: ImageFont.FreeTypeFont | None = None,
    font_artist: ImageFont.FreeTypeFont | None = None,
    font_album: ImageFont.FreeTypeFont | None = None,
    font_time: ImageFont.FreeTypeFont | None = None,
) -> Image.Image:
    lc = get_layout_config(layout)

    alpha_bg, alpha_wave, alpha_ui = compute_fade_alphas(frame_idx, n_frames, FPS)

    # ---- Background with fade ---------------------------------------------
    black = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    if alpha_bg >= 1.0:
        frame = bg.copy().convert("RGBA")
    else:
        frame = Image.blend(black, bg.convert("RGB"), alpha_bg).convert("RGBA")

    # ---- Wave layer -------------------------------------------------------
    wave_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    wave_draw = ImageDraw.Draw(wave_layer, "RGBA")

    def wa(base: int) -> int:
        return int(base * alpha_wave)

    wave_color = hex_to_rgba(color, wa(204))
    wave_fill = hex_to_rgba(color, wa(50))
    centre_color = hex_to_rgba(color, wa(40))

    # Parse wave gradient colours
    wave_gradient_colors: list[tuple[int, ...]] | None = None
    if wave_gradient:
        wave_gradient_colors = parse_gradient_colors(wave_gradient)

    # Draw waveform with selected style
    if wave_style == "circular":
        _draw_wave_circular(
            wave_draw,
            samples,
            lc,
            wave_color,
            wave_fill,
            centre_color,
            wave_gradient_colors,
        )
    else:
        _draw_wave_line(
            wave_draw,
            samples,
            lc,
            wave_color,
            wave_fill,
            centre_color,
            wave_gradient_colors,
        )

    # Edge fade (horizontal gradient -> infinite-wave illusion)
    # Only apply for line style; circular doesn't need it
    if wave_style == "line":
        wave_arr = np.array(wave_layer, dtype=np.float32)

        # Apply wave colour gradient if requested (pixel-level recolour)
        if wave_gradient_colors and len(wave_gradient_colors) >= 2:
            n = len(wave_gradient_colors)
            if wave_gradient_dir == "horizontal":
                w = wave_arr.shape[1]
                for col in range(w):
                    t = col / max(w - 1, 1)
                    seg_size = 1.0 / (n - 1)
                    idx = min(int(t / seg_size), n - 2)
                    t_local = (t - idx * seg_size) / seg_size
                    c0 = wave_gradient_colors[idx]
                    c1 = wave_gradient_colors[idx + 1]
                    cr = c0[0] + (c1[0] - c0[0]) * t_local
                    cg = c0[1] + (c1[1] - c0[1]) * t_local
                    cb = c0[2] + (c1[2] - c0[2]) * t_local
                    existing_alpha = wave_arr[:, col, 3]
                    wave_arr[:, col, 0] = np.where(
                        existing_alpha > 0, cr, wave_arr[:, col, 0]
                    )
                    wave_arr[:, col, 1] = np.where(
                        existing_alpha > 0, cg, wave_arr[:, col, 1]
                    )
                    wave_arr[:, col, 2] = np.where(
                        existing_alpha > 0, cb, wave_arr[:, col, 2]
                    )
            else:  # vertical
                h = wave_arr.shape[0]
                for row in range(h):
                    t = row / max(h - 1, 1)
                    seg_size = 1.0 / (n - 1)
                    idx = min(int(t / seg_size), n - 2)
                    t_local = (t - idx * seg_size) / seg_size
                    c0 = wave_gradient_colors[idx]
                    c1 = wave_gradient_colors[idx + 1]
                    cr = c0[0] + (c1[0] - c0[0]) * t_local
                    cg = c0[1] + (c1[1] - c0[1]) * t_local
                    cb = c0[2] + (c1[2] - c0[2]) * t_local
                    existing_alpha = wave_arr[row, :, 3]
                    wave_arr[row, :, 0] = np.where(
                        existing_alpha > 0, cr, wave_arr[row, :, 0]
                    )
                    wave_arr[row, :, 1] = np.where(
                        existing_alpha > 0, cg, wave_arr[row, :, 1]
                    )
                    wave_arr[row, :, 2] = np.where(
                        existing_alpha > 0, cb, wave_arr[row, :, 2]
                    )

        fade = np.ones(WIDTH, dtype=np.float32)
        x0 = _lc_int(lc, "wave_x_start", WAVE_X_START)
        x1 = x0 + _lc_int(lc, "wave_width", WAVE_WIDTH)
        fw = _lc_int(lc, "wave_fade_width", WAVE_FADE_WIDTH)
        fade[x0 : x0 + fw] = np.linspace(0.0, 1.0, fw)
        fade[x1 - fw : x1] = np.linspace(1.0, 0.0, fw)
        fade[:x0] = 0.0
        fade[x1:] = 0.0
        wave_arr[:, :, 3] *= fade[np.newaxis, :]
        wave_layer = Image.fromarray(np.clip(wave_arr, 0, 255).astype(np.uint8), "RGBA")

    frame = Image.alpha_composite(frame, wave_layer)

    # ---- UI layer (seek bar + text) ---------------------------------------
    ui_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(ui_layer, "RGBA")

    def ua(base: int) -> int:
        return int(base * alpha_ui)

    text_color = hex_to_rgba(color, ua(255))

    # Seek bar picks a colour from the active gradient for a cohesive look.
    # Prefer text gradient; fall back to wave gradient; else use flat colour.
    _seek_accent: tuple[int, ...] | None = None
    if text_gradient:
        _tg_colors = parse_gradient_colors(text_gradient)
        if _tg_colors:
            _seek_accent = _tg_colors[0]
    if _seek_accent is None and wave_gradient:
        _wg_colors = parse_gradient_colors(wave_gradient)
        if _wg_colors:
            _seek_accent = _wg_colors[0]

    if _seek_accent is not None:
        seek_bg_color = (_seek_accent[0], _seek_accent[1], _seek_accent[2], ua(50))
        seek_fg_color = (_seek_accent[0], _seek_accent[1], _seek_accent[2], ua(220))
        dot_color = (_seek_accent[0], _seek_accent[1], _seek_accent[2], ua(255))
    else:
        seek_bg_color = hex_to_rgba(color, ua(50))
        seek_fg_color = hex_to_rgba(color, ua(220))
        dot_color = hex_to_rgba(color, ua(255))

    # Seek bar
    sb_x = _lc_int(lc, "seek_bar_x", SEEK_BAR_X)
    sb_y = _lc_int(lc, "seek_bar_y", SEEK_BAR_Y)
    sb_w = _lc_int(lc, "seek_bar_w", SEEK_BAR_W)
    sb_h = _lc_int(lc, "seek_bar_h", SEEK_BAR_H)

    progress = frame_idx / max(n_frames - 1, 1)
    filled_w = int(sb_w * progress)

    draw.rectangle([sb_x, sb_y, sb_x + sb_w, sb_y + sb_h], fill=seek_bg_color)
    if filled_w > 0:
        draw.rectangle([sb_x, sb_y, sb_x + filled_w, sb_y + sb_h], fill=seek_fg_color)
    dot_r = max(10, sb_h)
    dot_x = sb_x + filled_w
    dot_y = sb_y + sb_h // 2
    draw.ellipse(
        [dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r],
        fill=dot_color,
    )

    # ---- Text --------------------------------------------------------------
    tx = _lc_int(lc, "text_x", TEXT_X)
    anchor: str | None = lc.get("text_anchor", None)  # type: ignore[assignment]
    max_w = _lc_int(lc, "text_max_width", SEEK_BAR_W)

    # Build fade-adjusted gradient colours (or None for flat colour)
    faded_grad: list[tuple[int, ...]] | None = None
    if text_gradient:
        text_gradient_colors = parse_gradient_colors(text_gradient)
        faded_grad = [(c[0], c[1], c[2], ua(c[3])) for c in text_gradient_colors]

    # Time label
    elapsed = frame_idx / FPS
    time_str = f"{format_time(elapsed)} / {format_time(duration)}"

    text_y_time = _lc_int(lc, "text_y_time", TEXT_Y_TIME)

    if faded_grad:
        draw_gradient_text(
            ui_layer,
            time_str,
            font_time,  # type: ignore[arg-type]
            tx,
            text_y_time,
            faded_grad,
            anchor,
            direction=text_gradient_dir,
        )
    elif anchor == "center":
        draw.text(
            (tx, text_y_time),
            time_str,
            font=font_time,
            fill=text_color,
            anchor="mt",
        )
    elif anchor == "right":
        draw.text(
            (tx, text_y_time),
            time_str,
            font=font_time,
            fill=text_color,
            anchor="rt",
        )
    else:
        draw.text((tx, text_y_time), time_str, font=font_time, fill=text_color)

    # Track info
    text_y_title = _lc_int(lc, "text_y_title", TEXT_Y_TITLE)
    text_y_artist = _lc_int(lc, "text_y_artist", TEXT_Y_ARTIST)
    text_y_album = _lc_int(lc, "text_y_album", TEXT_Y_ALBUM)

    for text, font, y in [
        (
            fit_text(title, font_title, max_w) if font_title else title,  # type: ignore[arg-type]
            font_title,
            text_y_title,
        ),
        (
            fit_text(artist, font_artist, max_w) if font_artist else artist,  # type: ignore[arg-type]
            font_artist,
            text_y_artist,
        ),
        (
            fit_text(album, font_album, max_w) if font_album else album,  # type: ignore[arg-type]
            font_album,
            text_y_album,
        ),
    ]:
        if faded_grad and font is not None:
            draw_gradient_text(
                ui_layer,
                text,
                font,
                tx,
                y,
                faded_grad,
                anchor,
                direction=text_gradient_dir,
            )
        elif anchor == "center":
            draw.text((tx, y), text, font=font, fill=text_color, anchor="mt")
        elif anchor == "right":
            draw.text((tx, y), text, font=font, fill=text_color, anchor="rt")
        else:
            draw.text((tx, y), text, font=font, fill=text_color)

    frame = Image.alpha_composite(frame, ui_layer)

    result = frame.convert("RGB")
    if grain > 0.0:
        result = _apply_grain(result, grain, frame_idx)

    return result
