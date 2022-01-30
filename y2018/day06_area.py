"""
Advent of Code 2018
Day 6: Chronal Coordinates
https://adventofcode.com/2018/day/6
"""

import string
from typing import Iterable

from common.file import relative_path
from common.iteration import dgroupby_pairs_set
from common.iteration import single_value
from common.rect import Pos
from common.rect import Rect


def part_1(coordinates: Iterable[Pos]) -> int:
    """
    The device on your wrist beeps several times, and once again you feel like you're falling.

    "Situation critical," the device announces. "Destination indeterminate. Chronal interference
    detected. Please specify new target coordinates."

    The device then produces a list of coordinates (your puzzle input). Are they places it thinks
    are safe or dangerous? It recommends you check manual page 729. The Elves did not give you
    a manual.

    **If they're dangerous**, maybe you can minimize the danger by finding the coordinate that gives
    the largest distance from the other points.

    Using only the Manhattan distance, determine the **area** around each coordinate by counting
    the number of integer X,Y locations that are **closest** to that coordinate (and aren't **tied
    in distance** to any other coordinate).

    Your goal is to find the size of the **largest area** that isn't infinite. For example, consider
    the following list of coordinates:

        >>> example_coordinates = coordinates_from_text('''
        ...     1, 1
        ...     1, 6
        ...     8, 3
        ...     3, 4
        ...     5, 5
        ...     8, 9
        ... ''')
        >>> example_coordinates
        [(1, 1), (1, 6), (8, 3), (3, 4), (5, 5), (8, 9)]

    If we name these coordinates `A` through `F`, we can draw them on a grid, putting `0,0` at the
    top left:

        >>> draw_coordinates(example_coordinates)
        ··········
        ·A········
        ··········
        ········C·
        ···D······
        ·····E····
        ·B········
        ··········
        ··········
        ········F·

    This view is partial - the actual grid extends infinitely in all directions. Using the Manhattan
    distance, each location's closest coordinate can be determined, shown here in lowercase:

        >>> draw_coordinates(example_coordinates, including_areas=True)
        aaaaa·cccc
        aAaaa·cccc
        aaaddecccc
        aadddeccCc
        ··dDdeeccc
        bb·deEeecc
        bBb·eeee··
        bbb·eeefff
        bbb·eeffff
        bbb·ffffFf

    Locations shown as `·` are equally far from two or more coordinates, and so they don't count as
    being closest to any.

    In this example, the areas of coordinates A, B, C, and F are infinite - while not shown here
    their areas extend forever outside the visible grid. However, the areas of coordinates D and E
    are finite: D is closest to 9 locations, and E is closest to 17 (both including the coordinate's
    location itself).

        >>> area_sizes(example_coordinates)
        {(3, 4): 9, (5, 5): 17}

    Therefore, in this example, the size of the largest area is **`17`**.

    **What is the size of the largest area** that isn't infinite?

        >>> part_1(example_coordinates)
        part 1: largest finite area has size 17
        17
    """
    result = max(area_sizes(coordinates).values())
    print(f"part 1: largest finite area has size {result}")
    return result


def part_2(coordinates: Iterable[Pos], distance_limit: int = 10_000) -> int:
    """
    On the other hand, **if the coordinates are safe**, maybe the best you can do is try to find
    a **region** near as many coordinates as possible.

    For example, suppose you want the sum of the Manhattan distance to all of the coordinates to be
    **less than 32**. For each location, add up the distances to all of the given coordinates; if
    the total of those distances is less than 32, that location is within the desired region. Using
    the same coordinates as above, the resulting region looks like this:

        >>> example_coordinates = coordinates_from_file('data/06-example.txt')
        >>> draw_coordinates(example_coordinates, distance_limit=32)
        ··········
        ·A········
        ··········
        ···###··C·
        ··#D###···
        ··###E#···
        ·B·###····
        ··········
        ··········
        ········F·

    In particular, consider the highlighted location `4,3` located at the top middle of the region.
    Its calculation is as follows:

        >>> [manhattan_distance(coor, (4, 3)) for coor in example_coordinates]
        [5, 6, 4, 2, 3, 10]
        >>> sum(_)
        30

    Because the total distance to all coordinates (`30`) is less than `32`, the location is
    **within** the region.

    This region, which also includes coordinates D and E, has a total size of **16**.

    Your actual region will need to be much larger than this example, though, instead including all
    locations with a total distance of less than **10_000**.

    **What is the size of the region containing all locations which have a total distance to all
    given coordinates of less than 10_000?**

        >>> part_2(example_coordinates, distance_limit=32)
        part 2: region closer than 32 to every point has size 16
        16
    """

    result = safe_region_size(coordinates, distance_limit)
    print(f"part 2: region closer than {distance_limit} to every point has size {result}")
    return result


