from collections import Counter
from typing import Iterable

from common.utils import minmax


Pos = tuple[int, int]


class Grid:
    def __init__(self, width: int, height: int, bugs: Iterable[Pos]):
        assert width > 0
        assert height > 0
        self.width = width
        self.height = height
        self.bugs = set(bugs)

        for x, y in self.bugs:
            assert 0 <= x < self.width
            assert 0 <= y < self.height

    def neighbors(self, pos: Pos) -> Iterable[Pos]:
        x, y = pos
        if x > 0:
            yield x-1, y
        if x < self.width-1:
            yield x+1, y
        if y > 0:
            yield x, y-1
        if y < self.height-1:
            yield x, y+1

    def step(self) -> int:
        adjs = Counter(
            neighbor
            for bug in self.bugs
            for neighbor in self.neighbors(bug)
        )
        self.bugs = {
            pos
            for pos, count in adjs.items()
            if (pos in self.bugs and count == 1)
            or (pos not in self.bugs and count in (1, 2))
        }
        return int(self)

    def run_until_repeat(self, draw: bool = False) -> int:
        states = {int(self)}

        def do_draw():
            if draw:
                self.draw()

        while True:
            do_draw()
            state = self.step()
            if state not in states:
                states.add(state)
            else:
                do_draw()
                return state

    def __int__(self):
        return sum(
            2 ** (y * self.width + x)
            for x, y in self.bugs
        )

    def __len__(self):
        return len(self.bugs)

    def draw(self):
        for y in range(self.height):
            print(''.join('#' if (x, y) in self.bugs else '.' for x in range(self.width)))
        print()

    @classmethod
    def load(cls, fn: str):
        width = None
        height = 0
        bugs = []

        for y, line in enumerate(open(fn)):
            line = line.strip()
            assert width is None or width == len(line)
            width = len(line)
            bugs.extend((x, y) for x, c in enumerate(line) if c == '#')
            height += 1

        return cls(
            width=width,
            height=height,
            bugs=bugs
        )


def part_1() -> int:
    g = Grid.load("data/24-input.txt")
    result = g.run_until_repeat(draw=True)
    print(f"part 1: biodiversity of first repeating state is {result}")
    return result


Pos3 = tuple[int, int, int]


class HyperGrid:
    def __init__(self, width: int, height: int, bugs: Iterable[Pos3]):
        assert width >= 3
        assert width % 2 == 1
        assert height >= 3
        assert height % 2 == 1

        self.width = width
        self.height = height
        self.bugs = set(bugs)

        self.center = (self.width // 2, self.height // 2)

        for x, y, z in self.bugs:
            assert 0 <= x < self.width
            assert 0 <= y < self.height
            assert (x, y) != self.center

    def neighbors(self, pos: Pos3) -> Iterable[Pos3]:
        x, y, z = pos

        # center tile has no neighbors
        assert (x, y) != self.center

        xc, yc = self.center
        xm, ym = self.width-1, self.height-1

        # normal X (without center)
        if x > 0:
            if (x-1, y) != self.center:
                yield (x-1, y, z)
        if x < xm:
            if (x+1, y) != self.center:
                yield (x+1, y, z)

        # normal Y (without center)
        if y > 0:
            if (x, y-1) != self.center:
                yield (x, y-1, z)
        if y < ym:
            if (x, y+1) != self.center:
                yield (x, y+1, z)

        # hyper X
        if x == 0:
            # hyper X out left
            yield (xc-1, yc, z-1)
        elif x == xm:
            # hyper X out right
            yield (xc+1, yc, z-1)
        elif x == xc:
            if y == yc-1:
                # hyper X in from up
                yield from ((ix, 0, z+1) for ix in range(self.width))
            elif y == yc+1:
                # hyper X in from down
                yield from ((ix, ym, z+1) for ix in range(self.width))

        # hyper Y
        if y == 0:
            # hyper Y out up
            yield (xc, yc-1, z-1)
        elif y == ym:
            # hyper Y out down
            yield (xc, yc+1, z-1)
        elif y == yc:
            if x == xc-1:
                # hyper Y in from right
                yield from ((0, iy, z+1) for iy in range(self.height))
            elif x == xc+1:
                # hyper Y in from left
                yield from ((xm, iy, z+1) for iy in range(self.height))

    def step(self) -> int:
        adjs = Counter(
            neighbor
            for bug in self.bugs
            for neighbor in self.neighbors(bug)
        )
        self.bugs = {
            pos
            for pos, count in adjs.items()
            if (pos in self.bugs and count == 1)
            or (pos not in self.bugs and count in (1, 2))
        }
        return len(self)

    def __len__(self):
        return len(self.bugs)

    def draw(self):
        if not self.bugs:
            print("all dead :(")
            return

        def c(x: int, y: int, z: int) -> str:
            pos = (x, y, z)
            if (x, y) == self.center:
                assert pos not in self.bugs
                return '?'
            elif pos in self.bugs:
                return '#'
            else:
                return '.'

        min_z, max_z = minmax(z for x, y, z in self.bugs)
        for z in range(min_z, max_z+1):
            print(f"Depth {z}:")
            for y in range(self.height):
                print(''.join(c(x, y, z) for x in range(self.width)))
            print()

    @classmethod
    def load(cls, fn: str):
        width = None
        height = 0
        bugs: list[Pos3] = []

        for y, line in enumerate(open(fn)):
            line = line.strip()
            assert width is None or width == len(line)
            width = len(line)
            bugs.extend((x, y, 0) for x, c in enumerate(line) if c == '#')
            height += 1

        return cls(
            width=width,
            height=height,
            bugs=bugs
        )


def test_hyper_neighbors():
    hg = HyperGrid(5, 5, [])
    # L R U D
    assert set(hg.neighbors((3, 3, 0))) == {(2, 3, 0), (4, 3, 0), (3, 2, 0), (3, 4, 0)}
    assert set(hg.neighbors((1, 1, 0))) == {(0, 1, 0), (2, 1, 0), (1, 0, 0), (1, 2, 0)}
    assert set(hg.neighbors((3, 0, 0))) == {(2, 0, 0), (4, 0, 0), (2, 1, -1), (3, 1, 0)}
    assert set(hg.neighbors((4, 0, 0))) == {(3, 0, 0), (3, 2, -1), (2, 1, -1), (4, 1, 0)}
    assert set(hg.neighbors((3, 2, 0))) == {
        (4, 0, 1), (4, 1, 1), (4, 2, 1), (4, 3, 1), (4, 4, 1),
        (4, 2, 0),
        (3, 1, 0),
        (3, 3, 0)
    }


def test_hyper_example():
    hg = HyperGrid.load("data/24-example.txt")
    for _ in range(10):
        hg.step()
    hg.draw()
    assert len(hg) == 99


def part_2() -> int:
    hg = HyperGrid.load("data/24-input.txt")
    for _ in range(200):
        hg.step()
    hg.draw()
    result = len(hg)
    print(f"part 2: after 200 minutes, there are {result} bugs")
    return result


if __name__ == '__main__':
    part_1()
    part_2()
