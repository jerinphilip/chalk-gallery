from PIL import Image as PILImage
from chalk import *
from colour import Color
from chalk import BoundingBox
from copy import deepcopy
from .color_map import qualitative
from argparse import ArgumentParser

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--path", type=str, required=True)
    args = parser.parse_args()
    width = 200
    height = 10
    rows = []
    for cmap in qualitative:
        n = len(cmap)
        w = width / n
        print(w, height)
        cells = [
            rectangle(w, height).fill_color(cmap[i]).line_width(0).center_xy()
            for i in range(n)
        ]
        row = hcat(cells).center_xy()
        rows.append(row)

    diagram = vcat(rows).center_xy()
    diagram.render_svg(args.path, height=512)
