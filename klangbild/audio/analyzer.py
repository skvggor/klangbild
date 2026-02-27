import numpy as np
import librosa
from tqdm import tqdm
from ..config.constants import SMOOTHING_WINDOW, TEMPORAL_ALPHA, WAVE_WIDTH


def moving_average(arr: np.ndarray, w: int) -> np.ndarray:
    if w <= 1:
        return arr
    kernel = np.ones(w) / w
    return np.convolve(arr, kernel, mode="same")


def analyze_audio(
    audio_path: str,
    fps: int,
    smoothing_window: int = SMOOTHING_WINDOW,
    temporal_alpha: float = TEMPORAL_ALPHA,
) -> tuple[np.ndarray, float]:
    print("Loading audio...")
    y, sr = librosa.load(audio_path, sr=None, mono=True)
    duration = librosa.get_duration(y=y, sr=sr)
    n_frames = int(duration * fps)

    if n_frames == 0:
        raise ValueError(
            f"Audio file '{audio_path}' has zero or near-zero duration ({duration:.3f}s). "
            "Cannot generate a video."
        )

    hop = len(y) / n_frames

    window_samples = int(sr * 0.06)
    if window_samples % 2 == 0:
        window_samples += 1

    n_columns = WAVE_WIDTH

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

        x_old = np.linspace(0, 1, len(chunk))
        x_new = np.linspace(0, 1, n_columns)
        resampled = np.interp(x_new, x_old, chunk)

        frames_samples[i] = moving_average(resampled, smoothing_window)

    for i in range(1, n_frames):
        frames_samples[i] = (
            temporal_alpha * frames_samples[i]
            + (1.0 - temporal_alpha) * frames_samples[i - 1]
        )

    return frames_samples, duration
