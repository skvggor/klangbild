<p align="center">
  <img src="assets/icon.svg" alt="klangbild icon" width="120" height="120"/><br/>
 <h1 align="center">klangbild</h1>
</p>

Generate a **4K audio visualizer video** (MP4) and a matching **cover image** (JPG) from any MP3 file.

- Centered, mirrored waveform (1800 × 300 px) that reacts to the audio
- Background image rendered as-is, without any darkening overlay
- Song title, artist, album, and a seek bar aligned to the left edge of the waveform
- Staggered fade-in / fade-out (background → wave → UI)
- Infinite-wave edge fade effect
- GPU encoding via NVENC or VAAPI (optional)
- Parallel CPU frame rendering piped directly to FFmpeg (no temp files)
- Batch mode: process an entire folder of MP3s at once

---

## Example

| Video (frame) | Cover image |
|:-------------:|:-----------:|
| ![Video frame](assets/video.jpg) | ![Cover](assets/cover.jpg) |

---

## Requirements

- Python ≥ 3.11
- [uv](https://github.com/astral-sh/uv) (package manager)
- FFmpeg ≥ 5 (must be in `$PATH`)
- For NVIDIA GPU encoding: NVENC-capable driver
- For Intel/AMD GPU encoding: Mesa VA-API

---

## Installation

```bash
git clone https://github.com/skvggor/klangbild.git
cd klangbild
uv sync
```

---

## Usage

### Single file

```bash
uv run python visualizer.py \
    --audio    "song.mp3" \
    --background "cover.jpg" \
    --title    "Song Title" \
    --artist   "Artist Name" \
    --album    "Album Name" \
    --color    "#FFFFFF" \
    --output   "visualizer.mp4"
```

`--title`, `--artist`, `--album` are optional (fall back to filename / empty string).

### Batch mode

Process every MP3 in a folder. Title, artist and album are read from each file's ID3 tags automatically.

```bash
uv run python visualizer.py \
    --input-dir "/path/to/mp3s" \
    --background "cover.jpg" \
    --color     "#FFFFFF" \
    --gpu       nvenc \
    --workers   30
```

Each MP3 produces a `.mp4` and `.jpg` in the same folder.

---

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--audio` | — | Path to MP3/WAV (single-file mode) |
| `--input-dir` | — | Folder of MP3s (batch mode) |
| `--background` | **required** | Background image path |
| `--title` | filename stem | Song title |
| `--artist` | `""` | Artist name |
| `--album` | `""` | Album name |
| `--color` | `#FFFFFF` | Hex color (`#RGB` or `#RRGGBB`) |
| `--output` | `output.mp4` | Output path (single-file mode) |
| `--gpu` | `none` | `none` · `nvenc` · `vaapi` |
| `--workers` | cpu_count − 2 | Parallel render workers |
| `--font` | system DejaVu/Liberation | Regular font `.ttf/.otf` |
| `--font-bold` | system DejaVu Bold | Bold font `.ttf/.otf` |
| `--lang` | `en` | Prefix language: `en` (by/from) · `pt` (por/de) |
| `--smoothing-window` | `15` | Spatial waveform smoothing window |
| `--temporal-alpha` | `0.35` | Temporal EMA between frames (0=frozen, 1=raw) |

---

## Visual layout

The output frame is 3840×2160 px. Key measurements:

| Element | Value |
|---------|-------|
| Waveform width | 1800 px (centered) |
| Waveform amplitude | ±150 px (300 px total height) |
| Font — title | 80 px bold |
| Font — artist | 60 px regular |
| Font — album | 50 px regular |
| Font — time | 40 px regular |
| Seek bar distance from bottom | 120 px |

A reference layout image (`assets/bg_spec.png`) is included in the repository and can be used as a template when preparing background images.

---

## Output

- `<output>.mp4` — 3840×2160 (4K), 30 fps, H.264, AAC 320 kbps
- `<output>.jpg` — 4K cover image with centered text

