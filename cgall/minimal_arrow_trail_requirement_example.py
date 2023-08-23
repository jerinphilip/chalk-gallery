from PIL import Image as PILImage
from chalk import *
from colour import Color
from copy import deepcopy
from argparse import ArgumentParser


EM = 12
LINE_WIDTH = 0.05

black = Color("#000000")
white = Color("#ffffff")
grey = Color("#cccccc")
green = Color("#00ff00")


def Block(
    label: str,
    width: int = 5 * EM,
    height: int = 2 * EM,
    stroke: Color = black,
    fill: Color = white,
):
    radius = min(width, height) / 20
    font_size = min(width, height) / 2
    container = (
        rectangle(width, height, radius)
        .line_color(stroke)
        .fill_color(fill)
        .line_width(LINE_WIDTH)
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

    A_block = Block("A").named("A")
    node = square(1).fill_color(None).line_color(None)
    A = vcat([node.named("a"), A_block]).center_xy()

    B_block = Block("B").named("B")
    B = hcat([node.named("b"), B_block]).center_xy()

    diagram = hcat([A, B], 2 * EM)
    trail = Trail.from_offsets(
        [
            V2(0, -EM),
            V2(EM, 0),
            V2(0, EM),
            V2(EM, 0),
        ]
    )

    arrow1_opts = ArrowOpts(
        **{
            "head_pad": 0,
            "tail_pad": 0,
            "trail": trail,
            "arc_height": 0,
            "shaft_style": Style.empty().line_color(grey),
        }
    )

    arrow2_opts = ArrowOpts(
        **{
            "head_pad": 0,
            "tail_pad": 0,
            "trail": trail,
            "arc_height": 0,
            "shaft_style": Style.empty().line_color(green),
        }
    )

    arrow_hidden_from_centers = diagram.connect("A", "B", arrow1_opts)
    arrow_outside = diagram.connect("a", "b", arrow2_opts)
    diagram = arrow_hidden_from_centers + diagram + arrow_outside

    diagram.render_svg(args.path, height=512)
