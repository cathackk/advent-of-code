"""
Advent of Code 2022
Day 9: Rope Bridge
https://adventofcode.com/2022/day/9
"""

from enum import Enum
from typing import Iterable, Self

from common.iteration import dgroupby_pairs
from common.math import sgn
from common.rect import Rect
from meta.aoc_tools import data_path


def part_1(moves: Iterable['Move']) -> int:
    """
    This rope bridge creaks as you walk along it. You aren't sure how old it is, or whether it can
    even support your weight. It seems to support the Elves just fine, though. The bridge spans
    a gorge which was carved out by the massive river far below you.

    You step carefully; as you do, the ropes stretch and twist. You decide to distract yourself by
    modeling rope physics; maybe you can even figure out where **not** to step.

    Consider a rope with a knot at each end; these knots mark the **head** and the **tail** of
    the rope. If the head moves far enough away from the tail, the tail is pulled toward the head.

    Due to nebulous reasoning involving Planck lengths, you should be able to model the positions of
    the knots on a two-dimensional grid. Then, by following a hypothetical **series of motions**
    (your puzzle input) for the head, you can determine how the tail will move.

    Due to the aforementioned Planck lengths, the rope must be quite short; in fact, the head (`H`)
    and tail (`T`) must **always be touching** (diagonally adjacent and even overlapping both count
    as touching):

        ····  ····  ···
        ·TH·  ·H··  ·H· (H covers T)
        ····  ··T·  ···
              ····

    If the head is ever two steps directly up, down, left, or right from the tail, the tail must
    also move one step in that direction, so it remains close enough:

        ·····    ·····    ·····
        ·TH·· -> ·T·H· -> ··TH·
        ·····    ·····    ·····

        ···    ···    ···
        ·T·    ·T·    ···
        ·H· -> ··· -> ·T·
        ···    ·H·    ·H·
        ···    ···    ···

    Otherwise, if the head and tail aren't touching and aren't in the same row or column, the tail
    always moves one step diagonally to keep up:

        ·····    ·····    ·····
        ·····    ··H··    ··H··
        ··H·· -> ····· -> ··T··
        ·T···    ·T···    ·····
        ·····    ·····    ·····

        ·····    ·····    ·····
        ·····    ·····    ·····
        ··H·· -> ···H· -> ··TH·
        ·T···    ·T···    ·····
        ·····    ·····    ·····

    You just need to work out where the tail goes as the head follows a series of motions.
    Assume the head and the tail both start at the same position, overlapping.

    For example:

        >>> ms = moves_from_text('''
        ...     R 4
        ...     U 4
        ...     L 3
        ...     D 1
        ...     R 4
        ...     D 1
        ...     L 5
        ...     R 2
        ... ''')

    This series of motions moves the head **right** four steps, then **up** four steps,
    then **left** three steps, then **down** one step, and so on.

        >>> ms  # doctest: +ELLIPSIS
        [(Direction.RIGHT, 4), (Direction.UP, 4), (Direction.LEFT, 3), (Direction.DOWN, 1), ...]
        >>> len(ms)
        8

    After each step, you'll need to update the position of the tail if the step means the head is no
    longer adjacent to the tail. Visually, these motions occur as follows (`s` marks the starting
    position as a reference point):

        >>> bounds = Rect((0, 0), (5, -4))
        >>> rs = list(create_ropes(ms, draw_progress_in=bounds))
        == Initial State ==
        ······
        ······
        ······
        ······
        H·····  (H covers T, s)
        == R 4 ==
        ······
        ······
        ······
        ······
        TH····  (T covers s)
        +
        ······
        ······
        ······
        ······
        sTH···
        +
        ······
        ······
        ······
        ······
        s·TH··
        +
        ······
        ······
        ······
        ······
        s··TH·
        == U 4 ==
        ······
        ······
        ······
        ····H·
        s··T··
        +
        ······
        ······
        ····H·
        ····T·
        s·····
        +
        ······
        ····H·
        ····T·
        ······
        s·····
        +
        ····H·
        ····T·
        ······
        ······
        s·····
        == L 3 ==
        ···H··
        ····T·
        ······
        ······
        s·····
        +
        ··HT··
        ······
        ······
        ······
        s·····
        +
        ·HT···
        ······
        ······
        ······
        s·····
        == D 1 ==
        ··T···
        ·H····
        ······
        ······
        s·····
        == R 4 ==
        ··T···
        ··H···
        ······
        ······
        s·····
        +
        ··T···
        ···H··
        ······
        ······
        s·····
        +
        ······
        ···TH·
        ······
        ······
        s·····
        +
        ······
        ····TH
        ······
        ······
        s·····
        == D 1 ==
        ······
        ····T·
        ·····H
        ······
        s·····
        == L 5 ==
        ······
        ····T·
        ····H·
        ······
        s·····
        +
        ······
        ····T·
        ···H··
        ······
        s·····
        +
        ······
        ······
        ··HT··
        ······
        s·····
        +
        ······
        ······
        ·HT···
        ······
        s·····
        +
        ······
        ······
        HT····
        ······
        s·····
        == R 2 ==
        ······
        ······
        ·H····  (H covers T)
        ······
        s·····
        +
        ······
        ······
        ·TH···
        ······
        s·····

    After simulating the rope, you can count up all of the positions the **tail visited at least
    once**. In this diagram, `s` again marks the starting position (which the tail also visited)
    and `#` marks other positions the tail visited:

        >>> tails = set(tail_positions(rs))
        >>> draw_positions(bounds, tails)
        ··##··
        ···##·
        ·####·
        ····#·
        s###··

    So, there are **13** positions the tail visited at least once.

        >>> len(tails)
        13

    Simulate your complete hypothetical series of motions.
    **How many positions does the tail of the rope visit at least once?**

        >>> part_1(ms)
        part 1: tail visited 13 positions
        13
    """

    result = len(set(tail_positions(create_ropes(moves))))

    print(f"part 1: tail visited {result} positions")
    return result


