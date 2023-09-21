from colour import Color
from chalk import *
from chalk.arrow import connect_outside_elbow
from .cli import basic_parser

if __name__ == "__main__":
    parser = basic_parser()
    args = parser.parse_args()
    color = Color("pink")

    def node(label):
        c = circle(0.75).fill_color(color).named(label) + text(label, 0.7).line_width(0)
        return c

    def make_diagram():
        points = [V2(3, 0), V2(0, 3), V2(-3, 0), V2(0, -3)]
        diagram = empty()
        for idx, point in enumerate(points):
            diagram = diagram + node(f"c{idx}").translate(point.x, point.y)

        return diagram

    clockwise = make_diagram()
    for idx in range(1, 4):
        direction = "hv" if idx % 2 == 0 else "vh"
        clockwise = connect_outside_elbow(clockwise, f"c{idx-1}", f"c{idx}", direction)

    direction = "hv"
    clockwise = connect_outside_elbow(clockwise, f"c3", f"c0", direction)

    counterclockwise = make_diagram()
    for idy in range(1, 4):
        idx = 4 - idy
        direction = "hv" if idx % 2 == 1 else "vh"
        counterclockwise = connect_outside_elbow(
            counterclockwise, f"c{idx}", f"c{idx-1}", direction
        )

    direction = "vh"
    counterclockwise = connect_outside_elbow(counterclockwise, f"c0", f"c3", direction)
    # dia2 = make_diagram()
    # dia2 = connect_outside_elbow(dia2, "src", "tgt", "vh")

    # dia = hcat([dia1, dia2], sep=2)
    diagram = hcat([clockwise, counterclockwise], sep=2)

    diagram.render_svg(args.path, height=256)
