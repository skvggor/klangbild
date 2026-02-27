#!/usr/bin/env python3
"""
Audio Visualizer - Generates a 4K MP4 video with waveform visualization.

Single-file mode:
    uv run python3 visualizer.py \
        --audio "minha_musica.mp3" \
        --background "capa.jpg" \
        --title "Nome da Música" \
        --artist "Nome do Artista" \
        --album "Nome do Álbum" \
        --color "#FFFFFF" \
        --gpu nvenc \
        --workers 30 \
        --font "regular.ttf" \
        --font-bold "bold.ttf" \
        --output "visualizer.mp4"

Batch mode (processes all MP3s in a folder):
    uv run python3 visualizer.py \
        --input-dir "/path/to/mp3s" \
        --background "capa.jpg" \
        --color "#FFFFFF" \
        --gpu nvenc \
        --workers 30

    In batch mode title/artist/album are read from each file's ID3 tags.
    Each MP3 produces a .mp4 and .jpg in the same folder.

Outputs:
    visualizer.mp4  — 4K video with audio visualizer
    visualizer.jpg  — 4K cover image

GPU options for --gpu:
    none   CPU libx264 (default, works everywhere)
    nvenc  NVIDIA GPU
    vaapi  Intel/AMD via VA-API

Layout options for --layout:
    classic      Original layout (default)
    spotlight    Large centred text + big seek bar above + waves below
    split-left   Waves on the left, text on the right, full-width seek below
    split-right  Text on the left, waves on the right, full-width seek below

Wave style options for --wave-style:
    line      Mirrored waveform lines (default)
    circular  Radial/circular waveform (bars projected from a circle)

Gradient options (at least 2 comma-separated #RGB or #RRGGBB colors):
    --text-gradient "#FF0000,#0000FF"
        Vertical gradient applied to all text (title, artist, album, time).
        Overrides --color for text when provided.

    --wave-gradient "#FF0000,#0000FF"
        Gradient applied to the waveform.
        line style:     vertical gradient (top → bottom)
        circular style: angular gradient (bars cycle through colors)
        Overrides --color for the waveform when provided.

    Both flags are independent and can be combined:
        --text-gradient "#FF0000,#FFFFFF,#0000FF" --wave-gradient "#00FF00,#FF00FF"

--workers:        parallel CPU workers for frame rendering (default: cpu_count - 2)
--font:           .ttf/.otf for regular text (artist, album, time)
--font-bold:      .ttf/.otf for bold text (title)
                  if omitted, system DejaVu/Liberation fonts are used
"""

import argparse
import subprocess
import sys
import os
import queue
import threading
import multiprocessing as mp
from pathlib import Path

import librosa
import numpy as np
from mutagen.id3 import ID3
from mutagen._util import MutagenError
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WIDTH = 3840
HEIGHT = 2160
FPS = 30

# Waveform: small and centered (~300x50 visual equivalent scaled to 4K)
# At 4K: 300px wide in 1080p = 1200px; 50px tall (half) in 1080p = 100px
WAVE_WIDTH = 1800  # horizontal span in pixels
WAVE_HEIGHT = 150  # max amplitude in pixels (half-side, mirrored)
WAVE_CENTER_Y = HEIGHT // 2
WAVE_X_START = (WIDTH - WAVE_WIDTH) // 2

# Seek bar — anchored near the very bottom
SEEK_BAR_H = 6
SEEK_BAR_Y = HEIGHT - 120
SEEK_BAR_X = (WIDTH - WAVE_WIDTH) // 2
SEEK_BAR_W = WAVE_WIDTH

# Text area (bottom-left, aligned with seek bar)
TEXT_X = SEEK_BAR_X
# Time label sits above seek bar with comfortable breathing room
TIME_MARGIN = 20  # gap between time text bottom and seek bar top
TEXT_Y_TIME = SEEK_BAR_Y - 40 - TIME_MARGIN  # 40 ≈ font height at 40px
# Track info stacks upward from the time label
TEXT_Y_ALBUM = TEXT_Y_TIME - 65
TEXT_Y_ARTIST = TEXT_Y_ALBUM - 65
TEXT_Y_TITLE = TEXT_Y_ARTIST - 95


# ---------------------------------------------------------------------------
# Layout configurations
# ---------------------------------------------------------------------------
# Each layout returns a dict with all the geometry needed by render_frame.
# Keys: wave_width, wave_height, wave_center_x, wave_center_y,
#       wave_x_start, seek_bar_x, seek_bar_y, seek_bar_w, seek_bar_h,
#       text_x, text_y_title, text_y_artist, text_y_album, text_y_time,
#       font_size_title, font_size_artist, font_size_album, font_size_time,
#       text_anchor (None = left, "center" = centred)
#       wave_fade_width


