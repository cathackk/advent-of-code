"""
Advent of Code 2017
Day 22: Sporifica Virus
https://adventofcode.com/2017/day/22
"""

from enum import Enum
from typing import Iterable
from typing import Iterator
from typing import NamedTuple

from tqdm import tqdm

from common.file import relative_path
from common.heading import Heading
from common.iteration import last
from common.iteration import single_value
from common.rect import Rect


def part_1(grid: 'Grid', bursts: int = 10_000) -> int:
    """
    Diagnostics indicate that the local **grid computing cluster** has been contaminated with the
    **Sporifica Virus**. The grid computing cluster is a seemingly-infinite two-dimensional grid of
    compute nodes. Each node is either **clean** or **infected** by the virus.

    To [prevent overloading](https://en.wikipedia.org/wiki/Morris_worm#The_mistake) the nodes (which
    would render them useless to the virus) or detection by system administrators, exactly one
    **virus carrier** moves through the network, infecting or cleaning nodes as it moves. The virus
    carrier is always located on a single node in the network (the **current node**) and keeps track
    of the **direction** it is facing.

    To avoid detection, the virus carrier works in bursts; in each burst, it **wakes up**, does some
    **work**, and goes back to **sleep**. The following steps are all executed in order one time
    each burst:

      - If the **current node** is **infected**, it turns to its **right**. Otherwise, it turns to
        its **left**. (Turning is done in-place; the **current node** does not change.)
      - If the **current node** is **clean**, it becomes **infected**. Otherwise, it becomes
        **cleaned**. (This is done **after** the node is considered for the purposes of changing
        direction.)
      - The virus carrier moves **forward** one node in the direction it is facing.

    Diagnostics have also provided a **map of the node infection status** (your puzzle input).
    **Clean** nodes are shown as `.`; **infected** nodes are shown as `#`. This map only shows the
    center of the grid; there are many more nodes beyond those shown, but none of them are currently
    infected.

    The virus carrier begins in the middle of the map facing **up**.

    For example, suppose you are given a map like this:

        >>> example_grid = Grid.from_text('''
        ...
        ...     ..#
        ...     #..
        ...     ...
        ...
        ... ''')
        >>> example_grid
        Grid({(1, -1): NodeState.INFECTED, (-1, 0): NodeState.INFECTED})

    Then, the middle of the infinite grid looks like this, with the virus carrier's position marked
    with `[ ]`:

        >>> run = run_virus(example_grid, bursts=70)
        >>> print(next(run))
        · · · · · · ·
        · · · · · · ·
        · · · · # · ·
        · · #[·]· · ·  (↑)
        · · · · · · ·
        · · · · · · ·

    The virus carrier is on a **clean** node, so it turns **left**, infects the node, and moves
    left:

        >>> print(next(run))
        · · · · · · ·
        · · · · · · ·
        · · · · # · ·
        · ·[#]# · · ·  (←)
        · · · · · · ·
        · · · · · · ·

    The virus carrier is on an **infected** node, so it turns **right**, **cleans** the node, and
    moves up:

        >>> print(next(run))
        · · · · · · ·
        · · · · · · ·
        · ·[·]· # · ·  (↑)
        · · · # · · ·
        · · · · · · ·
        · · · · · · ·

    Four times in a row, the virus carrier finds a **clean**, **infects** it, turns **left**, and
    moves forward, ending in the same place and still facing up:

        >>> from itertools import islice
        >>> print(last(islice(run, 4)))
        · · · · · · · ·
        · · · · · · · ·
        · · #[#]· # · ·  (↑)
        · · # # # · · ·
        · · · · · · · ·
        · · · · · · · ·

    Now on the same node as before, it sees an infection, which causes it to turn **right**,
    **clean** the node, and move forward:

        >>> print(state_7 := next(run))
        · · · · · · · ·
        · · · · · · · ·
        · · # ·[·]# · ·  (→)
        · · # # # · · ·
        · · · · · · · ·
        · · · · · · · ·

    After the above actions, a total of `7` bursts of activity had taken place. Of them, `5` bursts
    of activity caused an infection:

        >>> state_7.infections, state_7.bursts
        (5, 7)

    After a total of `70`, the grid looks like this:

        >>> print(state_70 := last(run))
        · · · · · · · · · · ·
        · · · · · · · · · · ·
        · · · · · # # · · · ·
        · · · · # · · # · · ·
        · · · # · · · · # · ·
        · · # · #[·]· · # · ·  (↑)
        · · # · # · · # · · ·
        · · · · · # # · · · ·
        · · · · · · · · · · ·
        · · · · · · · · · · ·

    By this time, `41` bursts of activity caused an infection (though most of those nodes have since
    been cleaned):

        >>> state_70.infections, state_70.bursts
        (41, 70)

    After a total of `10000` bursts of activity, `5587` bursts will have caused an infection.

        >>> part_1(example_grid)
        part 1: after 10000 bursts, 5587 nodes got infected
        5587

    Given your actual map, after `10000` bursts of activity, **how many bursts cause a node to
    become infected**? (Do not count nodes that begin infected.)
    """

    last_state = last(run_virus(grid, bursts))
    print(f"part 1: after {last_state.bursts} bursts, {last_state.infections} nodes got infected")
    return last_state.infections


