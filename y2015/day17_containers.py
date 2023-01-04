"""
Advent of Code 2015
Day 17: No Such Thing as Too Much
https://adventofcode.com/2015/day/17
"""

from typing import Iterable

from common.iteration import following
from common.iteration import min_all
from meta.aoc_tools import data_path


def part_1(containers: list[int], amount: int = 150) -> int:
    """
    The elves bought too much eggnog again - `150` liters this time. To fit it all into your
    refrigerator, you'll need to move it into smaller containers. You take an inventory of the
    capacities of the available containers.

    For example, suppose you have containers of size `20`, `15`, `10`, `5`, and `5` liters:

        >>> example_containers = [20, 15, 10, 5, 5]

    If you need to store `25` liters, there are four ways to do it:

        >>> list(generate_fillings(25, example_containers))
        [[20, 5], [20, 5], [15, 10], [15, 5, 5]]

    Filling all containers entirely, how many different **combinations of containers** can exactly
    fit all 150 liters of eggnog?

        >>> part_1(example_containers, amount=25)
        part 1: there are 4 combinations to contain 25 liters of eggnog
        4
    """

    combs_count = sum(1 for _ in generate_fillings(amount, containers))
    print(f"part 1: there are {combs_count} combinations to contain {amount} liters of eggnog")
    return combs_count


def part_2(containers: list[int], amount: int = 150) -> int:
    """
    While playing with all the containers in the kitchen, another load of eggnog arrives!
    The shipping and receiving department is requesting as many containers as you can spare.

    Find the minimum number of containers that can exactly fit all `150` liters of eggnog.
    **How many different ways** can you fill that number of containers and still hold exactly 150
    litres?

    In the example above, the minimum number of containers was two. There were three ways to use
    that many containers, and so the answer there would be `3`.

        >>> part_2([20, 15, 10, 5, 5], amount=25)
        part 2: there are 3 combinations of length 2 to contain 25 liters of eggnog
        3
    """
    min_fillings = min_all(generate_fillings(amount, containers), key=len)
    min_length = len(min_fillings[0])
    min_combs_count = len(min_fillings)
    print(
        f"part 2: there are {min_combs_count} combinations of length {min_length} "
        f"to contain {amount} liters of eggnog"
    )
    return min_combs_count


def generate_fillings(amount: int, containers: Iterable[int]) -> Iterable[list[int]]:
    if amount == 0:
        yield []
        return

    for container, rest_containers in following(containers):
        if container <= amount:
            rest_amount = amount - container
            yield from (
                [container] + subfilling
                for subfilling in generate_fillings(rest_amount, rest_containers)
            )


def containers_from_file(fn: str) -> list[int]:
    return [int(line.strip()) for line in open(fn)]


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    containers = containers_from_file(input_path)
    result_1 = part_1(containers)
    result_2 = part_2(containers)
    return result_1, result_2


if __name__ == '__main__':
    main()
