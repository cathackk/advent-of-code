"""
Advent of Code 2019
Day 3: Crossed Wires
https://adventofcode.com/2019/day/3
"""

from typing import Iterable

from common.heading import Heading
from common.iteration import mink
from common.rect import Rect
from meta.aoc_tools import data_path


def part_1(wire_1: 'Wire', wire_2: 'Wire') -> int:
    """
    The gravity assist was successful, and you're well on your way to the Venus refuelling station.
    During the rush back on Earth, the fuel management system wasn't completely installed, so that's
    next on the priority list.

    Opening the front panel reveals a jumble of wires. Specifically, **two wires** are connected to
    a central port and extend outward on a grid. You trace the path each wire takes as it leaves the
    central port, one wire per line of text (your puzzle input).

    The wires twist and turn, but the two wires occasionally cross paths. To fix the circuit, you
    need to **find the intersection point closest to the central port**. Because the wires are on
    a grid, use the Manhattan distance for this measurement. While the wires do technically cross
    right at the central port where they both start, this point does not count, nor does a wire
    count as crossing with itself.

    For example, if the first wire's path is `R8,U5,L5,D3`, then starting from the central port
    (`o`), it goes right `8`, up `5`, left `5`, and finally down `3`:

        >>> (example_wire_1a := wire_from_line('R8,U5,L5,D3'))
        [(Heading.EAST, 8), (Heading.NORTH, 5), (Heading.WEST, 5), (Heading.SOUTH, 3)]
        >>> draw_wires(example_wire_1a, bounds=Rect((-1, -8), (9, 1)))
        ···········
        ···········
        ···········
        ····+----+·
        ····|····|·
        ····|····|·
        ····|····|·
        ·········|·
        ·o-------+·
        ···········

    Then, if the second wire's path is `U7,R6,D4,L4`, it goes up `7`, right `6`, down `4`,
    and left `4`:

        >>> (example_wire_1b := wire_from_line('U7,R6,D4,L4'))
        [(Heading.NORTH, 7), (Heading.EAST, 6), (Heading.SOUTH, 4), (Heading.WEST, 4)]
        >>> draw_wires(example_wire_1a, example_wire_1b)
        ···········
        ·+-----+···
        ·|·····|···
        ·|··+--X-+·
        ·|··|··|·|·
        ·|·-X--+·|·
        ·|··|····|·
        ·|·······|·
        ·o-------+·
        ···········

    These wires cross at two locations (marked `X`), but the lower-left one is closer to the central
    port: its distance is `3 + 3 = 6`.

        >>> sorted(intersections(example_wire_1a, example_wire_1b))
        [(3, -3), (6, -5)]
        >>> closest_intersection(example_wire_1a, example_wire_1b)
        ((3, -3), 6)

    Here are a few more examples:

        >>> closest_intersection(
        ...     wire_from_line('R75,D30,R83,U83,L12,D49,R71,U7,L72'),
        ...     wire_from_line('U62,R66,U55,R34,D71,R55,D58,R83')
        ... )
        ((155, -4), 159)

        >>> closest_intersection(
        ...     wire_from_line('R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51'),
        ...     wire_from_line('U98,R91,D20,R16,D67,R40,U7,R15,U6,R7')
        ... )
        ((124, -11), 135)

    **What is the Manhattan distance** from the central port to the closest intersection?

        >>> part_1(example_wire_1a, example_wire_1b)
        part 1: closest intersection (by manhattan distance) is at (3, -3), distance=6
        6
    """

    pos, result = closest_intersection(wire_1, wire_2)

    print(f"part 1: closest intersection (by manhattan distance) is at {pos}, distance={result}")
    return result