def part_2(grid: 'Grid', bursts: int = 10_000_000) -> int:
    """
    As you go to remove the virus from the infected nodes, it **evolves** to resist your attempt.

    Now, before it infects a clean node, it will **weaken** it to disable your defenses. If it
    encounters an infected node, it will instead **flag** the node to be cleaned in the future. So:

      - **Clean** nodes become **weakened**.
      - **Weakened** nodes become **infected**.
      - **Infected** nodes become **flagged**.
      - **Flagged** nodes become **clean**.

    Every node is always in exactly one of the above states.

    The virus carrier still functions in a similar way, but now uses the following logic during its
    bursts of action:

      - Decide which way to turn based on the current node:
        - If it is **clean**, it turns **left**.
        - If it is **weakened**, it does **not** turn, and will continue moving in the same dir.
        - If it is **infected**, it turns **right**.
        - If it is **flagged**, it **reverses** direction, and will go back the way it came.
      - Modify the state of the **current node**, as described above.
      - The virus carrier moves **forward** one node in the direction it is facing.

    Start with the same map and still with the virus carrier starting in the middle and facing
    **up**.

    Using the same initial state as the previous example, and drawing **weakened** as `o` and
    **flagged** as `f`, the middle of the infinite grid looks like this, with the virus carrier's
    position again marked with `[ ]`:

        >>> example_grid = Grid.from_file('data/22-example.txt')
        >>> run = run_virus(example_grid, bursts=100, extended_states=True)
        >>> print(next(run))
        · · · · · · ·
        · · · · · · ·
        · · · · # · ·
        · · #[·]· · ·  (↑)
        · · · · · · ·
        · · · · · · ·

    This is the same as before, since no initial nodes are **weakened** or **flagged**. The virus
    carrier is on a clean node, so it still turns left, instead **weakens** the node, and moves
    left:

        >>> print(next(run))
        · · · · · · ·
        · · · · · · ·
        · · · · # · ·
        · ·[#]o · · ·  (←)
        · · · · · · ·
        · · · · · · ·

    The virus carrier is on an infected node, so it still turns right, instead **flags** the node,
    and moves up:

        >>> print(next(run))
        · · · · · · ·
        · · · · · · ·
        · ·[·]· # · ·  (↑)
        · · f o · · ·
        · · · · · · ·
        · · · · · · ·

    This process repeats three more times, ending on the previously-flagged node and facing right:

        >>> from itertools import islice
        >>> print(last(islice(run, 3)))
        · · · · · · · ·
        · · · · · · · ·
        · · o o · # · ·
        · · o[f]o · · ·  (→)
        · · · · · · · ·
        · · · · · · · ·

    Finding a flagged node, it reverses direction and **cleans** the node:

        >>> print(next(run))
        · · · · · · · ·
        · · · · · · · ·
        · · o o · # · ·
        · ·[o]· o · · ·  (←)
        · · · · · · · ·
        · · · · · · · ·

    The **weakened** node becomes infected, and it continues in the same direction:

        >>> print(next(run))
        · · · · · · · · ·
        · · · · · · · · ·
        · · · o o · # · ·
        · ·[·]# · o · · ·  (←)
        · · · · · · · · ·
        · · · · · · · · ·

    Of the first 100 bursts, 26 will result in infection:

        >>> state_100 = last(run)
        >>> state_100.infections, state_100.bursts
        (26, 100)

    Unfortunately, another feature of this evolved virus is speed; of the first `10_000_000` bursts,
    `2511944` will result in infection:

        >>> part_2(example_grid)
        part 2: after 10000000 bursts, 2511944 nodes got infected
        2511944

    Given your actual map, after `10_000_000` bursts of activity, **how many bursts cause a node to
    become infected**? (Do not count nodes that begin infected.)
    """

    last_state = last(run_virus(grid, bursts, extended_states=True))
    print(f"part 2: after {last_state.bursts} bursts, {last_state.infections} nodes got infected")
    return last_state.infections

    # TODO: could be probably optimized by detecting a cycle?


