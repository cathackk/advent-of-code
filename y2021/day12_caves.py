"""
Advent of Code 2021
Day 12: Passage Pathing
https://adventofcode.com/2021/day/12
"""

from typing import Iterable

from common.utils import relative_path


def part_1(caves: 'Graph') -> int:
    r"""
    With your submarine's subterranean subsystems subsisting suboptimally, the only way you're
    getting out of this cave anytime soon is by finding a path yourself. Not just **a** path -
    the only way to know if you've found the **best** path is to find **all** of them.

    Fortunately, the sensors are still mostly working, and so you build a rough map of the remaining
    caves (your puzzle input). For example:

        >>> g = Graph.from_text('''
        ...     start-A
        ...     start-b
        ...     A-c
        ...     A-b
        ...     b-d
        ...     A-end
        ...     b-end
        ... ''')
        >>> g  # doctest: +NORMALIZE_WHITESPACE
        Graph([('start', 'A'), ('start', 'b'), ('A', 'c'), ('A', 'b'),
               ('b', 'd'), ('A', 'end'), ('b', 'end')])

    This is a list of how all of the caves are connected. You start in the cave named `start`, and
    your destination is the cave named `end`. An entry like `b-d` means that cave `b` is connected
    to cave `d` - that is, you can move between them.

        >>> ('b', 'd') in g.edges_set
        True
        >>> ('d', 'b') in g.edges_set
        True
        >>> ('A', 'd') in g.edges_set
        False

    So, the above cave system looks roughly like this:

        start
        /   \
    c--A-----b--d
        \   /
         end

    Your goal is to find the number of distinct **paths** that start at `start`, end at `end`, and
    don't visit small caves more than once. There are two types of caves: **big** caves (written in
    uppercase, like `A`) and **small** caves (written in lowercase, like `b`). It would be a waste
    of time to visit any small cave more than once, but big caves are large enough that it might be
    worth visiting them multiple times. So, all paths you find should **visit small caves at most
    once**, and can **visit big caves any number of times**.

    Given these rules, there are **`10`** paths through this example cave system:

        >>> print_paths(g.paths())
        start,A,b,A,c,A,end
        start,A,b,A,end
        start,A,b,end
        start,A,c,A,b,A,end
        start,A,c,A,b,end
        start,A,c,A,end
        start,A,end
        start,b,A,c,A,end
        start,b,A,end
        start,b,end

    Note that in this cave system, cave `d` is never visited by any path: to do so, cave `b` would
    need to be visited twice (once on the way to cave `d` and a second time when returning from cave
    `d`), and since cave `b` is small, this is not allowed.

    Here is a slightly larger example:

        >>> g2 = Graph.from_text('''
        ...     dc-end
        ...     HN-start
        ...     start-kj
        ...     dc-start
        ...     dc-HN
        ...     LN-dc
        ...     HN-end
        ...     kj-sa
        ...     kj-HN
        ...     kj-dc
        ... ''')

    The 19 paths through it are as follows:

        >>> print_paths(g2.paths())
        start,HN,dc,HN,end
        start,HN,dc,HN,kj,HN,end
        start,HN,dc,end
        start,HN,dc,kj,HN,end
        start,HN,end
        start,HN,kj,HN,dc,HN,end
        start,HN,kj,HN,dc,end
        start,HN,kj,HN,end
        start,HN,kj,dc,HN,end
        start,HN,kj,dc,end
        start,dc,HN,end
        start,dc,HN,kj,HN,end
        start,dc,end
        start,dc,kj,HN,end
        start,kj,HN,dc,HN,end
        start,kj,HN,dc,end
        start,kj,HN,end
        start,kj,dc,HN,end
        start,kj,dc,end

    Finally, this even larger example has 226 paths through it:

        >>> g3 = Graph.from_file('data/12-example-even-larger.txt')
        >>> len(g3.edges)
        18
        >>> sum(1 for _ in g3.paths())
        226

    **How many paths through this cave system are there that visit small caves at most once?**

        >>> part_1(g3)
        part 1: there are 226 paths
        226
    """

    result = sum(1 for _ in caves.paths())

    print(f"part 1: there are {result} paths")
    return result


