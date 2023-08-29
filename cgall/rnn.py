from .color_map import qualitative
from .cli import basic_parser
from .prelude import connect_outside_elbow
from chalk import *
from colour import Color
from chalk.shapes.arrowheads import ArrowHead, dart, tri  # noqa: F401


black = Color("#000000")
white = Color("#ffffff")
grey = Color("#cccccc")

green = Color("#e1f7d0")
purple = Color("#dbacee")
red = Color("#f9d1d1")
yellow = Color("#f5ee9c")
blue = Color("#a2cdec")


green_fg = Color("#6d8759")

LATEX_SCALE = 2


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
        .scale(LATEX_SCALE)
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
    latex_scale: float = LATEX_SCALE,
):
    container = (
        circle(radius).line_color(stroke).fill_color(fill).line_width(line_width)
    ).center_xy()

    bounding_circle = container.scale(0.9).center_xy()
    render_label = (
        latex(label)
        .scale(latex_scale)
        .line_color(black)
        .line_width(0)
        .fill_color(black)
        .with_envelope(bounding_circle)
    ).translate(0, radius / 16)

    return container + render_label


def rnn_steps():
    ht = Node("$h_t$").fill_color(purple).named("ht")
    A = Block("A").fill_color(green).named("A").center_xy()

    e = A.get_envelope()
    w, h = e.width, e.height
    dw, dh = 1, 1
    pad = 0
    trail = Trail.from_offsets(
        [
            V2(dw, 0),
            V2(0, -1 * (h / 2 + dh)),
            V2(-1 * (2 * pad + w + 2 * dw), 0),
            V2(0, h / 2 + dh),
            V2(dw, 0),
        ]
    )
    recurrent = trail.stroke().line_color(grey).translate(
        w / 2 + pad, 0
    ) + dart().scale(0.5).translate(-1 * w / 2, 0)

    xt = Node("$x_t$").fill_color(blue).named("xt")
    vspace = 2
    hspace = 2
    stack = vcat([ht, A, xt], vspace).center_xy()
    stack = stack + recurrent
    a1 = stack.connect_outside("xt", "A")
    a2 = stack.connect_outside("A", "ht")
    single_recurrent = stack + a1 + a2

    def Single(t, tl=None):
        if tl is None:
            tl = str(t)
        ht = Node(f"$h_{{{tl}}}$").fill_color(purple).named(f"h{tl}")
        xt = Node(f"$x_{{{tl}}}$").fill_color(blue).named(f"x{tl}")
        name = "A_" + str(t)
        single = vcat([ht, A.named(name), xt], vspace)
        single = single.connect_outside(f"x{tl}", name)
        single = single.connect_outside(name, f"h{tl}")
        return single.center_xy()

    T = 3
    equal = text("=", 8).fill_color(black).scale(1 / 12).line_width(0.02)
    diagram = hcat(
        [single_recurrent, equal]
        + [Single(t) for t in range(T - 1)]
        + [empty(), Single(T - 1, "t")],
        hspace,
    )

    for t in range(1, T):
        previous = "A_" + str(t - 1)
        this = "A_" + str(t)
        diagram = diagram.connect_outside(previous, this)

    return diagram


