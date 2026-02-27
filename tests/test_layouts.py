"""Tests for klangbild.config.layouts."""

import pytest

from klangbild.config.constants import WIDTH, HEIGHT
from klangbild.config.layouts import get_layout_config

LAYOUTS = ["classic", "spotlight", "split-left", "split-right"]

# Every layout dict must contain these keys.
REQUIRED_KEYS = {
    "wave_width",
    "wave_height",
    "wave_center_x",
    "wave_center_y",
    "wave_x_start",
    "seek_bar_x",
    "seek_bar_y",
    "seek_bar_w",
    "seek_bar_h",
    "text_x",
    "text_y_title",
    "text_y_artist",
    "text_y_album",
    "text_y_time",
    "text_max_width",
    "font_size_title",
    "font_size_artist",
    "font_size_album",
    "font_size_time",
    "text_anchor",
    "wave_fade_width",
    "circular_radius",
}


class TestLayoutConfig:
    @pytest.mark.parametrize("layout", LAYOUTS)
    def test_has_all_required_keys(self, layout: str) -> None:
        lc = get_layout_config(layout)
        missing = REQUIRED_KEYS - set(lc.keys())
        assert not missing, f"Layout '{layout}' missing keys: {missing}"

    @pytest.mark.parametrize("layout", LAYOUTS)
    def test_wave_within_canvas(self, layout: str) -> None:
        lc = get_layout_config(layout)
        x0 = lc["wave_x_start"]
        w = lc["wave_width"]
        assert x0 >= 0, f"{layout}: wave_x_start < 0"
        assert x0 + w <= WIDTH, f"{layout}: wave extends beyond canvas width"

    @pytest.mark.parametrize("layout", LAYOUTS)
    def test_seek_bar_within_canvas(self, layout: str) -> None:
        lc = get_layout_config(layout)
        sb_x = lc["seek_bar_x"]
        sb_w = lc["seek_bar_w"]
        sb_y = lc["seek_bar_y"]
        sb_h = lc["seek_bar_h"]
        assert sb_x >= 0
        assert sb_x + sb_w <= WIDTH
        assert sb_y >= 0
        assert sb_y + sb_h <= HEIGHT

    @pytest.mark.parametrize("layout", LAYOUTS)
    def test_font_sizes_positive(self, layout: str) -> None:
        lc = get_layout_config(layout)
        for key in (
            "font_size_title",
            "font_size_artist",
            "font_size_album",
            "font_size_time",
        ):
            assert lc[key] > 0, f"{layout}: {key} is not positive"

    @pytest.mark.parametrize("layout", LAYOUTS)
    def test_font_size_hierarchy(self, layout: str) -> None:
        """Title should be largest, time should be smallest."""
        lc = get_layout_config(layout)
        assert lc["font_size_title"] > lc["font_size_artist"]
        assert lc["font_size_artist"] > lc["font_size_album"]
        assert lc["font_size_album"] > lc["font_size_time"]

    def test_classic_has_no_text_anchor(self) -> None:
        lc = get_layout_config("classic")
        assert lc["text_anchor"] is None

    def test_spotlight_has_center_anchor(self) -> None:
        lc = get_layout_config("spotlight")
        assert lc["text_anchor"] == "center"

    def test_split_left_has_no_anchor(self) -> None:
        lc = get_layout_config("split-left")
        assert lc["text_anchor"] is None

    def test_split_right_has_right_anchor(self) -> None:
        lc = get_layout_config("split-right")
        assert lc["text_anchor"] == "right"

    def test_unknown_layout_returns_classic(self) -> None:
        """Unknown layout name should fall through to classic defaults."""
        lc_unknown = get_layout_config("nonexistent")
        lc_classic = get_layout_config("classic")
        assert lc_unknown == lc_classic

    @pytest.mark.parametrize("layout", LAYOUTS)
    def test_circular_radius_positive(self, layout: str) -> None:
        lc = get_layout_config(layout)
        assert lc["circular_radius"] > 0
