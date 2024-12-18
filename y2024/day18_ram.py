"""
Advent of Code 2024
Day 18: RAM Run
https://adventofcode.com/2024/day/18
"""

from itertools import islice
from typing import Iterable

from common.bsrange import BSRange
from common.canvas import Canvas
from common.file import relative_path
from common.graph import shortest_path
from common.heading import Heading
from common.rect import Rect


Pos = tuple[int, int]
DEFAULT_BOUNDS = Rect.at_origin(width=71, height=71)
DEFAULT_BYTES_COUNT = 1024


def part_1(
    bytes_: Iterable[Pos],
    bytes_count: int = DEFAULT_BYTES_COUNT,
    bounds: Rect = DEFAULT_BOUNDS,
) -> int:
    """
    You and The Historians look a lot more pixelated than you remember. You're inside a computer
    (y2017/day02_spreadsheet.py) at the North Pole!

    Just as you're about to check out your surroundings, a program runs up to you. "This region of
    memory isn't safe! The User misunderstood what a pushdown automaton is and their algorithm is
    pushing whole bytes down on top of us! Run!"

    The algorithm is fast - it's going to cause a byte to fall into your memory space once every
    nanosecond! Fortunately, you're **faster**, and by quickly scanning the algorithm, you create
    a **list of which bytes will fall** (your puzzle input) in the order they'll land in your memory
    space.

    Your memory space is a two-dimensional grid with coordinates that range from `0` to `70` both
    horizontally and vertically. However, for the sake of example, suppose you're on a smaller grid
    with coordinates that range from `0` to `6` and the following list of incoming byte positions:

        >>> example_bytes = bytes_from_text('''
        ...     5,4
        ...     4,2
        ...     4,5
        ...     3,0
        ...     2,1
        ...     6,3
        ...     2,4
        ...     1,5
        ...     0,6
        ...     3,3
        ...     2,6
        ...     5,1
        ...     1,2
        ...     5,5
        ...     2,5
        ...     6,5
        ...     1,4
        ...     0,4
        ...     6,4
        ...     1,1
        ...     6,1
        ...     1,0
        ...     0,5
        ...     1,6
        ...     2,0
        ... ''')
        >>> example_bytes  # doctest: +ELLIPSIS
        [(5, 4), (4, 2), (4, 5), (3, 0), ..., (1, 6), (2, 0)]
        >>> len(example_bytes)
        25

    Each byte position is given as an `X,Y` coordinate, where `X` is the distance from the left edge
    of your memory space and `Y` is the distance from the top edge of your memory space.

    You and The Historians are currently in the top left corner of the memory space (at `0,0`) and
    need to reach the exit in the bottom right corner (at `70,70` in your memory space, but at `6,6`
    in this example). You'll need to simulate the falling bytes to plan out where it will be safe
    to run; for now, simulate just the first few bytes falling into your memory space.

        >>> example_bounds = Rect.at_origin(width=7, height=7)

    As bytes fall into your memory space, they make that coordinate **corrupted**. Corrupted memory
    coordinates cannot be entered by you or The Historians, so you'll need to plan your route
    carefully. You also cannot leave the boundaries of the memory space; your only hope is to reach
    the exit.

    In the above example, if you were to draw the memory space after the first `12` bytes have
    fallen (using `·` for safe and `#` for corrupted), it would look like this:

        >>> fallen_bytes = example_bytes[:12]
        >>> print_space(corruption=fallen_bytes[:12], bounds=example_bounds)
        ···#···
        ··#··#·
        ····#··
        ···#··#
        ··#··#·
        ·#··#··
        #·#····

    You can take steps up, down, left, or right. After just 12 bytes have corrupted locations in
    your memory space, the shortest path from the top left corner to the exit would take **`22`**
    steps. Here (marked with `O`) is one such path:

        >>> length, path = find_path(corruption=fallen_bytes, bounds=example_bounds)
        >>> length
        22
        >>> print_space(corruption=fallen_bytes, path=path, bounds=example_bounds)
        OO·#OOO
        ·O#OO#O
        ·OOO#OO
        ···#OO#
        ··#OO#·
        ·#·O#··
        #·#OOOO

    Simulate the first kilobyte (`1024` bytes) falling onto your memory space. Afterward,
    **what is the minimum number of steps needed to reach the exit?**

        >>> part_1(example_bytes, bytes_count=12, bounds=example_bounds)
        part 1: after the first 12 bytes fall down, the shortest path to the exit takes 22 steps
        22
    """

    bytes_list = list(islice(bytes_, bytes_count))
    assert len(bytes_list) == bytes_count

    result, _ = find_path(bytes_list, bounds)

    print(
        f"part 1: "
        f"after the first {bytes_count} bytes fall down, "
        f"the shortest path to the exit takes {result} steps"
    )
    return result


