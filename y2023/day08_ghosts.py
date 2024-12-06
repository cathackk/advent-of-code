"""
Advent of Code 2023
Day 8: Haunted Wasteland
https://adventofcode.com/2023/day/8
"""

from itertools import cycle as cycle_it
from typing import Iterable, Iterator

from common.file import relative_path
from common.iteration import ilen
from common.maths import lcm
from common.text import parse_line


def part_1(steps: 'Steps', network: 'Network', target: 'Node' = 'ZZZ') -> int:
    """
    You're still riding a camel across Desert Island when you spot a sandstorm quickly approaching.
    When you turn to warn the Elf, she disappears before your eyes! To be fair, she had just
    finished warning you about **ghosts** a few minutes ago.

    One of the camel's pouches is labeled "maps" - sure enough, it's full of documents (your puzzle
    input) about how to navigate the desert. At least, you're pretty sure that's what they are; one
    of the documents contains a list of left/right instructions, and the rest of the documents seem
    to describe some kind of **network** of labeled nodes.

    It seems like you're meant to use the **left/right** instructions to **navigate the network**.
    Perhaps if you have the camel follow the same instructions, you can escape the haunted
    wasteland!

    After examining the maps for a bit, two nodes stick out: `AAA` and `ZZZ`. You feel like `AAA` is
    where you are now, and you have to follow the left/right instructions until you reach `ZZZ`.

    This format defines each node of the network individually. For example:

        >>> steps_1, network_1 = input_from_text('''
        ...     RL
        ...
        ...     AAA = (BBB, CCC)
        ...     BBB = (DDD, EEE)
        ...     CCC = (ZZZ, GGG)
        ...     DDD = (DDD, DDD)
        ...     EEE = (EEE, EEE)
        ...     GGG = (GGG, GGG)
        ...     ZZZ = (ZZZ, ZZZ)
        ... ''')
        >>> steps_1
        [1, 0]
        >>> network_1  # doctest: +NORMALIZE_WHITESPACE
        {'AAA': ('BBB', 'CCC'), 'BBB': ('DDD', 'EEE'), 'CCC': ('ZZZ', 'GGG'), 'DDD': ('DDD', 'DDD'),
         'EEE': ('EEE', 'EEE'), 'GGG': ('GGG', 'GGG'), 'ZZZ': ('ZZZ', 'ZZZ')}

    Starting with `AAA`, you need to **look up the next element** based on the next left/right
    instruction in your input. In this example, start with `AAA` and go **right** (`R`) by choosing
    the right element of `AAA`, **`CCC`**:

        >>> network_1['AAA'][1]
        'CCC'

    Then, `L` means to choose the **left** element of `CCC`, **`ZZZ`**:

        >>> network_1['CCC'][0]
        'ZZZ'

    By following the left/right instructions, you reach `ZZZ` in **`2`** steps:

        >>> list(follow(steps_1, network_1, start='AAA', target='ZZZ'))
        ['CCC', 'ZZZ']

    Of course, you might not find `ZZZ` right away. If you run out of left/right instructions,
    repeat the whole sequence of instructions as necessary: `RL` really means `RLRLRLRLRLRLRLRL...`
    and so on. For example, here is a situation that takes **`6`** steps to reach `ZZZ`:

        >>> input_2 = input_from_text('''
        ...     LLR
        ...
        ...     AAA = (BBB, BBB)
        ...     BBB = (AAA, ZZZ)
        ...     ZZZ = (ZZZ, ZZZ)
        ... ''')
        >>> input_2
        ([0, 0, 1], {'AAA': ('BBB', 'BBB'), 'BBB': ('AAA', 'ZZZ'), 'ZZZ': ('ZZZ', 'ZZZ')})
        >>> list(follow(*input_2))
        ['BBB', 'AAA', 'BBB', 'AAA', 'BBB', 'ZZZ']
        >>> len(_)
        6

    Starting at `AAA`, follow the left/right instructions.
    **How many steps are required to reach `ZZZ`?**

        >>> part_1(*input_2)
        part 1: it takes 6 steps to reach ZZZ
        6
    """

    result = ilen(follow(steps, network, target=target))

    print(f"part 1: it takes {result} steps to reach {target}")
    return result


def part_2(steps: 'Steps', network: 'Network') -> int:
    """
    The sandstorm is upon you, and you aren't any closer to escaping the wasteland. You had the
    camel follow the instructions, but you've barely left your starting position. It's going to take
    **significantly more steps** to escape!

    What if the map isn't for people - what if the map is for **ghosts**? Are ghosts even bound by
    the laws of spacetime? Only one way to find out.

    After examining the maps a bit longer, your attention is drawn to a curious fact: the number of
    nodes with names ending in `A` is equal to the number ending in `Z`! If you were a ghost, you'd
    probably just **start at every node that ends with A** and follow all of the paths at the same
    time until they all simultaneously end up at nodes that end with `Z`.

    For example:

        >>> steps_1, network_1 = input_from_text('''
        ...     LR
        ...
        ...     11A = (11B, XXX)
        ...     11B = (XXX, 11Z)
        ...     11Z = (11B, XXX)
        ...     22A = (22B, XXX)
        ...     22B = (22C, 22C)
        ...     22C = (22Z, 22Z)
        ...     22Z = (22B, 22B)
        ...     XXX = (XXX, XXX)
        ... ''')

    Here, there are two starting nodes, `11A` and `22A` (because they both end with `A`):

        >>> list(ghosts_starting_nodes(network_1))
        ['11A', '22A']

    As you follow each left/right instruction, use that instruction to **simultaneously** navigate
    away from both nodes you're currently on. Repeat this process until **all** of the nodes you're
    currently on end with `Z`. (If only some of the nodes you're on end with `Z`, they act like any
    other node, and you continue as normal.) In this example, you would proceed as follows:

        >>> list(ghosts_follow(steps_1, network_1))  # doctest: +NORMALIZE_WHITESPACE
        [('11B', '22B'), ('11Z', '22C'), ('11B', '22Z'),
         ('11Z', '22B'), ('11B', '22C'), ('11Z', '22Z')]

    So, in this example, you end up entirely on nodes that end in `Z` after **`6`** steps.

        >>> len(_)
        6

    Simultaneously start on every node that ends with `A`.
    **How many steps does it take before you're only on nodes that end with `Z`?**

        >>> part_2(steps_1, network_1)
        part 2: it takes 6 steps for all 2 ghosts to reach target nodes
        6
    """

    ghosts_count = ilen(ghosts_starting_nodes(network))
    if ghosts_count > 2:
        result = ghosts_follow_optimized(steps, network)
    else:
        result = ilen(ghosts_follow(steps, network))

    print(f"part 2: it takes {result} steps for all {ghosts_count} ghosts to reach target nodes")
    return result