class NodeState(Enum):
    CLEAN = (0, '·')
    WEAKENED = (1, 'o')
    INFECTED = (2, '#')
    FLAGGED = (3, 'f')

    def __init__(self, code: int, char: str):
        self.code = code
        self.char = char

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'

    @classmethod
    def from_code(cls, code: int):
        code %= len(NodeState)
        return next(s for s in cls if s.code == code)

    @classmethod
    def from_char(cls, char: str):
        if char == '.':
            return NodeState.CLEAN
        return next(s for s in cls if s.char == char)

    def __add__(self, other):
        return NodeState.from_code(self.code + int(other))


Pos = tuple[int, int]
Node = tuple[Pos, NodeState]


class Grid:
    def __init__(self, nodes: Iterable[Node]):
        self.nodes = dict(nodes)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.nodes!r})'

    def __iter__(self) -> Iterator[Node]:
        return iter(self.nodes.items())

    def __getitem__(self, pos: Pos) -> NodeState:
        return self.nodes.get(pos, NodeState.CLEAN)

    def __setitem__(self, pos: Pos, state: NodeState):
        if state is NodeState.CLEAN:
            self.nodes.pop(pos)
        else:
            self.nodes[pos] = state

    @classmethod
    def from_text(cls, text: str) -> 'Grid':
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_file(cls, fn: str) -> 'Grid':
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Grid':
        lines_list = [line.strip() for line in lines]
        height = len(lines_list)
        width = single_value(set(len(line) for line in lines_list))

        off_x, off_y = width // 2, height // 2

        return cls((
            ((x - off_x, y - off_y), state)
            for y, line in enumerate(lines_list)
            for x, char in enumerate(line.strip())
            if (state := NodeState.from_char(char)) is not NodeState.CLEAN
        ))


class RunState(NamedTuple):
    pos: Pos
    heading: Heading
    grid: Grid
    bursts: int
    infections: int

    def __str__(self) -> str:
        return format(self)

    def __format__(self, format_spec: str) -> str:
        pad = int(format_spec) if format_spec else 2
        bounds = Rect.with_all(self.grid.nodes.keys()).grow_to_fit([self.pos]).grow_by(pad, pad)

        def char(pos: Pos) -> str:
            x, y = pos
            if pos == self.pos:
                suffix = "]"
            elif (x + 1, y) == self.pos:
                suffix = "["
            else:
                suffix = " "

            return self.grid[pos].char + suffix

        def lines() -> Iterable[str]:
            for y in bounds.range_y():
                status = f" ({self.heading.arrow})" if y == self.pos[1] else ""
                yield ("".join(char((x, y)) for x in bounds.range_x()) + status).rstrip()

        return "\n".join(lines())


def run_virus(
    grid: Grid,
    bursts: int,
    start: Pos = (0, 0),
    start_heading: Heading = Heading.NORTH,
    extended_states: bool = False
) -> Iterator[RunState]:
    grid = Grid(grid)
    pos = start
    heading = start_heading
    infections = 0

    yield RunState(pos, heading, grid, bursts=0, infections=infections)

    for burst in tqdm(
        range(1, bursts + 1), desc="running virus", unit=" bursts", unit_scale=True, delay=0.5
    ):
        match grid[pos]:
            case NodeState.CLEAN:
                heading = heading.left()
                new_state = NodeState.WEAKENED if extended_states else NodeState.INFECTED
            case NodeState.WEAKENED:
                # (no change in heading)
                new_state = NodeState.INFECTED
            case NodeState.INFECTED:
                heading = heading.right()
                new_state = NodeState.FLAGGED if extended_states else NodeState.CLEAN
            case NodeState.FLAGGED:
                heading = heading.opposite()
                new_state = NodeState.CLEAN
            case _:
                raise ValueError(grid[pos])

        if new_state is NodeState.INFECTED:
            infections += 1

        grid[pos] = new_state
        pos = heading.move(pos)
        yield RunState(pos, heading, grid, bursts=burst, infections=infections)


if __name__ == '__main__':
    grid_ = Grid.from_file('data/22-input.txt')
    part_1(grid_)
    part_2(grid_)
