#!/usr/bin/env python

import png
import click
from pathlib import Path


def is_white_full(x, y, size, width):
    test_1 = y in range(width) and x in range(width)
    test_2 = y in range(width, width * 2) and x in range(width, width * 3)
    test_3 = y in range(width * 2, width * 3) and x in range(width, width * 2)
    return test_1 or test_2 or test_3


def is_white_empty(x, y, size, width):
    test_1 = y in range(width) and x in range(width)
    test_2 = y in range(width, size - width) and x in range(width, size - width)
    return test_1 or test_2


def get_is_white_from_str(is_white_str):
    assert is_white_str in ('O', '.')
    if is_white_str == 'O':
        return is_white_full
    elif is_white_str == '.':
        return is_white_empty


def get_tetrominoe(rgb, is_white, size, width):
    if type(is_white) == str:
        is_white = get_is_white_from_str(is_white)
    image = []
    for y in range(size):
        row = []
        for x in range(size):
            if is_white(x, y, size, width):
                row += [255, 255, 255]
            else:
                row.extend(rgb)
        image.append(row)
    return image


def get_rgb(color):
    if color[0] == '#':
        return [
            int(color[1:3], 16),
            int(color[3:5], 16),
            int(color[5:7], 16)
        ]
    else:
        return [
            int(v) for v in color.replace('(', '').replace(')', '').split(',')
        ]


def concatenate_image(image1, image2):
    assert len(image1) == len(image2)
    return [image1[i] + image2[i] for i in range(len(image1))]


def concatenate_images(images):
    image_concat = images[0]
    for image in images[1:]:
        image_concat = concatenate_image(image_concat, image)
    return image_concat


@click.command()
@click.option(
    '--color',
    help="Color(s) used to generate the sprite sheet.",
    required=True
)
@click.option(
    '--size',
    default=14,
    help="Size of the square"
)
@click.option(
    '--width',
    default=None,
    help="Width of the band inside the tetrominoe. If `None` default to `max(size / 7, 2)`"
)
@click.option(
    '--fill',
    default="O.",
    help="Pattern use to fill the file."
)
@click.option(
    '--outdir',
    default="./",
    help="Output directory."
)
@click.option(
    '--filename',
    default=None,
    help=("Output filename(s).")
)
def main(color, size, width, fill, outdir, filename):
    """
    \b
    Utility to generate sprites of NES tetrominoe.

    \b
    Example:
        Generate two files one with two color and one with one color, both with full tetrominoe in the first line
        and empty tetrominoe in the second line.
        `./tetrominoes_maker.py --color #F00000:#AB0000;(0,255,6) --size 40 --fill O.`
    """
    if fill.count(";") != 0:
        assert fill.count(";") == color.count(";")
        for fill_pattern in fill.split(";"):
            assert all([char in ('O', '.') and len(fill_pattern) <= 2 for char in fill_pattern])
    else:
        assert all([char in ('O', '.') and len(fill) <= 2 for char in fill])
    if filename is not None:
        assert filename.count(";") == color.count(";")

    if width is None:
        width = max(int(size / 7), 2)
    color_groups = color.split(';')
    nb_colors = len(color_groups)
    fill = [fill] * nb_colors if fill.count(";") == 0 else fill.split(";")
    if filename is None:
        filename = [Path(outdir, f"{i}.png") for i in range(nb_colors)]
    else:
        filename = [Path(outdir, f) for f in filename.split(';')]


    for i, color_group in enumerate(color_groups):
        images = []
        for color in color_group.split(':'):
            rgb = get_rgb(color)
            image = get_tetrominoe(rgb, fill[i][0], size, width)
            if len(fill[i]) > 1:
                image.extend(get_tetrominoe(rgb, fill[i][1], size, width))
            images.append(image)
        image_concat = concatenate_images(images)
        with open(filename[i], 'wb') as outfile:
            w = png.Writer(
                int(len(image_concat[0]) / 3),
                len(image_concat),
                greyscale=False
            )
            w.write(outfile, image_concat)


if __name__ == '__main__':
    main()
