"""
Advent of Code 2015
Day 24: It Hangs in the Balance
https://adventofcode.com/2015/day/24
"""

import math
from itertools import islice
from typing import Iterable
from typing import Iterator

from tabulate import tabulate
from tqdm import tqdm

from common.iteration import following
from common.iteration import mink
from common.file import relative_path


def part_1(weights: list[int]) -> int:
    """
    It's Christmas Eve, and Santa is loading up the sleigh for this year's deliveries. However,
    there's one small problem: he can't get the sleigh to balance. If it isn't balanced, he can't
    defy physics, and nobody gets presents this year.

    No pressure.

    Santa has provided you a list of the weights of every package he needs to fit on the sleigh.
    The packages need to be split into **three groups of exactly the same weight**, and every
    package has to fit. The first group goes in the passenger compartment of the sleigh, and
    the second and third go in containers on either side. Only when all three groups weigh exactly
    the same amount will the sleigh be able to fly. Defying physics has rules, you know!

    Of course, that's not the only problem. The first group - the one going in the passenger
    compartment - needs as few packages as possible so that Santa has some legroom left over. It
    doesn't matter how many packages are in either of the other two groups, so long as all of the
    groups weigh the same.

    Furthermore, Santa tells you, if there are multiple ways to arrange the packages such that
    the fewest possible are in the first group, you need to choose the way where the first group has
    **the smallest quantum entanglement** to reduce the chance of any "complications". The quantum
    entanglement of a group of packages is the product of their weights, that is, the value you get
    when you multiply their weights together. Only consider quantum entanglement if the first group
    has the fewest possible number of packages in it and all groups weigh the same amount.

    For example, suppose you have ten packages with weights 1 through 5 and 7 through 11.

        >>> example_weights = [11, 10, 9, 8, 7, 5, 4, 3, 2, 1]

    For this situation, some of the unique first groups, their quantum entanglements, and a way to
    divide the remaining packages are as follows:

        >>> example_configs = unique_configs(example_weights, 3)
        >>> example_configs[0]
        ((11, 9), (10, 8, 2), (7, 5, 4, 3, 1))
        >>> print_configs(example_configs)  # doctest: +ELLIPSIS
        | Group 1    |   QE | Group 2   | Group 3    |
        |------------|------|-----------|------------|
        | 11 9       |   99 | 10 8 2    | 7 5 4 3 1  |
        ...
        | 10 9 1     |   90 | 11 7 2    | 8 5 4 3    |
        | 10 8 2     |  160 | 11 9      | 7 5 4 3 1  |
        | 10 7 3     |  210 | 11 9      | 8 5 4 2 1  |
        | 10 7 2 1   |  140 | 11 9      | 8 5 4 3    |
        | 10 5 4 1   |  200 | 11 9      | 8 7 3 2    |
        | 10 5 3 2   |  300 | 11 9      | 8 7 4 1    |
        | 10 4 3 2 1 |  240 | 11 9      | 8 7 5      |
        | 9 8 3      |  216 | 11 7 2    | 10 5 4 1   |
        | 9 8 2 1    |  144 | 11 5 4    | 10 7 3     |
        | 9 7 4      |  252 | 11 8 1    | 10 5 3 2   |
        | 9 7 3 1    |  189 | 11 5 4    | 10 8 2     |
        | 9 5 4 2    |  360 | 11 8 1    | 10 7 3     |
        | 8 7 5      |  280 | 11 9      | 10 4 3 2 1 |
        ...
        | 8 5 4 3    |  480 | 11 9      | 10 7 2 1   |
        | 8 5 4 2 1  |  320 | 11 9      | 10 7 3     |
        | 7 5 4 3 1  |  420 | 11 9      | 10 8 2     |

    Of these, although `10 9 1` has the smallest quantum entanglement (`90`), the configuration with
    only two packages, `11 9`, in the passenger compartment gives Santa the most legroom and wins.
    In this situation, the quantum entanglement for the ideal configuration is therefore `99`. Had
    there been two configurations with only two packages in the first group, the one with
    the smaller quantum entanglement would be chosen.

    What is the **quantum entanglement** of the first group of packages in the ideal configuration?

        >>> part_1(example_weights)
        part 1: ideal configuration has QE=99 (`11 9`, `10 8 2`, `7 5 4 3 1`)
        99
    """
    config, quantum_entanglement = ideal_configuration(weights, 3)
    config_str = ", ".join("`" + " ".join(str(w) for w in ws) + "`" for ws in config)
    print(f"part 1: ideal configuration has QE={quantum_entanglement} ({config_str})")
    return quantum_entanglement