def get_layout_config(layout: str) -> dict:
    """Return geometry constants for the given layout name."""

    if layout == "spotlight":
        # Large centred text, big seek bar above text, waveform below centre
        # Generous margins between all elements
        _seek_h = 10
        _seek_w = 2800
        _seek_x = (WIDTH - _seek_w) // 2
        _seek_y = HEIGHT // 2 - 400  # more margin above text block

        # Text block: centred, large fonts, with spacing between each line
        _text_x = WIDTH // 2
        _text_y_title = HEIGHT // 2 - 100
        _text_y_artist = _text_y_title + 180  # more gap
        _text_y_album = _text_y_artist + 140  # more gap
        _text_y_time = _text_y_album + 140  # more gap

        # Waveform: wide, below the text block with generous margin
        _wave_w = 2800
        _wave_h = 200
        _wave_cx = WIDTH // 2
        _wave_cy = _text_y_time + 400  # more margin below time for circular
        _wave_x_start = (WIDTH - _wave_w) // 2

        return dict(
            wave_width=_wave_w,
            wave_height=_wave_h,
            wave_center_x=_wave_cx,
            wave_center_y=_wave_cy,
            wave_x_start=_wave_x_start,
            seek_bar_x=_seek_x,
            seek_bar_y=_seek_y,
            seek_bar_w=_seek_w,
            seek_bar_h=_seek_h,
            text_x=_text_x,
            text_y_title=_text_y_title,
            text_y_artist=_text_y_artist,
            text_y_album=_text_y_album,
            text_y_time=_text_y_time,
            font_size_title=120,
            font_size_artist=80,
            font_size_album=64,
            font_size_time=56,
            text_anchor="center",
            wave_fade_width=220,
            circular_radius=450,  # fits below text block
        )

    if layout in ("split-left", "split-right"):
        # Two-column layout within a 2500px central area
        # Structure: gap | coluna | gap | coluna | gap
        _central_area = 2500
        _gap = 80  # gap between columns and edges
        # Each column = (central_area - 3 * gap) / 2
        _col_w = (_central_area - 3 * _gap) // 2

        _central_start = (WIDTH - _central_area) // 2

        # Waveform column: centred vertically
        _wave_h = 280
        _wave_cy = HEIGHT // 2

        if layout == "split-left":
            # Wave on left column, text on right
            _wave_col_start = _central_start + _gap
            _wave_col_end = _wave_col_start + _col_w
            _wave_cx = _wave_col_start + _col_w // 2
            _wave_x_start = _wave_col_start

            # Text column (right)
            _text_col_start = _wave_col_end + _gap
            _text_x = _text_col_start  # left-aligned in text column
            _text_anchor = None  # left-aligned
        else:
            # Text on left column, wave on right
            _text_col_start = _central_start + _gap
            _text_x = _text_col_start + _col_w  # right-aligned at end of text column
            _text_anchor = "right"

            # Wave column (right)
            _wave_col_start = _text_col_start + _col_w + _gap
            _wave_cx = _wave_col_start + _col_w // 2
            _wave_x_start = _wave_col_start

        _wave_w = _col_w

        # Text: vertically centred as a block
        _block_h = 120 + 90 + 80 + 70  # title + artist + album + time heights approx
        _text_y_title = HEIGHT // 2 - _block_h // 2
        _text_y_artist = _text_y_title + 140
        _text_y_album = _text_y_artist + 110
        _text_y_time = _text_y_album + 100

        # Seek bar: full-width below both columns
        _margin = 160
        _seek_h = 10
        _seek_w = WIDTH - 2 * _margin
        _seek_x = _margin
        _seek_y = HEIGHT - 160

        return dict(
            wave_width=_wave_w,
            wave_height=_wave_h,
            wave_center_x=_wave_cx,
            wave_center_y=_wave_cy,
            wave_x_start=_wave_x_start,
            seek_bar_x=_seek_x,
            seek_bar_y=_seek_y,
            seek_bar_w=_seek_w,
            seek_bar_h=_seek_h,
            text_x=_text_x,
            text_y_title=_text_y_title,
            text_y_artist=_text_y_artist,
            text_y_album=_text_y_album,
            text_y_time=_text_y_time,
            font_size_title=100,
            font_size_artist=72,
            font_size_album=60,
            font_size_time=52,
            text_anchor=_text_anchor,
            wave_fade_width=140,
            circular_radius=450,  # fits within column
        )

    # classic (default) — original layout
    return dict(
        wave_width=WAVE_WIDTH,
        wave_height=WAVE_HEIGHT,
        wave_center_x=WIDTH // 2,
        wave_center_y=WAVE_CENTER_Y,
        wave_x_start=WAVE_X_START,
        seek_bar_x=SEEK_BAR_X,
        seek_bar_y=SEEK_BAR_Y,
        seek_bar_w=SEEK_BAR_W,
        seek_bar_h=SEEK_BAR_H,
        text_x=TEXT_X,
        text_y_title=TEXT_Y_TITLE,
        text_y_artist=TEXT_Y_ARTIST,
        text_y_album=TEXT_Y_ALBUM,
        text_y_time=TEXT_Y_TIME,
        font_size_title=80,
        font_size_artist=60,
        font_size_album=50,
        font_size_time=40,
        text_anchor=None,
        wave_fade_width=WAVE_FADE_WIDTH,
        circular_radius=500,  # large circle for classic
    )


# Waveform smoothing
SMOOTHING_WINDOW = 15  # spatial: moving-average window along the X axis of each frame
#   larger = smoother shape per frame (was 7)

TEMPORAL_ALPHA = 0.35  # temporal EMA between consecutive frames
#   0.0 = frozen (never updates), 1.0 = no temporal smoothing
#   0.3–0.5 gives fluid motion; lower = more lag, higher = more jitter

# Waveform edge fade — number of pixels over which the wave fades to transparent
# on each side, creating the illusion of an infinite waveform.
WAVE_FADE_WIDTH = 180  # ~15% of WAVE_WIDTH (1200px)


# Localisation — prefixes for artist and album fields
LANG_PREFIXES: dict[str, dict[str, str]] = {
    "en": {"artist": "by ", "album": "from "},
    "pt": {"artist": "por ", "album": "de "},
}

