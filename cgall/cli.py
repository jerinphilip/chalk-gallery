from argparse import ArgumentParser


def add_basic_args(parser):
    parser.add_argument("--path", type=str, required=True)


def basic_parser():
    parser = ArgumentParser("Generate a diagram")
    add_basic_args(parser)
    return parser
