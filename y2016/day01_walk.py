from typing import Iterable
from typing import Union

from heading import Heading
from utils import last


def turn(direction: str, heading: Heading):
    if direction == 'R':
        return heading.right()
    elif direction == 'L':
        return heading.left()
    else:
        raise ValueError(direction)


Instr = tuple[str, int]
Pos = tuple[int, int]


def parse_instrs(s: str) -> Iterable[Instr]:
    for part in s.split(','):
        part = part.strip()
        yield part[0], int(part[1:])


def walk(
        instrs: Union[str, Iterable[Instr]],
        start: Pos = (0, 0),
        heading: Heading = Heading.NORTH
) -> Iterable[Pos]:
    if isinstance(instrs, str):
        instrs = parse_instrs(instrs)
    pos = start
    yield pos
    for direction, distance in instrs:
        heading = turn(direction, heading)
        for _ in range(distance):
            pos = heading.move(pos)
            yield pos


def distance_from_origin(pos: Pos) -> int:
    x, y = pos
    return abs(x) + abs(y)


def test_walk():
    assert last(walk('R2, L3')) == (2, -3)
    assert last(walk('R2, R2, R2')) == (0, 2)
    assert last(walk('R5, L5, R5, R3')) == (10, -2)


def test_distance():
    assert distance_from_origin((2, -3)) == 5
    assert distance_from_origin((0, 2)) == 2
    assert distance_from_origin((10, -2)) == 12


def part_1(instrs: Iterable[Instr]) -> int:
    pos = last(walk(instrs))
    distance = distance_from_origin(pos)
    print(f"part 1: ended up {distance} away at {pos}")
    return distance


def part_2(instrs: Iterable[Instr]) -> int:
    visited = set()
    for pos in walk(instrs):
        if pos not in visited:
            visited.add(pos)
        else:
            distance = distance_from_origin(pos)
            print(f"part 2: ended up {distance} away at {pos}")
            return distance


if __name__ == '__main__':
    instructions = list(parse_instrs(open("data/01-input.txt").readline().strip()))
    part_1(instructions)
    # 307 too high
    part_2(instructions)
