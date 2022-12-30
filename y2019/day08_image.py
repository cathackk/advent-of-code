"""
Advent of Code 2019
Day 8: Space Image Format
https://adventofcode.com/2019/day/8
"""

import itertools
from collections import Counter
from typing import Iterable

from common.ocr import FONT_6X5
from common.rect import HyperCuboid
from meta.aoc_tools import data_path


def part_1(image: 'Image') -> int:
    """
    The Elves' spirits are lifted when they realize you have an opportunity to reboot one of their
    Mars rovers, and so they are curious if you would spend a brief sojourn on Mars. You land your
    ship near the rover.

    When you reach the rover, you discover that it's already in the process of rebooting! It's just
    waiting for someone to enter a BIOS password. The Elf responsible for the rover takes a picture
    of the password (your puzzle input) and sends it to you via the Digital Sending Network.

    Unfortunately, images sent via the Digital Sending Network aren't encoded with any normal
    encoding; instead, they're encoded in a special Space Image Format. None of the Elves seem to
    remember why this is the case. They send you the instructions to decode it.

    Images are sent as a series of digits that each represent the color of a single pixel. The
    digits fill each row of the image left-to-right, then move downward to the next row, filling
    rows top-to-bottom until every pixel of the image is filled.

    Each image actually consists of a series of identically-sized layers that are filled in this
    way. So, the first digit corresponds to the top-left pixel of the first layer, the second digit
    corresponds to the pixel to the right of that on the same layer, and so on until the last digit,
    which corresponds to the bottom-right pixel of the last layer.

    For example, given an image `3` pixels wide and `2` pixels tall, the image data `123456789012`
    corresponds to the following image layers:

        >>> img = Image.from_line('123456789012', width=3, height=2)
        >>> print(format(img, 'layers'))
        Layer 1: 123
                 456
        Layer 2: 789
                 012
        >>> img.bounds.shape
        (3, 2, 2)

    Larger example:

        >>> img_large = Image.from_file(data_path(__file__, 'example.txt'), width=15, height=6)
        >>> print(format(img_large, 'layers'))
        Layer 1: 021202120202120
                 202121202020212
                 120202021212020
                 212121202020202
                 120202021212020
                 202120212021202
        Layer 2: 010000010001001
                 100000001010000
                 000101000000001
                 101000001010000
                 100101000000011
                 110000100000100
        >>> img_large.bounds.shape
        (15, 6, 2)

    The image you received is **`25` pixels wide and `6` pixels tall**.

    To make sure the image wasn't corrupted during transmission, the Elves would like you to find
    the layer that contains the **fewest `0` digits**. On that layer, what is **the number of `1`
    digits multiplied by the number of `2` digits?**

        >>> part_1(img_large)
        part 1: 18 ones * 45 twos = 810
        810
    """

    min_layer = min((Counter(layer) for layer in image.layers()), key=lambda c: c[0])
    ones, twos = min_layer[1], min_layer[2]
    result = ones * twos

    print(f"part 1: {ones} ones * {twos} twos = {result}")
    return result


