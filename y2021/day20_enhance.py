"""
Advent of Code 2021
Day 20: Trench Map
https://adventofcode.com/2021/day/20
"""

from collections import defaultdict
from typing import Iterable

from tqdm import tqdm

from common.rect import Rect
from common.utils import relative_path


def part_1(algorithm: 'Algorithm', image: 'Image', runs: int = 2) -> int:
    """
    With the scanners fully deployed, you turn their attention to mapping the floor of the ocean
    trench.

    When you get back the image from the scanners, it seems to just be random noise. Perhaps you can
    combine an image enhancement algorithm and the input image (your puzzle input) to clean it up
    a little.

    For example:

        >>> algo, img = input_from_text('''
        ...
        ...     ..#.#..#####.#.#.#.###.##.....###.##.#..###.####..#####..#....#..#..##..##
        ...     #..######.###...####..#..#####..##..#.#####...##.#.#..#.##..#.#......#.###
        ...     .######.###.####...#.##.##..#..#..#####.....#.#....###..#.##......#.....#.
        ...     .#..#..##..#...##.######.####.####.#.#...#.......#..#.#.#...####.##.#.....
        ...     .#..#...##.#.##..#...##.#.##..###.#......#.#.......#.#.#.####.###.##...#..
        ...     ...####.#..#..#.##.#....##..#.####....##...##..#...#......#.#.......#.....
        ...     ..##..####..#...#.#.#...##..#.#..###..#####........#..####......#..#
        ...
        ...     #..#.
        ...     #....
        ...     ##..#
        ...     ..#..
        ...     ..###
        ...
        ... ''')

    The first section is the **image enhancement algorithm**. It is normally given on a single line,
    but it has been wrapped to multiple lines in this example for legibility. The second section is
    the **input image**, a two-dimensional grid of **light pixels** (`#`) and **dark pixels** (`.`).

    The image enhancement algorithm describes how to enhance an image by **simultaneously**
    converting all pixels in the input image into an output image. Each pixel of the output image is
    determined by looking at a 3x3 square of pixels centered on the corresponding input image pixel.
    So, to determine the value of the pixel at (5,10) in the output image, nine pixels from the
    input image need to be considered: (4,9), (4,10), (4,11), (5,9), (5,10), (5,11), (6,9), (6,10),
    and (6,11). These nine input pixels are combined into a single binary number that is used as
    an index in the **image enhancement algorithm** string.

    For example, to determine the output pixel that corresponds to the very middle pixel of the
    input image, the nine pixels marked by `[...]` would need to be considered:

        # . . # .
        #[. . .].
        #[# . .]#
        .[. # .].
        . . # # #

    Starting from the top-left and reading across each row, these pixels are `...`, then `#..`,
    then `.#.`; combining these forms `...#...#.`. By turning dark pixels (`.`) into `0` and light
    pixels (`#`) into `1`, the binary number `000100010` can be formed, which is `34` in decimal.

    The image enhancement algorithm string is exactly 512 characters long, enough to match every
    possible 9-bit binary number. The character at index 34 is `#`. So, the output pixel in
    the center of the output image should be `#`, a light pixel.

        >>> algo[34]
        True
        >>> algo[0]
        False

    This process can then be repeated to calculate every pixel of the output image.

    Through advances in imaging technology, the images being operated on here are **infinite** in
    size. **Every** pixel of the infinite output image needs to be calculated exactly based on
    the relevant pixels of the input image. The small input image you have is only a small region of
    the actual infinite input image; the rest of the input image consists of dark pixels (`.`). For
    the purposes of the example, to save on space, only a portion of the infinite-sized input and
    output images will be shown.

    The starting input image, therefore, looks something like this, with more dark pixels (`·`)
    extending forever in every direction not shown here:

        >>> img.draw(context=5, dark_char='·')
        ···············
        ···············
        ···············
        ···············
        ···············
        ·····#··#······
        ·····#·········
        ·····##··#·····
        ·······#·······
        ·······###·····
        ···············
        ···············
        ···············
        ···············
        ···············

    By applying the image enhancement algorithm to every pixel simultaneously, the following output
    image can be obtained:

        >>> img_1 = algo.enhance(img)
        >>> img_1.draw(context=4, dark_char='·')
        ···············
        ···············
        ···············
        ···············
        ·····##·##·····
        ····#··#·#·····
        ····##·#··#····
        ····####··#····
        ·····#··##·····
        ······##··#····
        ·······#·#·····
        ···············
        ···············
        ···············
        ···············

    Through further advances in imaging technology, the above output image can also be used as
    an input image! This allows it to be enhanced a **second time**:

        >>> img_2 = algo.enhance(img_1)
        >>> img_2.draw(context=3, dark_char='·')
        ···············
        ···············
        ···············
        ··········#····
        ····#··#·#·····
        ···#·#···###···
        ···#···##·#····
        ···#·····#·#···
        ····#·#####····
        ·····#·#####···
        ······##·##····
        ·······###·····
        ···············
        ···············
        ···············

    Truly incredible - now the small details are really starting to come through. After enhancing
    the original input image twice, **`35`** pixels are lit.

        >>> img_2.lit_pixels_count
        35

    Start with the original input image and apply the image enhancement algorithm twice, being
    careful to account for the infinite size of the images.
    **How many pixels are lit in the resulting image?**

        >>> part_1(algo, img)
        part 1: after enhancing 2x, 35 pixels are lit
        35
    """

    result = algorithm.enhance(image, runs).lit_pixels_count

    print(f"part 1: after enhancing {runs}x, {result} pixels are lit")
    return result


