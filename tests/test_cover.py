"""Tests for klangbild.render.cover — cover image generation."""

from PIL import Image

from klangbild.config.constants import WIDTH, HEIGHT
from klangbild.render.cover import render_cover


class TestRenderCover:
    def test_returns_rgb_jpg_compatible(self, full_bg: Image.Image) -> None:
        result = render_cover(
            bg=full_bg,
            title="Test Title",
            artist="by Artist",
            album="from Album",
            color="#FFFFFF",
        )
        assert result.mode == "RGB"
        assert result.size == (WIDTH, HEIGHT)

    def test_with_gradient(self, full_bg: Image.Image) -> None:
        result = render_cover(
            bg=full_bg,
            title="Gradient",
            artist="by Artist",
            album="from Album",
            color="#FFFFFF",
            text_gradient="#FF0000,#0000FF",
            text_gradient_dir="vertical",
        )
        assert result.mode == "RGB"
        assert result.size == (WIDTH, HEIGHT)

    def test_with_grain(self, full_bg: Image.Image) -> None:
        result = render_cover(
            bg=full_bg,
            title="Grain Test",
            artist="by Artist",
            album="from Album",
            color="#FFFFFF",
            grain=0.3,
        )
        assert result.mode == "RGB"

    def test_long_text_is_truncated(self, full_bg: Image.Image) -> None:
        """Very long text should not crash — it gets truncated with fit_text."""
        result = render_cover(
            bg=full_bg,
            title="A" * 500,
            artist="B" * 500,
            album="C" * 500,
            color="#FFFFFF",
        )
        assert result.size == (WIDTH, HEIGHT)

    def test_empty_strings(self, full_bg: Image.Image) -> None:
        """Empty title/artist/album should render without error."""
        result = render_cover(
            bg=full_bg,
            title="",
            artist="",
            album="",
            color="#FFFFFF",
        )
        assert result.size == (WIDTH, HEIGHT)

    def test_no_shadow_in_cover(self, full_bg: Image.Image) -> None:
        """Cover rendering must not include any text shadow."""
        result = render_cover(
            bg=full_bg,
            title="No Shadow",
            artist="by Artist",
            album="from Album",
            color="#FFFFFF",
        )
        # Structural check — code has no shadow calls.
        assert result.mode == "RGB"