def area_sizes(coordinates: Iterable[Pos]) -> dict[Pos, int]:
    finite_areas = claim_areas(coordinates, include_infinite=False)
    return {pos: len(area) for pos, area in finite_areas.items()}


def claim_areas(coordinates: Iterable[Pos], include_infinite: bool = False) -> dict[Pos, set[Pos]]:
    def neighbors(pos: Pos) -> Iterable[Pos]:
        x, y = pos
        yield x + 1, y
        yield x - 1, y
        yield x, y + 1
        yield x, y - 1

    positions = sorted(coordinates)
    # determine boundaries
    bounds = Rect.with_all(positions).grow_by(+3, +3)
    # position -> claimed by which original coordinate
    claimed_by: dict[Pos, Pos | None] = {pos: pos for pos in positions}
    new_claims: dict[Pos, set[Pos]] = {pos: {pos} for pos in positions}

    while any(len(claimants) == 1 for claimants in new_claims.values()):
        # collect all new claims
        new_claims = dgroupby_pairs_set(
            (neighbor, claimant)
            for pos, claimants in new_claims.items()
            for neighbor in neighbors(pos)
            if neighbor not in claimed_by
            if neighbor in bounds
            for claimant in claimants
        )
        # mark new claims (with single claimant) and any position with draws
        claimed_by.update({
            pos: single_value(claimants) if len(claimants) == 1 else None
            for pos, claimants in new_claims.items()
        })

    # optionally ignore all claims reaching bounds (infinite?)
    if not include_infinite:
        ignored = set(claimant for pos in bounds.border_ps() if (claimant := claimed_by[pos]))
    else:
        ignored = set()

    # return the areas: claimant -> set of their claimed positions
    return dgroupby_pairs_set(
        (claimant, pos)
        for pos, claimant in claimed_by.items()
        if claimant
        if claimant not in ignored
    )


def manhattan_distance(pos_1: Pos, pos_2: Pos):
    x_1, y_1 = pos_1
    x_2, y_2 = pos_2
    return abs(x_1 - x_2) + abs(y_1 - y_2)


def safe_region_size(points: Iterable[Pos], distance_limit: int) -> int:
    bounds = Rect.with_all(points)
    dists = {
        (x, y): sum(manhattan_distance((x, y), p) for p in points)
        for (x, y) in bounds
    }
    assert all(dists[border_pos] >= distance_limit for border_pos in bounds.border_ps())
    return sum(1 for d in dists.values() if d < distance_limit)


def draw_coordinates(
    coordinates: Iterable[Pos],
    including_areas: bool = False,
    distance_limit: int = None,
    bounds: Rect = Rect.at_origin(10, 10),
    empty_char: str = '·',
    safe_char: str = '#',
) -> None:
    coordinates_list = list(coordinates)

    # draw points
    canvas = dict(zip(coordinates_list, string.ascii_uppercase))

    if including_areas:
        # draw claims for part 1
        areas = claim_areas(coordinates_list, include_infinite=True)
        canvas.update(
            (area_pos, canvas[pos].lower())
            for pos, area in areas.items()
            for area_pos in area
            if area_pos not in canvas
        )

    elif distance_limit is not None:
        # draw safe region for part 2
        canvas.update(
            (pos, safe_char)
            for pos in bounds
            if pos not in canvas
            if sum(manhattan_distance(pos, coor) for coor in coordinates_list) < distance_limit
        )

    for y in bounds.range_y():
        print("".join(canvas.get((x, y), empty_char) for x in bounds.range_x()))


def coordinates_from_text(text: str) -> list[Pos]:
    return list(coordinates_from_lines(text.strip().splitlines()))


def coordinates_from_file(fn: str) -> list[Pos]:
    return list(coordinates_from_lines(open(relative_path(__file__, fn))))


def coordinates_from_lines(lines: Iterable[str]) -> Iterable[Pos]:
    for line in lines:
        x, y = line.strip().split(',')
        yield int(x), int(y)


if __name__ == '__main__':
    points_ = coordinates_from_file('data/06-input.txt')
    part_1(points_)
    part_2(points_)