def part_2(algorithm: 'Algorithm', image: 'Image', runs: int = 50) -> int:
    """
    You still can't quite make out the details in the image. Maybe you just didn't enhance it
    enough.

    If you enhance the starting input image in the above example a total of **50** times, **`3351`**
    pixels are lit in the final output image.

        >>> algo, img = input_from_file('data/20-example.txt')
        >>> img_50 = algo.enhance(img, runs=50)
        >>> img_50.lit_pixels_count
        3351

    Start again with the original input image and apply the image enhancement algorithm 50 times.
    **How many pixels are lit in the resulting image?**

        >>> part_2(algo, img)
        part 2: after enhancing 50x, 3351 pixels are lit
        3351
    """

    result = algorithm.enhance(image, runs).lit_pixels_count

    print(f"part 2: after enhancing {runs}x, {result} pixels are lit")
    return result


Pos = tuple[int, int]
Pixel = tuple[Pos, bool]


class Image:
    def __init__(self, pixels: Iterable[Pixel], others: bool = False):
        self.lit = set(pos for pos, lit in pixels if lit != others)
        self.inverted = others
        self.bounds = Rect.with_all(self.lit)

    def __getitem__(self, pos: Pos) -> bool:
        return (pos in self.lit) != self.inverted

    def pixel_rows(self, context: int = 1) -> Iterable[Pixel]:
        return ((pos, self[pos]) for pos in self.bounds.grow_by(context, context))

    @property
    def lit_pixels_count(self) -> int:
        if not self.inverted:
            return len(self.lit)
        else:
            raise ValueError("infinite number of pixels is lit")

    @property
    def dark_pixels_count(self) -> int:
        if self.inverted:
            return len(self.lit)
        else:
            raise ValueError("infinite number of pixels is dark")

    def draw(self, context: int = 1, light_char: str = '#', dark_char: str = '.') -> None:
        assert len(light_char) == 1
        assert len(dark_char) == 1

        canvas = self.bounds.grow_by(context, context)

        def char(pos: Pos) -> str:
            return light_char if self[pos] else dark_char

        for y in canvas.range_y():
            print(''.join(char((x, y)) for x in canvas.range_x()))


class Algorithm:
    def __init__(self, rules: Iterable[bool]):
        self.rules = list(rules)
        assert len(self.rules) == 512
        # assert self.rules[0] is False

    def __str__(self) -> str:
        return ''.join('#' if rule else '.' for rule in self.rules)

    def __repr__(self) -> str:
        return f'{type(self).__name__}.from_str({str(self)!r})'

    def __getitem__(self, n: int) -> bool:
        return self.rules[n]

    @classmethod
    def from_str(cls, string: str, light_char: str = '#', dark_char: str = '.') -> 'Algorithm':
        assert len(light_char) == 1
        assert len(dark_char) == 1
        char_to_bool = {light_char: True, dark_char: False}
        return cls(char_to_bool[ch] for ch in string)

    def enhance(self, image: Image, runs: int = 1) -> Image:
        assert runs >= 0

        neighbors = {
            (dx - 1, dy - 1): 1 << (8 - (3 * dy + dx))
            for dy in range(3)
            for dx in range(3)
        }

        def new_lit(img: Image, pos: Pos) -> bool:
            x, y = pos
            total = sum(
                q
                for (dx, dy), q in neighbors.items()
                if img[x + dx, y + dy]
            )
            return self[total]

        for _ in tqdm(range(runs), desc="enhancing", unit='runs', delay=1.0):
            image = type(image)(
                pixels=((pos, new_lit(image, pos)) for pos, lit in image.pixel_rows(context=1)),
                others=self[511 if image.inverted else 0]
            )

        return image

    def enhance_wrong(self, image: Image, runs: int = 1) -> Image:
        assert runs >= 0

        neighbors = {
            (x - 1, y - 1): 1 << (x + 3 * y)
            for x in range(3)
            for y in range(3)
        }

        for _ in range(runs):

            totals = defaultdict(int)
            for (x, y), lit in image.pixel_rows():
                if not lit:
                    continue
                for (dx, dy), multiplier in neighbors.items():
                    totals[(x + dx, y + dy)] += multiplier

            others = self[511 if image.others else 0]

            image = type(image)(
                pixels=(
                    (pos, not others)
                    for pos, total in totals.items()
                    if self[total] != others
                ),
                others=others
            )

        return image


Input = tuple[Algorithm, Image]


def input_from_text(text: str) -> Input:
    return input_from_lines(text.strip().splitlines())


def input_from_file(fn: str) -> Input:
    return input_from_lines(open(relative_path(__file__, fn)))


def input_from_lines(lines: Iterable[str], light_char: str = '#', dark_char: str = '.') -> Input:
    lines = iter(lines)

    algorithm_string = ''
    while True:
        line = next(lines).strip()
        if line:
            algorithm_string += line
        else:
            break

    algorithm = Algorithm.from_str(algorithm_string, light_char=light_char, dark_char=dark_char)

    lit = {light_char: True, dark_char: False}
    image = Image(
        ((x, y), lit[ch])
        for y, line in enumerate(lines)
        for x, ch in enumerate(line.strip())
    )

    return algorithm, image


if __name__ == '__main__':
    algorithm_, image_ = input_from_file('data/20-input.txt')
    part_1(algorithm_, image_)
    part_2(algorithm_, image_)
