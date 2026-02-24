<p align="center">
  <img src="assets/icon.svg" alt="klangbild icon" width="120" height="120"/><br/>
 <h1 align="center">klangbild</h1>
</p>

Generate a **4K audio visualizer video** (MP4) and a matching **cover image** (JPG) from any MP3 file.

- Multiple layout options: classic, spotlight, split-left, split-right
- Two waveform styles: mirrored lines or radial/circular
- Background image rendered as-is, without any darkening overlay
- Song title, artist, album, and a seek bar positioned according to layout
- Staggered fade-in / fade-out (background → wave → UI)
- Infinite-wave edge fade effect (line style)
- GPU encoding via NVENC or VAAPI (optional)
- Parallel CPU frame rendering piped directly to FFmpeg (no temp files)
- Batch mode: process an entire folder of MP3s at once

---

## Examples

### Example 1: Classic + Line

| Video frame | Cover image |
|:-----------:|:-----------:|
| ![Video frame](assets/example1_frame.jpg) | ![Cover](assets/example1_cover.jpg) |

*Enkelmåte — "Enkelmåte" from Hvis Havet Ikke Hører Meg*

### Example 2: Split-left + Circular

| Video frame | Cover image |
|:-----------:|:-----------:|
| ![Video frame](assets/example2_frame.jpg) | ![Cover](assets/example2_cover.jpg) |

*SKVGGOR — "Jah Old Beat" from Random*

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
| `--background` | **required** | Background image path for video |
| `--cover-background` | same as `--background` | Separate background image for cover JPG |
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
| `--layout` | `classic` | Visual layout (see below) |
| `--wave-style` | `line` | Waveform drawing style (see below) |
| `--text-gradient` | — | Gradient colors for text (see below) |
| `--text-gradient-dir` | `horizontal` | Text gradient direction: `horizontal` · `vertical` |
| `--wave-gradient` | — | Gradient colors for waveform (see below) |
| `--wave-gradient-dir` | `horizontal` | Waveform gradient direction: `horizontal` · `vertical` |
| `--grain` | `0.0` | Film-grain intensity: `0.0` (off) → `1.0` (heavy) |
| `--smoothing-window` | `15` | Spatial waveform smoothing window |
| `--temporal-alpha` | `0.35` | Temporal EMA between frames (0=frozen, 1=raw) |

---

## Gradients

Both text and waveform support independent color gradients. Each flag accepts two or more `#RGB` or `#RRGGBB` values separated by commas.

```bash
# Text gradient only
uv run python visualizer.py \
    --audio "song.mp3" --background "cover.jpg" \
    --text-gradient "#C8860A,#E4DBC9"

# Waveform gradient only
uv run python visualizer.py \
    --audio "song.mp3" --background "cover.jpg" \
    --wave-gradient "#7B9BAF,#B8A8C8"

# Both combined, vertical direction
uv run python visualizer.py \
    --audio "song.mp3" --background "cover.jpg" \
    --text-gradient "#C8860A,#E4DBC9" --text-gradient-dir vertical \
    --wave-gradient "#7B9BAF,#B8A8C8" --wave-gradient-dir vertical

# Three-stop gradient
uv run python visualizer.py \
    --audio "song.mp3" --background "cover.jpg" \
    --text-gradient "#FF0000,#FFFFFF,#0000FF"
```

When `--text-gradient` is provided it overrides `--color` for all text elements. When `--wave-gradient` is provided it overrides `--color` for the waveform. Both flags are independent and can be combined freely.

**Direction:**

| Value | Text | Waveform (`line`) |
|-------|------|-------------------|
| `horizontal` *(default)* | left → right across each glyph | left → right across the wave |
| `vertical` | top → bottom across each glyph | top → bottom across the wave |

For the `circular` waveform style the gradient direction flag is ignored — colors cycle angularly around the ring instead.

### Gradient examples

| Name | Colors | Preview |
|------|--------|---------|
| Warm | `#C8860A → #E4DBC9` | ![warm](assets/gradient_quente.jpg) |
| Cool | `#7B9BAF → #B8A8C8` | ![cool](assets/gradient_frio.jpg) |
| High contrast | `#FFFFFF → #AAAAAA` | ![contrast](assets/gradient_contraste.jpg) |
| Monochrome | `#C8B89A → #F5EFE0` | ![mono](assets/gradient_monocromo.jpg) |
| Pastel | `#D4A8A0 → #A8C8B8` | ![pastel](assets/gradient_pastel.jpg) |

---

## Layouts

The `--layout` flag controls how elements are positioned on the 3840×2160 canvas.

| Layout | Description |
|--------|-------------|
| `classic` | Original layout. Waveform centred, text stacked below, seek bar at bottom. |
| `spotlight` | Large centred text with generous margins. Seek bar above text, waveform below. |
| `split-left` | Two-column layout. Waveform on the left, text on the right, full-width seek bar at bottom. |
| `split-right` | Two-column layout. Text on the left, waveform on the right, full-width seek bar at bottom. |

Reference layout images are included in `assets/`:

| Spec file | Description |
|-----------|-------------|
| `spec_classic_line.png` | classic + line waveform |
| `spec_classic_circular.png` | classic + circular waveform |
| `spec_spotlight_line.png` | spotlight + line waveform |
| `spec_spotlight_circular.png` | spotlight + circular waveform |
| `spec_split-left_line.png` | split-left + line waveform |
| `spec_split-left_circular.png` | split-left + circular waveform |
| `spec_split-right_line.png` | split-right + line waveform |
| `spec_split-right_circular.png` | split-right + circular waveform |
| `spec_cover.png` | cover image layout |

Each spec shows:
- Waveform area (blue for line, orange for circular)
- Text area (green)
- Seek bar (yellow)
- Dimensions and positions

---

## Wave Styles

The `--wave-style` flag controls how the waveform is drawn.

| Style | Description |
|-------|-------------|
| `line` | Classic mirrored waveform lines with fill. |
| `circular` | Radial waveform — bars project outward from a central ring. |

Both styles react to the audio in real-time. The circular style works best with spotlight layout.

---

## Film Grain

The `--grain` flag overlays animated film grain on every frame. The value is a float between `0.0` (no grain) and `1.0` (heavy grain). At `0.0` the effect is completely skipped with no performance cost.

```bash
# Subtle grain
uv run python visualizer.py \
    --audio "song.mp3" --background "cover.jpg" \
    --grain 0.1

# Noticeable grain
uv run python visualizer.py \
    --audio "song.mp3" --background "cover.jpg" \
    --grain 0.25
```

Each frame uses a unique random seed so the grain animates naturally without repeating patterns.

### Grain examples

| Intensity | Preview |
|-----------|---------|
| `0.0` — off | ![grain off](assets/grain_00.jpg) |
| `0.1` — subtle | ![grain 0.1](assets/grain_01.jpg) |
| `0.25` — noticeable | ![grain 0.25](assets/grain_025.jpg) |
| `0.15`, circular layout | ![grain circular](assets/grain_circular.jpg) |

---

## Output

- `<output>.mp4` — 3840×2160 (4K), 30 fps, H.264, AAC 320 kbps
- `<output>.jpg` — 4K cover image with centered text
