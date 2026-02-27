"""Tests for klangbild.utils.time."""

import pytest

from klangbild.config.constants import FADE_DURATION, FPS
from klangbild.utils.time import compute_fade_alphas, format_time


# ---------------------------------------------------------------------------
# format_time
# ---------------------------------------------------------------------------


class TestFormatTime:
    def test_zero(self) -> None:
        assert format_time(0.0) == "00:00"

    def test_one_minute(self) -> None:
        assert format_time(60.0) == "01:00"

    def test_mixed(self) -> None:
        assert format_time(125.0) == "02:05"

    def test_fractional_rounds_down(self) -> None:
        # int(65.9) == 65 -> 1:05
        assert format_time(65.9) == "01:05"

    def test_large_value(self) -> None:
        assert format_time(3600.0) == "60:00"

    def test_single_digit_padded(self) -> None:
        assert format_time(9.0) == "00:09"


# ---------------------------------------------------------------------------
# compute_fade_alphas
# ---------------------------------------------------------------------------


class TestComputeFadeAlphas:
    def test_middle_of_track_fully_opaque(self) -> None:
        """Well inside the track (not near start/end) everything should be ~1.0."""
        n_frames = FPS * 60  # 60 seconds
        mid = n_frames // 2
        bg, wave, ui = compute_fade_alphas(mid, n_frames, FPS)
        assert bg == pytest.approx(1.0, abs=0.01)
        assert wave == pytest.approx(1.0, abs=0.01)
        assert ui == pytest.approx(1.0, abs=0.01)

    def test_first_frame_nearly_zero(self) -> None:
        """At frame 0 everything should be at or near 0."""
        n_frames = FPS * 60
        bg, wave, ui = compute_fade_alphas(0, n_frames, FPS)
        assert bg == pytest.approx(0.0, abs=0.05)
        assert wave == pytest.approx(0.0, abs=0.05)
        assert ui == pytest.approx(0.0, abs=0.05)

    def test_last_frame_nearly_zero(self) -> None:
        """At the last frame everything should have faded out."""
        n_frames = FPS * 60
        bg, wave, ui = compute_fade_alphas(n_frames - 1, n_frames, FPS)
        assert bg <= 0.05
        assert wave <= 0.05
        assert ui <= 0.05

    def test_fade_in_ordering(self) -> None:
        """Background fades in first, then wave, then UI."""
        n_frames = FPS * 60
        # At 0.3 seconds: bg should be partially faded, wave/ui still at 0
        frame = int(0.3 * FPS)
        bg, wave, ui = compute_fade_alphas(frame, n_frames, FPS)
        assert bg > 0.0
        assert bg >= wave
        assert wave >= ui

    def test_alphas_in_valid_range(self) -> None:
        """All alpha values must be in [0.0, 1.0]."""
        n_frames = FPS * 30
        for i in range(0, n_frames, FPS):  # sample every second
            bg, wave, ui = compute_fade_alphas(i, n_frames, FPS)
            for val in (bg, wave, ui):
                assert 0.0 <= val <= 1.0, f"frame {i}: alpha {val} out of range"

    def test_very_short_track(self) -> None:
        """A track shorter than FADE_DURATION should not crash."""
        n_frames = int(FADE_DURATION * FPS) // 2  # half of fade duration
        # Should not raise
        bg, wave, ui = compute_fade_alphas(0, n_frames, FPS)
        assert 0.0 <= bg <= 1.0
