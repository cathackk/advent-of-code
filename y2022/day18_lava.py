"""
Advent of Code 2022
Day 18: Boiling Boulders
https://adventofcode.com/2022/day/18
"""

from typing import Iterable

from common.rect import HyperCuboid
from meta.aoc_tools import data_path


def part_1(cubes: Iterable['Pos3']) -> int:
    """
    You and the elephants finally reach fresh air. You've emerged near the base of a large volcano
    that seems to be actively erupting! Fortunately, the lava seems to be flowing away from you and
    toward the ocean.

    Bits of lava are still being ejected toward you, so you're sheltering in the cavern exit
    a little longer. Outside the cave, you can see the lava landing in a pond and hear it loudly
    hissing as it solidifies.

    Depending on the specific compounds in the lava and speed at which it cools, it might be forming
    obsidian! The cooling rate should be based on the surface area of the lava droplets, so you take
    a quick scan of a droplet as it flies past you (your puzzle input).

    Because of how quickly the lava is moving, the scan isn't very good; its resolution is quite low
    and, as a result, it approximates the shape of the lava droplet with **1x1x1 cubes on a 3D
    grid**, each given as its `x,y,z` position.

    To approximate the surface area, count the number of sides of each cube that are not immediately
    connected to another cube. So, if your scan were only two adjacent cubes like `1,1,1` and
    `2,1,1`, each cube would have a single side covered and five sides exposed, a total surface area
    of **10** sides.

        >>> surface_area([(1, 1, 1), (2, 1, 1)])
        10

    Here's a larger example:

        >>> cs = cubes_from_text('''
        ...     2,2,2
        ...     1,2,2
        ...     3,2,2
        ...     2,1,2
        ...     2,3,2
        ...     2,2,1
        ...     2,2,3
        ...     2,2,4
        ...     2,2,6
        ...     1,2,5
        ...     3,2,5
        ...     2,1,5
        ...     2,3,5
        ... ''')
        >>> cs  # doctest: +ELLIPSIS
        [(2, 2, 2), (1, 2, 2), (3, 2, 2), (2, 1, 2), (2, 3, 2), (2, 2, 1), (2, 2, 3), ...]
        >>> len(cs)
        13

    In the above example, after counting up all the sides that aren't connected to another cube,
    the total surface area is **64**.

        >>> surface_area(cs)
        64

    **What is the surface area of your scanned lava droplet?**

        >>> part_1(cs)
        part 1: surface area is 64
        64
    """

    result = surface_area(cubes)

    print(f"part 1: surface area is {result}")
    return result


def part_2(cubes: Iterable['Pos3']) -> int:
    """
    Something seems off about your calculation. The cooling rate depends on exterior surface area,
    but your calculation also included the surface area of air pockets trapped in the lava droplet.

    Instead, consider only cube sides that could be reached by the water and steam as the lava
    droplet tumbles into the pond. The steam will expand to reach as much as possible, completely
    displacing any air on the outside of the lava droplet but never expanding diagonally.

    In the larger example above, exactly one cube of air is trapped within the lava droplet
    (at `2,2,5`), so the exterior surface area of the lava droplet is **58**.

        >>> cs = cubes_from_file(data_path(__file__, 'example.txt'))
        >>> exterior_surface_area(cs)
        58

    What is the exterior surface area of your scanned lava droplet?

        >>> part_2(cs)
        part 2: exterior surface area is 58
        58
    """

    result = exterior_surface_area(cubes)

    print(f"part 2: exterior surface area is {result}")
    return result


Pos3 = tuple[int, int, int]


def neighbors(pos: Pos3) -> Iterable[Pos3]:
    """ Returns the six adjacent 3D positions to the given one. """

    x, y, z = pos

    yield x - 1, y, z
    yield x + 1, y, z
    yield x, y - 1, z
    yield x, y + 1, z
    yield x, y, z - 1
    yield x, y, z + 1


def surface_area(cubes: Iterable[Pos3]) -> int:
    cubes = set(cubes)
    return sum(
        1
        for cube in cubes
        for neighbor in neighbors(cube)
        if neighbor not in cubes
    )


def exterior_surface_area(cubes: Iterable[Pos3]) -> int:
    """
    Concept:
      - create cuboid encompassing all cubes,
      - expand it by 1 in all six directions,
      - starting in a corner of the cuboid, flood all non-cubes
      - count all neighboring cube faces encountered during the flooding
    """

    cubes = set(cubes)

    # cuboid encompassing all cubes, expanded by 1 in all six directions
    bounds = HyperCuboid.with_all(cubes).grow_by(+1)
    assert len(bounds.shape) == 3

    # surface counter
    total_surface = 0

    # flooding algorithm
    to_visit: list[Pos3] = [bounds.corner_min]  # type: ignore
    visited: set[Pos3] = set()
    while to_visit:
        air = to_visit.pop()
        if air in visited:
            continue
        visited.add(air)

        for neighbor in neighbors(air):
            if neighbor not in bounds:
                continue
            if neighbor in cubes:
                # air neighbors a solid cube = external cube face -> add to total surface
                total_surface += 1
            elif neighbor not in visited:
                # air neighbors unvisited air -> check it later
                to_visit.append(neighbor)

    return total_surface


def cubes_from_file(fn: str) -> list[Pos3]:
    return list(cubes_from_lines(open(fn)))


def cubes_from_text(text: str) -> list[Pos3]:
    return list(cubes_from_lines(text.strip().splitlines()))


def cubes_from_lines(lines: Iterable[str]) -> Iterable[Pos3]:
    for line in lines:
        x, y, z = line.strip().split(',')
        yield int(x), int(y), int(z)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    cubes = cubes_from_file(input_path)
    result_1 = part_1(cubes)
    result_2 = part_2(cubes)
    return result_1, result_2


if __name__ == '__main__':
    main()