def part_2(caves: 'Graph') -> int:
    r"""
    After reviewing the available paths, you realize you might have time to visit a single small
    cave **twice**. Specifically, big caves can be visited any number of times, a single small cave
    can be visited at most twice, and the remaining small caves can be visited at most once.
    However, the caves named `start` and `end` can only be visited **exactly once each**: once you
    leave the `start` cave, you may not return to it, and once you reach the `end` cave, the path
    must end immediately.

        >>> g = Graph.from_file('data/12-example-small.txt')
        >>> ('start', 'A') in g.edges_set
        True
        >>> ('A', 'start') in g.edges_set
        False
        >>> ('A', 'end') in g.edges_set
        True
        >>> ('end', 'A') in g.edges_set
        False

    Now, the `36` possible paths through the first example above are:

        >>> print_paths(g.paths(small_revisits_remaining=1))
        start,A,b,A,b,A,c,A,end
        start,A,b,A,b,A,end
        start,A,b,A,b,end
        start,A,b,A,c,A,b,A,end
        start,A,b,A,c,A,b,end
        start,A,b,A,c,A,c,A,end
        start,A,b,A,c,A,end
        start,A,b,A,end
        start,A,b,d,b,A,c,A,end
        start,A,b,d,b,A,end
        start,A,b,d,b,end
        start,A,b,end
        start,A,c,A,b,A,b,A,end
        start,A,c,A,b,A,b,end
        start,A,c,A,b,A,c,A,end
        start,A,c,A,b,A,end
        start,A,c,A,b,d,b,A,end
        start,A,c,A,b,d,b,end
        start,A,c,A,b,end
        start,A,c,A,c,A,b,A,end
        start,A,c,A,c,A,b,end
        start,A,c,A,c,A,end
        start,A,c,A,end
        start,A,end
        start,b,A,b,A,c,A,end
        start,b,A,b,A,end
        start,b,A,b,end
        start,b,A,c,A,b,A,end
        start,b,A,c,A,b,end
        start,b,A,c,A,c,A,end
        start,b,A,c,A,end
        start,b,A,end
        start,b,d,b,A,c,A,end
        start,b,d,b,A,end
        start,b,d,b,end
        start,b,end

    The slightly larger example above now has `103` paths through it, and the even larger example
    now has `3509` paths through it:

        >>> g2 = Graph.from_file('data/12-example-slightly-larger.txt')
        >>> sum(1 for _ in g2.paths(small_revisits_remaining=1))
        103
        >>> g3 = Graph.from_file('data/12-example-even-larger.txt')
        >>> sum(1 for _ in g3.paths(small_revisits_remaining=1))
        3509

    Given these new rules, **how many paths through this cave system are there?**

        >>> part_2(g3)
        part 2: there are 3509 paths
        3509
    """

    result = sum(1 for _ in caves.paths(small_revisits_remaining=1))

    print(f"part 2: there are {result} paths")
    return result


Edge = tuple[str, str]
Path = tuple[str, ...]


def print_paths(paths: Iterable[Path]) -> None:
    for path in paths:
        print(','.join(path))


class Graph:
    def __init__(self, edges: Iterable[Edge]):
        self.edges = list(edges)
        self.edges_set = {
            edge
            for c1, c2 in self.edges
            for edge in ((c1, c2), (c2, c1))
            if not edge[0] == 'end'
            if not edge[1] == 'start'
        }
        self.caves_set = set(c for e in self.edges for c in e)

        assert 'start' in self.caves_set
        assert 'end' in self.caves_set

        for c in self.caves_set:
            assert len(c) > 0
            # mixed case not allowed
            assert c.islower() or c.isupper()

        for cave_1, cave_2 in self.edges:
            assert cave_1 != cave_2
            # both caves cannot be big
            assert cave_1.islower() or cave_2.islower()

        self.cave_links: dict[str, list[str]] = {
            cave: sorted(
                dest
                for dest in self.caves_set
                if (cave, dest) in self.edges_set
            )
            for cave in self.caves_set
        }

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.edges!r})'

    @classmethod
    def from_text(cls, text: str) -> 'Graph':
        return cls.from_lines(text.strip().split('\n'))

    @classmethod
    def from_file(cls, fn: str) -> 'Graph':
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Graph':
        def parse_edge(t: str) -> Edge:
            cave_1, cave_2 = t.split('-')
            return cave_1, cave_2

        return cls(parse_edge(line.strip()) for line in lines)

    def paths(
        self,
        prefix: Path = ('start',),
        small_revisits_remaining: int = 0
    ) -> Iterable[Path]:
        assert len(prefix) > 0
        assert small_revisits_remaining >= 0

        current = prefix[-1]
        if current == 'end':
            return [prefix]

        return (
            longer_path
            for dest in self.cave_links[current]
            if not (revisiting := dest.islower() and dest in prefix) or small_revisits_remaining > 0
            for longer_path in self.paths(prefix + (dest,), small_revisits_remaining - revisiting)
        )


if __name__ == '__main__':
    caves_ = Graph.from_file('data/12-input.txt')
    part_1(caves_)
    part_2(caves_)
