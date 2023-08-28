from PIL import Image as PILImage
from chalk import *
from colour import Color
from chalk import BoundingBox
from copy import deepcopy
from .color_map import qualitative
from random import shuffle

from chalk.shapes.arrowheads import ArrowHead, dart, tri  # noqa: F401
from .cli import basic_parser
from .prelude import Block, black, white

if __name__ == "__main__":
    parser = basic_parser()
    args = parser.parse_args()
    python_program = Block("Python").named("py")
    torch_script = Block("TorchScript").named("ts")
    ltc = Block("LTC").named("ltc")

    def TextBox(text):
        return Block(text, width=40, height=10, stroke=None, fill=None, line_width=0)

    ops = [
        TextBox("Functionalize"),
        TextBox("Shape inference"),
        TextBox("dtype inference"),
        TextBox("simplify python"),
    ]

    pseudo = Block("", fill=None, stroke=None, line_width=0)

    ops_render = vcat(ops).center_xy()
    e = ops_render.get_envelope()
    ops_render = rectangle(e.width, e.height).pad(1.2) + ops_render.named("ops")

    vspace = 20
    hspace = 10

    l2 = hcat([torch_script, ltc], hspace).center_xy()
    l3 = hcat([ops_render, pseudo], hspace).center_xy()

    decompositions = Block("Decompositions").named("decomp")
    backend = Block("Backend").named("backend")

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

    diagram.render_svg(args.path, height=512)
