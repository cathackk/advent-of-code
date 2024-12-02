"""
Advent of Code 2020
Day 10: Adapter Array
https://adventofcode.com/2020/day/10
"""

from collections import Counter
from collections import defaultdict

from common.iteration import diffs
from meta.aoc_tools import data_path


def part_1(adapters: list[int]) -> int:
    """
    The charging outlet near your seat produces the wrong number of *jolts*. Always prepared, you
    make a list of all of the joltage adapters in your bag.

    Each of your joltage adapters is rated for a specific *output joltage* (your puzzle input). Any
    given adapter can take an input 1, 2, or 3 jolts *lower* than its rating and still produce its
    rated output joltage.

    In addition, your device has a built-in joltage adapter rated for 3 jolts higher than the
    highest-rated adapter in your bag. (If your adapter list were 3, 9, and 6, your device's
    built-in adapter would be rated for 12 jolts.)

    Treat the charging outlet near your seat as having an effective joltage rating of 0.

    If you *use every adapter* in your bag at once, what is the distribution of joltage differences
    between the charging outlet, the adapters, and your device?

    For example, suppose that in your bag, you have adapters with the following joltage ratings:

        >>> adapters_1 = [16, 10, 15, 5, 1, 11, 7, 19, 6, 12, 4]

    With these adapters, your device's built-in joltage adapter would be rated for
    19 + 3 = 22 jolts, 3 higher than the highest-rated adapter.

        >>> max(adapters_1) + 3
        22

    Because adapters can only connect to a source 1-3 jolts lower than its rating, in order to use
    every adapter, you'd need to choose them in ascending order of their joltage rating:

        >>> sorted(adapters_1)
        [1, 4, 5, 6, 7, 10, 11, 12, 15, 16, 19]

    In this example, when using every adapter, there are *7* differences of 1 jolt
    and *5* differences of 3 jolts:

        >>> incs = increases(adapters_1)
        >>> incs
        [1, 3, 1, 1, 1, 3, 1, 1, 3, 1, 3, 3]
        >>> Counter(incs)
        Counter({1: 7, 3: 5})

    Here is a larger example:

        >>> adapters_2 = [28, 33, 18, 42, 31, 14, 46, 20, 48, 47, 24, 23, 49, 45, 19, 38,
        ...               39, 11, 1, 32, 25, 35, 8, 17, 7, 9, 4, 2, 34, 10, 3]

    In this larger example, in a chain that uses all of the adapters, there are *22* differences of
    1 jolt and *10* differences of 3 jolts.

        >>> Counter(increases(adapters_2))
        Counter({1: 22, 3: 10})

    Find a chain that uses all of your adapters to connect the charging outlet to your device's
    built-in adapter and count the joltage differences between the charging outlet, the adapters,
    and your device. *What is the number of 1-jolt differences multiplied by the number of 3-jolt
    differences?

        >>> part_1(adapters_2)
        part 1: there are 22 and 10 diffs (1- and 3-jolt) -> result is 220
        220
    """

    incs = increases(adapters)

    incs_counts = Counter(incs)
    assert set(incs_counts.keys()) == {1, 3}
    incs_1 = incs_counts[1]
    incs_3 = incs_counts[3]
    result = incs_1 * incs_3

    print(f"part 1: there are {incs_1} and {incs_3} diffs (1- and 3-jolt) -> result is {result}")
    return result


def part_2(adapters: list[int]) -> int:
    """
    To completely determine whether you have enough adapters, you'll need to figure out how many
    different ways they can be arranged. Every arrangement needs to connect the charging outlet to
    your device. The previous rules about when adapters can successfully connect still apply.

    The first example above supports the following arrangements:

        (0), 1, 4, 5, 6, 7, 10, 11, 12, 15, 16, 19, (22)
        (0), 1, 4, 5, 6, 7, 10, 12, 15, 16, 19, (22)
        (0), 1, 4, 5, 7, 10, 11, 12, 15, 16, 19, (22)
        (0), 1, 4, 5, 7, 10, 12, 15, 16, 19, (22)
        (0), 1, 4, 6, 7, 10, 11, 12, 15, 16, 19, (22)
        (0), 1, 4, 6, 7, 10, 12, 15, 16, 19, (22)
        (0), 1, 4, 7, 10, 11, 12, 15, 16, 19, (22)
        (0), 1, 4, 7, 10, 12, 15, 16, 19, (22)

    (The charging outlet and your device's built-in adapter are shown in parentheses.) Given the
    adapters from the first example, the total number of arrangements that connect the charging
    outlet to your device is *8*.

        >>> arrangements_count([16, 10, 15, 5, 1, 11, 7, 19, 6, 12, 4])
        8

    The second example above has many arrangements. In total, this set of adapters can connect the
    charging outlet to your device in *19208* distinct arrangements.

        >>> adapters_2 = [28, 33, 18, 42, 31, 14, 46, 20, 48, 47, 24, 23, 49, 45, 19, 38,
        ...               39, 11, 1, 32, 25, 35, 8, 17, 7, 9, 4, 2, 34, 10, 3]
        >>> arrangements_count(adapters_2)
        19208

    You glance back down at your bag and try to remember why you brought so many adapters; there
    must be *more than a trillion* valid ways to arrange them! Surely, there must be an efficient
    way to count the arrangements. *What is the total number of distinct ways you can arrange the
    adapters to connect the charging outlet to your device?*

        >>> part_2(adapters_2)
        part 2: there are 19208 distinct valid arrangements
        19208
    """

    result = arrangements_count(adapters)

    print(f"part 2: there are {result} distinct valid arrangements")
    return result


def increases(adapters: list[int]) -> list[int]:
    return list(diffs([0] + sorted(adapters))) + [3]


def arrangements_count(adapters: list[int]) -> int:
    adapter_joltage = max(adapters) + 3
    joltages = [0] + sorted(adapters) + [adapter_joltage]
    # how many paths lead to this joltage?
    paths_to = defaultdict(int, {0: 1})

    for joltage in joltages:
        for step in (1, 2, 3):
            paths_to[joltage + step] += paths_to[joltage]

    return paths_to[adapter_joltage]


def load_data(fn: str) -> list[int]:
    return [
        int(line_stripped)
        for line in open(fn)
        if (line_stripped := line.strip())
    ]


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    adapters = load_data(input_path)
    result_1 = part_1(adapters)
    result_2 = part_2(adapters)
    return result_1, result_2


if __name__ == '__main__':
    main()
