"""Tests for klangbild.__main__ — ID3 fallback logic in single-file mode."""

from argparse import Namespace
from unittest.mock import MagicMock, patch


class TestSingleFileFallback:
    """Verify that single-file mode reads ID3 tags when CLI args are omitted."""

    def _make_args(self, **overrides: object) -> Namespace:
        defaults: dict[str, object] = dict(
            audio="song.mp3",
            input_dir=None,
            background="bg.jpg",
            cover_background=None,
            title=None,
            artist=None,
            album=None,
            output="output.mp4",
            color="#ffffff",
            gpu="none",
            workers=2,
            font=None,
            font_bold=None,
            lang="en",
            layout="classic",
            wave_style="line",
            smoothing_window=15,
            temporal_alpha=0.35,
            text_gradient=None,
            text_gradient_dir="horizontal",
            wave_gradient=None,
            wave_gradient_dir="horizontal",
            grain=0.0,
        )
        defaults.update(overrides)
        return Namespace(**defaults)

    @patch("klangbild.__main__.process_file")
    @patch("klangbild.__main__.prepare_background")
    @patch("klangbild.__main__.read_id3_tags")
    @patch("klangbild.__main__.parse_args")
    @patch("klangbild.__main__.Path")
    def test_id3_used_when_no_cli_args(
        self,
        mock_path: MagicMock,
        mock_parse: MagicMock,
        mock_id3: MagicMock,
        mock_bg: MagicMock,
        mock_process: MagicMock,
    ) -> None:
        """When --title/--artist/--album are omitted, ID3 tags should be used."""
        from klangbild.__main__ import main

        mock_parse.return_value = self._make_args()
        mock_id3.return_value = ("ID3 Title", "ID3 Artist", "ID3 Album")
        mock_bg.return_value = MagicMock()

        # Make Path(...).exists() return True
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.stem = "song"
        mock_path_instance.is_dir.return_value = False
        mock_path.return_value = mock_path_instance

        main()

        mock_id3.assert_called_once_with("song.mp3")
        # process_file should have been called with ID3 tag values
        call_kwargs = mock_process.call_args
        assert (
            call_kwargs[1]["title"] == "ID3 Title" or call_kwargs[0][2] == "ID3 Title"
        )

    @patch("klangbild.__main__.process_file")
    @patch("klangbild.__main__.prepare_background")
    @patch("klangbild.__main__.read_id3_tags")
    @patch("klangbild.__main__.parse_args")
    @patch("klangbild.__main__.Path")
    def test_cli_args_override_id3(
        self,
        mock_path: MagicMock,
        mock_parse: MagicMock,
        mock_id3: MagicMock,
        mock_bg: MagicMock,
        mock_process: MagicMock,
    ) -> None:
        """CLI --title/--artist/--album should take precedence over ID3."""
        from klangbild.__main__ import main

        mock_parse.return_value = self._make_args(
            title="CLI Title",
            artist="CLI Artist",
            album="CLI Album",
        )
        mock_id3.return_value = ("ID3 Title", "ID3 Artist", "ID3 Album")
        mock_bg.return_value = MagicMock()

        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        main()

        call_kwargs = mock_process.call_args
        # CLI values should win
        assert (
            call_kwargs[1]["title"] == "CLI Title" or call_kwargs[0][2] == "CLI Title"
        )

    @patch("klangbild.__main__.process_file")
    @patch("klangbild.__main__.prepare_background")
    @patch("klangbild.__main__.read_id3_tags")
    @patch("klangbild.__main__.parse_args")
    @patch("klangbild.__main__.Path")
    def test_partial_cli_partial_id3(
        self,
        mock_path: MagicMock,
        mock_parse: MagicMock,
        mock_id3: MagicMock,
        mock_bg: MagicMock,
        mock_process: MagicMock,
    ) -> None:
        """CLI title given but not artist/album — artist/album should come from ID3."""
        from klangbild.__main__ import main

        mock_parse.return_value = self._make_args(title="My CLI Title")
        mock_id3.return_value = ("ID3 Title", "ID3 Artist", "ID3 Album")
        mock_bg.return_value = MagicMock()

        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        main()

        call_args = mock_process.call_args
        # Title from CLI, artist/album from ID3
        if call_args[1]:
            assert call_args[1]["title"] == "My CLI Title"
            assert call_args[1]["artist"] == "ID3 Artist"
            assert call_args[1]["album"] == "ID3 Album"
        else:
            assert call_args[0][2] == "My CLI Title"
            assert call_args[0][3] == "ID3 Artist"
            assert call_args[0][4] == "ID3 Album"