# Fade in / fade out
FADE_DURATION = 3.0  # seconds for the full fade window at each end
# Staggered delays within the fade window (seconds after fade window starts)
FADE_DELAY_WAVE = 0.5  # wave starts fading in after the background
FADE_DELAY_UI = 1.0  # texts + seek start fading in after the background
#
# Fade-in order:  bg (0.0s) → wave (0.5s) → ui (1.0s)  — all finish at 3.0s
# Fade-out order: ui (end-3.0s) → wave (end-2.5s) → bg (end-2.0s) — all finish at end


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def hex_to_rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    """Convert a hex color string (#RRGGBB or #RGB) to an RGBA tuple."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r, g, b, alpha)


def validate_hex_color(value: str) -> str:
    """argparse type= validator for hex color strings (#RGB or #RRGGBB)."""
    h = value.lstrip("#")
    if len(h) not in (3, 6) or not all(c in "0123456789abcdefABCDEF" for c in h):
        raise argparse.ArgumentTypeError(
            f"Invalid color '{value}'. Expected #RGB or #RRGGBB (e.g. #FFF or #FFFFFF)."
        )
    return value


def read_id3_tags(audio_path: str) -> tuple[str, str, str]:
    """
    Read title, artist and album from the ID3 tags of an MP3 file.
    Falls back to the filename stem for title and empty string for artist/album
    if the tags are missing or unreadable.
    """
    stem = Path(audio_path).stem
    title, artist, album = stem, "", ""
    try:
        tags = ID3(audio_path)
        if tags.get("TIT2"):
            title = str(tags["TIT2"].text[0]).strip() or stem
        if tags.get("TPE1"):
            artist = str(tags["TPE1"].text[0]).strip()
        if tags.get("TALB"):
            album = str(tags["TALB"].text[0]).strip()
    except MutagenError:
        pass
    return title, artist, album


def compute_fade_alphas(
    frame_idx: int,
    n_frames: int,
    fps: int,
) -> tuple[float, float, float]:
    """
    Return (alpha_bg, alpha_wave, alpha_ui) in [0.0, 1.0] for the given frame,
    applying staggered fade-in at the start and staggered fade-out at the end.

    Fade-in order  (each starts at its delay, all reach 1.0 at FADE_DURATION):
        bg   starts at t=0
        wave starts at t=FADE_DELAY_WAVE
        ui   starts at t=FADE_DELAY_UI

    Fade-out order (mirror, each ends at its corresponding offset from the end):
        ui   finishes fading out first
        wave finishes next
        bg   finishes last (at the very last frame)
    """
    t = frame_idx / fps
    total = n_frames / fps

    def ramp(t_start: float, t_end: float) -> float:
        """Linear ramp from 0→1 over [t_start, t_end]."""
        if t_end <= t_start:
            return 1.0
        return float(np.clip((t - t_start) / (t_end - t_start), 0.0, 1.0))

    def ramp_out(t_start: float, t_end: float) -> float:
        """Linear ramp from 1→0 over [t_start, t_end]."""
        if t_end <= t_start:
            return 0.0
        return float(np.clip(1.0 - (t - t_start) / (t_end - t_start), 0.0, 1.0))

    # ---- fade in -----------------------------------------------------------
    a_bg_in = ramp(0.0, FADE_DURATION)
    a_wave_in = ramp(FADE_DELAY_WAVE, FADE_DURATION)
    a_ui_in = ramp(FADE_DELAY_UI, FADE_DURATION)

    # ---- fade out ----------------------------------------------------------
    # bg   fades from (end - FADE_DURATION) to end
    # wave fades from (end - FADE_DURATION) to (end - FADE_DELAY_WAVE)  [finishes earlier]
    # ui   fades from (end - FADE_DURATION) to (end - FADE_DELAY_UI)    [finishes first]
    # Clamp fo_start to 0 so tracks shorter than FADE_DURATION*2 don't produce
    # a negative start, which would keep all layers permanently transparent.
    fo_start = max(0.0, total - FADE_DURATION)
    a_bg_out = ramp_out(fo_start, total)
    a_wave_out = ramp_out(fo_start, total - FADE_DELAY_WAVE)
    a_ui_out = ramp_out(fo_start, total - FADE_DELAY_UI)

    # Combine: both fades can overlap, take the minimum (most transparent wins)
    alpha_bg = min(a_bg_in, a_bg_out) if t >= fo_start else a_bg_in
    alpha_wave = min(a_wave_in, a_wave_out) if t >= fo_start else a_wave_in
    alpha_ui = min(a_ui_in, a_ui_out) if t >= fo_start else a_ui_in

    return alpha_bg, alpha_wave, alpha_ui


def load_font_bold(size: int, custom_path: str | None = None) -> ImageFont.FreeTypeFont:
    """Load a bold font. Uses custom_path if provided, otherwise falls back to system fonts."""
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
    """Load a regular font. Uses custom_path if provided, otherwise falls back to system fonts."""
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
        "No suitable regular font found. Install dejavu-fonts or liberation-fonts."
    )


def moving_average(arr: np.ndarray, w: int) -> np.ndarray:
    if w <= 1:
        return arr
    kernel = np.ones(w) / w
    return np.convolve(arr, kernel, mode="same")


def format_time(seconds: float) -> str:
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m:02d}:{s:02d}"


# ---------------------------------------------------------------------------
# Audio analysis
# ---------------------------------------------------------------------------