Steps = list[int]
Node = str
Network = dict[Node, tuple[Node, Node]]


def follow(
    steps: Steps,
    network: Network,
    start: Node = 'AAA',
    target: Node | None = 'ZZZ',
) -> Iterator[Node]:
    node = start
    steps_it = cycle_it(steps)

    while node != target:
        node = network[node][next(steps_it)]
        yield node


def ghosts_follow(steps: Steps, network: Network) -> Iterator[tuple[Node, ...]]:
    nodes = tuple(ghosts_starting_nodes(network))
    steps_it = cycle_it(steps)

    while not all(is_ghost_target(node) for node in nodes):
        step = next(steps_it)
        nodes = tuple(network[node][step] for node in nodes)
        yield nodes


def ghosts_follow_optimized(steps: Steps, network: Network) -> int:

    # for the following algorithm to work, the steps need not be reducible,
    # i.e. it can't be possible to split it into shorter version with the same cyclic result
    assert not is_reducible(steps)

    def detect_cycle_length(start: Node) -> int:
        # detects cycle within the ghosts path returns its length
        # NOTE: this asserts two assumptions about the data:
        #       1. there is only **one** target within the cycle
        #       2. cycle length and the number of steps to reach the target is the same

        # state is tuple of (index of last taken step within the step cycle, current node)
        states = zip(cycle_it(range(len(steps))), follow(steps, network, start, target=None))
        # we'll traverse the states and detect first state repeat using state set
        visited_states: set[tuple[int, Node]] = {(len(steps) - 1, start)}
        # also keep track of the path traversed
        path: list[tuple[int, Node]] = list(visited_states)

        # traverse states ...
        for state in states:
            if state not in visited_states:
                # no repeat found yet ...
                visited_states.add(state)
                path.append(state)
            else:
                # repeat detected!
                steps_to_enter_cycle = path.index(state)
                cycle_length = len(path) - steps_to_enter_cycle
                # check assumption 1: there is only one target within the cycle
                target_state, = (st for st in path[steps_to_enter_cycle:] if is_ghost_target(st[1]))
                # check assumption 2: cycle length and # of steps to reach target is the same
                assert path.index(target_state) == cycle_length
                return cycle_length

        # TODO: remove when mypy realizes this is unreachable
        assert False

    # thanks to the assumptions, all ghosts reach their targets within the cycles at once
    # within LCM(cycle lengths) steps
    return lcm(*(detect_cycle_length(node) for node in ghosts_starting_nodes(network)))


def ghosts_starting_nodes(network: Network) -> Iterable[Node]:
    return (node for node in network if is_ghost_start(node))


def is_ghost_start(node: Node) -> bool:
    return node.endswith('A')


def is_ghost_target(node: Node) -> bool:
    return node.endswith('Z')


def is_reducible(values: list[int]) -> bool:
    """
    Can the list be split into N equal sublists?

        >>> is_reducible([1, 2, 3, 1, 2, 3])
        True
        >>> is_reducible([1, 2, 3, 1, 2, 4])
        False
        >>> is_reducible([1, 2, 1, 2, 1, 2])
        True
        >>> is_reducible([1, 1])
        True
        >>> is_reducible([1, 2])
        False
        >>> is_reducible([1, 2, 1])
        False
    """
    n = len(values)
    return any(
        len({tuple(values[k:k+p]) for k in range(0, n, p)}) == 1
        for p in range(1, n // 2 + 1)
        if n % p == 0
    )


def input_from_file(fn: str) -> tuple[Steps, Network]:
    return input_from_lines(open(relative_path(__file__, fn)))


def input_from_text(text: str) -> tuple[Steps, Network]:
    return input_from_lines(text.strip().splitlines())


def input_from_lines(lines: Iterable[str]) -> tuple[Steps, Network]:
    lines_it = iter(lines)

    # steps
    # -> 'LLLRRR'
    steps_line = next(lines_it)
    steps = [{'L': 0, 'R': 1}[step_char] for step_char in steps_line.strip()]

    # empty line separator
    assert not next(lines_it).strip()

    # network
    # -> 'AAA = (BBB, CCC)'
    def parse_instruction(line: str) -> tuple[Node, tuple[Node, Node]]:
        origin, left, right = parse_line(line, '$ = ($, $)')
        return origin, (left, right)

    network = dict(parse_instruction(line.strip()) for line in lines_it)

    return steps, network


def main(input_fn: str = 'data/08-input.txt') -> tuple[int, int]:
    steps, network = input_from_file(input_fn)
    result_1 = part_1(steps, network)
    result_2 = part_2(steps, network)
    return result_1, result_2


if __name__ == '__main__':
    main()
