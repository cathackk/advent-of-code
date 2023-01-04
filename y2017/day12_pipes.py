"""
Advent of Code 2017
Day 12: Digital Plumber
https://adventofcode.com/2017/day/12
"""

from typing import Iterable

from common.containers import IdentitySet
from common.text import parse_line
from meta.aoc_tools import data_path


def part_1(links: Iterable['Link']) -> int:
    """
    Walking along the memory banks of the stream, you find a small village that is experiencing
    a little confusion: some programs can't communicate with each other.

    Programs in this village communicate using a fixed system of **pipes**. Messages are passed
    between programs using these pipes, but most programs aren't connected to each other directly.
    Instead, programs pass messages between each other until the message reaches the intended
    recipient.

    For some reason, though, some of these messages aren't ever reaching their intended recipient,
    and the programs suspect that some pipes are missing. They would like you to investigate.

    You walk through the village and record the ID of each program and the IDs with which it can
    communicate directly (your puzzle input). Each program has one or more programs with which it
    can communicate, and these pipes are bidirectional; if `8` says it can communicate with `11`,
    then `11` will say it can communicate with `8`.

    You need to figure out how many programs are in the group that contains program ID `0`.

    For example, suppose you go door-to-door like a travelling salesman and record the following
    list:

        >>> example_links = links_from_text('''
        ...     0 <-> 2
        ...     1 <-> 1
        ...     2 <-> 0, 3, 4
        ...     3 <-> 2, 4
        ...     4 <-> 2, 3, 6
        ...     5 <-> 6
        ...     6 <-> 4, 5
        ... ''')
        >>> example_links
        [(0, [2]), (1, [1]), (2, [0, 3, 4]), (3, [2, 4]), (4, [2, 3, 6]), (5, [6]), (6, [4, 5])]

    In this example, the following programs are in the group that contains program ID `0`:

      - Program `0` by definition.
      - Program `2`, directly connected to program `0`.
      - Program `3` via program `2`.
      - Program `4` via program `2`.
      - Program `5` via programs `6`, then `4`, then `2`.
      - Program `6` via programs `4`, then `2`.

    Therefore, a total of `6` programs are in this group; all but program `1`, which has a pipe that
    connects it to itself:

        >>> sorted(create_groups_dict(example_links)[0])
        [0, 2, 3, 4, 5, 6]

    **How many programs** are in the group that contains program ID 0?

        >>> part_1(example_links)
        part 1: the group that contains program ID 0 has total 6 programs in it
        6
    """
    group_0 = create_groups_dict(links)[0]
    assert 0 in group_0
    result = len(group_0)

    print(f"part 1: the group that contains program ID 0 has total {result} programs in it")
    return result


def part_2(links: Iterable['Link']) -> int:
    """
    There are more programs than just the ones in the group containing program ID `0`. The rest of
    them have no way of reaching that group, and still might have no way of reaching each other.

    A **group** is a collection of programs that can all communicate via pipes either directly or
    indirectly. The programs you identified just a moment ago are all part of the same group. Now,
    they would like you to determine the total number of groups.

    In the example above, there were `2` groups: one consisting of programs `0,2,3,4,5,6`, and the
    other consisting solely of program `1`.

        >>> example_links = links_from_file('data/12-example.txt')
        >>> create_groups(example_links)
        [[0, 2, 3, 4, 5, 6], [1]]

    **How many groups are there** in total?

        >>> part_2(example_links)
        part 2: there are 2 groups in total
        2
    """

    result = len(create_groups(links))
    print(f"part 2: there are {result} groups in total")
    return result


Link = tuple[int, list[int]]
Group = set[int]
SortedGroup = list[int]


def create_groups(links: Iterable[Link]) -> list[SortedGroup]:
    # dict of program id -> its group
    # each group is present N times in the dict, where N is its length
    groups_dict = create_groups_dict(links)

    # return only unique objects from the dict's values
    return sorted(sorted(group) for group in IdentitySet(groups_dict.values()))


def create_groups_dict(links: Iterable[Link]) -> dict[int, Group]:
    groups: dict[int, Group] = {}

    for source, targets in links:
        for target in targets:
            group_source, group_target = groups.get(source), groups.get(target)

            if group_source and group_target:
                # both source and target are in an existing group
                if group_source is not group_target:
                    # ... and they are not the same item -> join the two groups
                    group_source.update(group_target)
                    groups.update((t, group_source) for t in group_target)

            elif group_source and not group_target:
                # only source is in an existing group
                # -> add target to it
                group_source.add(target)
                groups[target] = group_source

            elif not group_source and group_target:
                # only target is in an existing group
                # add source to it
                group_target.add(source)
                groups[source] = group_target

            else:
                # neither source nor target are in a group
                # -> create a new group with both in it
                group = {source, target}
                groups[source] = group
                groups[target] = group

    return groups


def links_from_text(text: str) -> list[Link]:
    return list(links_from_lines(text.strip().splitlines()))


def links_from_file(fn: str) -> list[Link]:
    return list(links_from_lines(open(fn)))


def links_from_lines(lines: Iterable[str]) -> Iterable[Link]:
    for line in lines:
        # 1977 <-> 197, 879, 1237
        source, targets = parse_line(line.strip(), "$ <-> $")
        yield int(source), [int(v) for v in targets.split(", ")]


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    links = links_from_file(input_path)
    result_1 = part_1(links)
    result_2 = part_2(links)
    return result_1, result_2


if __name__ == '__main__':
    main()
