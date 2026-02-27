import argparse
from typing import Any


def hex_to_rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r, g, b, alpha)


def validate_hex_color(value: str) -> str:
    h = value.lstrip("#")
    if len(h) not in (3, 6) or not all(c in "0123456789abcdefABCDEF" for c in h):
        raise argparse.ArgumentTypeError(
            f"Invalid color '{value}'. Expected #RGB or #RRGGBB (e.g. #FFF or #FFFFFF)."
        )
    return value.lower()


def validate_gradient_colors(value: str) -> str:
    colors = value.split(",")
    if len(colors) < 2:
        raise argparse.ArgumentTypeError(
            f"Gradient requires at least 2 colors, got: '{value}'. "
            "Format: #RRGGBB,#RRGGBB or #RRGGBB,#RRGGBB,#RRGGBB,..."
        )
    for color in colors:
        color = color.strip()
        h = color.lstrip("#")
        if (
            not color.startswith("#")
            or len(h) not in (3, 6)
            or not all(c in "0123456789abcdefABCDEF" for c in h)
        ):
            raise argparse.ArgumentTypeError(
                f"Invalid gradient color '{color}'. Expected #RGB or #RRGGBB."
            )
    return value.lower()


def parse_gradient_colors(color_str: str) -> list[tuple]:
    if not color_str:
        return []

    colors = color_str.split(",")
    rgba_colors = []
    for color in colors:
        color = color.strip()
        if not color.startswith("#"):
            raise ValueError(f"Gradient color must start with #: {color}")
        if len(color) not in [4, 7]:
            raise ValueError(f"Gradient color must be #RGB or #RRGGBB: {color}")

        if len(color) == 4:
            r = int(color[1] * 2, 16)
            g = int(color[2] * 2, 16)
            b = int(color[3] * 2, 16)
        else:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)

        rgba_colors.append((r, g, b, 255))

    return rgba_colors
