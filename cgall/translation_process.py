from PIL import Image as PILImage
from chalk import *
from colour import Color
from chalk import BoundingBox
from copy import deepcopy

from chalk.shapes.arrowheads import ArrowHead, dart, tri  # noqa: F401


import math
import random

from itertools import product
from argparse import ArgumentParser

random.seed(0)

# Data is a nested structure.
black = Color("#000000")
white = Color("#ffffff")
red = Color("#ff0000")
green = Color("#00ff00")
gold = Color("#ffff00")
blue = Color("#0000ff")
grey = Color("#cccccc")

LINE_WIDTH = 0.05


def Cube(side: int = 3):
    # Assemble cube
    line_width = 0.025
    face_m = rectangle(side, side).line_width(line_width).align_tl()
    face_t = rectangle(side, side / 2).line_width(line_width).shear_x(-1).align_bl()
    face_r = rectangle(side / 2, side).line_width(line_width).shear_y(-1).align_tr()
    cube = (face_t + face_m).align_tr() + face_r

    # Replace envelope with front face.
    return cube.align_bl().with_envelope(face_m.align_bl())


def Tensor(depth, rows, columns):
    "Draw a tensor"
    cube = Cube()
    # Fix this ...
    em = 3
    hyp = (unit_y * 0.5 * em).shear_x(-1)
    # Build a matrix.
    front = cat(
        [hcat([cube for i in range(columns)]) for j in reversed(range(rows))], -unit_y
    ).align_t()

    # Build depth
    cube3d = concat(
        front.translate(-k * hyp.x, -k * hyp.y) for k in reversed(range(depth))
    ).center_xy()

    return cube3d


def Block(
    label: str,
    width: int = 80,
    height: int = 24,
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

    embedding = Block("Embed").center_xy().named("embed")
    embedding_out = Tensor(depth=3, rows=1, columns=24).named("embed_out")
    encoder = Block("Encoder").center_xy().named("encoder")

    def Token(text):
        return Block(text, width=24, height=12)

    labels = ["1", "2", "eos"]
    tokens = empty()
    for i, label in enumerate(reversed(labels)):
        n = len(labels)
        factor = 10
        tokens = tokens + Token(label).translate(
            (n - i) * factor, -1 * (n - i) * factor
        )

    tokens = tokens.center_xy().named("encoder_tokens")

    spacing = 18
    encoder_stack = vcat(
        [encoder, embedding_out, embedding, tokens], spacing
    ).center_xy()

    arrow_pad = 3
    default_arrow_opts = {
        "head_pad": arrow_pad,
        "tail_pad": arrow_pad,
        "head_arrow": dart().scale(3).translate(2, 0),
        # "head_arrow": triangle(3),
        "head_style": Style.empty().fill_color(black),
        # "arc_height": 0.5,
        "arc_height": 0.0,
        "shaft_style": Style.empty().line_color(black),
    }

    arrow0 = encoder_stack.connect_outside(
        "encoder_tokens",
        "embed",
        ArrowOpts(**default_arrow_opts),
    )

    # arrow1 = encoder_stack.connect_outside(
    #     "encoder_embed",
    #     "encoder_embed_out",
    #     ArrowOpts(**default_arrow_opts),
    # )

    # arrow2 = encoder_stack.connect_outside(
    #     "encoder_embed_out",
    #     "encoder_encoder",
    #     ArrowOpts(**default_arrow_opts),
    # )

    encoder_stack = encoder_stack + arrow0  # + arrow1 + arrow2

    decoder = Block("Decoder").center_xy()
    decoder_unrolled = []
    predictions = ["1", "2", "eos"]
    decoder_steps = ["", "1", "2"]
    for t, (decoder_step, prediction) in enumerate(zip(decoder_steps, predictions)):
        decoder_instance = decoder
        decoder_instance = decoder_instance.named("decoder_" + str(t))
        decoder_token = Token(decoder_step).named("decoder_token")
        predicted_token = Token(prediction).named("predicted_token")
        decoder_stack = vcat(
            [
                predicted_token,
                decoder_instance,
                embedding_out,
                embedding,
                decoder_token,
            ],
            spacing,
        ).center_xy()

        a0 = decoder_stack.connect_outside(
            "decoder_token", "embed", ArrowOpts(**default_arrow_opts)
        )

        a3 = decoder_stack.connect_outside(
            "decoder_" + str(t), "predicted_token", ArrowOpts(**default_arrow_opts)
        )

        decoder_stack = decoder_stack + a0 + a3
        decoder_unrolled.append(decoder_stack)

    decoder_unrolled = hcat(decoder_unrolled, 2 * spacing).center_xy()
    for t in range(1, len(predictions)):
        a = decoder_unrolled.connect_outside(
            "decoder_" + str(t - 1),
            "decoder_" + str(t),
            ArrowOpts(**default_arrow_opts),
        )
        decoder_unrolled = decoder_unrolled + a

    encoder_stack = encoder_stack.translate(0, 2 * spacing)

    diagram = hcat([encoder_stack, decoder_unrolled], 4 * spacing).center_xy()
    diagram.render_svg(args.path, height=512)
