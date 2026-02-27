"""Tests for klangbild.cli — argument parsing."""

import sys
from argparse import Namespace
from unittest.mock import patch

import pytest

from klangbild.cli import parse_args
from klangbild.config.constants import SMOOTHING_WINDOW, TEMPORAL_ALPHA


def _parse(*args: str) -> Namespace:
    """Run parse_args with the given CLI arguments."""
    with patch.object(sys, "argv", ["klangbild", *args]):
        return parse_args()


class TestCliDefaults:
    def test_minimal_single_file(self) -> None:
        ns = _parse("--audio", "song.mp3", "--background", "bg.jpg")
        assert ns.audio == "song.mp3"
        assert ns.background == "bg.jpg"
        assert ns.output == "output.mp4"
        assert ns.gpu == "none"
        assert ns.color == "#ffffff"
        assert ns.layout == "classic"
        assert ns.wave_style == "line"
        assert ns.grain == 0.0
        assert ns.text_gradient is None
        assert ns.wave_gradient is None
        assert ns.cover_background is None
        assert ns.smoothing_window == SMOOTHING_WINDOW
        assert ns.temporal_alpha == TEMPORAL_ALPHA

    def test_batch_mode(self) -> None:
        ns = _parse("--input-dir", "/music", "--background", "bg.jpg")
        assert ns.input_dir == "/music"
        assert ns.audio is None

    def test_title_artist_album(self) -> None:
        ns = _parse(
            "--audio",
            "x.mp3",
            "--background",
            "bg.jpg",
            "--title",
            "My Song",
            "--artist",
            "Me",
            "--album",
            "My Album",
        )
        assert ns.title == "My Song"
        assert ns.artist == "Me"
        assert ns.album == "My Album"

    def test_default_title_is_none(self) -> None:
        """When --title is not given it should be None (not the stem)."""
        ns = _parse("--audio", "x.mp3", "--background", "bg.jpg")
        assert ns.title is None
        assert ns.artist is None
        assert ns.album is None


