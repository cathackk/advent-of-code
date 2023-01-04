"""
Advent of Code 2018
Day 10: The Stars Align
https://adventofcode.com/2018/day/10
"""

from functools import lru_cache
from typing import Iterable
from typing import Iterator

from tqdm import tqdm

from common import ocr
from common.rect import Rect
from common.text import parse_line
from common.xy import Point
from common.xy import Vector
from meta.aoc_tools import data_path


def part_1(stars: 'Stars', font: ocr.Font = ocr.FONT_10X8) -> str:
    """
    It's no use; your navigation system simply isn't capable of providing walking directions in the
    arctic circle, and certainly not in 1018.

    The Elves suggest an alternative. In times like these, North Pole rescue operations will arrange
    points of light in the sky to guide missing Elves back to base. Unfortunately, the message is
    easy to miss: the points move slowly enough that it takes hours to align them, but have so much
    momentum that they only stay aligned for a second. If you blink at the wrong time, it might be
    hours before another message appears.

    You can see these points of light floating in the distance, and record their position in the sky
    and their velocity, the relative change in position per second (your puzzle input). The coordi-
    nates are all given from your perspective; given enough time, those positions and velocities
    will move the points into a cohesive message!

    Rather than wait, you decide to fast-forward the process and calculate what the points will
    eventually spell.

    For example, suppose you note the following points:

        >>> example_stars = stars_from_text('''
        ...     position=< 9,  1> velocity=< 0,  2>
        ...     position=< 7,  0> velocity=<-1,  0>
        ...     position=< 3, -2> velocity=<-1,  1>
        ...     position=< 6, 10> velocity=<-2, -1>
        ...     position=< 2, -4> velocity=< 2,  2>
        ...     position=<-6, 10> velocity=< 2, -2>
        ...     position=< 1,  8> velocity=< 1, -1>
        ...     position=< 1,  7> velocity=< 1,  0>
        ...     position=<-3, 11> velocity=< 1, -2>
        ...     position=< 7,  6> velocity=<-1, -1>
        ...     position=<-2,  3> velocity=< 1,  0>
        ...     position=<-4,  3> velocity=< 2,  0>
        ...     position=<10, -3> velocity=<-1,  1>
        ...     position=< 5, 11> velocity=< 1, -2>
        ...     position=< 4,  7> velocity=< 0, -1>
        ...     position=< 8, -2> velocity=< 0,  1>
        ...     position=<15,  0> velocity=<-2,  0>
        ...     position=< 1,  6> velocity=< 1,  0>
        ...     position=< 8,  9> velocity=< 0, -1>
        ...     position=< 3,  3> velocity=<-1,  1>
        ...     position=< 0,  5> velocity=< 0, -1>
        ...     position=<-2,  2> velocity=< 2,  0>
        ...     position=< 5, -2> velocity=< 1,  2>
        ...     position=< 1,  4> velocity=< 2,  1>
        ...     position=<-2,  7> velocity=< 2, -2>
        ...     position=< 3,  6> velocity=<-1, -1>
        ...     position=< 5,  0> velocity=< 1,  0>
        ...     position=<-6,  0> velocity=< 2,  0>
        ...     position=< 5,  9> velocity=< 1, -2>
        ...     position=<14,  7> velocity=<-2,  0>
        ...     position=<-3,  6> velocity=< 2, -1>
        ... ''')
        >>> len(example_stars)
        31
        >>> example_stars[:3]
        ((Point(9, 1), Vector(0, 2)), (Point(7, 0), Vector(-1, 0)), (Point(3, -2), Vector(-1, 1)))

    Each line represents one point. Positions are given as `<X, Y>` pairs: X represents how far left
    (negative) or right (positive) the point appears, while Y represents how far up (negative) or
    down (positive) the point appears.

    At `0` seconds, each point has the position given. Each second, each point's velocity is added
    to its position. So, a point with velocity `<1, -2>` is moving to the right, but is moving
    upward twice as quickly. If this point's initial position were `<3, 9>`, after `3` seconds, its
    position would become `<6, 3>`.

    Over time, the points listed above would move like this:

        >>> moving_stars = move(example_stars)
        >>> frame = Rect((-6, -4), (15, 11))
        >>> print(drawn(next(moving_stars), frame))  # initially
        ········*·············
        ················*·····
        ·········*·*··*·······
        ······················
        *··········*·*·······*
        ···············*······
        ····*·················
        ··*·*····*············
        ·······*··············
        ······*···············
        ···*···*·*···*········
        ····*··*··*·········*·
        ·······*··············
        ···········*··*·······
        *···········*·········
        ···*·······*··········
        >>> print(drawn(next(moving_stars), frame))  # after 1 second
        ······················
        ······················
        ··········*····*······
        ········*·····*·······
        ··*·········*······*··
        ······················
        ······*···············
        ····**·········*······
        ······*·*·············
        ·····**·**··*·········
        ········*·*···········
        ········*···*·····*···
        ··*···········*·······
        ····*·····*·*·········
        ······················
        ······················
        >>> print(drawn(next(moving_stars), frame))  # after 2 seconds
        ······················
        ······················
        ······················
        ··············*·······
        ····*··*···****··*····
        ······················
        ········*····*········
        ······*·*·············
        ·······*···*··········
        ·······*··*··*·*······
        ····*····*·*··········
        ·····*···*···**·*·····
        ········*·············
        ······················
        ······················
        ······················
        >>> print(drawn(next(moving_stars), frame))  # after 3 seconds
        ······················
        ······················
        ······················
        ······················
        ······*···*··***······
        ······*···*···*·······
        ······*···*···*·······
        ······*****···*·······
        ······*···*···*·······
        ······*···*···*·······
        ······*···*···*·······
        ······*···*··***······
        ······················
        ······················
        ······················
        ······················
        >>> print(drawn(next(moving_stars), frame))  # after 4 seconds
        ······················
        ······················
        ······················
        ············*·········
        ········**···*·*······
        ······*·····*··*······
        ·····*··**·**·*·······
        ·······**·*····*······
        ···········*····*·····
        ··············*·······
        ····*······*···*······
        ·····*·····**·········
        ···············*······
        ···············*······
        ······················
        ······················

    After 3 seconds, the message appeared briefly: **`HI`**. Of course, your message will be much
    longer and will take many more seconds to appear.

    **What message will eventually appear in the sky?**

        >>> part_1(example_stars, font=ocr.FONT_8X6)
        part 1: message says 'HI'
        'HI'
    """

    message, _ = watch_for_message(stars, font)
    print(f"part 1: message says {message!r}")
    return message


