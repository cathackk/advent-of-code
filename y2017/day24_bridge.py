from collections import defaultdict
from typing import Callable
from typing import Iterable
from typing import Iterator
from typing import Optional

from utils import timeit


class Link:
    def __init__(self, *ports: int):
        assert len(ports) >= 2
        assert len(ports) % 2 == 0
        self.ports = tuple(ports)
        self.strength = sum(self.ports)

    def __repr__(self):
        return f'{type(self).__name__}({", ".join(str(p) for p in self.ports)})'

    def __str__(self):
        def delimiter(i):
            if i == 0:
                return ''
            elif i % 2 == 0:
                return '--'
            else:
                return '/'
        return ''.join(delimiter(i) + str(p).zfill(2) for i, p in enumerate(self.ports))

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
        return Link(*reversed(self.ports))

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


def load_links(fn: str) -> Iterable[Link]:
    for line in open(fn):
        a, b = line.strip().split('/')
        a, b = int(a), int(b)
        if a > b:
            a, b = b, a
        yield Link(a, b)


def preprocessed_links(links: Iterable[Link]) -> set[Link]:
    links: set[Link] = set(links)
    port_to_links: dict[int, set[Link]] = defaultdict(set)
    for link in links:
        for port in set(link.outer_ports()):
            port_to_links[port].add(link)

    # (1) remove orphaned links
    orphaned_links = [
        link for link in links if
        all(len(port_to_links[p]) == 1 for p in link.outer_ports())
    ]
    for link in orphaned_links:
        for p in set(link.outer_ports()):
            del port_to_links[p]
    links.difference_update(orphaned_links)

    # (2) pre-join
    while True:
        # find a pair
        pp = next((
            (port, plinks)
            for port, plinks in port_to_links.items()
            if len(plinks) == 2 and port != 0
        ), None)

        # no more pairs -> we are done
        if pp is None:
            return links

        # join links
        common_port, (link_left, link_right) = pp
        link_joined = link_left.oriented_right(common_port) + link_right.oriented_left(common_port)

        # remove the two links
        links.remove(link_left)
        links.remove(link_right)
        del port_to_links[common_port]
        port_to_links[link_joined.left_port].discard(link_left)
        port_to_links[link_joined.right_port].discard(link_right)

        # add the new joined link
        if link_joined.left_port > link_joined.right_port:
            link_joined = link_joined.reversed()
        links.add(link_joined)
        port_to_links[link_joined.left_port].add(link_joined)
        port_to_links[link_joined.right_port].add(link_joined)


def max_bridge(
        from_port: int,
        links: set[Link],
        key: Callable[[Link], int]
) -> Optional[Link]:
    return max((
        link.oriented_left(from_port) + max_bridge(
            from_port=link.other_port(from_port),
            links=links.difference([link]),
            key=key
        )
        for link in links
        if from_port in link.outer_ports()
    ), key=key, default=None)


@timeit
def part_1(links: set[Link]) -> int:
    strongest_bridge = max_bridge(0, links, key=lambda b: b.strength)
    print(
        f"part 1: strength of the strongest bridge is {strongest_bridge.strength} "
        f"(length={len(strongest_bridge)})"
    )
    return strongest_bridge.strength


@timeit
def part_2(links: set[Link]) -> int:
    longest_bridge = max_bridge(0, links, key=lambda b: len(b))
    print(
        f"part 2: strength of longest bridge is {longest_bridge.strength} "
        f"(length={len(longest_bridge)})"
    )
    return longest_bridge.strength


if __name__ == '__main__':
    links_ = preprocessed_links(load_links("data/24-input.txt"))
    part_1(links_)
    part_2(links_)