def SSRU():
    forget = Block("$W_f; b_f$").named("forget")

    W = Block("$W$").named("W").with_envelope(forget)
    add = Node("$+$", fill=yellow).with_envelope(forget)
    mul = Node("$\\times$", fill=yellow).with_envelope(forget)
    one_minus = Node("$1 - $", fill=yellow).named("one_minus").with_envelope(forget)

    relu = (
        Node("ReLU", fill=yellow, latex_scale=1.0).named("relu").with_envelope(forget)
    )

    em = empty().with_envelope(forget)
    junction = circle(1).with_envelope(forget)

    ct_ = (
        Node("$c_{t-1}$", line_width=0, fill=None, stroke=None)
        .named("ct_")
        .with_envelope(forget)
    )
    ct = (
        Node("$c_{t}$", line_width=0, fill=None, stroke=None)
        .named("ct")
        .with_envelope(forget)
    )
    xt = (
        Node("$x_{t}$", line_width=0, fill=None, stroke=None)
        .named("xt")
        .with_envelope(forget)
    )

    ht = (
        Node("$h_{t}$", line_width=0, fill=None, stroke=None)
        .named("ht")
        .with_envelope(forget)
    )

    hspace = 2
    vspace = 2

    xin = empty().with_envelope(forget).named("xin")
    # fmt: off
    row1 = hcat([mul.named("cf"), em, add.named("cf+fx")], hspace)
    row2 = hcat([forget, one_minus, mul.named("fx")], hspace)
    row3 = hcat([xin, em, W], hspace)
    # row4 = hcat([junction, em, junction], hspace)
    # fmt: on

    grid = vcat([row1, row2, row3], vspace)

    grid = grid.connect_outside("cf", "cf+fx")
    grid = grid.connect_outside("forget", "cf")
    grid = grid.connect_outside("forget", "one_minus")
    grid = grid.connect_outside("one_minus", "fx")
    grid = grid.connect_outside("W", "fx")
    grid = grid.connect_outside("fx", "cf+fx")

    cf_plus_fx_loc = grid.get_subdiagram("cf+fx").boundary_from(V2(0, -1))
    cf_plus_fx = grid.get_subdiagram("cf+fx")
    envelope = cf_plus_fx.get_envelope()
    above_cf_plus_fx = cf_plus_fx_loc + V2(0, -1 * (hspace + envelope.height / 2))
    grid += relu.translate(*above_cf_plus_fx)

    rnn_envelope = grid.get_envelope()
    rnn_wrap = (
        rectangle(rnn_envelope.width, rnn_envelope.height, radius=0.05)
        .fill_color(green)
        .line_color(green_fg)
        .scale(1.05)
    )
    grid = rnn_wrap.center_xy() + grid.center_xy()

    cf_loc = grid.get_subdiagram("cf").boundary_from(V2(-1, 0))
    envelope = ct_.get_envelope()
    beside_cf = cf_loc + V2(-1 * (hspace + envelope.width / 2), 0)
    grid += ct_.translate(*beside_cf)

    xin_loc = grid.get_subdiagram("xin").get_location()
    envelope = em.get_envelope()
    below_xin = xin_loc + V2(0, 1 * (hspace + envelope.height / 2))
    grid += xt.translate(*below_xin)

    relu_absolute_loc = grid.get_subdiagram("relu").boundary_from(V2(0, -1))
    relu_absolute = grid.get_subdiagram("relu")
    envelope = relu_absolute.get_envelope()
    above_relu_absolute = relu_absolute_loc + V2(0, -1 * (hspace + envelope.height / 2))
    grid += ht.translate(*above_relu_absolute)

    cf_plus_fx_loc = grid.get_subdiagram("cf+fx").boundary_from(V2(1, 0))
    envelope = ct_.get_envelope()
    beside_cf_plus_fx = cf_plus_fx_loc + V2(1 * (hspace + envelope.width / 2), 0)
    grid += ct.translate(*beside_cf_plus_fx)

    grid = grid.connect_outside("ct_", "cf")
    grid = grid.connect_outside("xt", "forget")
    grid = connect_outside_elbow(grid, "xt", "W", -1 * unit_y)
    grid = grid.connect_outside("cf+fx", "relu")
    grid = grid.connect_outside("cf+fx", "ct")
    grid = grid.connect_outside("relu", "ht")
    return grid


if __name__ == "__main__":
    parser = basic_parser()
    parser.add_argument(
        "-d", "--diagram", type=str, choices=["rnn_steps", "ssru"], required=True
    )
    args = parser.parse_args()

    diagram = None
    if args.diagram == "rnn_steps":
        diagram = rnn_steps()
    elif args.diagram == "ssru":
        diagram = SSRU()
    else:
        print(args.diagram)
        pass

    if args.path.endswith(".svg"):
        diagram.render_svg(args.path, height=512)
    elif args.path.endswith(".png"):
        diagram.render_png(args.path, height=512)
    else:
        print("Unknown output type")
