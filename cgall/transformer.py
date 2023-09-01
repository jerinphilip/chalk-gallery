from .color_map import qualitative
from .cli import basic_parser
from .prelude import connect_outside_elbow, arrow_outside_up, arrow_outside_up_free
from chalk import *
from colour import Color
from chalk.shapes.arrowheads import ArrowHead, dart, tri  # noqa: F401

black = Color("#000000")
white = Color("#ffffff")
grey = Color("#cccccc")

green = Color("#cce7cf")
purple = Color("#c4bedf")
red = Color("#f9cbdf")
yellow = Color("#fef9c1")
blue = Color("#a2cdec")

linear_green = Color("#e8eeeb")
green_fg = Color("#6d8759")

CAPTION_SIZE = 12


def Block(
    label: str,
    width: int = 40,
    height: int = 10,
    stroke: Color = black,
    fill: Color = white,
    line_width: float = 0.10,
):
    radius = min(width, height) / 20
    font_size = min(width, height) / 1.5
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


def sdpa():
    q = Block("Q", width=10, line_width=0).named("Q")
    k = Block("K", width=10, line_width=0).named("K")
    v = Block("V", width=10, line_width=0).named("V")

    scale = Block("Scale", fill=yellow).named("scale")
    matmul1 = Block("MatMul", fill=purple).named("mm1")
    matmul2 = Block("MatMul", fill=purple).named("mm2")
    mask = Block("Mask (opt)", fill=red).named("mask")
    softmax = Block("SoftMax", fill=green).named("softmax")

    em = empty().with_envelope(q)

    hspace = 10
    vspace = 5
    diagram = vcat(
        [
            matmul2.center_xy(),
            hcat([softmax, em], hspace).center_xy(),
            hcat([mask, em], hspace).center_xy(),
            hcat([scale, em], hspace).center_xy(),
            hcat([matmul1, em], hspace).center_xy(),
            hcat([q, k, v], hspace - 3).center_xy(),
        ],
        vspace,
    )

    diagram = arrow_outside_up(diagram, "Q", "mm1")
    diagram = arrow_outside_up(diagram, "K", "mm1")

    diagram = arrow_outside_up(diagram, "V", "mm2")
    diagram = arrow_outside_up(diagram, "mm1", "scale")
    diagram = arrow_outside_up(diagram, "scale", "mask")
    diagram = arrow_outside_up(diagram, "mask", "softmax")
    diagram = arrow_outside_up(diagram, "softmax", "mm2")
    diagram = arrow_outside_up_free(diagram, "mm2", vspace)

    # diagram = vcat(
    #     [
    #         diagram,
    #         text("Scaled Dot Product Attention", CAPTION_SIZE)
    #         .fill_color(black)
    #         .scale(0.2),
    #     ],
    #     vspace,
    # )
    return diagram


def mha():
    hspace = 10
    vspace = 10

    factor = 2.0

    def head(i):
        dx = -1 * head_id * factor
        dy = head_id * factor
        min_opacity = 0.2
        opacity = min_opacity + (1 - min_opacity) * (i + 1) / 3

        q, k, v = [
            Block("Linear", fill=linear_green, width=30).named(
                "linear_" + x + "_" + str(i)
            )
            for x in ["v", "k", "q"]
        ]
        sdpa = Block(
            "Scaled Dot Product Attention", width=3 * 40 + 2 * hspace / 2, fill=purple
        ).named("sdpa_" + str(i))

        def center(xs):
            return list(map(lambda x: x.center_xy(), xs))

        return (
            vcat(center([sdpa, hcat([q, k, v], hspace / 2)]), vspace)
            .center_xy()
            .translate(dx, dy)
            .fill_opacity(opacity)
        )

    num_heads = 3
    heads = empty()
    for head_id in range(num_heads):
        heads = heads + head(head_id)

    heads = heads.center_xy().translate(-1 * factor, factor)

    concat = Block("Concat", fill=yellow).named("concat")
    out = Block("Linear", fill=linear_green, width=30).named("out")

    labels = hcat(
        [
            Block("V", line_width=0, width=30).named("v"),
            Block("K", line_width=0, width=30).named("k"),
            Block("Q", line_width=0, width=30).named("q"),
        ],
        hspace,
    )
    split = hcat(
        [
            Block("Split", fill=yellow, width=30).named("split_" + x)
            for x in ["v", "k", "q"]
        ],
        hspace,
    )

    centered = list(
        map(
            lambda x: x.center_xy(),
            [out, concat, heads, split, labels],
        )
    )

    diagram = vcat(
        centered,
        vspace,
    )

    for x in ["q", "k", "v"]:
        diagram = arrow_outside_up(diagram, x, "split_" + x, left=False)

    for head_id in range(num_heads):
        diagram = arrow_outside_up(diagram, "sdpa_" + str(head_id), "concat")

        for x in ["q", "k", "v"]:
            diagram = arrow_outside_up(
                diagram,
                f"linear_{x}_" + str(head_id),
                "sdpa_" + str(head_id),
                left=False,
            )
            diagram = arrow_outside_up(
                diagram, f"split_{x}", f"linear_{x}_" + str(head_id), left=False
            )

    diagram = arrow_outside_up(diagram, "concat", "out")
    diagram = arrow_outside_up_free(diagram, "out", vspace)
    # diagram = vcat(
    #     [
    #         diagram,
    #         text("MultiHead Attention", CAPTION_SIZE).fill_color(black).scale(0.2),
    #     ],
    #     vspace,
    # )
    return diagram


if __name__ == "__main__":
    parser = basic_parser()
    parser.add_argument(
        "-d", "--diagram", type=str, choices=["sdpa", "mha"], required=True
    )
    args = parser.parse_args()

    diagram = None
    if args.diagram == "sdpa":
        diagram = sdpa()
    elif args.diagram == "mha":
        diagram = mha()

    if args.path.endswith(".svg"):
        diagram.render_svg(args.path, height=512)
    elif args.path.endswith(".png"):
        diagram.render_png(args.path, height=512)
    else:
        print("Unknown output type")