def part_2(bytes_: Iterable[Pos], bounds: Rect = DEFAULT_BOUNDS) -> str:
    """
    The Historians aren't as used to moving around in this pixelated universe as you are. You're
    afraid they're not going to be fast enough to make it to the exit before the path is completely
    blocked.

    To determine how fast everyone needs to go, you need to determine **the first byte that will cut
    off the path to the exit**.

    In the above example, after the byte at `1,1` falls, there is still a path to the exit:

        >>> example_bytes = bytes_from_file('data/18-example.txt')
        >>> example_bytes.index((1, 1))
        19
        >>> example_bounds = Rect.at_origin(width=7, height=7)
        >>> _, path = find_path(example_bytes[:20], example_bounds)
        >>> print_space(corruption=example_bytes[:20], path=path, bounds=example_bounds, )
        O··#OOO
        O##OO#O
        O#OO#OO
        OOO#OO#
        ###OO##
        ·##O###
        #·#OOOO

    However, after adding the very next byte (at `6,1`), there is no longer a path to the exit:

        >>> example_bytes[20]
        (6, 1)
        >>> find_path(example_bytes[:21], example_bounds)
        Traceback (most recent call last):
        ...
        ValueError: path not found
        >>> print_space(example_bytes[:21], example_bounds)
        ···#···
        ·##··##
        ·#··#··
        ···#··#
        ###··##
        ·##·###
        #·#····

    So, in this example, the coordinates of the first byte that prevents the exit from being
    reachable are **`6,1`**.

        >>> first_byte_to_block_path(example_bytes, example_bounds)
        (20, (6, 1))

    Simulate more of the bytes that are about to corrupt your memory space.
    **What are the coordinates of the first byte that will prevent the exit from being reachable
    from your starting position?**
    (Provide the answer as two integers separated by a comma with no other characters.)

        >>> part_2(example_bytes, bounds=example_bounds)
        part 2: the first byte to block the path lands after 21 nanoseconds at 6,1
        '6,1'
    """

    nano, pos = first_byte_to_block_path(bytes_, bounds)
    result = f"{pos[0]},{pos[1]}"

    print(f"part 2: the first byte to block the path lands after {nano+1} nanoseconds at {result}")
    return result


def print_space(corruption: Iterable[Pos], bounds: Rect, path: Iterable[Pos] = ()) -> None:
    c = Canvas(bounds=bounds)
    c.draw_many((pos, '#') for pos in corruption)
    c.draw_many((pos, 'O') for pos in path)
    if path:
        c.draw((0, 0), 'O')
    print(c.render(empty_char='·'))


def find_path(
    corruption: Iterable[Pos],
    bounds: Rect,
    start: Pos = (0, 0),
    target: Pos | None = None,
) -> tuple[int, list[Pos]]:
    corrupted = set(corruption)

    def edges(node: Pos) -> Iterable[tuple[Pos, Pos, int]]:
        return (
            (pos, pos, 1)
            for heading in Heading
            if (pos := node + heading) in bounds
            if pos not in corrupted
        )

    if target is None:
        target = bounds.bottom_right

    assert start not in corrupted
    assert target not in corrupted

    return shortest_path(start, target, edges, nodes_count=bounds.area)


def first_byte_to_block_path(bytes_: Iterable[Pos], bounds: Rect) -> tuple[int, Pos]:
    bytes_list = list(bytes_)

    def has_path(nano: int) -> bool:
        try:
            find_path(bytes_list[:nano], bounds)
        except ValueError as not_found:
            assert not_found.args == ("path not found",)
            return False
        else:
            return True

    # binary search
    nanos_range = BSRange(0, len(bytes_list))
    while not nanos_range.has_single_value():
        tested_nano = nanos_range.mid
        if has_path(tested_nano):
            # look further
            nanos_range = BSRange(tested_nano, nanos_range.upper)
        else:
            # look sooner
            nanos_range = BSRange(nanos_range.lower, tested_nano)

    result_index = nanos_range.single_value
    result_pos = bytes_list[result_index]
    return result_index, result_pos


def bytes_from_file(fn: str) -> list[Pos]:
    return list(bytes_from_lines(open(relative_path(__file__, fn))))


def bytes_from_text(text: str) -> list[Pos]:
    return list(bytes_from_lines(text.strip().splitlines()))


def bytes_from_lines(lines: Iterable[str]) -> Iterable[Pos]:
    for line in lines:
        x, y = line.strip().split(',')
        yield int(x), int(y)


def main(input_fn: str = 'data/18-input.txt') -> tuple[int, str]:
    bytes_ = bytes_from_file(input_fn)
    result_1 = part_1(bytes_)
    result_2 = part_2(bytes_)
    return result_1, result_2


if __name__ == '__main__':
    main()
