from typing import Iterable

from common.heading import Heading
from common.iteration import mink

Pos = tuple[int, int]
PosTime = tuple[Pos, int]
Move = tuple[Heading, int]
Wire = list[Move]


hs = {
    'U': Heading.NORTH,
    'D': Heading.SOUTH,
    'L': Heading.WEST,
    'R': Heading.EAST,
}


def load_wires(fn: str) -> Iterable[Wire]:
    return (parse_wire(line) for line in open(fn))


def parse_wire(line: str) -> Wire:
    return [(hs[p[0]], int(p[1:])) for p in line.strip().split(',')]


def follow(wire: Wire, origin: Pos = (0, 0)) -> Iterable[Pos]:
    pos = origin
    for heading, distance in wire:
        for _ in range(distance):
            pos = heading.move(pos)
            yield pos


def intersections(wire1: Wire, wire2: Wire) -> set[Pos]:
    pos1 = set(follow(wire1))
    pos2 = set(follow(wire2))
    return pos1 & pos2


def timed_intersections(wire1: Wire, wire2: Wire) -> set[PosTime]:
    t1 = {pos: t+1 for t, pos in enumerate(follow(wire1))}
    t2 = {pos: t+1 for t, pos in enumerate(follow(wire2))}
    return {(x, t1[x] + t2[x]) for x in t1.keys() & t2.keys()}


def md(pos: Pos) -> int:
    return abs(pos[0]) + abs(pos[1])


def part_1(wire1: Wire, wire2: Wire):
    closest_xs, distance = mink(intersections(wire1, wire2), key=md)
    print(f"part 1: closest xs is at {closest_xs}, distance={distance}")


def part_2(wire1: Wire, wire2: Wire):
    earliest_xs, distance = min(timed_intersections(wire1, wire2), key=lambda pt: pt[1])
    print(f"part 2: earliest xs is at {earliest_xs}, time={distance}")


if __name__ == '__main__':
    w1, w2 = load_wires("data/03-input.txt")
    part_1(w1, w2)
    part_2(w1, w2)
