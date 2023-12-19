"""
Advent of Code 2023
Day 18: Lavaduct Lagoon
https://adventofcode.com/2023/day/18
"""

from dataclasses import dataclass
from itertools import accumulate
from typing import Iterable

from common.file import relative_path
from common.heading import Heading
from common.iteration import zip1
from common.rect import Rect
from common.text import parse_line
from common.utils import some


def part_1(dig_plan: Iterable['Dig']) -> int:
    """
    Thanks to your efforts, the machine parts factory is one of the first factories up and running
    since the lavafall came back. However, to catch up with the large backlog of parts requests,
    the factory will also need a **large supply of lava** for a while; the Elves have already
    started creating a large lagoon nearby for this purpose.

    However, they aren't sure the lagoon will be big enough; they've asked you to take a look at
    the **dig plan** (your puzzle input). For example:

        >>> example = dig_plan_from_text('''
        ...     R 6 (#70c710)
        ...     D 5 (#0dc571)
        ...     L 2 (#5713f0)
        ...     D 2 (#d2c081)
        ...     R 2 (#59c680)
        ...     D 2 (#411b91)
        ...     L 5 (#8ceee2)
        ...     U 2 (#caa173)
        ...     L 1 (#1b58a2)
        ...     U 2 (#caa171)
        ...     R 2 (#7807d2)
        ...     U 3 (#a77fa3)
        ...     L 2 (#015232)
        ...     U 2 (#7a21e3)
        ... ''')
        >>> len(example)
        14
        >>> example[:3]  # doctest: +NORMALIZE_WHITESPACE
        [Dig(heading=Heading.EAST, distance=6, color='70c710'),
         Dig(heading=Heading.SOUTH, distance=5, color='0dc571'),
         Dig(heading=Heading.WEST, distance=2, color='5713f0')]

    The digger starts in a 1 meter cube hole in the ground. They then dig the specified number of
    meters **up** (`U`), **down** (`D`), **left** (`L`), or **right** (`R`), clearing full 1 meter
    cubes as they go. The directions are given as seen from above, so if "up" were north, then
    "right" would be east, and so on. Each trench is also listed with **the color that the edge of
    the trench should be painted** as an RGB hexadecimal color code.

    When viewed from above, the above example dig plan would result in the following loop of
    **trench** (`#`) having been dug out from otherwise **ground-level terrain** (`·`):

        >>> draw_trench(example)
        #######
        #·····#
        ###···#
        ··#···#
        ··#···#
        ###·###
        #···#··
        ##··###
        ·#····#
        ·######

    At this point, the trench could contain 38 cubic meters of lava. However, this is just the edge
    of the lagoon; the next step is to **dig out the interior** (`X`) so that it is one meter deep
    as well:

        >>> draw_trench(example, interior_char='X')
        #######
        #XXXXX#
        ###XXX#
        ··#XXX#
        ··#XXX#
        ###X###
        #XXX#··
        ##XX###
        ·#XXXX#
        ·######

    Now, the lagoon can contain a much more respectable **`62`** cubic meters of lava.

        >>> lagoon_size(example)
        62

    While the interior is dug out, the edges are also painted according to the color codes in the
    dig plan.

    The Elves are concerned the lagoon won't be large enough; if they follow their dig plan,
    **how many cubic meters of lava could it hold?**

        >>> part_1(example)
        part 1: the lagoon can hold 62 cubic meters of lava
        62
    """

    result = lagoon_size(dig_plan)

    print(f"part 1: the lagoon can hold {result} cubic meters of lava")
    return result


def part_2(dig_plan: Iterable['Dig']) -> int:
    r"""
    The Elves were right to be concerned; the planned lagoon would be **much too small**.

    After a few minutes, someone realizes what happened; someone **swapped the color and instruction
    parameters** when producing the dig plan. They don't have time to fix the bug; one of them asks
    if you can **extract the correct instructions** from the hexadecimal codes.

    Each hexadecimal code is **six hexadecimal digits** long. The first five hexadecimal digits
    encode the **distance in meters** as a five-digit hexadecimal number. The last hexadecimal digit
    encodes the **direction to dig**: `0` means `R`, `1` means `D`, `2` means `L` and `3` means `U`.

    So, in the above example, the hexadecimal codes can be converted into the true instructions:

        >>> example = dig_plan_from_file('data/18-example.txt')
        >>> example_1 = [Dig.from_color(dig.color) for dig in example]
        >>> print('\n'.join(f"#{dig.color} = {dig_1}" for dig, dig_1 in zip(example, example_1)))
        #70c710 = R 461937
        #0dc571 = D 56407
        #5713f0 = R 356671
        #d2c081 = D 863240
        #59c680 = R 367720
        #411b91 = D 266681
        #8ceee2 = L 577262
        #caa173 = U 829975
        #1b58a2 = L 112010
        #caa171 = D 829975
        #7807d2 = L 491645
        #a77fa3 = U 686074
        #015232 = L 5411
        #7a21e3 = U 500254

    Digging out this loop and its interior produces a lagoon that can hold an impressive
    **`952408144115`** cubic meters of lava:

        >>> lagoon_size_optimized(example_1)
        952408144115

    Convert the hexadecimal color codes into the correct instructions; if the Elves follow this new
    dig plan, **how many cubic meters of lava could the lagoon hold?**


        >>> part_2(example)
        part 2: the lagoon can actually hold 952408144115 cubic meters of lava
        952408144115
    """

    result = lagoon_size_optimized(Dig.from_color(some(dig.color)) for dig in dig_plan)

    print(f"part 2: the lagoon can actually hold {result} cubic meters of lava")
    return result


