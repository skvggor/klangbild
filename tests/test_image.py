"""Tests for klangbild.utils.image — background preparation."""

from pathlib import Path

import numpy as np
from PIL import Image

from klangbild.config.constants import WIDTH, HEIGHT
from klangbild.utils.image import prepare_background


class TestPrepareBackground:
    def _save_tmp_image(
        self, tmp_path: Path, w: int, h: int, color: tuple[int, int, int]
    ) -> str:
        img = Image.new("RGB", (w, h), color)
        path = str(tmp_path / "bg.jpg")
        img.save(path, "JPEG")
        return path

    def test_output_is_correct_size(self, tmp_path: Path) -> None:
        path = self._save_tmp_image(tmp_path, 4000, 2200, (100, 150, 200))
        result = prepare_background(path)
        assert result.size == (WIDTH, HEIGHT)

    def test_output_is_rgb(self, tmp_path: Path) -> None:
        path = self._save_tmp_image(tmp_path, 4000, 2200, (100, 150, 200))
        result = prepare_background(path)
        assert result.mode == "RGB"

    def test_no_darkening_applied(self, tmp_path: Path) -> None:
        """Background must NOT be darkened — pixel values should stay the same.

        We use a solid-color image so after resize+crop the pixels should
        remain at the original color (within JPEG compression tolerance).
        """
        color = (180, 120, 60)
        path = self._save_tmp_image(tmp_path, WIDTH, HEIGHT, color)
        result = prepare_background(path)
        arr = np.array(result)
        mean_r = arr[:, :, 0].mean()
        mean_g = arr[:, :, 1].mean()
        mean_b = arr[:, :, 2].mean()
        # JPEG compression may shift values slightly, but should be close
        assert abs(mean_r - color[0]) < 5, (
            f"Red channel darkened: {mean_r} vs {color[0]}"
        )
        assert abs(mean_g - color[1]) < 5, (
            f"Green channel darkened: {mean_g} vs {color[1]}"
        )
        assert abs(mean_b - color[2]) < 5, (
            f"Blue channel darkened: {mean_b} vs {color[2]}"
        )

    def test_wider_image_is_cropped_correctly(self, tmp_path: Path) -> None:
        """A wider-than-target image should be center-cropped horizontally."""
        path = self._save_tmp_image(tmp_path, 6000, 2160, (200, 200, 200))
        result = prepare_background(path)
        assert result.size == (WIDTH, HEIGHT)

    def test_taller_image_is_cropped_correctly(self, tmp_path: Path) -> None:
        """A taller-than-target image should be center-cropped vertically."""
        path = self._save_tmp_image(tmp_path, 3840, 4000, (200, 200, 200))
        result = prepare_background(path)
        assert result.size == (WIDTH, HEIGHT)

    def test_small_image_is_upscaled(self, tmp_path: Path) -> None:
        """A tiny image should be upscaled to fill the canvas."""
        path = self._save_tmp_image(tmp_path, 100, 100, (50, 100, 150))
        result = prepare_background(path)
        assert result.size == (WIDTH, HEIGHT)

    def test_exact_size_image_unchanged(self, tmp_path: Path) -> None:
        """An image already at target size should pass through cleanly."""
        color = (128, 64, 32)
        # Use PNG to avoid JPEG compression artifacts
        img = Image.new("RGB", (WIDTH, HEIGHT), color)
        path = str(tmp_path / "exact.png")
        img.save(path, "PNG")
        result = prepare_background(path)
        assert result.size == (WIDTH, HEIGHT)
        # With PNG there should be no compression artifacts
        px = result.getpixel((WIDTH // 2, HEIGHT // 2))
        assert px == color
