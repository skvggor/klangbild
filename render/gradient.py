from PIL import Image, ImageDraw, ImageFont


def _lerp_color(c0: tuple, c1: tuple, t: float) -> tuple[int, int, int, int]:
    return (
        int(c0[0] + (c1[0] - c0[0]) * t),
        int(c0[1] + (c1[1] - c0[1]) * t),
        int(c0[2] + (c1[2] - c0[2]) * t),
        int(c0[3] + (c1[3] - c0[3]) * t),
    )


def _make_gradient_image(
    width: int,
    height: int,
    colors: list[tuple],
    direction: str = "horizontal",
) -> Image.Image:
    img = Image.new("RGBA", (width, height))
    draw = ImageDraw.Draw(img)
    n = len(colors)
    steps = height if direction == "vertical" else width

    for i in range(steps):
        t = i / max(steps - 1, 1)
        if n == 1:
            c = colors[0]
        else:
            seg_size = 1.0 / (n - 1)
            idx = min(int(t / seg_size), n - 2)
            t_local = (t - idx * seg_size) / seg_size
            c = _lerp_color(colors[idx], colors[idx + 1], t_local)
        if direction == "vertical":
            draw.line([(0, i), (width, i)], fill=c)
        else:
            draw.line([(i, 0), (i, height)], fill=c)

    return img


def draw_gradient_text(
    canvas: Image.Image,
    text: str,
    font: ImageFont.FreeTypeFont,
    x: int,
    y: int,
    gradient_colors: list[tuple],
    anchor: str | None = None,
    direction: str = "horizontal",
) -> None:
    if not gradient_colors:
        return

    bb = font.getbbox(text)
    tw = int(bb[2] - bb[0])
    th = int(bb[3] - bb[1])
    if tw <= 0 or th <= 0:
        return

    if anchor == "center":
        tx = int(x - tw // 2)
        ty = int(y - th // 2)
    elif anchor == "right":
        tx = int(x - tw)
        ty = int(y)
    else:
        tx = int(x)
        ty = int(y)

    text_img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_img)
    text_draw.text((-bb[0], -bb[1]), text, font=font, fill=(255, 255, 255, 255))

    grad_img = _make_gradient_image(tw, th, gradient_colors, direction=direction)

    text_alpha = text_img.split()[3]
    grad_img.putalpha(text_alpha)

    canvas.alpha_composite(grad_img, dest=(tx, ty))
