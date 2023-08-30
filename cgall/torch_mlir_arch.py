from PIL import Image as PILImage
from chalk import *
from colour import Color
from chalk import BoundingBox
from copy import deepcopy
from .color_map import qualitative
from random import shuffle

from chalk.shapes.arrowheads import ArrowHead, dart, tri  # noqa: F401
from .cli import basic_parser
from .prelude import black, white

green = Color("#e1f7d0")
purple = Color("#dbacee")
red = Color("#f9d1d1")
yellow = Color("#f5ee9c")
blue = Color("#a2cdec")


def Block(
    label: str,
    width: int = 60,
    height: int = 18,
    stroke: Color = black,
    fill: Color = white,
    line_width: float = 0.05,
    font_scale: float = 1.0,
):
    radius = min(width, height) / 20
    font_size = min(width, height) / 3 * font_scale
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


if __name__ == "__main__":
    parser = basic_parser()
    args = parser.parse_args()
    python_program = Block("Python Program").named("py")
    torch_script = Block("TorchScript").named("ts")
    ltc = Block("LazyTensorCore").named("ltc")

    def TextBox(text):
        return Block(
            text,
            width=60,
            height=10,
            stroke=None,
            fill=None,
            line_width=0,
            font_scale=1.5,
        )

    ops = [
        TextBox("Functionalize"),
        TextBox("Shape inference"),
        TextBox("dtype inference"),
        TextBox("simplify python"),
    ]

    pseudo = Block("", fill=None, stroke=None, line_width=0).fill_opacity(0)

    ops_render = vcat(ops).center_xy()
    e = ops_render.get_envelope()
    ops_render = rectangle(e.width, e.height).pad(1.2) + ops_render.named("ops")

    vspace = 20
    hspace = 10

    l2 = hcat([torch_script, ltc], hspace).center_xy()
    l3 = hcat([ops_render, pseudo], hspace).center_xy()

    decompositions = Block("Decompositions").named("decomp")
    backend = Block("Backend", fill=green).named("backend")

    linalg = Block("LinAlg").named("la")
    tosa = Block("TOSA").named("tosa")
    mhlo = Block("MHLO").named("mhlo")

    l6 = hcat([linalg, tosa, mhlo], hspace).center_xy()

    diagram = vcat(
        [python_program.center_xy(), l2, l3, decompositions, backend, l6], vspace
    )

    # Connections
    arrow_pad = 4
    arrow_opts = ArrowOpts(
        **{
            "head_pad": arrow_pad,
            "tail_pad": arrow_pad,
            "head_arrow": dart().scale(2),
            "head_style": Style.empty().fill_color(black),
            "arc_height": 0.0,
            "shaft_style": Style.empty().line_color(black),
        }
    )

    diagram = diagram.connect_outside("py", "ts", arrow_opts)
    diagram = diagram.connect_outside("py", "ltc", arrow_opts)
    diagram = diagram.connect_outside("ts", "ops", arrow_opts)
    diagram = diagram.connect_outside("ops", "decomp", arrow_opts)
    diagram = diagram.connect_outside("ltc", "decomp", arrow_opts)
    diagram = diagram.connect_outside("decomp", "backend", arrow_opts)
    diagram = diagram.connect_outside("backend", "la", arrow_opts)
    diagram = diagram.connect_outside("backend", "tosa", arrow_opts)
    diagram = diagram.connect_outside("backend", "mhlo", arrow_opts)

    envelope = diagram.get_envelope()
    diagram = diagram.center_xy()
    backend_hrule_origin = diagram.get_subdiagram("backend").get_location()
    backend_hrule = make_path([(0, 0), (envelope.width, 0)]).dashing([2, 2], 0)
    legend_size = 6
    label = (
        text("Torch MLIR Backend", legend_size)
        .fill_color(black)
        .line_width(0)
        .with_envelope(rectangle(60, 10))
    )
    offset = V2(0, 10)
    backend_hrule = backend_hrule.align_r().above(label.align_r())
    backend_hrule = backend_hrule.center_xy().translate(*(backend_hrule_origin))
    diagram = backend_hrule + diagram
    diagram = diagram.center_xy()

    ts_bottom = diagram.get_subdiagram("ts").boundary_from(-1 * unit_y)
    ops_top = diagram.get_subdiagram("ops").boundary_from(-1 * unit_y)
    loc_v = ts_bottom + (ops_top - ts_bottom) / 2

    # marker = (
    #     Trail.from_offsets([V2(0, 0), -1 * (ops_top - ts_bottom)])
    #     .translate(*ops_top)
    #     .stroke()
    # )
    # diagram = diagram + marker

    loc_h = (
        diagram.get_subdiagram("ts").get_location()
        + diagram.get_subdiagram("ltc").get_location()
    ) / 2

    frontend_hrule_origin = V2(loc_h.x, loc_v.y)
    frontend_hrule = make_path([(0, 0), (envelope.width, 0)]).dashing([2, 2], 0)
    legend_size = 6
    label_below = (
        text("Torch MLIR Frontend", legend_size)
        .fill_color(black)
        .line_width(0)
        .with_envelope(rectangle(60, 10))
    ).center_xy()
    label_above = (
        text("PyTorch", legend_size)
        .fill_color(black)
        .line_width(0)
        .center_xy()
        .with_envelope(rectangle(20, 10))
    )
    offset = V2(0, 10)
    frontend_hrule = (
        label_above.align_r()
        .above(frontend_hrule.align_r())
        .above(label_below.align_r())
    )
    frontend_hrule = frontend_hrule.center_xy().translate(
        *(frontend_hrule_origin + offset)
    )
    diagram = frontend_hrule + diagram

    diagram.render_svg(args.path, height=512)
