import numpy as np
from ..config.constants import FADE_DURATION, FADE_DELAY_WAVE, FADE_DELAY_UI, FPS


def format_time(seconds: float) -> str:
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m:02d}:{s:02d}"


def compute_fade_alphas(
    frame_idx: int,
    n_frames: int,
    fps: int,
) -> tuple[float, float, float]:
    t = frame_idx / fps
    total = n_frames / fps

    def ramp(t_start: float, t_end: float) -> float:
        if t_end <= t_start:
            return 1.0
        return float(np.clip((t - t_start) / (t_end - t_start), 0.0, 1.0))

    def ramp_out(t_start: float, t_end: float) -> float:
        if t_end <= t_start:
            return 0.0
        return float(np.clip(1.0 - (t - t_start) / (t_end - t_start), 0.0, 1.0))

    a_bg_in = ramp(0.0, FADE_DURATION)
    a_wave_in = ramp(FADE_DELAY_WAVE, FADE_DURATION)
    a_ui_in = ramp(FADE_DELAY_UI, FADE_DURATION)

    fo_start = max(0.0, total - FADE_DURATION)
    a_bg_out = ramp_out(fo_start, total)
    a_wave_out = ramp_out(fo_start, total - FADE_DELAY_WAVE)
    a_ui_out = ramp_out(fo_start, total - FADE_DELAY_UI)

    alpha_bg = min(a_bg_in, a_bg_out) if t >= fo_start else a_bg_in
    alpha_wave = min(a_wave_in, a_wave_out) if t >= fo_start else a_wave_in
    alpha_ui = min(a_ui_in, a_ui_out) if t >= fo_start else a_ui_in

    return alpha_bg, alpha_wave, alpha_ui
