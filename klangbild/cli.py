import argparse
import multiprocessing as mp

from .config.constants import SMOOTHING_WINDOW, TEMPORAL_ALPHA
from .utils.colors import validate_hex_color, validate_gradient_colors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a 4K audio visualizer video for YouTube.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single-file, CPU (default) — outputs visualizer.mp4 + visualizer.jpg (cover)
  python __main__.py \\
      --audio my_song.mp3 \\
      --background cover.jpg \\
      --title "My Song" \\
      --artist "My Artist" \\
      --album "My Album" \\
      --color "#FFFFFF" \\
      --output visualizer.mp4

  # Custom fonts
  python __main__.py --audio ... --font regular.ttf --font-bold bold.ttf --output visualizer.mp4

  # NVIDIA GPU encoding + all 30 workers
  python __main__.py --audio ... --gpu nvenc --workers 30 --output visualizer.mp4

  # Intel/AMD GPU
  python __main__.py --audio ... --gpu vaapi --output visualizer.mp4

  # Batch mode — process all MP3s in a folder (reads ID3 tags automatically)
  python __main__.py \\
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
        help="Separate background image for cover JPG (default: same as --background).",
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
        help="Visual layout (default: classic).",
    )
    parser.add_argument(
        "--wave-style",
        choices=["line", "circular"],
        default="line",
        dest="wave_style",
        help="Waveform drawing style (default: line).",
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
    parser.add_argument(
        "--text-gradient",
        default=None,
        type=validate_gradient_colors,
        dest="text_gradient",
        help=(
            "Gradient colors for text (e.g., #FFFFFF,#808080). "
            "Overrides --color for text elements."
        ),
    )
    parser.add_argument(
        "--text-gradient-dir",
        choices=["horizontal", "vertical"],
        default="horizontal",
        dest="text_gradient_dir",
        help="Text gradient direction (default: horizontal).",
    )
    parser.add_argument(
        "--wave-gradient",
        default=None,
        type=validate_gradient_colors,
        dest="wave_gradient",
        help=(
            "Gradient colors for waveform (e.g., #FFFFFF,#808080). "
            "Overrides --color for waveform."
        ),
    )
    parser.add_argument(
        "--wave-gradient-dir",
        choices=["horizontal", "vertical"],
        default="horizontal",
        dest="wave_gradient_dir",
        help="Waveform gradient direction (default: horizontal).",
    )
    parser.add_argument(
        "--grain",
        type=float,
        default=0.0,
        help="Film-grain intensity: 0.0 (off) to 1.0 (default: 0.0).",
    )
    return parser.parse_args()
