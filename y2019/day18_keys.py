import string
from collections import defaultdict
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

from utils import timeit

Pos = Tuple[int, int]
Tile = Tuple[Pos, str]
Solution = Tuple[int, List[str]]
SolutionCache = Dict[Tuple[str, str], Solution]
Path = Tuple[Tuple[str, str], int, List[str]]
PathsCache = Dict[str, Dict[str, Tuple[int, Set[str]]]]
Layer = List[Tuple[Pos, List[str]]]

SPACE = '.'
WALL = '#'


def is_key(c: Optional[str]) -> bool:
    return c and c in string.ascii_lowercase


def is_door(c: Optional[str]) -> bool:
    return c and c in string.ascii_uppercase


def is_space(c: Optional[str]) -> bool:
    return c == SPACE


def is_start(c: Optional[str]) -> bool:
    return c and c in '@1234'


def neighbors(pos: Pos) -> Iterable[Pos]:
    x, y = pos
    yield x, y-1,
    yield x+1, y
    yield x, y+1
    yield x-1, y


class Maze:
    def __init__(self, width: int, height: int, start: Tile, tiles: Iterable[Tile]):
        self.width = width
        self.height = height
        self.pos, self.start_char = start
        self.tiles = dict(tiles)
        self.keys = ''.join(sorted(c for c in self.tiles.values() if is_key(c)))
        self._validate()

    def _validate(self):
        # validate
        # - pos in bounds
        pos_x, pos_y = self.pos
        assert 0 <= pos_x < self.width, f"pos x out of bounds: x={pos_x}, width={self.width}"
        assert 0 <= pos_y < self.height, f"pos y out of bounds: y={pos_y}, height={self.height}"
        # - pos in space
        assert is_space(self.tiles[self.pos]), \
            f"pos {self.pos} not in space: {self.tiles[self.pos]!r}"
        for (x, y), c in self.tiles.items():
            # - tiles in bounds
            assert 0 <= x < self.width, \
                f"x out of bounds: x={x}, y={y}, c={c!r}, width={self.width}"
            assert 0 <= y < self.height, \
                f"y out of bounds: x={x}, y={y}, c={c!r}, height={self.height}"
            # - correct tiles
            assert is_space(c) or is_key(c) or is_door(c), \
                f"wrong character: x={x}, y={y}, c={c!r}"
        # - wall all around
        for x in range(self.width):
            for y in (0, self.height-1):
                assert (x, y) not in self.tiles, \
                    f"not wall at x={x}, y={y}, c={self.tiles[(x, y)]!r}"
        for y in range(self.height):
            for x in (0, self.width-1):
                assert (x, y) not in self.tiles, \
                    f"not wall at x={x}, y={y}, c={self.tiles[(x, y)]!r}"

    def solve(self) -> Solution:
        paths: PathsCache = defaultdict(dict)
        for (kfrom, kto), distance, items in self._precompute_paths():
            paths[kfrom][kto] = (distance, set(c.lower() for c in items))
        return _solution(
            current_key=self.start_char,
            remaining_keys=list(self.keys),
            paths=dict(paths),
            cache=dict()
        )

    def solve_multi(self) -> Solution:
        submazes = self.split_into_four()
        paths: PathsCache = defaultdict(dict)
        for submaze in submazes:
            for (kfrom, kto), distance, items in submaze._precompute_paths():
                paths[kfrom][kto] = (distance, set(c.lower() for c in items))
        return _multi_solution(
            current_keys=list('1234'),
            remaining_keys=list(self.keys),
            paths=dict(paths),
            cache=dict()
        )

    def split_into_four(self) -> Tuple['Maze', 'Maze', 'Maze', 'Maze']:
        cx, cy = self.pos
        tiles = dict(self.tiles)
        assert all(
            is_space(tiles[(x, y)])
            for x in range(cx-1, cx+2)
            for y in range(cy-1, cy+2)
        )

        # ...    @#@
        # .@. -> ###
        # ...    @#@

        # create four submazes
        return (
            # north-west
            Maze(
                width=cx+1,
                height=cy+1,
                start=((cx-1, cy-1), '1'),
                tiles=(((x, y), c) for (x, y), c in tiles.items() if x < cx and y < cy)
            ),
            # north-east
            Maze(
                width=self.width - cx,
                height=cy+1,
                start=((1, cy-1), '2'),
                tiles=(((x-cx, y), c) for (x, y), c in tiles.items() if x > cx and y < cy)
            ),
            # south-west
            Maze(
                width=cx+1,
                height=self.height - cy,
                start=((cx-1, 1), '3'),
                tiles=(((x, y-cy), c) for (x, y), c in tiles.items() if x < cx and y > cy)
            ),
            # south-east
            Maze(
                width=self.width - cx,
                height=self.height - cy,
                start=((1, 1), '4'),
                tiles=(((x-cx, y-cy), c) for (x, y), c in tiles.items() if x > cx and y > cy)
            )
        )

    def _precompute_paths(self) -> Iterable[Path]:
        keys_positions = [
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if is_key(self.tiles.get((x, y)))
        ]
        return (
            path
            for start in ([self.pos] + keys_positions)
            for path in self._find_paths_from(start)
        )

    def _find_paths_from(self, start: Pos) -> Iterable[Path]:
        last_layer: Layer = [(start, [])]
        last_distance = 0

        unprocessed = dict(self.tiles)
        start_tile = unprocessed.pop(start)
        if is_space(start_tile):
            assert self.pos == start
            start_tile = self.start_char

        while last_layer:
            next_layer: Layer = []
            nposs = (
                (npos, items)
                for pos, items in last_layer
                for npos in neighbors(pos)
                if npos in unprocessed
            )
            for npos, items in nposs:
                tile = unprocessed.pop(npos)
                if is_space(tile):
                    next_layer.append((npos, items))
                elif is_door(tile):
                    next_layer.append((npos, items+[tile]))
                elif is_key(tile):
                    next_layer.append((npos, items+[tile]))
                    yield (start_tile, tile), last_distance + 1, items

            last_layer = next_layer
            last_distance += 1

    def draw(self):
        for y in range(self.height):
            print(''.join(
                (
                    self.tiles.get((x, y), WALL)
                    if (x, y) != self.pos
                    else self.start_char
                )
                for x in range(self.width)
            ))

    @classmethod
    def load(cls, fn: str):
        with open(fn) as f:
            lines = [line.strip() for line in f]
        widths = set(len(line) for line in lines)
        assert len(widths) == 1
        width = next(iter(widths))
        height = len(lines)
        start = next(
            ((x, y), c)
            for y, line in enumerate(lines)
            for x, c in enumerate(line)
            if is_start(c)
        )
        tiles = (
            ((x, y), (c if (x, y) != start[0] else SPACE))
            for y, line in enumerate(lines)
            for x, c in enumerate(line)
            if c != WALL
        )
        return cls(
            width=width,
            height=height,
            start=start,
            tiles=tiles
        )