def part_2(moves: Iterable['Move']) -> int:
    """
    A rope snaps! Suddenly, the river is getting a lot closer than you remember. The bridge is still
    there, but some of the ropes that broke are now whipping toward you as you fall through the air!

    The ropes are moving too quickly to grab; you only have a few seconds to choose how to arch your
    body to avoid being hit. Fortunately, your simulation can be extended to support longer ropes.

    Rather than two knots, you now must simulate a rope consisting of **ten** knots. One knot is
    still the head of the rope and moves according to the series of motions. Each knot further down
    the rope follows the knot in front of it using the same rules as before.

    Using the same series of motions as the above example, but with the knots marked `H`, `1`, `2`,
    ..., `9`, the motions now occur as follows:

        >>> moves_1 = moves_from_file(data_path(__file__, 'example.txt'))
        >>> len(moves_1)
        8
        >>> bounds_1 = Rect((0, 0), (5, -4))
        >>> ropes_1 = list(create_ropes(moves_1, length=10, draw_progress_in=bounds_1))
        == Initial State ==
        ······
        ······
        ······
        ······
        H·····  (H covers 1, 2, 3, 4, 5, 6, 7, 8, 9, s)
        == R 4 ==
        ······
        ······
        ······
        ······
        1H····  (1 covers 2, 3, 4, 5, 6, 7, 8, 9, s)
        +
        ······
        ······
        ······
        ······
        21H···  (2 covers 3, 4, 5, 6, 7, 8, 9, s)
        +
        ······
        ······
        ······
        ······
        321H··  (3 covers 4, 5, 6, 7, 8, 9, s)
        +
        ······
        ······
        ······
        ······
        4321H·  (4 covers 5, 6, 7, 8, 9, s)
        == U 4 ==
        ······
        ······
        ······
        ····H·
        4321··  (4 covers 5, 6, 7, 8, 9, s)
        +
        ······
        ······
        ····H·
        ·4321·
        5·····  (5 covers 6, 7, 8, 9, s)
        +
        ······
        ····H·
        ····1·
        ·432··
        5·····  (5 covers 6, 7, 8, 9, s)
        +
        ····H·
        ····1·
        ··432·
        ·5····
        6·····  (6 covers 7, 8, 9, s)
        == L 3 ==
        ···H··
        ····1·
        ··432·
        ·5····
        6·····  (6 covers 7, 8, 9, s)
        +
        ··H1··
        ···2··
        ··43··
        ·5····
        6·····  (6 covers 7, 8, 9, s)
        +
        ·H1···
        ···2··
        ··43··
        ·5····
        6·····  (6 covers 7, 8, 9, s)
        == D 1 ==
        ··1···
        ·H·2··
        ··43··
        ·5····
        6·····  (6 covers 7, 8, 9, s)
        == R 4 ==
        ··1···
        ··H2··
        ··43··
        ·5····
        6·····  (6 covers 7, 8, 9, s)
        +
        ··1···
        ···H··  (H covers 2)
        ··43··
        ·5····
        6·····  (6 covers 7, 8, 9, s)
        +
        ······
        ···1H·  (1 covers 2)
        ··43··
        ·5····
        6·····  (6 covers 7, 8, 9, s)
        +
        ······
        ···21H
        ··43··
        ·5····
        6·····  (6 covers 7, 8, 9, s)
        == D 1 ==
        ······
        ···21·
        ··43·H
        ·5····
        6·····  (6 covers 7, 8, 9, s)
        == L 5 ==
        ······
        ···21·
        ··43H·
        ·5····
        6·····  (6 covers 7, 8, 9, s)
        +
        ······
        ···21·
        ··4H··  (H covers 3)
        ·5····
        6·····  (6 covers 7, 8, 9, s)
        +
        ······
        ···2··
        ··H1··  (H covers 4; 1 covers 3)
        ·5····
        6·····  (6 covers 7, 8, 9, s)
        +
        ······
        ···2··
        ·H13··  (1 covers 4)
        ·5····
        6·····  (6 covers 7, 8, 9, s)
        +
        ······
        ······
        H123··  (2 covers 4)
        ·5····
        6·····  (6 covers 7, 8, 9, s)
        == R 2 ==
        ······
        ······
        ·H23··  (H covers 1; 2 covers 4)
        ·5····
        6·····  (6 covers 7, 8, 9, s)
        +
        ······
        ······
        ·1H3··  (H covers 2, 4)
        ·5····
        6·····  (6 covers 7, 8, 9, s)

    Now, you need to keep track of the positions the new tail, `9`, visits. In this example, the
    tail never moves, and so it only visits **1** position. However, **be careful**: more types of
    motion are possible than before, so you might want to visually compare your simulated rope to
    the one above.

    Here's a larger example:

        >>> moves_2 = moves_from_text('''
        ...     R 5
        ...     U 8
        ...     L 8
        ...     D 3
        ...     R 17
        ...     D 10
        ...     L 25
        ...     U 20
        ... ''')

    These motions occur as follows (individual steps are not shown):

        >>> bounds_2 = Rect((-11, -15), (14, 5))
        >>> ropes_2 = list(
        ...     create_ropes(moves_2, length=10, draw_progress_in=bounds_2, draw_steps=False)
        ... )
        == Initial State ==
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ···········H··············  (H covers 1, 2, 3, 4, 5, 6, 7, 8, 9, s)
        ··························
        ··························
        ··························
        ··························
        ··························
        == R 5 ==
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ···········54321H·········  (5 covers 6, 7, 8, 9, s)
        ··························
        ··························
        ··························
        ··························
        ··························
        == U 8 ==
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ················H·········
        ················1·········
        ················2·········
        ················3·········
        ···············54·········
        ··············6···········
        ·············7············
        ············8·············
        ···········9··············  (9 covers s)
        ··························
        ··························
        ··························
        ··························
        ··························
        == L 8 ==
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ········H1234·············
        ············5·············
        ············6·············
        ············7·············
        ············8·············
        ············9·············
        ··························
        ··························
        ···········s··············
        ··························
        ··························
        ··························
        ··························
        ··························
        == D 3 ==
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ·········2345·············
        ········1···6·············
        ········H···7·············
        ············8·············
        ············9·············
        ··························
        ··························
        ···········s··············
        ··························
        ··························
        ··························
        ··························
        ··························
        == R 17 ==
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ················987654321H
        ··························
        ··························
        ··························
        ··························
        ···········s··············
        ··························
        ··························
        ··························
        ··························
        ··························
        == D 10 ==
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ···········s·········98765
        ·························4
        ·························3
        ·························2
        ·························1
        ·························H
        == L 25 ==
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ···········s··············
        ··························
        ··························
        ··························
        ··························
        H123456789················
        == U 20 ==
        H·························
        1·························
        2·························
        3·························
        4·························
        5·························
        6·························
        7·························
        8·························
        9·························
        ··························
        ··························
        ··························
        ··························
        ··························
        ···········s··············
        ··························
        ··························
        ··························
        ··························
        ··························

    Now, the tail (`9`) visits **36** positions (including `s`) at least once:

        >>> len(tails_2 := set(tail_positions(ropes_2)))
        36
        >>> draw_positions(bounds_2, tails_2)
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        ··························
        #·························
        #·············###·········
        #············#···#········
        ·#··········#·····#·······
        ··#··········#·····#······
        ···#········#·······#·····
        ····#······s·········#····
        ·····#··············#·····
        ······#············#······
        ·······#··········#·······
        ········#········#········
        ·········########·········

    Simulate your complete series of motions on a larger rope with ten knots.
    **How many positions does the tail of the rope visit at least once?**

        >>> part_2(moves_2)
        part 2: tail visited 36 positions
        36
    """

    result = len(set(tail_positions(create_ropes(moves, length=10))))

    print(f"part 2: tail visited {result} positions")
    return result


