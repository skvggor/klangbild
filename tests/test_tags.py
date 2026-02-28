"""Tests for klangbild.audio.tags — ID3 tag reading."""

import pytest
from mutagen.id3 import ID3, TIT2, TPE1, TALB

from klangbild.audio.tags import read_id3_tags


def _make_mp3_with_tags(
    path: str,
    title: str | None = None,
    artist: str | None = None,
    album: str | None = None,
) -> None:
    """Create a minimal valid MP3 file with optional ID3 tags.

    We write a tiny MPEG frame (silence) so mutagen recognises it as audio,
    then overlay ID3v2 tags.
    """
    # Minimal valid MPEG audio frame (MPEG1 Layer3, 128kbps, 44100Hz, stereo)
    # Frame header: 0xFFFB9004 followed by zeros to fill one frame (417 bytes).
    frame_header = b"\xff\xfb\x90\x04"
    frame_data = frame_header + b"\x00" * 413
    with open(path, "wb") as f:
        f.write(frame_data * 3)  # write a few frames

    # Now write ID3 tags
    tags = ID3()
    if title is not None:
        tags.add(TIT2(encoding=3, text=[title]))
    if artist is not None:
        tags.add(TPE1(encoding=3, text=[artist]))
    if album is not None:
        tags.add(TALB(encoding=3, text=[album]))
    tags.save(path)


class TestReadId3Tags:
    def test_reads_all_tags(self, tmp_path: pytest.TempPathFactory) -> None:
        mp3 = str(tmp_path / "song.mp3")  # type: ignore[operator]
        _make_mp3_with_tags(
            mp3, title="My Song", artist="The Artist", album="The Album"
        )
        title, artist, album = read_id3_tags(mp3)
        assert title == "My Song"
        assert artist == "The Artist"
        assert album == "The Album"

    def test_missing_tags_fallback(self, tmp_path: pytest.TempPathFactory) -> None:
        """When no ID3 tags exist, title falls back to filename stem."""
        mp3 = str(tmp_path / "cool_track.mp3")  # type: ignore[operator]
        # Write a bare MP3 without tags
        frame_header = b"\xff\xfb\x90\x04"
        with open(mp3, "wb") as f:
            f.write((frame_header + b"\x00" * 413) * 3)
        title, artist, album = read_id3_tags(mp3)
        assert title == "cool_track"
        assert artist == ""
        assert album == ""

    def test_partial_tags(self, tmp_path: pytest.TempPathFactory) -> None:
        """Only title set — artist/album should be empty."""
        mp3 = str(tmp_path / "partial.mp3")  # type: ignore[operator]
        _make_mp3_with_tags(mp3, title="Only Title")
        title, artist, album = read_id3_tags(mp3)
        assert title == "Only Title"
        assert artist == ""
        assert album == ""

    def test_empty_title_falls_back_to_stem(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """A tag with empty text should fall back to filename stem."""
        mp3 = str(tmp_path / "fallback.mp3")  # type: ignore[operator]
        _make_mp3_with_tags(mp3, title="", artist="Artist")
        title, artist, album = read_id3_tags(mp3)
        assert title == "fallback"  # stem
        assert artist == "Artist"

    def test_whitespace_title_falls_back(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        mp3 = str(tmp_path / "spaces.mp3")  # type: ignore[operator]
        _make_mp3_with_tags(mp3, title="   ", artist="A")
        title, artist, album = read_id3_tags(mp3)
        # .strip() turns "   " into "" which is falsy -> stem
        assert title == "spaces"

    def test_corrupt_file_returns_defaults(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """A corrupt/non-MP3 file should not crash — returns defaults."""
        bad = str(tmp_path / "corrupt.mp3")  # type: ignore[operator]
        with open(bad, "wb") as f:
            f.write(b"this is not an mp3")
        title, artist, album = read_id3_tags(bad)
        assert title == "corrupt"
        assert artist == ""
        assert album == ""