def _solution(
        current_key: str,
        remaining_keys: List[str],
        paths: PathsCache,
        cache: SolutionCache
) -> Solution:
    if not remaining_keys:
        return 0, []

    assert current_key not in remaining_keys
    cacheby = current_key, ''.join(remaining_keys)
    if cacheby in cache:
        return cache[cacheby]

    def gen_solutions() -> Iterable[Solution]:
        for target_key in remaining_keys:
            distance, items = paths[current_key][target_key]
            if is_passable(items, remaining_keys):
                sub_distance, sub_sequence = _solution(
                    current_key=target_key,
                    remaining_keys=[k for k in remaining_keys if k != target_key],
                    paths=paths,
                    cache=cache
                )
                yield (sub_distance + distance, [target_key] + sub_sequence)

    solution = min(gen_solutions())
    cache[cacheby] = solution
    return solution


def _multi_solution(
        current_keys: List[str],
        remaining_keys: List[str],
        paths: PathsCache,
        cache: SolutionCache
) -> Solution:
    if not remaining_keys:
        return 0, []

    assert all((key not in remaining_keys) for key in current_keys)
    cacheby = ''.join(current_keys), ''.join(remaining_keys)
    if cacheby in cache:
        return cache[cacheby]

    remaining_keys_s = set(remaining_keys) if len(remaining_keys) >= 4 else remaining_keys

    def gen_solutions() -> Iterable[Solution]:
        for current_key_index, current_key in enumerate(current_keys):
            if current_key not in paths:
                continue
            for target_key, (distance, items) in paths[current_key].items():
                if target_key not in remaining_keys_s:
                    continue
                if not is_passable(items, remaining_keys):
                    continue
                next_keys = [
                    target_key if i == current_key_index else ck
                    for i, ck in enumerate(current_keys)
                ]
                sub_distance, sub_sequence = _multi_solution(
                    current_keys=next_keys,
                    remaining_keys=[k for k in remaining_keys if k != target_key],
                    paths=paths,
                    cache=cache
                )
                yield (sub_distance + distance, [target_key] + sub_sequence)

    solution = min(gen_solutions())
    cache[cacheby] = solution
    return solution


def is_passable(items: Set[str], remaining_keys: List[str]):
    return not any((key in items) for key in remaining_keys)


def test_example_1():
    maze = Maze.load("data/18-example-1.txt")
    assert maze.width == 24
    assert maze.height == 5
    assert maze.pos == (15, 1)
    assert len(maze.keys) == 6
    assert maze.solve() == (86, list('abcdef'))


def test_example_2():
    maze = Maze.load("data/18-example-2.txt")
    assert maze.solve() == (132, list('bacdfeg'))


def test_example_3():
    maze = Maze.load("data/18-example-3.txt")
    assert maze.solve()[0] == 136


def test_example_4():
    maze = Maze.load("data/18-example-4.txt")
    assert maze.solve()[0] == 81


def test_example_multi1():
    maze = Maze.load("data/18-example-m1.txt")
    assert maze.width == 7
    assert maze.height == 7
    assert maze.pos == (3, 3)
    assert maze.keys == 'abcd'

    quadrants = maze.split_into_four()
    assert all(q.width == 4 for q in quadrants)
    assert all(q.height == 4 for q in quadrants)

    nw, ne, sw, se = quadrants
    assert nw.pos == (2, 2)
    assert nw.keys == 'a'
    assert ne.pos == (1, 2)
    assert ne.keys == 'd'
    assert sw.pos == (2, 1)
    assert sw.keys == 'c'
    assert se.pos == (1, 1)
    assert se.keys == 'b'

    assert maze.solve_multi() == (8, list('abcd'))


def test_example_multi2():
    maze = Maze.load("data/18-example-m2.txt")
    assert maze.solve_multi()[0] == 24


def test_example_multi3():
    maze = Maze.load("data/18-example-m3.txt")
    assert maze.solve_multi()[0] == 72


@timeit
def part_1(maze):
    print(maze.solve())


@timeit
def part_2(maze):
    print(maze.solve_multi())


if __name__ == '__main__':
    maze = Maze.load("data/18-input.txt")
    maze.draw()
    part_1(maze)

    for submaze in maze.split_into_four():
        print()
        submaze.draw()
    part_2(maze)
