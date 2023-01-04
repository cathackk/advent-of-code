"""
Advent of Code 2015
Day 3: Perfectly Spherical Houses in a Vacuum
https://adventofcode.com/2015/day/3
"""

from typing import Iterable

from meta.aoc_tools import data_path


def part_1(moves: str) -> int:
    """
    Santa is delivering presents to an infinite two-dimensional grid of houses.

    He begins by delivering a present to the house at his starting location, and then an elf at the
    North Pole calls him via radio and tells him where to move next. Moves are always exactly one
    house to the north (`^`), south (`v`), east (`>`), or west (`<`). After each move, he delivers
    another present to the house at his new location.

    However, the elf back at the north pole has had a little too much eggnog, and so his directions
    are a little off, and Santa ends up visiting some houses more than once.

    For example:

      - `>` delivers presents to `2` houses: one at the starting location, and one to the east:

        >>> presents_count('>')
        2

      - `^>v<` delivers presents to `4` houses in a square, including twice to the house at his
        starting/ending location:

        >>> presents_count('^>v<')
        4

      - `^v^v^v^v^v` delivers a bunch of presents to some very lucky children at only `2` houses:

        >>> presents_count('^v^v^v^v^v')
        2

    How many houses receive **at least one present**?

        >>> part_1('^>v<')
        part 1: Santa delivers to 4 houses
        4
    """

    result = presents_count(moves)
    print(f"part 1: Santa delivers to {result} houses")
    return result


def part_2(moves: str) -> int:
    """
    The next year, to speed up the process, Santa creates a robot version of himself,
    **Robo-Santa**, to deliver presents with him.

    Santa and Robo-Santa start at the same location (delivering two presents to the same starting
    house), then take turns moving based on instructions from the elf, who is eggnoggedly reading
    from the same script as the previous year.

    For example:

      - `^v` delivers presents to `3` houses, because Santa goes north, and then Robo-Santa goes
        south:

        >>> presents_count('^v', robo_santa=True)
        3

      - `^>v<` now delivers presents to `3` houses, and Santa and Robo-Santa end up back where they
        started:

        >>> presents_count('^>v<', robo_santa=True)
        3

      - `^v^v^v^v^v` now delivers presents to `11` houses, with Santa going one direction and
        Robo-Santa going the other:

        >>> presents_count('^v^v^v^v^v', robo_santa=True)
        11

    This year, how many houses receive **at least one present**?

        >>> part_2('^>v<')
        part 2: Santa and Robo-Santa deliver to 3 houses
        3
    """

    result = presents_count(moves, robo_santa=True)
    print(f"part 2: Santa and Robo-Santa deliver to {result} houses")
    return result


Pos = tuple[int, int]


MOVES = {
    '^': (0, -1),
    '>': (+1, 0),
    'v': (0, +1),
    '<': (-1, 0)
}


def trail(moves: str, start: Pos = (0, 0)) -> Iterable[Pos]:
    yield start
    x, y = start
    for move in moves:
        dx, dy = MOVES[move]
        x, y = x + dx, y + dy
        yield x, y


def presents_count(moves: str, robo_santa: bool = False) -> int:
    if not robo_santa:
        return len(set(trail(moves)))
    else:
        santas_houses = set(trail(moves[0::2]))
        robosantas_houses = set(trail(moves[1::2]))
        return len(santas_houses | robosantas_houses)


def moves_from_file(fn: str) -> str:
    return open(fn).readline().strip()


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    moves = moves_from_file(input_path)
    result_1 = part_1(moves)
    result_2 = part_2(moves)
    return result_1, result_2


if __name__ == '__main__':
    main()
