from itertools import permutations
from typing import Dict
from typing import Iterable

from utils import mink
from utils import slidingw

Pos = tuple[int, int]
Target = tuple[Pos, str]


class Maze:
    def __init__(self, floors: Iterable[Pos], targets: Iterable[Target]):
        self.floors = set(floors)
        self.targets = dict(targets)

        self.width = max(x for x, _ in self.floors) + 2
        self.height = max(y for _, y in self.floors) + 2

        assert self.floors
        assert self.targets
        for target_pos, target_code in self.targets.items():
            assert target_pos in self.floors
            assert len(target_code) == 1

    def paths(self, start_code: str = '0') -> Iterable[str]:
        other_codes = set(self.targets.values()) - {start_code}
        return (
            start_code + ''.join(path)
            for path in permutations(other_codes)
        )

    def closed_paths(self, start_code: str == '0') -> Iterable[str]:
        other_codes = set(self.targets.values()) - {start_code}
        return (
            start_code + ''.join(path) + start_code
            for path in permutations(other_codes)
        )

    def shortest_path(self, start_code: str = '0') -> tuple[str, int]:
        distances = self.calculate_distances()
        return mink(
            self.paths(start_code),
            key=lambda path: sum(distances[(a, b)] for a, b in slidingw(path, 2))
        )

    def shortest_closed_path(self, start_code: str = '0') -> tuple[str, int]:
        distances = self.calculate_distances()
        return mink(
            self.closed_paths(start_code),
            key=lambda path: sum(distances[(a, b)] for a, b in slidingw(path, 2))
        )

    def neighbors(self, pos: Pos) -> Iterable[Pos]:
        x, y = pos
        return (
            (x+dx, y+dy)
            for (dx, dy) in [(+1, 0), (-1, 0), (0, +1), (0, -1)]
            if (x+dx, y+dy) in self.floors
        )

    def calculate_distances(self) -> Dict[tuple[str, str], int]:
        return dict(
            ccd
            for t1 in self.targets.items()
            for ccd in self._calculate_distances_from(t1)
        )

    def _calculate_distances_from(self, target: Target) -> Iterable[tuple[tuple[str, str], int]]:
        pos1, code1 = target

        visited: set[Pos] = {pos1}
        current_layer: set[Pos] = {pos1}
        current_distance: int = 0
        codes_left: set[str] = set(self.targets.values()) - {code1}

        while current_layer and codes_left:
            next_layer: set[Pos] = set()

            for pos in current_layer:
                for npos in self.neighbors(pos):
                    if npos in visited:
                        continue

                    visited.add(npos)
                    next_layer.add(npos)

                    if npos in self.targets:
                        code2 = self.targets[npos]
                        codes_left.remove(code2)
                        yield (code1, code2), current_distance + 1

            current_layer = next_layer
            current_distance += 1

    def draw(self):
        def t(p: Pos) -> str:
            if p in self.targets:
                return self.targets[p]
            elif p in self.floors:
                return '.'
            else:
                return '#'
        for y in range(self.height):
            print(''.join(t((x, y)) for x in range(self.width)))

    @classmethod
    def load(cls, fn: str) -> 'Maze':
        floors: list[Pos] = []
        targets: list[Target] = []
        for y, line in enumerate(open(fn)):
            for x, c in enumerate(line.strip()):
                if c != '#':
                    pos = (x, y)
                    floors.append(pos)
                    if c.isdigit():
                        targets.append((pos, c))
        return cls(floors, targets)


def test():
    maze = Maze.load("data/24-example.txt")
    assert maze.width == 11
    assert maze.height == 5
    assert maze.targets[(1, 1)] == '0'

    distances = maze.calculate_distances()
    assert distances[('0', '1')] == 2
    assert distances[('1', '2')] == 6
    assert distances[('2', '1')] == 6
    assert distances[('2', '4')] == 10

    path, dist = maze.shortest_path('0')
    assert path == '04123'
    assert dist == 14


def part_1(maze: Maze) -> int:
    path, dist = maze.shortest_path('0')
    print(f"part 1: shortest path is {dist} long ({path})")
    return dist


def part_2(maze: Maze) -> int:
    path, dist = maze.shortest_closed_path('0')
    print(f"part 2: shortest closed path is {dist} long ({path})")
    return dist


if __name__ == '__main__':
    maze_ = Maze.load("data/24-input.txt")
    part_1(maze_)
    part_2(maze_)