def analyze_audio(
    audio_path: str,
    fps: int,
    smoothing_window: int = SMOOTHING_WINDOW,
    temporal_alpha: float = TEMPORAL_ALPHA,
    wave_width: int = WAVE_WIDTH,
) -> tuple[np.ndarray, float]:
    """
    Load audio and compute per-frame waveform samples.

    Returns:
        frames_samples: shape (n_frames, n_columns) – amplitude values in [-1, 1]
        duration: total duration in seconds
    """
    print("Loading audio...")
    y, sr = librosa.load(audio_path, sr=None, mono=True)
    duration = librosa.get_duration(y=y, sr=sr)
    n_frames = int(duration * fps)

    if n_frames == 0:
        raise ValueError(
            f"Audio file '{audio_path}' has zero or near-zero duration ({duration:.3f}s). "
            "Cannot generate a video."
        )

    # Number of audio samples per video frame
    hop = len(y) / n_frames

    # For each frame, grab a window of samples to plot as waveform
    # Window = ~60 ms of audio centred at the frame's midpoint
    window_samples = int(sr * 0.06)
    if window_samples % 2 == 0:
        window_samples += 1

    n_columns = wave_width  # one waveform point per horizontal pixel

    print(f"Duration: {duration:.1f}s  |  Frames: {n_frames}  |  SR: {sr} Hz")

    frames_samples = np.zeros((n_frames, n_columns), dtype=np.float32)

    for i in tqdm(range(n_frames), desc="Analyzing audio", unit="frame"):
        center = int(i * hop + hop / 2)
        half = window_samples // 2
        start = max(0, center - half)
        end = min(len(y), center + half + 1)
        chunk = y[start:end]

        if len(chunk) == 0:
            continue

        # Resample chunk to n_columns points via linear interpolation
        x_old = np.linspace(0, 1, len(chunk))
        x_new = np.linspace(0, 1, n_columns)
        resampled = np.interp(x_new, x_old, chunk)

        # Smooth the waveform spatially (along X axis)
        frames_samples[i] = moving_average(resampled, smoothing_window)

    # Temporal smoothing: EMA across consecutive frames so the waveform
    # transitions fluidly instead of jumping frame-to-frame.
    # frame[i] = alpha * raw[i] + (1 - alpha) * frame[i-1]
    for i in range(1, n_frames):
        frames_samples[i] = (
            temporal_alpha * frames_samples[i]
            + (1.0 - temporal_alpha) * frames_samples[i - 1]
        )

    return frames_samples, duration


# ---------------------------------------------------------------------------
# Background preparation
# ---------------------------------------------------------------------------


def prepare_background(image_path: str) -> Image.Image:
    """Load, resize, blur and darken the background image."""
    print("Preparing background...")
    bg = Image.open(image_path).convert("RGB")

    # Resize to cover the full frame (crop to centre)
    bg_ratio = bg.width / bg.height
    target_ratio = WIDTH / HEIGHT

    if bg_ratio > target_ratio:
        # wider than target: scale by height
        new_h = HEIGHT
        new_w = int(HEIGHT * bg_ratio)
    else:
        # taller than target: scale by width
        new_w = WIDTH
        new_h = int(WIDTH / bg_ratio)

    bg = bg.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Centre crop
    left = (new_w - WIDTH) // 2
    top = (new_h - HEIGHT) // 2
    bg = bg.crop((left, top, left + WIDTH, top + HEIGHT))

    return bg


# ---------------------------------------------------------------------------
# Waveform drawing helpers
# ---------------------------------------------------------------------------


def draw_wave_line(
    wave_draw: ImageDraw.ImageDraw,
    samples: np.ndarray,
    lc: dict,
    wave_color: tuple,
    wave_fill: tuple,
    centre_color: tuple,
) -> None:
    """Draw the classic mirrored-line waveform."""
    n_cols = len(samples)
    w_width = lc["wave_width"]
    w_height = lc["wave_height"]
    w_x_start = lc["wave_x_start"]
    w_cy = lc["wave_center_y"]

    xs = np.linspace(w_x_start, w_x_start + w_width, n_cols, dtype=int)
    amplitudes = np.clip(samples, -1.0, 1.0)

    peak = np.percentile(np.abs(amplitudes), 99)
    if peak > 0:
        amplitudes = amplitudes / peak * 0.80

    ys = (amplitudes * w_height).astype(int)

    poly_top = [(xs[i], w_cy - ys[i]) for i in range(n_cols)]
    poly_bot = [(xs[i], w_cy + ys[i]) for i in range(n_cols - 1, -1, -1)]
    wave_draw.polygon(poly_top + poly_bot, fill=wave_fill)

    top_points = [(xs[i], w_cy - ys[i]) for i in range(n_cols)]
    bot_points = [(xs[i], w_cy + ys[i]) for i in range(n_cols)]
    if len(top_points) > 1:
        wave_draw.line(top_points, fill=wave_color, width=3)
        wave_draw.line(bot_points, fill=wave_color, width=3)


def draw_wave_circular(
    wave_draw: ImageDraw.ImageDraw,
    samples: np.ndarray,
    lc: dict,
    wave_color: tuple,
    wave_fill: tuple,
    centre_color: tuple,
) -> None:
    """
    Draw a radial/circular waveform — bars project outward from a ring.
    Gradient effect: brighter/more opaque near the inner ring, fading outward.
    """
    cx = lc["wave_center_x"]
    cy = lc["wave_center_y"]
    max_radius = lc.get("circular_radius", 400)
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

        n_segments = max(4, int(bar_len / 6))
        for seg in range(n_segments):
            seg_start = inner_r + (bar_len * seg / n_segments)
            seg_end = inner_r + (bar_len * (seg + 1) / n_segments)

            x1 = cx + np.cos(angle) * seg_start
            y1 = cy + np.sin(angle) * seg_start
            x2 = cx + np.cos(angle) * seg_end
            y2 = cy + np.sin(angle) * seg_end

            # Gradient: high alpha at inner ring, lower at outer
            # Also respect the base_alpha from fade
            t = seg / n_segments
            gradient_factor = 1.0 - t * 0.5
            amp_factor = 0.6 + 0.4 * amp
            seg_alpha = int(base_alpha * gradient_factor * amp_factor)
            seg_col = (base_r, base_g, base_b, seg_alpha)

            wave_draw.line(
                [(int(x1), int(y1)), (int(x2), int(y2))],
                fill=seg_col,
                width=5,
            )

        # Dot at tip
        x_outer = cx + np.cos(angle) * (inner_r + bar_len)
        y_outer = cy + np.sin(angle) * (inner_r + bar_len)
        dot_alpha = int(base_alpha * 0.7 * amp)
        dot_col = (base_r, base_g, base_b, dot_alpha)
        dot_r = 4
        ix, iy = int(x_outer), int(y_outer)
        wave_draw.ellipse(
            [ix - dot_r, iy - dot_r, ix + dot_r, iy + dot_r],
            fill=dot_col,
        )


