from collections import Counter
from typing import Iterable
from typing import Tuple


Pos = Tuple[int, int]


class Grid:
    def __init__(self, width: int, height: int, cells: Iterable[Pos]):
        assert width > 0
        assert height > 0

        self.width = width
        self.height = height
        self.cells = set(cells)

        for cell in self.cells:
            x, y = cell
            assert 0 <= x < self.width
            assert 0 <= y < self.height

    def __len__(self):
        return len(self.cells)

    def neighbors(self, pos: Pos) -> Iterable[Pos]:
        x, y = pos
        return (
            (nx, ny)
            for nx in range(max(x-1, 0), min(x+2, self.width))
            for ny in range(max(y-1, 0), min(y+2, self.height))
            if nx != x or ny != y
        )

    def step(self):
        def rule(lives: bool, adjc: int) -> bool:
            return adjc in (2, 3) if lives else adjc == 3
        adjs = Counter(neighbor for cell in self.cells for neighbor in self.neighbors(cell))
        self.cells = {pos for pos, count in adjs.items() if rule(pos in self.cells, count)}

    def draw(self):
        def c(cx: int, cy: int) -> str:
            return '#' if (cx, cy) in self.cells else '.'
        for y in range(self.height):
            print(''.join(c(x, y) for x in range(self.width)))
        print()

    @classmethod
    def load(cls, fn: str) -> 'Grid':
        width = None
        height = 0
        cells = []

        for y, line in enumerate(open(fn)):
            line = line.strip()
            if width is None:
                width = len(line)
            else:
                assert width == len(line)
            height += 1
            cells.extend((x, y) for x, c in enumerate(line) if c == '#')

        return cls(
            width=width,
            height=height,
            cells=cells
        )


def part_1() -> int:
    g = Grid.load("data/18-input.txt")
    steps = 100
    for _ in range(steps):
        g.step()
    print(f"part 1: after {steps} steps, there are {len(g)} lights on")
    return len(g)


def part_2() -> int:
    g = Grid.load("data/18-input.txt")
    steps = 100
    mx, my = g.width-1, g.height-1
    for _ in range(steps):
        g.step()
        g.cells.update([(0, 0), (mx, 0), (0, my), (mx, my)])
    print(f"part 2: after {steps} steps, there are {len(g)} lights on")
    return len(g)


if __name__ == '__main__':
    part_1()
    part_2()