def part_2(stars: 'Stars', font: ocr.Font = ocr.FONT_10X8) -> int:
    """
    Good thing you didn't have to wait, because that would have taken a long time - much longer than
    the **`3`** seconds in the example above.

    Impressed by your sub-hour communication capabilities, the Elves are curious: **exactly how many
    seconds would they have needed to wait for that message to appear?

        >>> example_stars = stars_from_file('data/10-example.txt')
        >>> part_2(example_stars, font=ocr.FONT_8X6)
        part 2: message appears in 3 seconds
        3
    """

    _, seconds = watch_for_message(stars, font)
    print(f"part 2: message appears in {seconds} seconds")
    return seconds


Star = tuple[Point, Vector]
Stars = tuple[Star, ...]


def move(stars: Stars) -> Iterator[Stars]:
    while True:
        yield stars
        stars = tuple((pos + vel, vel) for pos, vel in stars)


@lru_cache(maxsize=4)
def watch_for_message(stars: Stars, font: ocr.Font) -> tuple[str, int]:
    return next(
        (font.read_string(drawn(stars, bounds)), tick)
        for tick, stars in tqdm(
            enumerate(move(stars)), desc="watching stars", unit=" ticks", unit_scale=True, delay=0.5
        )
        if (bounds := Rect.with_all((x, y) for (x, y), _ in stars)).height <= font.char_height
    )


def drawn(stars: Stars, bounds: Rect = None, char_star='*', char_sky='·') -> str:
    positions = set(tuple(pos) for pos, _ in stars)
    if bounds is None:
        bounds = Rect.with_all((x, y) for x, y in positions)

    return "\n".join(
        ''.join(char_star if (x, y) in positions else char_sky for x in bounds.range_x())
        for y in bounds.range_y()
    )


def stars_from_text(text: str) -> Stars:
    return tuple(stars_from_lines(text.strip().splitlines()))


def stars_from_file(fn: str) -> Stars:
    return tuple(stars_from_lines(open(fn)))


def stars_from_lines(lines: Iterable[str]) -> Iterable[Star]:
    for line in lines:
        p_x, p_y, v_x, v_y = parse_line(line.strip(), "position=<$, $> velocity=<$, $>")
        yield Point(int(p_x), int(p_y)), Vector(int(v_x), int(v_y))


def main(input_path: str = data_path(__file__)) -> tuple[str, int]:
    stars = stars_from_file(input_path)
    result_1 = part_1(stars)
    result_2 = part_2(stars)
    return result_1, result_2


if __name__ == '__main__':
    main()