def part_2(wire_1: 'Wire', wire_2: 'Wire') -> int:
    """
    It turns out that this circuit is very timing-sensitive; you actually need to **minimize the
    signal delay**.

    To do this, calculate the **number of steps** each wire takes to reach each intersection; choose
    the intersection where the **sum of both wires' steps** is lowest. If a wire visits a position
    on the grid multiple times, use the steps value from the **first** time it visits that position
    when calculating the total value of a specific intersection.

    The number of steps a wire takes is the total number of grid squares the wire has entered to get
    to that location, including the intersection being considered. Again consider the example from
    above:

        >>> example_wires = wires_from_file('data/03-example.txt')
        >>> draw_wires(*example_wires)
        ···········
        ·+-----+···
        ·|·····|···
        ·|··+--X-+·
        ·|··|··|·|·
        ·|·-X--+·|·
        ·|··|····|·
        ·|·······|·
        ·o-------+·
        ···········

    In the above example, the intersection closest to the central port is reached after `8+5+5+2
    = 20` steps by the first wire and `7+6+4+3 = 20` steps by the second wire for a total of
    `20+20 = 40` steps.

        >>> x1, x2 = sorted(timed_intersections(*example_wires).items())
        >>> x1
        ((3, -3), 40)

    However, the top-right intersection is better: the first wire takes only `8+5+2 = 15` and the
    second wire takes only `7+6+2 = 15`, a total of `15+15 = 30` steps.

        >>> x2
        ((6, -5), 30)

    Here are the best steps for the extra examples from above:

        >>> closest_timed_intersection(
        ...     wire_from_line('R75,D30,R83,U83,L12,D49,R71,U7,L72'),
        ...     wire_from_line('U62,R66,U55,R34,D71,R55,D58,R83')
        ... )
        ((158, 12), 610)
        >>> closest_timed_intersection(
        ...     wire_from_line('R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51'),
        ...     wire_from_line('U98,R91,D20,R16,D67,R40,U7,R15,U6,R7')
        ... )
        ((107, -47), 410)

    **What is the fewest combined steps the wires must take to reach an intersection?**

        >>> part_2(*example_wires)
        part 2: closest intersection (by num of steps) is at (6, -5), steps=30
        30
    """

    pos, result = closest_timed_intersection(wire_1, wire_2)

    print(f"part 2: closest intersection (by num of steps) is at {pos}, steps={result}")
    return result


Pos = tuple[int, int]
Move = tuple[Heading, int]
Wire = list[Move]


def draw_wires(
    wire_1: Wire,
    wire_2: Wire = None,
    bounds: Rect = None,
    origin: Pos = (0, 0),
) -> None:
    canvas: dict[Pos, str] = {origin: 'o'}
    heading_chars = {
        Heading.NORTH: '|',
        Heading.SOUTH: '|',
        Heading.WEST: '-',
        Heading.EAST: '-',
    }

    def draw_wire(wire: Wire) -> None:
        prev_pos, prev_heading = None, None
        for pos, heading in follow(wire, origin):
            if prev_heading and prev_heading != heading:
                assert prev_pos
                assert canvas[prev_pos] in ('|', '-')
                canvas[prev_pos] = '+'  # curve

            if pos not in canvas:
                canvas[pos] = heading_chars[heading]
            else:
                assert canvas[pos] == heading_chars[heading.right()]
                canvas[pos] = 'X'

            prev_pos, prev_heading = pos, heading

    draw_wire(wire_1)
    draw_wire(wire_2 or [])

    if not bounds:
        bounds = Rect.with_all(canvas).grow_by(1, 1)

    for y in bounds.range_y():
        print(''.join(canvas.get((x, y), '·') for x in bounds.range_x()))


def follow(wire: Wire, origin: Pos = (0, 0)) -> Iterable[tuple[Pos, Heading]]:
    pos = origin
    for heading, distance in wire:
        for _ in range(distance):
            pos = heading.move(pos)
            yield pos, heading


def intersections(wire_1: Wire, wire_2: Wire) -> set[Pos]:
    positions_1 = {pos for pos, _ in follow(wire_1)}
    positions_2 = {pos for pos, _ in follow(wire_2)}
    return positions_1 & positions_2


def closest_intersection(wire_1: Wire, wire_2: Wire) -> tuple[Pos, int]:
    return mink(intersections(wire_1, wire_2), key=manhattan_distance_from_origin)


def timed_intersections(wire_1: Wire, wire_2: Wire) -> dict[Pos, int]:
    def pos_time_dict(wire: Wire) -> dict[Pos, int]:
        return {pos: t for t, (pos, _) in enumerate(follow(wire), start=1)}

    pos_times_1 = pos_time_dict(wire_1)
    pos_times_2 = pos_time_dict(wire_2)
    intersects = pos_times_1.keys() & pos_times_2.keys()
    return {pos: pos_times_1[pos] + pos_times_2[pos] for pos in intersects}


def closest_timed_intersection(wire_1: Wire, wire_2: Wire) -> tuple[Pos, int]:
    timed_xs = timed_intersections(wire_1, wire_2)
    return mink(timed_xs, key=timed_xs.get)


def manhattan_distance_from_origin(pos: Pos) -> int:
    x, y = pos
    return abs(x) + abs(y)


def wires_from_file(fn: str) -> list[Wire]:
    return [wire_from_line(line) for line in open(fn)]


def wire_from_line(line: str) -> Wire:
    headings = {
        'U': Heading.NORTH,
        'D': Heading.SOUTH,
        'L': Heading.WEST,
        'R': Heading.EAST,
    }
    return [(headings[p[0]], int(p[1:])) for p in line.strip().split(',')]


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    wires = wires_from_file(input_path)
    result_1 = part_1(*wires)
    result_2 = part_2(*wires)
    return result_1, result_2


if __name__ == '__main__':
    main()
