import numpy as np
from PIL import Image
from ..config.layouts import get_layout_config
from ..render.frame import render_frame
from ..utils.fonts import load_font_bold, load_font_regular


def _render_worker(args_tuple: tuple) -> tuple[int, bytes]:
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
        text_gradient,
        text_gradient_dir,
        wave_gradient,
        wave_gradient_dir,
        grain,
        layout,
        wave_style,
    ) = args_tuple

    samples = np.frombuffer(samples_bytes, dtype=np.float32).copy()
    bg = Image.frombytes("RGB", bg_size, bg_bytes)

    # Use layout-specific font sizes
    lc = get_layout_config(layout)
    font_title = load_font_bold(lc.get("font_size_title", 80), font_bold_path)
    font_artist = load_font_regular(lc.get("font_size_artist", 60), font_path)
    font_album = load_font_regular(lc.get("font_size_album", 50), font_path)
    font_time = load_font_regular(lc.get("font_size_time", 40), font_path)

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
        text_gradient=text_gradient,
        text_gradient_dir=text_gradient_dir,
        wave_gradient=wave_gradient,
        wave_gradient_dir=wave_gradient_dir,
        grain=grain,
        layout=layout,
        wave_style=wave_style,
        font_title=font_title,
        font_artist=font_artist,
        font_album=font_album,
        font_time=font_time,
    )
    return frame_idx, img.tobytes()
