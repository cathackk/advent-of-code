from enum import Enum
from itertools import count
from typing import Generator
from typing import Iterable
from typing import Iterator

from common.heading import Heading
from common.iteration import exhaust
from common.iteration import last
from common.iteration import minmax
from common.logging import ilog
from common.utils import some


class NodeState(Enum):
    CLEAN = (0, '.')
    WEAKENED = (1, 'o')
    INFECTED = (2, '#')
    FLAGGED = (3, 'f')

    def __init__(self, code: int, char: str):
        self.code = code
        self.char = char

    @classmethod
    def from_code(cls, code: int):
        code %= len(NodeState)
        return next(s for s in cls if s.code == code)

    @classmethod
    def from_char(cls, char: str):
        return next(s for s in cls if s.char == char)

    def __add__(self, other):
        return NodeState.from_code(self.code + int(other))


Pos = tuple[int, int]
Node = tuple[Pos, NodeState]


class Grid:
    def __init__(self, nodes: Iterable[Node]):
        self.nodes = dict(nodes)

    def __iter__(self) -> Iterator[Node]:
        for pos, state in self.nodes.items():
            yield pos, state

    def __getitem__(self, pos: Pos) -> NodeState:
        return self.nodes.get(pos, NodeState.CLEAN)

    def __setitem__(self, pos: Pos, state: NodeState):
        if state is NodeState.CLEAN:
            self.nodes.pop(pos)
        else:
            self.nodes[pos] = state

    def range_x(self) -> range:
        min_x, max_x = minmax(x for (x, _), s in self.nodes.items())
        return range(min_x, max_x+1)

    def range_y(self) -> range:
        min_y, max_y = minmax(y for (_, y), s in self.nodes.items())
        return range(min_y, max_y)

    def middle_pos(self) -> Pos:
        r_x = self.range_x()
        r_y = self.range_y()
        return r_x.start + len(r_x) // 2, r_y.start + len(r_y) // 2

    def draw(self):
        print('\n'.join(
            ''.join(self[(x, y)].char for x in self.range_x())
            for y in self.range_y()
        ))

    @classmethod
    def load(cls, fn: str) -> 'Grid':
        return cls((
            ((x, y), NodeState.from_char(c))
            for y, line in enumerate(open(fn))
            for x, c in enumerate(line.strip())
            if c != NodeState.CLEAN.char  # pylint: disable=no-member
        ))


def run_virus(
        grid: Grid,
        start: Pos = None,
        start_heading: Heading = Heading.NORTH,
        steps_limit: int = None
) -> Generator[Pos, None, int]:
    pos = start or grid.middle_pos()
    heading = start_heading
    infected_count = 0

    for step in count(1):
        if grid[pos] == NodeState.INFECTED:
            heading = heading.right()
            grid[pos] = NodeState.CLEAN
        else:
            heading = heading.left()
            grid[pos] = NodeState.INFECTED
            infected_count += 1

        pos = heading.move(pos)
        yield pos

        if steps_limit and step >= steps_limit:
            return infected_count

    # unreachable
    assert False


def run_virus_2(
        grid: Grid,
        start: Pos = None,
        start_heading: Heading = Heading.NORTH,
        steps_limit: int = None
) -> Generator[int, None, None]:
    pos = start or grid.middle_pos()
    heading = start_heading
    infected_count = 0

    for step in count(1):
        state = grid[pos]
        if state == NodeState.CLEAN:
            heading = heading.left()
        elif state == NodeState.WEAKENED:
            infected_count += 1
        elif state == NodeState.INFECTED:
            heading = heading.right()
        elif state == NodeState.FLAGGED:
            heading = heading.opposite()

        grid[pos] = state + 1
        pos = heading.move(pos)
        yield infected_count

        if steps_limit and step >= steps_limit:
            return


def test_virus():
    g_init = Grid([
        ((0, 1), NodeState.INFECTED),
        ((2, 0), NodeState.INFECTED)
    ])
    v_pos = (1, 1)

    assert exhaust(run_virus(Grid(g_init), v_pos, steps_limit=7)) == 5
    assert exhaust(run_virus(Grid(g_init), v_pos, steps_limit=70)) == 41
    assert exhaust(run_virus(Grid(g_init), v_pos, steps_limit=10_000)) == 5587


def test_virus_2():
    g_init = Grid([
        ((0, 1), NodeState.INFECTED),
        ((2, 0), NodeState.INFECTED)
    ])
    v_pos = (1, 1)

    assert exhaust(run_virus_2(Grid(g_init), v_pos, steps_limit=100)) == 26
    assert exhaust(run_virus_2(Grid(g_init), v_pos, steps_limit=10_000_000)) == 2_511_944


def part_1(fn: str, steps: int = 10_000) -> int:
    grid = Grid.load(fn)
    infected_count = exhaust(run_virus(grid, steps_limit=steps))
    # grid.draw()
    print(f"part 1: {infected_count} infected nodes after {steps} bursts")
    return infected_count


def part_2(fn: str, steps: int = 10_000_000) -> int:
    grid = Grid.load(fn)
    infected_count = some(last(ilog(
        run_virus_2(grid, steps_limit=steps),
        every=10_000,
        formatter=lambda step, infected: f"> {step//1_000}K -> {infected} infected"
    )))
    print(f"part 2: {infected_count} infected nodes after {steps} bursts")
    return infected_count

    # TODO: could be probably optimized by detecting a cycle?


if __name__ == '__main__':
    FILENAME = "data/22-input.txt"
    part_1(FILENAME)
    part_2(FILENAME)
