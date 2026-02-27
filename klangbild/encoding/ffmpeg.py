import subprocess
import sys
import queue
import threading
import multiprocessing as mp

import numpy as np
from PIL import Image
from tqdm import tqdm

from ..config.constants import WIDTH, HEIGHT
from .worker import _render_worker


def _build_video_codec_args(gpu: str) -> list[str]:
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
    text_gradient: str | None = None,
    text_gradient_dir: str = "horizontal",
    wave_gradient: str | None = None,
    wave_gradient_dir: str = "horizontal",
    grain: float = 0.0,
    layout: str = "classic",
    wave_style: str = "line",
) -> None:
    codec_args = _build_video_codec_args(gpu)

    cmd = [
        "ffmpeg",
        "-y",
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

    write_queue: queue.Queue[tuple[int, bytes] | None] = queue.Queue(
        maxsize=workers * 2
    )
    write_error: list[str] = []
    abort_event = threading.Event()

    pending: dict[int, bytes] = {}
    next_idx = 0

    def writer_thread() -> None:
        nonlocal next_idx
        while True:
            item = write_queue.get()
            if item is None:
                break
            if abort_event.is_set():
                continue
            frame_idx, raw = item
            pending[frame_idx] = raw
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
            text_gradient,
            text_gradient_dir,
            wave_gradient,
            wave_gradient_dir,
            grain,
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

    write_queue.put(None)
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
