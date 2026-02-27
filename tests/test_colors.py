"""Tests for klangbild.utils.colors."""

import argparse
import pytest

from klangbild.utils.colors import (
    hex_to_rgba,
    parse_gradient_colors,
    validate_gradient_colors,
    validate_hex_color,
)


# ---------------------------------------------------------------------------
# hex_to_rgba
# ---------------------------------------------------------------------------


class TestHexToRgba:
    def test_full_hex_white(self) -> None:
        assert hex_to_rgba("#FFFFFF") == (255, 255, 255, 255)

    def test_full_hex_black(self) -> None:
        assert hex_to_rgba("#000000") == (0, 0, 0, 255)

    def test_full_hex_arbitrary(self) -> None:
        assert hex_to_rgba("#1A2B3C") == (0x1A, 0x2B, 0x3C, 255)

    def test_short_hex(self) -> None:
        # #FFF -> #FFFFFF
        assert hex_to_rgba("#FFF") == (255, 255, 255, 255)

    def test_short_hex_color(self) -> None:
        # #F00 -> #FF0000
        assert hex_to_rgba("#F00") == (255, 0, 0, 255)

    def test_custom_alpha(self) -> None:
        assert hex_to_rgba("#FF0000", alpha=128) == (255, 0, 0, 128)

    def test_alpha_zero(self) -> None:
        assert hex_to_rgba("#ABCDEF", alpha=0) == (0xAB, 0xCD, 0xEF, 0)

    def test_no_hash_prefix(self) -> None:
        # The function strips '#' with lstrip
        assert hex_to_rgba("FF8000") == (255, 128, 0, 255)

    def test_lowercase_hex(self) -> None:
        assert hex_to_rgba("#abcdef") == (0xAB, 0xCD, 0xEF, 255)


# ---------------------------------------------------------------------------
# validate_hex_color
# ---------------------------------------------------------------------------


class TestValidateHexColor:
    def test_valid_6_digit(self) -> None:
        assert validate_hex_color("#FFFFFF") == "#ffffff"

    def test_valid_3_digit(self) -> None:
        assert validate_hex_color("#FFF") == "#fff"

    def test_returns_lowercase(self) -> None:
        assert validate_hex_color("#AABBCC") == "#aabbcc"

    def test_invalid_length(self) -> None:
        with pytest.raises(argparse.ArgumentTypeError, match="Invalid color"):
            validate_hex_color("#FFFF")

    def test_invalid_chars(self) -> None:
        with pytest.raises(argparse.ArgumentTypeError, match="Invalid color"):
            validate_hex_color("#GGGGGG")

    def test_empty_after_hash(self) -> None:
        with pytest.raises(argparse.ArgumentTypeError):
            validate_hex_color("#")


# ---------------------------------------------------------------------------
# validate_gradient_colors
# ---------------------------------------------------------------------------


class TestValidateGradientColors:
    def test_valid_two_colors(self) -> None:
        result = validate_gradient_colors("#FFFFFF,#000000")
        assert result == "#ffffff,#000000"

    def test_valid_three_colors(self) -> None:
        result = validate_gradient_colors("#FF0000,#00FF00,#0000FF")
        assert result == "#ff0000,#00ff00,#0000ff"

    def test_single_color_rejected(self) -> None:
        with pytest.raises(argparse.ArgumentTypeError, match="at least 2 colors"):
            validate_gradient_colors("#FFFFFF")

    def test_invalid_color_in_list(self) -> None:
        with pytest.raises(argparse.ArgumentTypeError, match="Invalid gradient color"):
            validate_gradient_colors("#FFFFFF,notacolor")

    def test_short_hex_in_gradient(self) -> None:
        result = validate_gradient_colors("#FFF,#000")
        assert result == "#fff,#000"


# ---------------------------------------------------------------------------
# parse_gradient_colors
# ---------------------------------------------------------------------------


class TestParseGradientColors:
    def test_two_colors(self) -> None:
        result = parse_gradient_colors("#FFFFFF,#000000")
        assert result == [(255, 255, 255, 255), (0, 0, 0, 255)]

    def test_three_colors(self) -> None:
        result = parse_gradient_colors("#FF0000,#00FF00,#0000FF")
        assert len(result) == 3
        assert result[0] == (255, 0, 0, 255)
        assert result[1] == (0, 255, 0, 255)
        assert result[2] == (0, 0, 255, 255)

    def test_short_hex(self) -> None:
        result = parse_gradient_colors("#F00,#0F0")
        assert result[0] == (255, 0, 0, 255)
        assert result[1] == (0, 255, 0, 255)

    def test_empty_string(self) -> None:
        assert parse_gradient_colors("") == []

    def test_invalid_no_hash(self) -> None:
        with pytest.raises(ValueError, match="must start with #"):
            parse_gradient_colors("FFFFFF,000000")

    def test_invalid_length(self) -> None:
        with pytest.raises(ValueError, match="#RGB or #RRGGBB"):
            parse_gradient_colors("#FFFF,#000000")

    def test_spaces_are_stripped(self) -> None:
        result = parse_gradient_colors("#FFFFFF, #000000")
        assert result == [(255, 255, 255, 255), (0, 0, 0, 255)]

    def test_alpha_always_255(self) -> None:
        result = parse_gradient_colors("#808080,#C0C0C0")
        for rgba in result:
            assert rgba[3] == 255
