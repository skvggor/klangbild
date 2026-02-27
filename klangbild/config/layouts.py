from .constants import (
    HEIGHT,
    SEEK_BAR_H,
    SEEK_BAR_W,
    SEEK_BAR_X,
    SEEK_BAR_Y,
    TEXT_X,
    TEXT_Y_ALBUM,
    TEXT_Y_ARTIST,
    TEXT_Y_TIME,
    TEXT_Y_TITLE,
    WAVE_CENTER_Y,
    WAVE_FADE_WIDTH,
    WAVE_HEIGHT,
    WAVE_WIDTH,
    WAVE_X_START,
    WIDTH,
)


def get_layout_config(layout: str) -> dict:
    if layout == "spotlight":
        _seek_h = 10
        _seek_w = 2800
        _seek_x = (WIDTH - _seek_w) // 2
        _seek_y = HEIGHT // 2 - 400

        _text_x = WIDTH // 2
        _text_y_title = HEIGHT // 2 - 100
        _text_y_artist = _text_y_title + 180
        _text_y_album = _text_y_artist + 140
        _text_y_time = _text_y_album + 140

        _wave_w = 2800
        _wave_h = 200
        _wave_cx = WIDTH // 2
        _wave_cy = _text_y_time + 400
        _wave_x_start = (WIDTH - _wave_w) // 2

        return dict(
            wave_width=_wave_w,
            wave_height=_wave_h,
            wave_center_x=_wave_cx,
            wave_center_y=_wave_cy,
            wave_x_start=_wave_x_start,
            seek_bar_x=_seek_x,
            seek_bar_y=_seek_y,
            seek_bar_w=_seek_w,
            seek_bar_h=_seek_h,
            text_x=_text_x,
            text_y_title=_text_y_title,
            text_y_artist=_text_y_artist,
            text_y_album=_text_y_album,
            text_y_time=_text_y_time,
            text_max_width=_seek_w,
            font_size_title=120,
            font_size_artist=80,
            font_size_album=64,
            font_size_time=56,
            text_anchor="center",
            wave_fade_width=220,
            circular_radius=450,
        )

    if layout in ("split-left", "split-right"):
        _central_area = 3200
        _gap = 80
        _col_w = (_central_area - 3 * _gap) // 2
        _central_start = (WIDTH - _central_area) // 2

        _wave_h = 280
        _wave_cy = HEIGHT // 2

        if layout == "split-left":
            _wave_col_start = _central_start + _gap
            _wave_col_end = _wave_col_start + _col_w
            _wave_cx = _wave_col_start + _col_w // 2
            _wave_x_start = _wave_col_start
            _text_col_start = _wave_col_end + _gap
            _text_x = _text_col_start
            _text_anchor = None
        else:
            _text_col_start = _central_start + _gap
            _text_x = _text_col_start + _col_w
            _text_anchor = "right"
            _wave_col_start = _text_col_start + _col_w + _gap
            _wave_cx = _wave_col_start + _col_w // 2
            _wave_x_start = _wave_col_start

        _wave_w = _col_w

        _block_h = 120 + 90 + 80 + 70
        _text_y_title = HEIGHT // 2 - _block_h // 2
        _text_y_artist = _text_y_title + 140
        _text_y_album = _text_y_artist + 110
        _text_y_time = _text_y_album + 100

        _margin = 160
        _seek_h = 10
        _seek_w = WIDTH - 2 * _margin
        _seek_x = _margin
        _seek_y = HEIGHT - 160

        return dict(
            wave_width=_wave_w,
            wave_height=_wave_h,
            wave_center_x=_wave_cx,
            wave_center_y=_wave_cy,
            wave_x_start=_wave_x_start,
            seek_bar_x=_seek_x,
            seek_bar_y=_seek_y,
            seek_bar_w=_seek_w,
            seek_bar_h=_seek_h,
            text_x=_text_x,
            text_y_title=_text_y_title,
            text_y_artist=_text_y_artist,
            text_y_album=_text_y_album,
            text_y_time=_text_y_time,
            text_max_width=_col_w,
            font_size_title=100,
            font_size_artist=72,
            font_size_album=60,
            font_size_time=52,
            text_anchor=_text_anchor,
            wave_fade_width=140,
            circular_radius=450,
        )

    return dict(
        wave_width=WAVE_WIDTH,
        wave_height=WAVE_HEIGHT,
        wave_center_x=WIDTH // 2,
        wave_center_y=WAVE_CENTER_Y,
        wave_x_start=WAVE_X_START,
        seek_bar_x=SEEK_BAR_X,
        seek_bar_y=SEEK_BAR_Y,
        seek_bar_w=SEEK_BAR_W,
        seek_bar_h=SEEK_BAR_H,
        text_x=TEXT_X,
        text_y_title=TEXT_Y_TITLE,
        text_y_artist=TEXT_Y_ARTIST,
        text_y_album=TEXT_Y_ALBUM,
        text_y_time=TEXT_Y_TIME,
        text_max_width=SEEK_BAR_W,
        font_size_title=80,
        font_size_artist=60,
        font_size_album=50,
        font_size_time=40,
        text_anchor=None,
        wave_fade_width=WAVE_FADE_WIDTH,
        circular_radius=500,
    )