# ---------------------------------------------------------------------------
# Frame rendering
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
    font_title: ImageFont.FreeTypeFont,
    font_artist: ImageFont.FreeTypeFont,
    font_album: ImageFont.FreeTypeFont,
    font_time: ImageFont.FreeTypeFont,
    layout_config: dict | None = None,
    wave_style: str = "line",
) -> Image.Image:
    # Use classic layout if none provided (backwards compat)
    lc = layout_config if layout_config is not None else get_layout_config("classic")

    # ---- Fade alphas -------------------------------------------------------
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

    # Draw waveform with selected style
    if wave_style == "circular":
        draw_wave_circular(wave_draw, samples, lc, wave_color, wave_fill, centre_color)
    else:
        draw_wave_line(wave_draw, samples, lc, wave_color, wave_fill, centre_color)

    # Edge fade (horizontal gradient → infinite-wave illusion)
    # Only apply for line style; circular doesn't need it
    if wave_style == "line":
        wave_arr = np.array(wave_layer, dtype=np.float32)
        fade = np.ones(WIDTH, dtype=np.float32)
        x0 = lc["wave_x_start"]
        x1 = x0 + lc["wave_width"]
        fw = lc["wave_fade_width"]
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
    seek_bg_color = hex_to_rgba(color, ua(50))
    seek_fg_color = hex_to_rgba(color, ua(220))
    dot_color = hex_to_rgba(color, ua(255))

    # Seek bar
    sb_x = lc["seek_bar_x"]
    sb_y = lc["seek_bar_y"]
    sb_w = lc["seek_bar_w"]
    sb_h = lc["seek_bar_h"]

    progress = frame_idx / max(n_frames - 1, 1)
    filled_w = int(sb_w * progress)

    draw.rectangle(
        [sb_x, sb_y, sb_x + sb_w, sb_y + sb_h],
        fill=seek_bg_color,
    )
    if filled_w > 0:
        draw.rectangle(
            [sb_x, sb_y, sb_x + filled_w, sb_y + sb_h],
            fill=seek_fg_color,
        )
    dot_r = max(10, sb_h)  # dot radius scales with seek bar height
    dot_x = sb_x + filled_w
    dot_y = sb_y + sb_h // 2
    draw.ellipse(
        [dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r],
        fill=dot_color,
    )

    # Time label
    elapsed = frame_idx / FPS
    time_str = f"{format_time(elapsed)} / {format_time(duration)}"

    tx = lc["text_x"]
    anchor = lc["text_anchor"]

    if anchor == "center":
        draw.text(
            (tx, lc["text_y_time"]),
            time_str,
            font=font_time,
            fill=text_color,
            anchor="mt",
        )
    elif anchor == "right":
        draw.text(
            (tx, lc["text_y_time"]),
            time_str,
            font=font_time,
            fill=text_color,
            anchor="rt",
        )
    else:
        draw.text((tx, lc["text_y_time"]), time_str, font=font_time, fill=text_color)

    # Track info
    for text, font, y in [
        (title, font_title, lc["text_y_title"]),
        (artist, font_artist, lc["text_y_artist"]),
        (album, font_album, lc["text_y_album"]),
    ]:
        if anchor == "center":
            draw.text((tx, y), text, font=font, fill=text_color, anchor="mt")
        elif anchor == "right":
            draw.text((tx, y), text, font=font, fill=text_color, anchor="rt")
        else:
            draw.text((tx, y), text, font=font, fill=text_color)

    frame = Image.alpha_composite(frame, ui_layer)

    return frame.convert("RGB")


# ---------------------------------------------------------------------------
# Cover image
# ---------------------------------------------------------------------------


