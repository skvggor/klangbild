"""Shared fixtures for klangbild tests."""

import pytest
from PIL import Image, ImageFont

from klangbild.config.constants import WIDTH, HEIGHT
from klangbild.utils.fonts import load_font_bold, load_font_regular


@pytest.fixture()
def small_bg() -> Image.Image:
    """A small 200x100 RGB image for fast tests (avoids 4K overhead)."""
    return Image.new("RGB", (200, 100), (50, 100, 150))


@pytest.fixture()
def full_bg() -> Image.Image:
    """Full 4K RGBA background for integration-level tests."""
    return Image.new("RGB", (WIDTH, HEIGHT), (30, 30, 30))


@pytest.fixture()
def font_regular() -> ImageFont.FreeTypeFont:
    return load_font_regular(40)


@pytest.fixture()
def font_bold() -> ImageFont.FreeTypeFont:
    return load_font_bold(80)
