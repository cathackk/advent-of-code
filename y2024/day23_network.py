"""
Advent of Code 2024
Day 23: LAN Party
https://adventofcode.com/2024/day/23
"""

from typing import Callable, Iterable, Self

from common.file import relative_path


def part_1(network: 'Network', prefix: str = 't') -> int:
    """
    As The Historians wander around a secure area at Easter Bunny HQ, you come across posters for
    a LAN party scheduled for today! Maybe you can find it; you connect to a nearby datalink port
    (y2016/day09_compression.py) and download a map of the local network (your puzzle input).

    The network map provides a list of every **connection between two computers**. For example:

        >>> example_net = Network.from_text('''
        ...     kh-tc
        ...     qp-kh
        ...     de-cg
        ...     ka-co
        ...     yn-aq
        ...     qp-ub
        ...     cg-tb
        ...     vc-aq
        ...     tb-ka
        ...     wh-tc
        ...     yn-cg
        ...     kh-ub
        ...     ta-co
        ...     de-co
        ...     tc-td
        ...     tb-wq
        ...     wh-td
        ...     ta-ka
        ...     td-qp
        ...     aq-cg
        ...     wq-ub
        ...     ub-vc
        ...     de-ta
        ...     wq-aq
        ...     wq-vc
        ...     wh-yn
        ...     ka-de
        ...     kh-ta
        ...     co-tc
        ...     wh-qp
        ...     tb-vc
        ...     td-yn
        ... ''')
        >>> len(example_net)
        32

    Each line of text in the network map represents a single connection; the line `kh-tc` represents
    a connection between the computer named `kh` and the computer named `tc`. Connections aren't
    directional; `tc-kh` would mean exactly the same thing.

        >>> ('kh', 'tc') in example_net
        True
        >>> ('tc', 'kh') in example_net
        True
        >>> ('tc', 'ka') in example_net
        False

    LAN parties typically involve multiplayer games, so maybe you can locate it by finding groups of
    connected computers. Start by looking for **sets of three computers** where each computer in the
    set is connected to the other two computers.

    In this example, there are `12` such sets of three interconnected computers:

        >>> list(example_net.triangles())  # doctest: +NORMALIZE_WHITESPACE
        [('aq', 'cg', 'yn'),
         ('aq', 'vc', 'wq'),
         ('co', 'de', 'ka'),
         ('co', 'de', 'ta'),
         ('co', 'ka', 'ta'),
         ('de', 'ka', 'ta'),
         ('kh', 'qp', 'ub'),
         ('qp', 'td', 'wh'),
         ('tb', 'vc', 'wq'),
         ('tc', 'td', 'wh'),
         ('td', 'wh', 'yn'),
         ('ub', 'vc', 'wq')]
        >>> len(_)
        12

    If the Chief Historian is here, **and** he's at the LAN party, it would be best to know that
    right away. You're pretty sure his computer's name starts with `t`, so consider only sets of
    three computers where at least one computer's name starts with `t`. That narrows the list down
    to **`7`** sets of three interconnected computers:

        >>> list(example_net.triangles(with_node=lambda c: c[0] == 't'))
        ... # doctest: +NORMALIZE_WHITESPACE
        [('ta', 'co', 'de'),
         ('ta', 'co', 'ka'),
         ('ta', 'de', 'ka'),
         ('tb', 'vc', 'wq'),
         ('tc', 'td', 'wh'),
         ('td', 'qp', 'wh'),
         ('td', 'wh', 'yn')]
        >>> len(_)
        7

    Find all the sets of three interconnected computers.
    **How many contain at least one computer with a name that starts with `t`?**

        >>> part_1(example_net)
        part 1: there are 7 triangles containing a computer starting with 't'
        7
    """

    result = sum(1 for _ in network.triangles(lambda n: n.startswith(prefix)))

    print(f"part 1: there are {result} triangles containing a computer starting with {prefix!r}")
    return result