def part_2(weights: list[int]) -> int:
    """
    That's weird... the sleigh still isn't balancing.

    "Ho ho ho", Santa muses to himself. "I forgot the trunk".

    Balance the sleigh again, but this time, separate the packages into **four groups** instead of
    three. The other constraints still apply.

    Given the example packages above, this would be some of the new unique first groups, their
    quantum entanglements, and one way to divide the remaining packages:

        >>> example_weights = weights_from_file('data/24-example.txt')
        >>> print_configs(unique_configs(example_weights, 4))
        | Group 1   |   QE | Group 2   | Group 3   | Group 4   |
        |-----------|------|-----------|-----------|-----------|
        | 11 4      |   44 | 10 5      | 8 7       | 9 3 2 1   |
        | 11 3 1    |   33 | 10 5      | 8 7       | 9 4 2     |
        | 10 5      |   50 | 11 4      | 8 7       | 9 3 2 1   |
        | 10 3 2    |   60 | 11 4      | 8 7       | 9 5 1     |
        | 9 5 1     |   45 | 11 4      | 8 7       | 10 3 2    |
        | 9 4 2     |   72 | 10 5      | 8 7       | 11 3 1    |
        | 9 3 2 1   |   54 | 11 4      | 10 5      | 8 7       |
        | 8 7       |   56 | 11 4      | 10 5      | 9 3 2 1   |

    Of these, there are three arrangements that put the minimum (two) number of packages in the
    first group: `11 4`, `10 5`, and `8 7`. Of these, `11 4` has the lowest quantum entanglement,
    and so it is selected.

    Now, what is the **quantum entanglement** of the first group of packages in the ideal
    configuration?

        >>> part_2(example_weights)
        part 2: ideal configuration has QE=44 (`11 4`, `10 5`, `8 7`, `9 3 2 1`)
        44
    """

    config, quantum_entanglement = ideal_configuration(weights, 4)
    config_str = ", ".join("`" + " ".join(str(w) for w in ws) + "`" for ws in config)
    print(f"part 2: ideal configuration has QE={quantum_entanglement} ({config_str})")
    return quantum_entanglement


Config = tuple[tuple[int, ...], ...]


def unique_configs(all_weights: list[int], containers_count: int) -> list[Config]:
    configs = generate_configs(all_weights, containers_count)
    return sorted(configs, reverse=True)


def generate_configs(all_weights: list[int], containers_count: int) -> Iterator[Config]:
    assert containers_count >= 2

    total_weights = sum(all_weights)
    assert total_weights % containers_count == 0
    container_weight = total_weights // containers_count

    rem_containers_count = containers_count - 1
    for this_weights in subsqs(all_weights, container_weight):
        rem_weights = sorted(set(all_weights) - set(this_weights), reverse=True)
        if rem_containers_count > 1:
            yield from (
                (this_weights,) + subconfig
                for subconfig in islice(generate_configs(rem_weights, rem_containers_count), 1)
            )
        else:
            yield this_weights, tuple(rem_weights)


def subsqs(values: list[int], tsum: int) -> Iterable[tuple[int, ...]]:
    return (
        ss
        for length in range(1, len(values) + 1)
        for ss in subsqs_of_length(values, tsum, length)
    )


def subsqs_of_length(values: list[int], tsum: int, length: int) -> Iterable[tuple[int, ...]]:
    assert tsum >= 0
    assert length >= 0

    if tsum == 0 and length == 0:
        return [()]  # one empty tuple
    if tsum == 0 or length == 0:
        return []  # nothing

    return (
        (value,) + ss
        for value, others in following(values)
        if value <= tsum
        for ss in subsqs_of_length(others, tsum - value, length - 1)
    )


def print_configs(configs: Iterable[Config]):
    def ws_str(weights: tuple[int, ...]) -> str:
        return " ".join(str(w) for w in weights)

    headers = ["Group 1", "QE"] + [f"Group {g}" for g in (2, 3, 4)]
    rows = (
        (ws_str(config[0]), math.prod(config[0])) + tuple(ws_str(c) for c in config[1:])
        for config in configs
    )
    print(tabulate(rows, headers=headers, tablefmt='github'))


def ideal_configuration(weights: list[int], containers_count: int) -> tuple[Config, int]:
    weights = sorted(weights, reverse=True)

    def generate_configs_with_shortest_c1():
        prev_config = None
        for config in generate_configs(weights, containers_count):
            # pylint: disable=unsubscriptable-object
            if prev_config and len(prev_config[0]) < len(config[0]):
                return
            yield config
            prev_config = config

    best_config, quantum_entanglement = mink(
        tqdm(generate_configs_with_shortest_c1(), delay=1.0, unit=" configs"),
        key=lambda c: math.prod(c[0])
    )
    return best_config, quantum_entanglement


def weights_from_file(fn: str) -> list[int]:
    return sorted((int(line) for line in open(relative_path(__file__, fn))), reverse=True)


if __name__ == '__main__':
    weights_ = weights_from_file('data/24-input.txt')
    part_1(weights_)
    part_2(weights_)
