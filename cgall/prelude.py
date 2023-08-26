from chalk import *
from colour import Color

black = Color("#000000")
white = Color("#ffffff")


def Block(
    label: str,
    width: int = 40,
    height: int = 18,
    stroke: Color = black,
    fill: Color = white,
    line_width: float = 0.05,
):
    radius = min(width, height) / 20
    font_size = min(width, height) / 3
    container = (
        rectangle(width, height, radius)
        .line_color(stroke)
        .fill_color(fill)
        .line_width(line_width)
    ).center_xy()

    bounding_rect = container.scale(0.9).center_xy()
    render_label = (
        text(label, font_size)
        .line_color(black)
        .line_width(0)
        .fill_color(black)
        .with_envelope(bounding_rect)
    ).translate(0, height / 16)

    return container + render_label