class TestCliOptions:
    def test_gpu_nvenc(self) -> None:
        ns = _parse("--audio", "x.mp3", "--background", "bg.jpg", "--gpu", "nvenc")
        assert ns.gpu == "nvenc"

    def test_gpu_vaapi(self) -> None:
        ns = _parse("--audio", "x.mp3", "--background", "bg.jpg", "--gpu", "vaapi")
        assert ns.gpu == "vaapi"

    def test_invalid_gpu(self) -> None:
        with pytest.raises(SystemExit):
            _parse("--audio", "x.mp3", "--background", "bg.jpg", "--gpu", "cuda")

    def test_layout_choices(self) -> None:
        for layout in ("classic", "spotlight", "split-left", "split-right"):
            ns = _parse(
                "--audio", "x.mp3", "--background", "bg.jpg", "--layout", layout
            )
            assert ns.layout == layout

    def test_invalid_layout(self) -> None:
        with pytest.raises(SystemExit):
            _parse("--audio", "x.mp3", "--background", "bg.jpg", "--layout", "crazy")

    def test_wave_style_choices(self) -> None:
        for style in ("line", "circular"):
            ns = _parse(
                "--audio", "x.mp3", "--background", "bg.jpg", "--wave-style", style
            )
            assert ns.wave_style == style

    def test_grain_value(self) -> None:
        ns = _parse("--audio", "x.mp3", "--background", "bg.jpg", "--grain", "0.5")
        assert ns.grain == 0.5

    def test_color_validated(self) -> None:
        ns = _parse("--audio", "x.mp3", "--background", "bg.jpg", "--color", "#FF8000")
        assert ns.color == "#ff8000"

    def test_invalid_color(self) -> None:
        with pytest.raises(SystemExit):
            _parse("--audio", "x.mp3", "--background", "bg.jpg", "--color", "notacolor")

    def test_text_gradient(self) -> None:
        ns = _parse(
            "--audio",
            "x.mp3",
            "--background",
            "bg.jpg",
            "--text-gradient",
            "#FF0000,#0000FF",
        )
        assert ns.text_gradient == "#ff0000,#0000ff"

    def test_wave_gradient(self) -> None:
        ns = _parse(
            "--audio",
            "x.mp3",
            "--background",
            "bg.jpg",
            "--wave-gradient",
            "#00FF00,#FFFF00",
        )
        assert ns.wave_gradient == "#00ff00,#ffff00"

    def test_lang_en(self) -> None:
        ns = _parse("--audio", "x.mp3", "--background", "bg.jpg", "--lang", "en")
        assert ns.lang == "en"

    def test_lang_pt(self) -> None:
        ns = _parse("--audio", "x.mp3", "--background", "bg.jpg", "--lang", "pt")
        assert ns.lang == "pt"

    def test_workers(self) -> None:
        ns = _parse("--audio", "x.mp3", "--background", "bg.jpg", "--workers", "8")
        assert ns.workers == 8

    def test_cover_background(self) -> None:
        ns = _parse(
            "--audio",
            "x.mp3",
            "--background",
            "bg.jpg",
            "--cover-background",
            "cover_bg.jpg",
        )
        assert ns.cover_background == "cover_bg.jpg"

    def test_background_is_required(self) -> None:
        with pytest.raises(SystemExit):
            _parse("--audio", "x.mp3")

    def test_text_gradient_dir_horizontal(self) -> None:
        ns = _parse(
            "--audio",
            "x.mp3",
            "--background",
            "bg.jpg",
            "--text-gradient",
            "#FF0000,#0000FF",
            "--text-gradient-dir",
            "horizontal",
        )
        assert ns.text_gradient_dir == "horizontal"

    def test_text_gradient_dir_vertical(self) -> None:
        ns = _parse(
            "--audio",
            "x.mp3",
            "--background",
            "bg.jpg",
            "--text-gradient",
            "#FF0000,#0000FF",
            "--text-gradient-dir",
            "vertical",
        )
        assert ns.text_gradient_dir == "vertical"

    def test_wave_gradient_dir_horizontal(self) -> None:
        ns = _parse(
            "--audio",
            "x.mp3",
            "--background",
            "bg.jpg",
            "--wave-gradient",
            "#00FF00,#FFFF00",
            "--wave-gradient-dir",
            "horizontal",
        )
        assert ns.wave_gradient_dir == "horizontal"

    def test_wave_gradient_dir_vertical(self) -> None:
        ns = _parse(
            "--audio",
            "x.mp3",
            "--background",
            "bg.jpg",
            "--wave-gradient",
            "#00FF00,#FFFF00",
            "--wave-gradient-dir",
            "vertical",
        )
        assert ns.wave_gradient_dir == "vertical"

    def test_invalid_gradient_dir(self) -> None:
        with pytest.raises(SystemExit):
            _parse(
                "--audio",
                "x.mp3",
                "--background",
                "bg.jpg",
                "--text-gradient-dir",
                "diagonal",
            )

    def test_smoothing_window_custom(self) -> None:
        ns = _parse(
            "--audio",
            "x.mp3",
            "--background",
            "bg.jpg",
            "--smoothing-window",
            "25",
        )
        assert ns.smoothing_window == 25

    def test_temporal_alpha_custom(self) -> None:
        ns = _parse(
            "--audio",
            "x.mp3",
            "--background",
            "bg.jpg",
            "--temporal-alpha",
            "0.5",
        )
        assert ns.temporal_alpha == 0.5

    def test_font_and_font_bold(self) -> None:
        ns = _parse(
            "--audio",
            "x.mp3",
            "--background",
            "bg.jpg",
            "--font",
            "Regular.ttf",
            "--font-bold",
            "Bold.ttf",
        )
        assert ns.font == "Regular.ttf"
        assert ns.font_bold == "Bold.ttf"

    def test_default_font_is_none(self) -> None:
        ns = _parse("--audio", "x.mp3", "--background", "bg.jpg")
        assert ns.font is None
        assert ns.font_bold is None

    def test_default_lang_is_en(self) -> None:
        ns = _parse("--audio", "x.mp3", "--background", "bg.jpg")
        assert ns.lang == "en"

    def test_invalid_lang(self) -> None:
        with pytest.raises(SystemExit):
            _parse("--audio", "x.mp3", "--background", "bg.jpg", "--lang", "fr")

    def test_invalid_wave_style(self) -> None:
        with pytest.raises(SystemExit):
            _parse(
                "--audio",
                "x.mp3",
                "--background",
                "bg.jpg",
                "--wave-style",
                "spiral",
            )

    def test_default_gradient_dirs(self) -> None:
        ns = _parse("--audio", "x.mp3", "--background", "bg.jpg")
        assert ns.text_gradient_dir == "horizontal"
        assert ns.wave_gradient_dir == "horizontal"

    def test_output_custom_path(self) -> None:
        ns = _parse(
            "--audio",
            "x.mp3",
            "--background",
            "bg.jpg",
            "--output",
            "/tmp/my_video.mp4",
        )
        assert ns.output == "/tmp/my_video.mp4"