Pos = tuple[int, int]
Rope = list[Pos]


class Direction(Enum):
    # TODO: extract into common? (taken from 2016/17)
    UP = ('U', 0, -1)
    DOWN = ('D', 0, +1)
    LEFT = ('L', -1, 0)
    RIGHT = ('R', +1, 0)

    def __init__(self, letter: str, dx: int, dy: int):
        self.letter = letter
        self.dx = dx
        self.dy = dy

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'

    def __add__(self, pos: Pos) -> Pos:
        x, y = pos
        return x + self.dx, y + self.dy

    __radd__ = __add__

    @classmethod
    def from_letter(cls, letter: str) -> Self:
        try:
            return next(d for d in cls if d.letter == letter)
        except StopIteration as stop:
            raise KeyError(letter) from stop


Move = tuple[Direction, int]


def create_ropes(
    moves: Iterable[Move],
    origin: Pos = (0, 0),
    length: int = 2,
    draw_progress_in: Rect | None = None,
    draw_steps: bool = True
) -> Iterable[Rope]:
    assert length >= 2
    knots = [origin] * length

    if draw_progress_in:
        draw_rope(draw_progress_in, knots, origin)

    for direction, distance in moves:
        for step in range(distance):
            head_x, head_y = knots[0]
            new_head = head_x + direction.dx, head_y + direction.dy
            new_knots = [new_head]
            for knot in knots[1:]:
                new_knots.append(follow_knot(new_knots[-1], knot))
            knots = new_knots

            if draw_progress_in and draw_steps:
                draw_rope(draw_progress_in, knots, origin, (direction, distance), step)

            yield knots

        if draw_progress_in and not draw_steps:
            draw_rope(draw_progress_in, knots, origin, (direction, distance))


