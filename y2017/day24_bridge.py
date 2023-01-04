"""
Advent of Code 2017
Day 24: Electromagnetic Moat
https://adventofcode.com/2017/day/24
"""

from collections import defaultdict
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Iterator
from typing import Optional

from common.iteration import max_all
from common.utils import some
from meta.aoc_tools import data_path


def part_1(links: Iterable['Link']) -> int:
    """
    The CPU itself is a large, black building surrounded by a bottomless pit. Enormous metal tubes
    extend outward from the side of the building at regular intervals and descend down into the
    void. There's no way to cross, but you need to get inside.

    No way, of course, other than building a **bridge** out of the magnetic components strewn about
    nearby.

    Each component has two **ports**, one on each end. The ports come in all different types, and
    only matching types can be connected. You take an inventory of the components by their port
    types (your puzzle input). Each port is identified by the number of **pins** it uses; more pins
    mean a stronger connection for your bridge. A `3/7` component, for example, has a type-3 port on
    one side, and a type-7 port on the other.

        >>> Link.from_str('3/7')
        Link(3, 7)

    Your side of the pit is metallic; a perfect surface to connect a magnetic, **zero-pin port**.
    Because of this, the first port you use must be of type `0`. It doesn't matter what type of port
    you end with; your goal is just to make the bridge as strong as possible.

    The **strength** of a bridge is the sum of the port types in each component. For example, if
    your bridge is made of components `0/3`, `3/7`, and `7/4`, your bridge has a strength of
    `0+3 + 3+7 + 7+4 = 24`.

        >>> print(triple_link := Link(0, 3) + Link(3, 7) + Link(7, 4))
        0/3--3/7--7/4
        >>> triple_link.strength
        24

    For example, suppose you had the following components:

        >>> example_links = links_from_text('''
        ...     0/2
        ...     2/2
        ...     2/3
        ...     3/4
        ...     3/5
        ...     0/1
        ...     10/1
        ...     9/10
        ... ''')
        >>> example_links  # doctest: +NORMALIZE_WHITESPACE
        [Link(0, 2), Link(2, 2), Link(2, 3), Link(3, 4),
         Link(3, 5), Link(0, 1), Link(1, 10), Link(9, 10)]

    With them, you could make the following valid bridges:

        >>> for bridge in valid_bridges(links=example_links):
        ...     print(bridge)
        0/1
        0/1--1/10
        0/1--1/10--10/9
        0/2
        0/2--2/3
        0/2--2/3--3/4
        0/2--2/3--3/5
        0/2--2/2
        0/2--2/2--2/3
        0/2--2/2--2/3--3/4
        0/2--2/2--2/3--3/5

    (Note how, as shown by `10/1`, order of ports within a component doesn't matter. However, you
    may only use each port on a component once.)

    Of these bridges, the **strongest** one is `0/1--1/10--10/9`; it has a strength of
    `0+1 + 1+10 + 10+9 = 31`.

        >>> (strongest := strongest_bridge(example_links))
        Link(0, 1, 1, 10, 10, 9)
        >>> strongest.strength
        31

    **What is the strength of the strongest bridge you can make** with the components you have
    available?

        >>> part_1(example_links)
        part 1: strongest bridge has strength 31
        31
    """

    result = strongest_bridge(links).strength
    print(f"part 1: strongest bridge has strength {result}")
    return result


def part_2(links: Iterable['Link']) -> int:
    """
    The bridge you've built isn't long enough; you can't jump the rest of the way.

    In the example above, there are two longest bridges:

        >>> example_links = links_from_file('data/24-example.txt')
        >>> bridges = longest_bridges(example_links)
        >>> for bridge in bridges:
        ...     print(bridge)
        0/2--2/2--2/3--3/4
        0/2--2/2--2/3--3/5

    Of them, the one which uses the `3/5` component is stronger; its strength is
    `0+2 + 2+2 + 2+3 + 3+5 = 19`.

        >>> (longest_and_strongest := max(bridges, key=lambda b: b.strength))
        Link(0, 2, 2, 2, 2, 3, 3, 5)
        >>> longest_and_strongest.strength
        19

    **What is the strength of the longest bridge you can make?** If you can make multiple bridges of
    the longest length, pick the **strongest** one.

        >>> part_2(example_links)
        part 2: strongest among the longest bridges has strength 19
        19
    """

    result = longest_and_strongest_bridge(links).strength
    print(f"part 2: strongest among the longest bridges has strength {result}")
    return result


