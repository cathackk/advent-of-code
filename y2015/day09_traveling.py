from itertools import permutations
from typing import Dict
from typing import Iterable
from typing import Set

from utils import minmax
from utils import zip1


Road = tuple[int, str, str]
Route = Iterable[str]


def load_roads(fn: str) -> Iterable[Road]:
    for line in open(fn):
        p1, to, p2, eq, dist = line.strip().split(' ')
        assert to == "to"
        assert eq == "="
        yield int(dist), p1, p2


def create_distances(roads: Iterable[Road]) -> Dict[tuple[str, str], int]:
    ds = {}
    for dist, p1, p2 in roads:
        ds[(p1, p2)] = dist
        ds[(p2, p1)] = dist
    return ds


if __name__ == '__main__':
    roads = list(load_roads("data/09-input.txt"))
    distances = create_distances(roads)
    places: Set[str] = set(p for r in roads for p in r[1:])

    def route_length(route: Route) -> int:
        return sum(distances[(p1, p2)] for p1, p2 in zip1(route))

    routes = permutations(places)
    shortest_route, longest_route = minmax(routes, key=route_length)
    print(f"part 1: shortest route length is {route_length(shortest_route)}")
    print(f"part 2: longest  route length is {route_length(longest_route)}")