def follow_knot(head: Pos, following: Pos) -> Pos:
    head_x, head_y = head
    foll_x, foll_y = following
    dx = foll_x - head_x
    dy = foll_y - head_y

    if abs(dx) <= 1 and abs(dy) <= 1:
        # no correction needed
        return following

    elif abs(dx) == 2 or abs(dy) == 2:
        return foll_x - sgn(dx), foll_y - sgn(dy)

    else:
        raise ValueError((head, following))


def draw_rope(bounds: Rect, rope: Rope, origin: Pos, move: Move = None, step: int = 0):
    if step == 0:
        if move:
            direction, distance = move
            print(f'== {direction.letter} {distance} ==')
        else:
            print('== Initial State ==')
    else:
        print('+')

    char_to_pos = dict(zip('HT' if len(rope) == 2 else 'H123456789', rope))
    char_to_pos['s'] = origin
    # reversed so that head covers tail
    pos_to_char = {pos: char for char, pos in reversed(char_to_pos.items())}

    covers = dgroupby_pairs(
        (y, items)
        for (_, y), items in dgroupby_pairs(
            (pos, char) for char, pos in char_to_pos.items()
        ).items()
        if len(items) > 1
    )

    for y in bounds.range_y():
        line = ''.join(pos_to_char.get((x, y), '·') for x in bounds.range_x())
        note = '; '.join(
            f'{covering} covers {", ".join(covered)}'
            for covering, *covered in covers.get(y, ())
        )
        if note:
            note = f'  ({note})'
        print(line + note)


def tail_positions(ropes: Iterable[Rope]) -> Iterable[Pos]:
    return (rope[-1] for rope in ropes)


def draw_positions(
    bounds: Rect,
    positions: Iterable[Pos],
    origin: Pos = (0, 0),
) -> None:
    pos_to_char = {pos: '#' for pos in positions}
    pos_to_char[origin] = 's'

    for y in bounds.range_y():
        print(''.join(pos_to_char.get((x, y), '·') for x in bounds.range_x()))


def moves_from_file(fn: str) -> list[Move]:
    return list(moves_from_lines(open(fn)))


def moves_from_text(text: str) -> list[Move]:
    return list(moves_from_lines(text.strip().splitlines()))


def moves_from_lines(lines: Iterable[str]) -> Iterable[Move]:
    for line in lines:
        dir_letter, distance = line.strip().split()
        yield Direction.from_letter(dir_letter), int(distance)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    moves = moves_from_file(input_path)
    result_1 = part_1(moves)
    result_2 = part_2(moves)
    return result_1, result_2


if __name__ == '__main__':
    main()
