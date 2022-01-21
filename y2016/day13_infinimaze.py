"""
Advent of Code 2016
Day 13: A Maze of Twisty Little Cubicles
https://adventofcode.com/2016/day/13
"""

from typing import Iterable

from common.file import relative_path
from common.graph import shortest_path
from common.rect import Rect


def part_1(seed: int, start: 'Pos' = (1, 1), end: 'Pos' = (31, 39)) -> int:
    """
    You arrive at the first floor of this new building to discover a much less welcoming environment
    than the shiny atrium of the last one. Instead, you are in a maze of twisty little cubicles, all
    alike.

    Every location in this area is addressed by a pair of non-negative integers (`x,y`). Each such
    coordinate is either a wall or an open space. You can't move diagonally. The cube maze starts at
    `0,0` and seems to extend infinitely toward **positive** `x` and `y`; negative values are
    invalid, as they represent a location outside the building. You are in a small waiting area at
    `1,1`.

    While it seems chaotic, a nearby morale-boosting poster explains, the layout is actually quite
    logical. You can determine whether a given `x,y` coordinate will be a wall or an open space
    using a simple system:

      - Find `x*x + 3*x + 2*x*y + y + y*y`.
      - Add the office designer's favorite number (your puzzle input).
      - Find the binary representation of that sum; count the **number** of bits that are `1`.
        - If the number of bits that are `1` is **even**, it's an **open space**.
        - If the number of bits that are `1` is **odd**, it's a **wall**.

    For example, if the office designer's favorite number were `10`, drawing walls as `#` and open
    spaces as `·`, the corner of the building containing `0,0` would look like this:

        >>> shown = Rect.at_origin(10, 7)
        >>> draw_map(seed=10, region=shown)
          0123456789
        0 ·#·####·##
        1 ··#··#···#
        2 #····##···
        3 ###·#·###·
        4 ·##··#··#·
        5 ··##····#·
        6 #···##·###

    Now, suppose you wanted to reach `7,4`. The shortest route you could take is marked as `O`:

        >>> distance, path = find_path(seed=10, start=(1, 1), end=(7, 4))
        >>> draw_map(seed=10, region=shown, highlighted=path)
          0123456789
        0 ·#·####·##
        1 ·O#··#···#
        2 #OOO·##···
        3 ###O#·###·
        4 ·##OO#OO#·
        5 ··##OOO·#·
        6 #···##·###

    Thus, reaching `7,4` would take a minimum of `11` steps (starting from your current location,
    `1,1`).

        >>> distance
        11

    What is the **fewest number of steps required{{ for you to reach `31,39`?

        >>> part_1(seed=10, end=(7, 4))
        part 1: distance from (1, 1) to (7, 4) is 11
        11
    """

    dist, _ = find_path(seed, start, end)
    print(f"part 1: distance from {start} to {end} is {dist}")
    return dist


def part_2(seed: int, start: 'Pos' = (1, 1), max_distance: int = 50) -> int:
    """
    **How many locations** (distinct `x,y` coordinates, including your starting location) can you
    reach in at most `50` steps?

        >>> flooded = flood(seed=10, start=(1, 1), max_distance=9)
        >>> draw_map(seed=10, region=Rect.at_origin(10, 7), highlighted=flooded)
          0123456789
        0 O#·####·##
        1 OO#OO#···#
        2 #OOOO##···
        3 ###O#·###·
        4 ·##OO#··#·
        5 ··##OOO·#·
        6 #···##·###

        >>> part_2(seed=10, max_distance=9)
        part 2: in 9 steps you can reach 15 locations
        15
    """

    result = len(flood(seed, start, max_distance))
    print(f"part 2: in {max_distance} steps you can reach {result} locations")
    return result


Pos = tuple[int, int]


def is_wall(seed: int, pos: Pos):
    x, y = pos

    if x < 0 or y < 0:
        return True

    n = x * (x+3) + y * (2*x+y+1) + seed
    return sum(int(d) for d in bin(n)[2:]) % 2 == 1


def draw_map(
    seed: int,
    region: Rect,
    *,
    highlighted: Iterable[Pos] = (),
    char_space='·',
    char_wall='#',
    char_highlighted='O'
) -> None:

    highlighted = set(highlighted)

    def char(pos: Pos) -> str:
        if pos in highlighted:
            return char_highlighted
        elif is_wall(seed, pos):
            return char_wall
        else:
            return char_space

    assert region.width <= 10
    assert region.height <= 10

    x_coor = "".join(str(x)[-1] for x in region.range_x())
    print(f"  {x_coor}")

    for y in region.range_y():
        row = ''.join(char((x, y)) for x in region.range_x())
        print(f'{y} {row}')


def neighbors(pos: Pos) -> Iterable[Pos]:
    x, y = pos
    yield x + 1, y
    yield x - 1, y
    yield x, y + 1
    yield x, y - 1


def open_neighbors(pos: Pos, seed: int) -> Iterable[Pos]:
    return (npos for npos in neighbors(pos) if not is_wall(seed, npos))


def find_path(seed: int, start: Pos, end: Pos) -> tuple[int, list[Pos]]:
    assert not is_wall(seed, start), "cannot start in wall!"
    assert not is_wall(seed, end), "cannot end in wall!"
    distance, path = shortest_path(
        start=start,
        target=end,
        edges=lambda pos: ((n, n, 1) for n in open_neighbors(pos, seed))
    )
    return distance, [start] + path


def flood(seed: int, start: Pos, max_distance: int) -> set[Pos]:
    visited: set[Pos] = set()
    to_visit: set[Pos] = {start}

    for _ in range(max_distance+1):
        visited.update(to_visit)
        to_visit = {
            npos
            for pos in to_visit
            for npos in open_neighbors(pos, seed)
            if npos not in visited
        }

    return visited


def seed_from_file(fn: str) -> int:
    return int(open(relative_path(__file__, fn)).readline().strip())


if __name__ == '__main__':
    seed_ = seed_from_file('data/13-input.txt')
    part_1(seed_)
    part_2(seed_)