HEADINGS = [Heading.EAST, Heading.SOUTH, Heading.WEST, Heading.NORTH]
CHAR_TO_HEADING = dict(zip('RDLU', HEADINGS))
HEADING_TO_CHAR = {heading: char for char, heading in CHAR_TO_HEADING.items()}


Pos = tuple[int, int]


@dataclass(frozen=True)
class Dig:
    heading: Heading
    distance: int
    color: str | None = None

    def __str__(self) -> str:
        h_char = HEADING_TO_CHAR[self.heading]
        head = f"{h_char} {self.distance}"
        return f"{head} #{self.color}" if self.color else head

    @classmethod
    def from_line(cls, line: str) -> 'Dig':
        # 'R 6 (#70c710)'
        h, d, color = parse_line(line, '$ $ (#$)')
        return cls(CHAR_TO_HEADING[h], int(d), color)

    @classmethod
    def from_color(cls, color: str) -> 'Dig':
        assert len(color) == 6
        return cls(
            heading=HEADINGS[int(color[-1])],
            distance=int(color[:-1], 16),
        )

    @classmethod
    def between(cls, pos_1: Pos, pos_2: Pos) -> 'Dig':
        x_1, y_1 = pos_1
        x_2, y_2 = pos_2
        match x_2 - x_1, y_2 - y_1:
            case 0, 0:
                raise ValueError("no distance")
            case d_x, 0:
                return cls(heading=Heading.EAST if d_x > 0 else Heading.WEST, distance=abs(d_x))
            case 0, d_y:
                return cls(heading=Heading.SOUTH if d_y > 0 else Heading.NORTH, distance=abs(d_y))
            case unexpected:
                raise ValueError(unexpected)


def trace_trench(dig_plan: Iterable[Dig], init_pos: Pos = (0, 0)) -> Iterable[Pos]:
    return accumulate(
        initial=init_pos,
        func=lambda pos, heading: heading.move(pos),
        iterable=(
            dig.heading
            for dig in dig_plan
            for _ in range(dig.distance)
        ),
    )


def adjacent(pos: Pos) -> Iterable[Pos]:
    return (heading.move(pos) for heading in Heading)


def fill(trench: set[Pos]) -> Iterable[Pos]:
    x_0, y_0 = min(trench)
    assert (x_0 + 1, y_0) in trench
    assert (x_0, y_0 + 1) in trench
    assert (init_pos := (x_0 + 1, y_0 + 1)) not in trench

    to_fill = [init_pos]
    filled: set[Pos] = set()

    while to_fill:
        pos = to_fill.pop()
        yield pos
        filled.add(pos)
        to_fill.extend(
            npos
            for heading in Heading
            if (npos := heading.move(pos)) not in trench
            if npos not in filled
        )


def lagoon_size(dig_plan: Iterable[Dig]) -> int:
    trench = set(trace_trench(dig_plan))
    interior = set(fill(trench))
    return len(trench) + len(interior)


def lagoon_size_optimized(dig_plan: Iterable[Dig]) -> int:
    corners = list(
        accumulate(
            initial=(0, 0),
            func=lambda pos, dig: dig.heading.move(pos, dig.distance),
            iterable=dig_plan,
        )
    )
    assert corners[0] == corners[-1]

    grid_xs = sorted(set(x + dx for x, _ in corners for dx in range(2)))
    grid_ys = sorted(set(y + dy for _, y in corners for dy in range(2)))
    simplified_trench = set(
        trace_trench(
            dig_plan=(
                Dig.between(*pos_pair)
                for pos_pair in zip1(
                    (grid_xs.index(x), grid_ys.index(y))
                    for x, y in corners
                )
            ),
            init_pos=(grid_xs.index(0), grid_ys.index(0)),
        )
    )
    simplified_interior = set(fill(simplified_trench))

    def real_size(x: int, y: int) -> int:
        d_x = grid_xs[x+1] - grid_xs[x]
        d_y = grid_ys[y+1] - grid_ys[y]
        return d_x * d_y

    return sum(real_size(x, y) for x, y in (simplified_trench | simplified_interior))


def draw_trench(
    dig_plan: Iterable[Dig],
    trench_char: str = '#',
    ground_char: str = '·',
    interior_char: str = None,
) -> None:
    canvas: dict[Pos, str] = {}

    trench = set(trace_trench(dig_plan))
    canvas.update((pos, trench_char) for pos in trench)

    if interior_char:
        canvas.update((pos, interior_char) for pos in fill(trench))

    bounds = Rect.with_all(canvas)
    for y in bounds.range_y():
        print(''.join(canvas.get((x, y), ground_char) for x in bounds.range_x()))


def dig_plan_from_file(fn: str) -> list[Dig]:
    return list(dig_plan_from_lines(open(relative_path(__file__, fn))))


def dig_plan_from_text(text: str) -> list[Dig]:
    return list(dig_plan_from_lines(text.strip().splitlines()))


def dig_plan_from_lines(lines: Iterable[str]) -> Iterable[Dig]:
    return (Dig.from_line(line.strip()) for line in lines)


def main(input_fn: str = 'data/18-input.txt') -> tuple[int, int]:
    dig_plan = dig_plan_from_file(input_fn)
    result_1 = part_1(dig_plan)
    result_2 = part_2(dig_plan)
    return result_1, result_2


if __name__ == '__main__':
    main()