def part_2(image: 'Image') -> str:
    """
    Now you're ready to decode the image. The image is rendered by stacking the layers and aligning
    the pixels with the same positions in each layer. The digits indicate the color of the
    corresponding pixel: `0` is black, `1` is white, and `2` is transparent.

    The layers are rendered with the first layer in front and the last layer in back. So, if a given
    position has a transparent pixel in the first and second layers, a black pixel in the third
    layer, and a white pixel in the fourth layer, the final image would have a **black** pixel at
    that position.

    For example, given an image 2 pixels wide and 2 pixels tall, the image data `0222112222120000`
    corresponds to the following image layers:

        >>> img = Image.from_line('0222112222120000', 2, 2)
        >>> print(format(img, 'layers'))
        Layer 1: 02
                 22
        Layer 2: 11
                 22
        Layer 3: 22
                 12
        Layer 4: 00
                 00

    Then, the full image can be found by determining the top visible pixel in each position:

      - The top-left pixel is **black** because the top layer is `0`.
      - The top-right pixel is **white** because the top layer is `2` (transparent),
        but the second layer is `1`.
      - The bottom-left pixel is **white** because the top two layers are `2`,
        but the third layer is `1`.
      - The bottom-right pixel is **black** because the only visible pixel in that position is `0`
        (from layer 4).

    So, the final image looks like this:

        >>> print(img)
        01
        10

    Larger example:

        >>> img_large = Image.from_file(data_path(__file__, 'example.txt'), width=15, height=6)
        >>> print(format(img_large, '·█'))
        ·██···██···██··
        █··█·█··█·█··█·
        █··█·█··█·█····
        ████·█··█·█····
        █··█·█··█·█··█·
        █··█··██···██··

    **What message is produced after decoding your image?**

        >>> part_2(img_large)
        part 2: image produced message 'AOC'
        'AOC'
    """

    result = FONT_6X5.read_string(str(image))

    print(f"part 2: image produced message {result!r}")
    return result


BLACK = 0
WHITE = 1
TRANSPARENT = 2

Pos3 = tuple[int, int, int]


def enumerate_pixels(pixels: Iterable[int], width: int, height: int) -> Iterable[tuple[Pos3, int]]:
    positions = (
        (x, y, z)
        for z in itertools.count(0)
        for y in range(height)
        for x in range(width)
    )
    return zip(positions, pixels)


class Image:
    def __init__(self, pixels: Iterable[int], width: int, height: int):
        self.pixels = dict(enumerate_pixels(pixels, width=width, height=height))
        self.bounds = HyperCuboid.with_all(self.pixels)
        assert self.bounds.shape[0] == width
        assert self.bounds.shape[1] == height
        assert self.bounds.volume == len(self.pixels)

    def layers(self) -> Iterable[list[int]]:
        return (
            [self.pixels[x, y, z] for y in self.bounds[1] for x in self.bounds[0]]
            for z in self.bounds[2]
        )

    def __format__(self, format_spec: str) -> str:
        if not format_spec:
            return str(self)

        elif len(format_spec) == 2:
            black_char, white_char = tuple(format_spec)
            return (
                str(self)
                .replace(str(BLACK), black_char)
                .replace(str(WHITE), white_char)
                .replace(str(TRANSPARENT), '?')
            )

        elif format_spec == 'layers':
            return self.layers_str()

        else:
            raise ValueError(format_spec)

    def __str__(self) -> str:
        def pixel_at(x: int, y: int) -> int:
            return next((pixel for z in self.bounds[2] if (pixel := self.pixels[x, y, z]) != 2), 2)

        return "\n".join(
            "".join(str(pixel_at(x, y)) for x in self.bounds[0])
            for y in self.bounds[1]
        )

    def layers_str(self) -> str:
        def header(layer_no: int, line_no: int):
            if line_no == 0:
                return f"Layer {layer_no + 1}: "
            else:
                return " " * 9

        return '\n'.join(
            header(z, y) + ''.join(str(self.pixels[x, y, z]) for x in self.bounds[0])
            for z in self.bounds[2]
            for y in self.bounds[1]
        )

    @classmethod
    def from_file(cls, fn: str, width: int, height: int) -> 'Image':
        return cls.from_line(line=open(fn).readline(), width=width, height=height)

    @classmethod
    def from_line(cls, line: str, width: int, height: int) -> 'Image':
        return cls(pixels=(int(char) for char in line.strip()), width=width, height=height)


def main(input_path: str = data_path(__file__)) -> tuple[int, str]:
    image = Image.from_file(input_path, width=25, height=6)
    result_1 = part_1(image)
    result_2 = part_2(image)
    return result_1, result_2


if __name__ == '__main__':
    main()