def part_2(network: 'Network') -> str:
    """
    There are still way too many results to go through them all. You'll have to find the LAN party
    another way and go there yourself.

    Since it doesn't seem like any employees are around, you figure they must all be at the LAN
    party. If that's true, the LAN party will be **the largest set of computers that are all
    connected to each other**. That is, for each computer at the LAN party, that computer will have
    a connection to every other computer at the LAN party.

    In the above example, the largest set of computers that are all connected to each other is made
    up of `co`, `de`, `ka`, and `ta`. Each computer in this set has a connection to every other
    computer in the set.

        >>> example_net = Network.from_file('data/23-example.txt')
        >>> example_clique = ['co', 'de', 'ka', 'ta']
        >>> from itertools import combinations
        >>> all(edge in example_net for edge in combinations(example_clique, 2))
        True

    The LAN party posters say that the **password** to get into the LAN party is the name of every
    computer at the LAN party, sorted alphabetically, then joined together with commas. (The people
    running the LAN party are clearly a bunch of nerds.) In this example, the password would be:

        >>> password(example_clique)
        'co,de,ka,ta'

    What is the password to get into the LAN party?

        >>> part_2(example_net)
        part 2: LAN party password is co,de,ka,ta
        'co,de,ka,ta'
    """

    result = password(network.maximal_clique())

    print(f"part 2: LAN party password is {result}")
    return result


Edge = tuple[str, str]


class Network:
    def __init__(self, edges: Iterable[Edge]):
        self.edges: set[Edge] = set()

        neighbors: dict[str, list[str]] = {}
        for n_1, n_2 in edges:
            self.edges.add((n_1, n_2))
            self.edges.add((n_2, n_1))
            neighbors.setdefault(n_1, []).append(n_2)
            neighbors.setdefault(n_2, []).append(n_1)

        self.neighbors = {node: sorted(adjs) for node, adjs in sorted(neighbors.items())}

    @property
    def nodes(self) -> Iterable[str]:
        return self.neighbors.keys()

    def __len__(self) -> int:
        return len(self.edges) // 2

    def __contains__(self, edge: Edge) -> bool:
        return edge in self.edges or tuple(edge[::-1]) in self.edges

    def triangles(
        self,
        with_node: Callable[[str], bool] | None = None,
    ) -> Iterable[tuple[str, str, str]]:
        tested_nodes: set[str] = set()
        for node, adjs in self.neighbors.items():
            if with_node and not with_node(node):
                continue
            for k, adj_1 in enumerate(adjs):
                if adj_1 in tested_nodes:
                    continue
                for adj_2 in adjs[k+1:]:
                    if adj_2 in tested_nodes:
                        continue
                    if (adj_1, adj_2) in self:
                        yield node, adj_1, adj_2
            tested_nodes.add(node)

    def maximal_clique(self) -> list[str]:
        return max((self.clique_with_node(node) for node in self.nodes), key=len)

    def clique_with_node(self, starting_node: str) -> list[str]:
        clique = {starting_node}

        # neighbors of the starting node
        candidates = set(self.neighbors[starting_node])

        # iteratively add nodes to the clique
        while candidates:
            node = candidates.pop()
            # check if the candidate connects to all current clique members
            if all((node, member) for member in clique):
                clique.add(node)
                # update candidates to only those connected to the current clique
                candidates.intersection_update(self.neighbors[node])

        return sorted(clique)

    @classmethod
    def from_file(cls, fn: str) -> Self:
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_text(cls, text: str) -> Self:
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        def edges() -> Iterable[Edge]:
            for line in lines:
                n_1, n_2 = line.strip().split('-')
                yield (n_1, n_2)

        return cls(edges())


def password(nodes: Iterable[str]) -> str:
    return ','.join(sorted(nodes))


def main(input_fn: str = 'data/23-input.txt') -> tuple[int, str]:
    network = Network.from_file(input_fn)
    result_1 = part_1(network)
    result_2 = part_2(network)
    return result_1, result_2


if __name__ == '__main__':
    main()