def render_cover(
    bg: Image.Image,
    title: str,
    artist: str,
    album: str,
    color: str,
    font_path: str | None = None,
    font_bold_path: str | None = None,
) -> Image.Image:
    """
    Render a 4K cover image: same background, text centred and larger.
    Layout (top → bottom, all centred horizontally):
        title  (bold, 160px)
        artist (regular, 120px)
        album  (regular, 96px)
    """
    font_title = load_font_bold(160, font_bold_path)
    font_artist = load_font_regular(120, font_path)
    font_album = load_font_regular(96, font_path)

    cover = bg.copy().convert("RGBA")
    draw = ImageDraw.Draw(cover, "RGBA")

    text_color = hex_to_rgba(color, 255)

    cx = WIDTH // 2  # horizontal centre

    # Measure each line so we can stack them with consistent spacing
    def text_size(text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
        bb = font.getbbox(text)  # (left, top, right, bottom)
        return int(bb[2] - bb[0]), int(bb[3] - bb[1])

    tw, th = text_size(title, font_title)
    aw, ah = text_size(artist, font_artist)
    lw, lh = text_size(album, font_album)

    GAP_TITLE_ARTIST = 80  # px between title bottom and artist top
    GAP_ARTIST_ALBUM = 60  # px between artist bottom and album top

    block_h = th + GAP_TITLE_ARTIST + ah + GAP_ARTIST_ALBUM + lh

    # Centre the whole block vertically
    y = (HEIGHT - block_h) // 2

    def draw_text_centred(text: str, font: ImageFont.FreeTypeFont, y_top: int) -> None:
        w, _ = text_size(text, font)
        x = cx - w // 2
        draw.text((x, y_top), text, font=font, fill=text_color)

    # Title
    draw_text_centred(title, font_title, y)
    y += th + GAP_TITLE_ARTIST

    # Artist
    draw_text_centred(artist, font_artist, y)
    y += ah + GAP_ARTIST_ALBUM

    # Album
    draw_text_centred(album, font_album, y)

    return cover.convert("RGB")


# ---------------------------------------------------------------------------
# Parallel frame rendering → FFmpeg stdin pipe
# ---------------------------------------------------------------------------


def _render_worker(args_tuple: tuple) -> tuple[int, bytes]:
    """
    Top-level function (required for multiprocessing pickling).
    Renders a single frame and returns (frame_idx, raw_rgb_bytes).
    """
    (
        frame_idx,
        n_frames,
        duration,
        samples_bytes,
        n_columns,
        bg_bytes,
        bg_size,
        title,
        artist,
        album,
        color,
        font_path,
        font_bold_path,
        layout_name,
        wave_style,
    ) = args_tuple

    samples = np.frombuffer(samples_bytes, dtype=np.float32).copy()
    bg = Image.frombytes("RGB", bg_size, bg_bytes)

    lc = get_layout_config(layout_name)

    font_title = load_font_bold(lc["font_size_title"], font_bold_path)
    font_artist = load_font_regular(lc["font_size_artist"], font_path)
    font_album = load_font_regular(lc["font_size_album"], font_path)
    font_time = load_font_regular(lc["font_size_time"], font_path)

    img = render_frame(
        bg=bg,
        samples=samples,
        frame_idx=frame_idx,
        n_frames=n_frames,
        duration=duration,
        title=title,
        artist=artist,
        album=album,
        color=color,
        font_title=font_title,
        font_artist=font_artist,
        font_album=font_album,
        font_time=font_time,
        layout_config=lc,
        wave_style=wave_style,
    )
    return frame_idx, img.tobytes()  # raw RGB24


def _build_video_codec_args(gpu: str) -> list[str]:
    """
    Return the FFmpeg video codec arguments for the requested encoder.

    gpu choices:
        "none"  – CPU libx264 (default, works everywhere)
        "nvenc" – NVIDIA NVENC (requires nvidia GPU + driver)
        "vaapi" – Intel/AMD VAAPI (requires Mesa/VA-API setup)
    """
    if gpu == "nvenc":
        return [
            "-c:v",
            "h264_nvenc",
            "-preset",
            "p4",
            "-rc",
            "vbr",
            "-cq",
            "18",
            "-b:v",
            "0",
            "-pix_fmt",
            "yuv420p",
        ]
    if gpu == "vaapi":
        return [
            "-vaapi_device",
            "/dev/dri/renderD128",
            "-c:v",
            "h264_vaapi",
            "-vf",
            "format=nv12,hwupload",
            "-qp",
            "18",
            "-pix_fmt",
            "vaapi",
        ]
    return [
        "-c:v",
        "libx264",
        "-preset",
        "slow",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
    ]


def render_and_encode(
    frames_samples: np.ndarray,
    bg: Image.Image,
    n_frames: int,
    duration: float,
    title: str,
    artist: str,
    album: str,
    color: str,
    audio_path: str,
    output_path: str,
    fps: int,
    gpu: str = "none",
    workers: int = 1,
    font_path: str | None = None,
    font_bold_path: str | None = None,
    layout: str = "classic",
    wave_style: str = "line",
) -> None:
    """
    Render all frames in parallel and stream raw RGB24 directly into FFmpeg
    via stdin — no intermediate JPEG files, no disk I/O bottleneck.

    Architecture:
        Pool workers (CPU, parallel) → ordered queue → writer thread → FFmpeg stdin → GPU encoder
    """
    codec_args = _build_video_codec_args(gpu)

    cmd = [
        "ffmpeg",
        "-y",
        # raw video on stdin
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-s",
        f"{WIDTH}x{HEIGHT}",
        "-pix_fmt",
        "rgb24",
        "-r",
        str(fps),
        "-i",
        "pipe:0",
        # audio from file
        "-i",
        audio_path,
        *codec_args,
        "-c:a",
        "aac",
        "-b:a",
        "320k",
        "-movflags",
        "+faststart",
        "-shortest",
        output_path,
    ]

    ffmpeg = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    if ffmpeg.stdin is None:
        raise RuntimeError("Failed to open FFmpeg stdin pipe.")
    ffmpeg_stdin = ffmpeg.stdin

    # Shared state for the writer thread
    write_queue: queue.Queue[tuple[int, bytes] | None] = queue.Queue(
        maxsize=workers * 2
    )
    write_error: list[str] = []
    abort_event = threading.Event()  # set on pipe error to unblock pool put()

    # Pending buffer: frames that arrived out-of-order
    pending: dict[int, bytes] = {}
    next_idx = 0

    def writer_thread() -> None:
        nonlocal next_idx
        while True:
            item = write_queue.get()
            if item is None:
                break
            if abort_event.is_set():
                # Drain queue without writing so pool put() never blocks
                continue
            frame_idx, raw = item
            pending[frame_idx] = raw
            # Flush consecutive frames in order
            while next_idx in pending:
                try:
                    ffmpeg_stdin.write(pending.pop(next_idx))
                except BrokenPipeError as e:
                    write_error.append(str(e))
                    abort_event.set()
                    return
                next_idx += 1

    wt = threading.Thread(target=writer_thread, daemon=True)
    wt.start()

    bg_bytes = bg.tobytes()
    bg_size = (bg.width, bg.height)

    tasks = [
        (
            i,
            n_frames,
            duration,
            frames_samples[i].tobytes(),
            len(frames_samples[i]),
            bg_bytes,
            bg_size,
            title,
            artist,
            album,
            color,
            font_path,
            font_bold_path,
            layout,
            wave_style,
        )
        for i in range(n_frames)
    ]

    with mp.Pool(processes=workers) as pool:
        for result in tqdm(
            pool.imap_unordered(_render_worker, tasks, chunksize=4),
            total=n_frames,
            desc="Rendering + encoding",
            unit="frame",
        ):
            if abort_event.is_set():
                pool.terminate()
                break
            write_queue.put(result)

    write_queue.put(None)  # signal writer to stop
    wt.join()

    try:
        ffmpeg_stdin.close()
    except Exception:
        pass

    _, stderr = ffmpeg.communicate()
    if write_error:
        print(f"Pipe write error: {write_error[0]}")
        sys.exit(1)
    if ffmpeg.returncode != 0:
        print("FFmpeg error:")
        print(stderr.decode(errors="replace")[-3000:])
        sys.exit(1)

    print(f"Video saved: {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a 4K audio visualizer video for YouTube.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single-file, CPU (default) — outputs visualizer.mp4 + visualizer.jpg (cover)
  python visualizer.py \\
      --audio my_song.mp3 \\
      --background cover.jpg \\
      --title "My Song" \\
      --artist "My Artist" \\
      --album "My Album" \\
      --color "#FFFFFF" \\
      --output visualizer.mp4

  # Custom fonts
  python visualizer.py --audio ... --font regular.ttf --font-bold bold.ttf --output visualizer.mp4

  # NVIDIA GPU encoding + all 30 workers
  python visualizer.py --audio ... --gpu nvenc --workers 30 --output visualizer.mp4

  # Intel/AMD GPU
  python visualizer.py --audio ... --gpu vaapi --output visualizer.mp4

  # Batch mode — process all MP3s in a folder (reads ID3 tags automatically)
  python visualizer.py \\
      --input-dir /path/to/mp3s \\
      --background cover.jpg \\
      --color "#FFFFFF" \\
      --gpu nvenc \\
      --workers 30
        """,
    )
    parser.add_argument(
        "--audio",
        default=None,
        help="Path to the MP3/WAV audio file. Required in single-file mode.",
    )
    parser.add_argument(
        "--input-dir",
        default=None,
        dest="input_dir",
        help=(
            "Batch mode: path to a folder containing MP3 files. "
            "Title/artist/album are read from each file's ID3 tags. "
            "Each MP3 produces a .mp4 and .jpg in the same folder. "
            "Mutually exclusive with --audio."
        ),
    )
    parser.add_argument(
        "--background", required=True, help="Path to the background image."
    )
    parser.add_argument(
        "--cover-background",
        default=None,
        dest="cover_background",
        help=(
            "Path to a separate background image for the cover JPG. "
            "If omitted, the same background as the video is used."
        ),
    )
    parser.add_argument("--title", default=None, help="Song title (single-file mode).")
    parser.add_argument(
        "--artist", default=None, help="Artist name (single-file mode)."
    )
    parser.add_argument("--album", default=None, help="Album name (single-file mode).")
    parser.add_argument(
        "--color",
        default="#FFFFFF",
        type=validate_hex_color,
        help="Hex color for the visualizer elements (default: #FFFFFF). Format: #RGB or #RRGGBB.",
    )
    parser.add_argument(
        "--output",
        default="output.mp4",
        help=(
            "Output MP4 file path (single-file mode, default: output.mp4). "
            "In batch mode the output is placed next to each MP3 automatically."
        ),
    )
    parser.add_argument(
        "--gpu",
        choices=["none", "nvenc", "vaapi"],
        default="none",
        help=(
            "GPU encoder to use for faster video encoding. "
            "'none' = CPU libx264 (default, works everywhere); "
            "'nvenc' = NVIDIA GPU; "
            "'vaapi' = Intel/AMD via VA-API."
        ),
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=max(1, mp.cpu_count() - 2),
        help=(
            "Number of parallel workers for frame rendering "
            f"(default: cpu_count - 2 = {max(1, mp.cpu_count() - 2)})."
        ),
    )
    parser.add_argument(
        "--font",
        default=None,
        help="Path to a .ttf/.otf font file used for regular text (artist, album, time).",
    )
    parser.add_argument(
        "--font-bold",
        default=None,
        dest="font_bold",
        help="Path to a .ttf/.otf font file used for bold text (title).",
    )
    parser.add_argument(
        "--lang",
        choices=["en", "pt"],
        default="en",
        dest="lang",
        help=(
            "Language for artist/album prefixes. "
            "'en' = 'by / from' (default); 'pt' = 'por / de'."
        ),
    )
    parser.add_argument(
        "--layout",
        choices=["classic", "spotlight", "split-left", "split-right"],
        default="classic",
        help=(
            "Visual layout for the video. "
            "'classic' = original layout (default); "
            "'spotlight' = large centred text, big seek bar above, waves below; "
            "'split-left' = waves on the left, text on the right, full-width seek below; "
            "'split-right' = text on the left, waves on the right, full-width seek below."
        ),
    )
    parser.add_argument(
        "--wave-style",
        choices=["line", "circular"],
        default="line",
        dest="wave_style",
        help=(
            "Waveform drawing style. "
            "'line' = mirrored waveform lines (default); "
            "'circular' = radial/circular waveform (bars projected from a circle)."
        ),
    )
    parser.add_argument(
        "--smoothing-window",
        type=int,
        default=SMOOTHING_WINDOW,
        dest="smoothing_window",
        help=(
            f"Spatial smoothing: moving-average window size along the waveform X axis "
            f"(default: {SMOOTHING_WINDOW}). Larger = smoother shape per frame."
        ),
    )
    parser.add_argument(
        "--temporal-alpha",
        type=float,
        default=TEMPORAL_ALPHA,
        dest="temporal_alpha",
        help=(
            f"Temporal smoothing: EMA blending factor between consecutive frames "
            f"(default: {TEMPORAL_ALPHA}). Range 0.0–1.0. "
            "Lower = more lag/fluid, higher = more reactive/jittery."
        ),
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Per-file processing
# ---------------------------------------------------------------------------


def process_file(
    audio_path: str,
    background_path: str,
    title: str,
    artist: str,
    album: str,
    output_path: str,
    args: argparse.Namespace,
    bg: Image.Image | None = None,
) -> None:
    """
    Analyze audio, render all frames, encode to MP4, and save a cover JPG.

    `bg` may be passed in (already prepared) to avoid re-processing the
    background image on every file in batch mode.
    """
    print(f"\n--- Processing: {audio_path} ---")

    # Apply language-specific prefixes for display
    prefixes = LANG_PREFIXES.get(args.lang, LANG_PREFIXES["en"])
    display_artist = f"{prefixes['artist']}{artist}" if artist else artist
    display_album = f"{prefixes['album']}{album}" if album else album

    # Resolve layout geometry so analyze_audio uses the correct wave_width
    lc = get_layout_config(args.layout)

    frames_samples, duration = analyze_audio(
        audio_path,
        FPS,
        smoothing_window=args.smoothing_window,
        temporal_alpha=args.temporal_alpha,
        wave_width=lc["wave_width"],
    )
    n_frames = len(frames_samples)

    if bg is None:
        bg = prepare_background(background_path)

    print(
        f"Rendering {n_frames} frames with {args.workers} workers → piping to FFmpeg "
        f"({args.gpu if args.gpu != 'none' else 'libx264 CPU'})..."
    )
    render_and_encode(
        frames_samples=frames_samples,
        bg=bg,
        n_frames=n_frames,
        duration=duration,
        title=title,
        artist=display_artist,
        album=display_album,
        color=args.color,
        audio_path=audio_path,
        output_path=output_path,
        fps=FPS,
        gpu=args.gpu,
        workers=args.workers,
        font_path=args.font,
        font_bold_path=args.font_bold,
        layout=args.layout,
        wave_style=args.wave_style,
    )

    cover_path = str(Path(output_path).with_suffix(".jpg"))
    print("Generating cover image...")

    # Use separate background for cover if provided
    if args.cover_background:
        cover_bg = prepare_background(args.cover_background)
    else:
        cover_bg = bg

    cover = render_cover(
        bg=cover_bg,
        title=title,
        artist=display_artist,
        album=display_album,
        color=args.color,
        font_path=args.font,
        font_bold_path=args.font_bold,
    )
    cover.save(cover_path, "JPEG", quality=95, subsampling=0)
    print(f"Cover saved: {cover_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    args = parse_args()

    # ---- Validate mode -------------------------------------------------------
    if args.input_dir and args.audio:
        print("Error: --input-dir and --audio are mutually exclusive.")
        sys.exit(1)

    if not args.input_dir and not args.audio:
        print("Error: one of --audio (single-file) or --input-dir (batch) is required.")
        sys.exit(1)

    # ---- Validate background -------------------------------------------------
    if not Path(args.background).exists():
        print(f"Error: background file not found: {args.background}")
        sys.exit(1)

    # ---- Validate optional font paths ----------------------------------------
    for path, label in [
        (args.font, "--font"),
        (args.font_bold, "--font-bold"),
    ]:
        if path and not Path(path).exists():
            print(f"Error: font file not found ({label}): {path}")
            sys.exit(1)

    # Prepare background once (shared across all files)
    bg = prepare_background(args.background)

    # ---- Batch mode ----------------------------------------------------------
    if args.input_dir:
        input_dir = Path(args.input_dir)
        if not input_dir.is_dir():
            print(f"Error: --input-dir is not a directory: {args.input_dir}")
            sys.exit(1)

        mp3_files = sorted(input_dir.glob("*.mp3"))
        if not mp3_files:
            print(f"No MP3 files found in: {args.input_dir}")
            sys.exit(1)

        print(f"Batch mode: {len(mp3_files)} file(s) found in {args.input_dir}")

        for mp3_path in mp3_files:
            title, artist, album = read_id3_tags(str(mp3_path))
            output_path = str(mp3_path.with_suffix(".mp4"))
            process_file(
                audio_path=str(mp3_path),
                background_path=args.background,
                title=title,
                artist=artist,
                album=album,
                output_path=output_path,
                args=args,
                bg=bg,
            )

        print("\nBatch done!")
        return

    # ---- Single-file mode ----------------------------------------------------
    if not Path(args.audio).exists():
        print(f"Error: audio file not found: {args.audio}")
        sys.exit(1)

    title = args.title or Path(args.audio).stem
    artist = args.artist or ""
    album = args.album or ""
    output_path = args.output

    process_file(
        audio_path=args.audio,
        background_path=args.background,
        title=title,
        artist=artist,
        album=album,
        output_path=output_path,
        args=args,
        bg=bg,
    )

    print("Done!")


if __name__ == "__main__":
    main()
