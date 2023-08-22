from PIL import Image as PILImage
from chalk import *
from colour import Color
from chalk import BoundingBox


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

LINE_WIDTH = 0.1


def Cube(side: int = 3):
    # Assemble cube
    face_m = rectangle(side, side).align_tl()
    face_t = rectangle(side, side / 2).shear_x(-1).align_bl()
    face_r = rectangle(side / 2, side).shear_y(-1).align_tr()
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
    return concat(
        front.translate(-k * hyp.x, -k * hyp.y) for k in reversed(range(depth))
    ).center_xy()


def Block(
    label: str,
    width: int = 100,
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
    ).center_xy()

    return container + render_label


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--path", type=str, required=True)
    args = parser.parse_args()

    embedding = Block("Embedding").center_xy()
    embedding_out = Tensor(depth=3, rows=1, columns=24)
    encoder = Block("Encoder").center_xy()

    def Token(text):
        return Block(text, width=24, height=12)

    tokens = hcat([Token("1"), Token("2"), Token("eos")], 3).center_xy()

    encoder_stack = vcat([encoder, embedding_out, embedding, tokens], 12).center_xy()

    decoder = Block("Decoder").center_xy()
    decoder_unrolled = []
    predictions = ["1", "2", "eos"]
    decoder_steps = ["", "1", "2"]
    for decoder_step, prediction in zip(decoder_steps, predictions):
        decoder_token = Token(decoder_step)
        predicted_token = Token(prediction)
        decoder_stack = vcat(
            [predicted_token, decoder, embedding_out, embedding, decoder_token], 12
        ).center_xy()
        decoder_unrolled.append(decoder_stack)

    decoder_unrolled = hcat(decoder_unrolled, 12).center_xy()

    diagram = hcat([encoder_stack, decoder_unrolled], 12).center_xy()
    diagram.render_svg(args.path, height=512)
