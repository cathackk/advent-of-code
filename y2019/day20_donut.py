import string
from typing import Iterable
from typing import Optional

Pos = tuple[int, int]
PosD = tuple[Pos, int]
Portal = tuple[str, Pos, Pos]

START = '<'
END = '>'
FLOOR = '.'
WALL = '#'
PORTALS = set(string.ascii_letters)


class Maze:
    def __init__(
            self,
            floors: Iterable[Pos],
            start: Pos,
            end: Pos,
            portals: Iterable[Portal]
    ):
        self.floors = set(floors)
        self.width = max(x for x, y in self.floors) + 1
        self.height = max(y for x, y in self.floors) + 1

        self.start = start
        self.end = end

        # portals
        self.portals = list(portals)
        self.portal_names: dict[Pos, str] = dict()
        self.portal_paths: dict[Pos, PosD] = dict()

        def is_outer(pos: Pos) -> bool:
            x, y = pos
            return x == 0 or y == 0 or x == self.width - 1 or y == self.height - 1

        def is_inner(pos: Pos) -> bool:
            return not is_outer(pos)

        for pn, p1, p2 in self.portals:
            self.portal_names[p1] = pn
            self.portal_names[p2] = pn

            if is_outer(p2):
                assert is_inner(p1)
                inner, outer = p1, p2
            else:
                assert is_inner(p2)
                assert is_outer(p1)
                inner, outer = p2, p1

            self.portal_paths[inner] = (outer, +1)
            self.portal_paths[outer] = (inner, -1)

        # validate
        for x, y in self.floors:
            assert 0 <= x < self.width
            assert 0 <= y < self.height
        assert self.start in self.floors
        assert self.end in self.floors
        assert self.start != self.end
        for pn, p1, p2 in self.portals:
            assert p1 in self.floors
            assert p2 in self.floors
            assert p1 not in (self.start, self.end)
            assert p2 not in (self.start, self.end)
        assert len(self.portal_paths) == len(self.portals) * 2
        assert len(set(pn for pn, _, _ in self.portals)) == len(self.portals)

    def tile_at(self, pos: Pos) -> str:
        if pos in self.portal_names:
            return self.portal_names[pos]
        elif pos == self.start:
            return '<'
        elif pos == self.end:
            return '>'
        elif pos in self.floors:
            return '.'
        else:
            return '#'

    def draw(self):
        for y in range(self.height):
            print(''.join(self.tile_at((x, y)) for x in range(self.width)))

    @classmethod
    def load(cls, fn: str):
        with open(fn) as f:
            lines = [line.strip() for line in f]

        floors: list[Pos] = []
        start: Optional[Pos] = None
        end: Optional[Pos] = None
        unfinished_portals: dict[str, Pos] = dict()
        finished_portals: list[Portal] = []

        for y, line in enumerate(lines):
            for x, c in enumerate(line):
                pos = (x, y)
                if c == FLOOR:
                    floors.append(pos)
                elif c == START:
                    floors.append(pos)
                    start = pos
                elif c == END:
                    floors.append(pos)
                    end = pos
                elif c in PORTALS:
                    floors.append(pos)
                    if c not in unfinished_portals:
                        unfinished_portals[c] = pos
                    else:
                        other = unfinished_portals.pop(c)
                        finished_portals.append((c, pos, other))

        assert start is not None
        assert end is not None
        assert len(unfinished_portals) == 0

        return Maze(
            floors=floors,
            start=start,
            end=end,
            portals=finished_portals
        )

    def solve(self) -> Optional[int]:
        layer: list[Pos] = [self.start]
        distance = 0

        unprocessed = set(self.floors)
        unprocessed.remove(self.start)

        while layer:
            next_layer = []
            nposs = (
                npos
                for pos in layer
                for npos in self.neighbors(pos)
                if npos in unprocessed
            )

            for npos in nposs:
                if npos == self.end:
                    return distance + 1
                unprocessed.remove(npos)
                next_layer.append(npos)

            layer = next_layer
            distance += 1

        else:
            return None

    def neighbors(self, pos: Pos) -> Iterable[Pos]:
        if pos in self.portal_paths:
            yield self.portal_paths[pos][0]

        x, y = pos
        if x > 0:
            yield x - 1, y
        if y > 0:
            yield x, y - 1
        if x < self.width - 1:
            yield x + 1, y
        if y < self.height - 1:
            yield x, y + 1

    def solve3(self) -> Optional[int]:
        start3 = self.start, 0
        end3 = self.end, 0

        layer: list[PosD] = [start3]
        distance = 0

        max_depth = len(self.portals)
        unprocessed = set((pos, depth) for pos in self.floors for depth in range(max_depth))

        while layer:
            next_layer = []
            nposds = (
                nposd
                for posd in layer
                for nposd in self.neighbors3(posd)
                if nposd in unprocessed
            )

            for nposd in nposds:
                if nposd == end3:
                    return distance + 1
                unprocessed.remove(nposd)
                next_layer.append(nposd)

            layer = next_layer
            distance += 1

        else:
            return None

    def neighbors3(self, posd: PosD) -> Iterable[PosD]:
        pos, depth = posd
        if pos in self.portal_paths:
            pos1, ddepth = self.portal_paths[pos]
            yield pos1, depth + ddepth

        x, y = pos
        if x > 0:
            yield (x - 1, y), depth
        if y > 0:
            yield (x, y - 1), depth
        if x < self.width - 1:
            yield (x + 1, y), depth
        if y < self.height - 1:
            yield (x, y + 1), depth


def part_1(maze):
    distance = maze.solve()
    print(f"part 1: path is {distance} long")


def part_2(maze):
    distance = maze.solve3()
    print(f"part 2: path is {distance} long")


if __name__ == '__main__':
    m = Maze.load("data/20-input.txt")
    m.draw()
    part_1(m)
    part_2(m)
