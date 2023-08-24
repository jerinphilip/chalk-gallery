from PIL import Image as PILImage
from chalk import *
from colour import Color
from chalk import BoundingBox
from copy import deepcopy
from .color_map import qualitative
from argparse import ArgumentParser


black = Color("#000000")
white = Color("#ffffff")


def Block(
    label: str,
    width: int = 40,
    height: int = 18,
    stroke: Color = black,
    fill: Color = white,
):
    radius = min(width, height) / 20
    font_size = min(width, height) / 3
    container = (
        rectangle(width, height, radius)
        .line_color(stroke)
        .fill_color(fill)
        .line_width(0)
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


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--path", type=str, required=True)
    args = parser.parse_args()
    width = 200
    height = 10
    rows = []
    for name, cmap in qualitative.items():
        n = len(cmap)
        w = width / n
        print(w, height)
        cells = [
            rectangle(w, height).fill_color(cmap[i]).line_width(0).center_xy()
            for i in range(n)
        ]

        label = [Block(name, width / 10, height)]
        row = hcat(label + cells).center_xy()
        rows.append(row)

    diagram = vcat(rows).center_xy()
    diagram.render_svg(args.path, height=512)
