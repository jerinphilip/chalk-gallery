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


def connect_outside_elbow(diagram, source, target, direction):
    source_sb = diagram.get_subdiagram(source)
    target_sb = diagram.get_subdiagram(target)
    source_origin = source_sb.get_location()
    target_origin = target_sb.get_location()

    # remove direction component
    def decompose(src, tgt, direction):
        r = tgt - src
        print(src, tgt)
        print(r, r.dot(direction))
        perpendicular = r - r.dot(direction) * direction
        parallel = r.dot(direction) * direction
        return perpendicular, parallel

    perpendicular, parallel = decompose(source_origin, target_origin, direction)
    unit_perpendicular = perpendicular.normalized()
    unit_parallel = parallel.normalized()

    p0 = source_sb.boundary_from(direction)
    pf = target_sb.boundary_from(-1 * unit_perpendicular)

    perpendicular, parallel = decompose(p0, pf, direction)

    elbow_trail = Trail.from_offsets([V2(0, 0), parallel, perpendicular])
    elbow_connector = elbow_trail.stroke().translate(p0.x, p0.y) + dart().scale(
        0.2
    ).translate(pf.x, pf.y)
    return diagram + elbow_connector
