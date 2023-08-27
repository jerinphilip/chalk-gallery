from .color_map import qualitative
from .cli import basic_parser
from chalk import *
from colour import Color
from chalk.shapes.arrowheads import ArrowHead, dart, tri  # noqa: F401


black = Color("#000000")
white = Color("#ffffff")
grey = Color("#cccccc")


def Block(
    label: str,
    width: int = 5,
    height: int = 2,
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
        latex(label)
        .line_color(black)
        .line_width(0)
        .fill_color(black)
        .with_envelope(bounding_rect)
    ).translate(0, height / 16)

    return container + render_label


def Node(
    label: str,
    radius: int = 1,
    stroke: Color = black,
    fill: Color = white,
    line_width: float = 0.05,
):
    container = (
        circle(radius).line_color(stroke).fill_color(fill).line_width(line_width)
    ).center_xy()

    bounding_circle = container.scale(0.9).center_xy()
    render_label = (
        latex(label)
        .line_color(black)
        .line_width(0)
        .fill_color(black)
        .with_envelope(bounding_circle)
    ).translate(0, radius / 16)

    return container + render_label


if __name__ == "__main__":
    parser = basic_parser()
    args = parser.parse_args()

    ht = Node("$h_t$").named("ht")
    A = Block("A").named("A").center_xy()

    e = A.get_envelope()
    w, h = e.width, e.height
    dw, dh = 1, 1
    trail = Trail.from_offsets(
        [
            V2(dw, 0),
            V2(0, -1 * (h / 2 + dh)),
            V2(-1 * (w + 2 * dw), 0),
            V2(0, h / 2 + dh),
            V2(dw, 0),
        ]
    )
    recurrent = trail.stroke().line_color(grey).translate(w / 2, 0) + dart().scale(
        0.1
    ).translate(-1 * w / 2, 0)
    A = A + recurrent

    xt = Node("$x_t$").named("xt")
    vspace = 1
    diagram = vcat([ht, A, xt], 1)
    a1 = diagram.connect_outside("xt", "A")
    a2 = diagram.connect_outside("A", "ht")
    diagram = diagram + a1 + a2
    diagram.render_svg(args.path, height=512)
