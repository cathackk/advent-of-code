"""
Advent of Code 2015
Day 9: All in a Single Night
https://adventofcode.com/2015/day/9
"""

from itertools import permutations
from typing import Iterable

from common.text import parse_line
from common.file import relative_path
from common.iteration import zip1


Distances = dict[tuple[str, str], int]


def part_1(distances: Distances) -> int:
    """
    Every year, Santa manages to deliver all of his presents in a single night.

    This year, however, he has some new locations to visit; his elves have provided him the
    distances between every pair of locations. He can start and end at any two (different) locations
    he wants, but he must visit each location exactly once. What is the shortest distance he can
    travel to achieve this?

    For example, given the following distances:

        >>> example_distances = distances_from_text('''
        ...     London to Dublin = 464
        ...     London to Belfast = 518
        ...     Dublin to Belfast = 141
        ... ''')

    The possible routes are therefore:

        >>> print_routes(generate_routes(example_distances))
        Belfast -> Dublin -> London = 605
        Belfast -> London -> Dublin = 982
        Dublin -> Belfast -> London = 659
        Dublin -> London -> Belfast = 982
        London -> Belfast -> Dublin = 659
        London -> Dublin -> Belfast = 605

    The shortest of these is `London -> Dublin -> Belfast = 605`, and so the answer is `605` in this
    example.

    **What is the distance of the shortest route?**

        >>> part_1(example_distances)
        part 1: shortest route has distance 605
        605
    """

    result, _ = min(generate_routes(distances))
    print(f"part 1: shortest route has distance {result}")
    return result


def part_2(distances: Distances) -> int:
    """
    The next year, just to show off, Santa decides to take the route with the **longest distance**
    instead.

    He can still start and end at any two (different) locations he wants, and he still must visit
    each location exactly once.

    For example, given the distances above, the longest route would be 982 via (for example)
    `Dublin -> London -> Belfast`.


        >>> part_2(distances_from_file('data/09-example.txt'))
        part 2: longest route has distance 982
        982
    """

    result, _ = max(generate_routes(distances))
    print(f"part 2: longest route has distance {result}")
    return result


Road = tuple[tuple[str, str], int]
Route = tuple[int, Iterable[str]]


def generate_routes(distances: Distances) -> Iterable[Route]:
    places = sorted(set(p for ps in distances.keys() for p in ps))
    return (
        (sum(distances[ps] for ps in zip1(route_places)), route_places)
        for route_places in permutations(places)
    )


def print_routes(routes: Iterable[Route]) -> None:
    for length, places in routes:
        print(f"{' -> '.join(places)} = {length}")


def distances_from_text(text: str) -> Distances:
    return dict(roads_from_lines(text.strip().splitlines()))


def distances_from_file(fn: str) -> Distances:
    return dict(roads_from_lines(open(relative_path(__file__, fn))))


def roads_from_lines(lines: Iterable[str]) -> Iterable[Road]:
    # "London to Dublin = 464"
    for line in lines:
        place_1, place_2, distance_str = parse_line(line.strip(), "$ to $ = $")
        distance = int(distance_str)
        yield (place_1, place_2), distance
        yield (place_2, place_1), distance


if __name__ == '__main__':
    distances_ = distances_from_file('data/09-input.txt')
    part_1(distances_)
    part_2(distances_)
