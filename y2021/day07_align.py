"""
Advent of Code 2021
Day 7: The Treachery of Whales
https://adventofcode.com/2021/day/7
"""

from typing import Callable

from common.iteration import minmax
from meta.aoc_tools import data_path


def part_1(positions: list[int]) -> int:
    """
    ...

    You quickly make a list of **the horizontal position of each crab** (your puzzle input). Crab
    submarines have limited fuel, so you need to find a way to make all of their horizontal
    positions match while requiring them to spend as little fuel as possible.

    For example, consider the following horizontal positions:

        >>> crabs = [16, 1, 2, 0, 4, 2, 7, 1, 2, 14]

    This means there's a crab with horizontal position `16`, a crab with horizontal position `1`,
    and so on.

    Each change of `1` step in horizontal position of a single crab costs `1` fuel. You could choose
    any horizontal position to align them all on, but the one that costs the least fuel is
    horizontal position `2`:

      - Move from `16` to `2`: `14` fuel
      - Move from  `1` to `2`:  `1` fuel
      - Move from  `2` to `2`:  `0` fuel
      - Move from  `0` to `2`:  `2` fuel
      - Move from  `4` to `2`:  `2` fuel
      - Move from  `2` to `2`:  `0` fuel
      - Move from  `7` to `2`:  `5` fuel
      - Move from  `1` to `2`:  `1` fuel
      - Move from  `2` to `2`:  `0` fuel
      - Move from `14` to `2`: `12` fuel

    This costs a total of `37` fuel.

        >>> alignment_cost(crabs, destination=2)
        37

    This is the cheapest possible outcome:

        >>> best_destination(crabs)
        2

    More expensive outcomes include:

        >>> alignment_cost(crabs, destination=1)
        41
        >>> alignment_cost(crabs, destination=3)
        39
        >>> alignment_cost(crabs, destination=10)
        71

    Determine the horizontal position that the crabs can align to using the least fuel possible.
    **How much fuel must they spend to align to that position?**

        >>> part_1(crabs)
        part 1: crabs align at position 2, which costs 37 fuel
        37
    """

    destination = best_destination(positions)
    cost = alignment_cost(positions, destination)

    print(f"part 1: crabs align at position {destination}, which costs {cost} fuel")
    return cost


def part_2(positions: list[int]) -> int:
    """
    As it turns out, crab submarine engines don't burn fuel at a constant rate. Instead, each change
    of 1 step in horizontal position costs 1 more unit of fuel than the last: the first step costs
    `1`, the second step costs `2`, the third step costs `3`, and so on.

    As each crab moves, moving further becomes more expensive. This changes the best horizontal
    position to align them all on; in the example above, this becomes `5`:

      - Move from `16` to `5`: `66` fuel
      - Move from  `1` to `5`: `10` fuel
      - Move from  `2` to `5`:  `6` fuel
      - Move from  `0` to `5`: `15` fuel
      - Move from  `4` to `5`:  `1` fuel
      - Move from  `2` to `5`:  `6` fuel
      - Move from  `7` to `5`:  `3` fuel
      - Move from  `1` to `5`: `10` fuel
      - Move from  `2` to `5`:  `6` fuel
      - Move from `14` to `5`: `45` fuel

    This costs a total of `168` fuel.

        >>> crabs = [16, 1, 2, 0, 4, 2, 7, 1, 2, 14]
        >>> alignment_cost(crabs, 5, cost_quadratic)
        168

    This is the new cheapest possible outcome:

        >>> best_destination(crabs, cost_quadratic)
        5

    The old alignment position `2` now costs `206` fuel instead:

        >>> alignment_cost(crabs, 2, cost_quadratic)
        206

    Determine the horizontal position that the crabs can align to using the least fuel possible so
    they can make you an escape route! **How much fuel must they spend to align to that position?**

        >>> part_2(crabs)
        part 2: crabs align at position 5, which costs 168 fuel
        168
    """

    destination = best_destination(positions, cost_quadratic)
    cost = alignment_cost(positions, destination, cost_quadratic)

    print(f"part 2: crabs align at position {destination}, which costs {cost} fuel")
    return cost


CostFunction = Callable[[int, int], int]


def cost_linear(pos_1: int, pos_2: int) -> int:
    # distance
    return abs(pos_1 - pos_2)


def cost_quadratic(pos_1: int, pos_2: int) -> int:
    # 1 + 2 + 3 + 4 + ... per unit of distance
    dist = abs(pos_1 - pos_2)
    return (dist * (dist + 1)) // 2


def alignment_cost(
    positions: list[int],
    destination: int,
    cost_fn: CostFunction = cost_linear,
) -> int:
    return sum(cost_fn(pos, destination) for pos in positions)


def best_destination(positions: list[int], cost_fn: CostFunction = cost_linear):
    # TODO: optimize
    # convex function -> stop after it starts to grow
    # can be likely estimated with a quadratic function (for both cost_fns?)
    # part 1 -> probably median works?
    return min(
        range(*minmax(positions)),
        key=lambda d: alignment_cost(positions, d, cost_fn)
    )


def positions_from_file(fn: str) -> list[int]:
    return [int(v) for v in next(open(fn)).strip().split(',')]


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    positions = positions_from_file(input_path)
    result_1 = part_1(positions)
    result_2 = part_2(positions)
    return result_1, result_2


if __name__ == '__main__':
    main()