class Link:
    def __init__(self, *ports: int):
        assert len(ports) >= 2
        assert len(ports) % 2 == 0
        self.ports = tuple(ports)
        self.strength = sum(self.ports)

    def __repr__(self):
        return f'{type(self).__name__}({", ".join(str(p) for p in self.ports)})'

    def __str__(self):
        def delimiter(index):
            if index == 0:
                return ''
            elif index % 2 == 0:
                return '--'
            else:
                return '/'

        return ''.join(delimiter(ix) + str(p) for ix, p in enumerate(self.ports))

    @classmethod
    def from_str(cls, line: str) -> 'Link':
        # only single-link components supported
        left, right = line.split('/')

        if (left_int := int(left)) > (right_int := int(right)):
            left_int, right_int = right_int, left_int

        return cls(left_int, right_int)

    def __len__(self):
        return len(self.ports) // 2

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.ports == other.ports

    def __hash__(self):
        return hash(self.ports)

    @property
    def left_port(self) -> int:
        return self.ports[0]

    @property
    def right_port(self) -> int:
        return self.ports[-1]

    def outer_ports(self) -> Iterator[int]:
        yield self.left_port
        yield self.right_port

    def other_port(self, port: int) -> int:
        if port == self.left_port:
            return self.right_port
        elif port == self.right_port:
            return self.left_port
        else:
            raise KeyError(port)

    def reversed(self) -> 'Link':
        return type(self)(*reversed(self.ports))

    def oriented_left(self, port_to_left: int) -> 'Link':
        if port_to_left == self.left_port:
            return self
        elif port_to_left == self.right_port:
            return self.reversed()
        else:
            raise KeyError(port_to_left)

    def oriented_right(self, port_to_right: int) -> 'Link':
        if port_to_right == self.right_port:
            return self
        elif port_to_right == self.left_port:
            return self.reversed()
        else:
            raise KeyError(port_to_right)

    def __add__(self, other: Optional['Link']) -> 'Link':
        if other is not None:
            assert self.right_port == other.left_port
            return type(self)(*(self.ports + other.ports))
        else:
            return self


def valid_bridges(links: Iterable[Link]) -> Iterable[Link]:
    return (
        bridge
        for bridge in _valid_bridges(from_port=0, links=set(links))
        if bridge is not None
    )


def _valid_bridges(from_port: int, links: set[Link]) -> Iterable[Link | None]:
    yield None
    yield from (
        link.oriented_left(from_port) + rest
        for link in links
        if from_port in link.outer_ports()
        for rest in _valid_bridges(
            from_port=link.other_port(from_port),
            links=links.difference([link])
        )
    )


def longest_bridges(links: Iterable[Link]) -> list[Link]:
    return max_all(valid_bridges(links), key=len)


def strongest_bridge(links: Iterable[Link]) -> Link:
    return some(max_bridge(from_port=0, links=set(links), key=lambda b: b.strength))


def longest_and_strongest_bridge(links: Iterable[Link]) -> Link:
    return some(max_bridge(from_port=0, links=set(links), key=lambda b: (len(b), b.strength)))


def max_bridge(from_port: int, links: set[Link], key: Callable[[Link], Any]) -> Optional[Link]:
    bridges: Iterable[Link] = (
        link.oriented_left(from_port) + max_bridge(
            from_port=link.other_port(from_port),
            links=links.difference([link]),
            key=key
        )
        for link in links
        if from_port in link.outer_ports()
    )
    return max(bridges, key=key, default=None)  # type: ignore


def preprocessed_links(links: Iterable[Link]) -> set[Link]:
    links_set = set(links)
    port_to_links: dict[int, set[Link]] = defaultdict(set)
    for link in links_set:
        for port in set(link.outer_ports()):
            port_to_links[port].add(link)

    # (1) remove orphaned links
    orphaned_links = [
        link for link in links_set if
        all(len(port_to_links[p]) == 1 for p in link.outer_ports())
    ]
    for link in orphaned_links:
        for port in set(link.outer_ports()):
            del port_to_links[port]
    links_set.difference_update(orphaned_links)

    # (2) pre-join
    while True:
        # find a pair
        port_plinks = next((
            (port, plinks)
            for port, plinks in port_to_links.items()
            if len(plinks) == 2 and port != 0
        ), None)

        # no more pairs -> we are done
        if port_plinks is None:
            return links_set

        # join links
        common_port, (link_left, link_right) = port_plinks
        link_joined = link_left.oriented_right(common_port) + link_right.oriented_left(common_port)

        # remove the two links
        links_set.remove(link_left)
        links_set.remove(link_right)
        del port_to_links[common_port]
        port_to_links[link_joined.left_port].discard(link_left)
        port_to_links[link_joined.right_port].discard(link_right)

        # add the new joined link
        if link_joined.left_port > link_joined.right_port:
            link_joined = link_joined.reversed()
        links_set.add(link_joined)
        port_to_links[link_joined.left_port].add(link_joined)
        port_to_links[link_joined.right_port].add(link_joined)


def links_from_text(text: str) -> list[Link]:
    return list(links_from_lines(text.strip().splitlines()))


def links_from_file(fn: str) -> list[Link]:
    return list(links_from_lines(open(fn)))


def links_from_lines(lines: Iterable[str]) -> Iterable[Link]:
    return (Link.from_str(line.strip()) for line in lines)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    links = preprocessed_links(links_from_file(input_path))
    result_1 = part_1(links)
    result_2 = part_2(links)
    return result_1, result_2


if __name__ == '__main__':
    main()
