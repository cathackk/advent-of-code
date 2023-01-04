"""
Advent of Code 2018
Day 8: Memory Maneuver
https://adventofcode.com/2018/day/8
"""

from collections import Counter
from itertools import islice
from typing import Iterable
from typing import Iterator

from meta.aoc_tools import data_path


def part_1(root_node: 'Node') -> int:
    """
    The sleigh is much easier to pull than you'd expect for something its weight. Unfortunately,
    neither you nor the Elves know which way the North Pole is from here.

    You check your wrist device for anything that might help. It seems to have some kind of
    navigation system! Activating the navigation system produces more bad news: "Failed to start
    navigation system. Could not read software license file."

    The navigation system's license file consists of a list of numbers (your puzzle input). The
    numbers define a data structure which, when processed, produces some kind of tree that can be
    used to calculate the license number.

    The **tree** is made up of **nodes**; a single, outermost node forms the tree's root, and it
    contains all other nodes in the tree (or contains nodes that contain nodes, and so on).

    Specifically, a node consists of:

      - A **header**, which is always exactly two numbers:
        - The quantity of child nodes.
        - The quantity of metadata entries.
      - Zero or more **child nodes** (as specified in the header).
      - One or more **metadata entries** (as specified in the header).

        >>> example_data = [2, 3, 0, 3, 10, 11, 12, 1, 1, 0, 1, 99, 2, 1, 1, 2]
        >>> example_node = Node.from_data(example_data)
        >>> example_node
        Node(children=[Node(md=[10, 11, 12]), Node(children=[Node(md=[99])], md=[2])], md=[1, 1, 2])
        >>> list(example_node.data()) == example_data
        True

    Each child node is itself a node that has its own header, child nodes, and metadata.
    For example:

        2 3 0 3 10 11 12 1 1 0 1 99 2 1 1 2
        A----------------------------------
            B----------- C-----------
                             D-----

    In this example, each node of the tree is also marked with an underline starting with a letter
    for easier identification. In it, there are four nodes:

      - `A`, which has `2` child nodes (`B`, `C`) and `3` metadata entries (`1`, `1`, `2`).
      - `B`, which has `0` child nodes and `3` metadata entries (`10`, `11`, `12`).
      - `C`, which has `1` child node (`D`) and `1` metadata entry (`2`).
      - `D`, which has `0` child nodes and `1` metadata entry (`99`).

    The first check done on the license file is to simply add up all of the metadata entries.
    In this example, that sum is `1+1+2+10+11+12+2+99=138`.

        >>> example_node.metadata_sum()
        138

    **What is the sum of all metadata entries?**

        >>> part_1(example_node)
        part 1: metadata sum is 138
        138
    """

    result = root_node.metadata_sum()
    print(f"part 1: metadata sum is {result}")
    return result


def part_2(root_node: 'Node') -> int:
    """
    The second check is slightly more complicated: you need to find the value of the root node
    (`A` in the example above).

        >>> node_a = Node.from_file(data_path(__file__, 'example.txt'))
        >>> node_b, node_c = node_a.children
        >>> node_d, = node_c.children

    The **value of a node** depends on whether it has child nodes.

    If a node has **no child nodes**, its value is the sum of its metadata entries. So, the value of
    node `B` is `10+11+12=33`, and the value of node `D` is `99`.

        >>> node_b.value()
        33
        >>> node_d.value()
        99

    However, if a node **does have child nodes**, the metadata entries become indexes which refer to
    those child nodes. A metadata entry of `1` refers to the first child node, `2` to the second,
    `3` to the third, and so on. The value of this node is the sum of the values of the child nodes
    referenced by the metadata entries. If a referenced child node does not exist, that reference is
    skipped. A child node can be referenced multiple time and counts each time it is referenced.
    A metadata entry of `0` does not refer to any child node.

    For example, again using the above nodes:

      - Node `C` has one metadata entry, `2`. Because node `C` has only one child node, `2`
        references a child node which does not exist, and so the value of node `C` is `0`.

        >>> node_c.value()
        0

      - Node `A` has three metadata entries: `1`, `1`, and `2`. The `1` references node `A`'s first
        child node, `B`, and the `2` references node `A`'s second child node, `C`. Because node `B`
        has a value of `33` and node `C` has a value of `0`, the value of node `A` is `33+33+0=66`.

        >>> node_a.value()
        66

    So, in this example, the value of the root node is `66`.

    **What is the value of the root node?**

        >>> part_2(node_a)
        part 2: value of the root node is 66
        66
    """

    result = root_node.value()
    print(f"part 2: value of the root node is {result}")
    return result


class Node:
    def __init__(self, children: Iterable['Node'] = (), metadata: Iterable[int] = ()):
        self.children = list(children)
        self.metadata = list(metadata)

    def __repr__(self) -> str:
        def parts() -> Iterable[str]:
            if self.children:
                yield f'children={self.children!r}'
            if self.metadata:
                yield f'md={self.metadata}'

        return f'{type(self).__name__}({", ".join(parts())})'

    def metadata_sum(self) -> int:
        return sum(self.metadata) + sum(child.metadata_sum() for child in self.children)

    def value(self) -> int:
        if not self.children:
            return self.metadata_sum()

        index_range = range(len(self.children))
        ch_counts = Counter(index for val in self.metadata if (index := val - 1) in index_range)
        return sum(self.children[index].value() * count for index, count in ch_counts.items())

    @classmethod
    def from_file(cls, fn: str) -> 'Node':
        return cls.from_str(open(fn).readline())

    @classmethod
    def from_str(cls, line: str) -> 'Node':
        return cls.from_data(int(v) for v in line.split())

    @classmethod
    def from_data(cls, data: Iterable[int]) -> 'Node':
        data_iter = iter(data)
        children_count = next(data_iter)
        metadata_count = next(data_iter)
        children = [Node.from_data(data_iter) for _ in range(children_count)]
        metadata = list(islice(data_iter, metadata_count))
        return cls(children, metadata)

    def data(self) -> Iterator[int]:
        yield len(self.children)
        yield len(self.metadata)
        yield from (val for child in self.children for val in child.data())
        yield from self.metadata


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    root_node = Node.from_file(input_path)
    result_1 = part_1(root_node)
    result_2 = part_2(root_node)
    return result_1, result_2


if __name__ == '__main__':
    main()
