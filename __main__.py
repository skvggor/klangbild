import sys
from pathlib import Path
from PIL import Image
from config.constants import FPS, LANG_PREFIXES
from cli import parse_args
from audio import analyze_audio, read_id3_tags
from utils import prepare_background
from render import render_cover
from encoding import render_and_encode


def process_file(
    audio_path: str,
    background_path: str,
    title: str,
    artist: str,
    album: str,
    output_path: str,
    args,
    bg: Image.Image | None = None,
) -> None:
    print(f"\n--- Processing: {audio_path} ---")

    prefixes = LANG_PREFIXES.get(args.lang, LANG_PREFIXES["en"])
    display_artist = f"{prefixes['artist']}{artist}" if artist else artist
    display_album = f"{prefixes['album']}{album}" if album else album

    frames_samples, duration = analyze_audio(
        audio_path,
        FPS,
        smoothing_window=args.smoothing_window,
        temporal_alpha=args.temporal_alpha,
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
    )

    cover_path = str(Path(output_path).with_suffix(".jpg"))
    print("Generating cover image...")
    cover = render_cover(
        bg=bg,
        title=title,
        artist=display_artist,
        album=display_album,
        color=args.color,
        font_path=args.font,
        font_bold_path=args.font_bold,
    )
    cover.save(cover_path, "JPEG", quality=95, subsampling=0)
    print(f"Cover saved: {cover_path}")


def main() -> None:
    args = parse_args()

    if args.input_dir and args.audio:
        print("Error: --input-dir and --audio are mutually exclusive.")
        sys.exit(1)

    if not args.input_dir and not args.audio:
        print("Error: one of --audio (single-file) or --input-dir (batch) is required.")
        sys.exit(1)

    if not Path(args.background).exists():
        print(f"Error: background file not found: {args.background}")
        sys.exit(1)

    for path, label in [
        (args.font, "--font"),
        (args.font_bold, "--font-bold"),
    ]:
        if path and not Path(path).exists():
            print(f"Error: font file found ({label}): {path}")
            sys.exit(1)

    bg = prepare_background(args.background)

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
