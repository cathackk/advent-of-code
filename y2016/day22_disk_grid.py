"""
Advent of Code 2016
Day 22: Grid Computing
https://adventofcode.com/2016/day/22
"""

from typing import Iterable, Self

from common.graph import shortest_path
from common.iteration import single_value
from common.rect import Rect
from common.text import parse_line
from meta.aoc_tools import data_path


def part_1(grid: 'Grid') -> int:
    """
    You gain access to a massive storage cluster arranged in a grid; each storage node is only
    connected to the four nodes directly adjacent to it (three if the node is on an edge, two if
    it's in a corner).

    You can directly access data **only** on node `/dev/grid/node-x0-y0`, but you can perform some
    limited actions on the other nodes:

      - You can get the disk usage of all nodes (via `df`). The result of doing this is in your
        puzzle input.

        >>> (example_grid := Grid.from_text('''
        ...     Filesystem            Size  Used  Avail  Use%
        ...     /dev/grid/node-x0-y0   10T    8T     2T   80%
        ...     /dev/grid/node-x0-y1   11T    6T     5T   54%
        ...     /dev/grid/node-x0-y2   32T   28T     4T   87%
        ...     /dev/grid/node-x1-y0    9T    7T     2T   77%
        ...     /dev/grid/node-x1-y1    8T    0T     8T    0%
        ...     /dev/grid/node-x1-y2   11T    7T     4T   63%
        ...     /dev/grid/node-x2-y0   10T    6T     4T   60%
        ...     /dev/grid/node-x2-y1    9T    8T     1T   88%
        ...     /dev/grid/node-x2-y2    9T    6T     3T   66%
        ... '''))  # doctest: +NORMALIZE_WHITESPACE
        Grid([Node(pos=(0, 0), size=10, used=8),
         Node(pos=(0, 1), size=11, used=6),
         Node(pos=(0, 2), size=32, used=28),
         Node(pos=(1, 0), size=9, used=7),
         Node(pos=(1, 1), size=8, used=0),
         Node(pos=(1, 2), size=11, used=7),
         Node(pos=(2, 0), size=10, used=6),
         Node(pos=(2, 1), size=9, used=8),
         Node(pos=(2, 2), size=9, used=6)])

      - You can instruct a node to **move** (not copy) **all** of its data to an adjacent node
        (if the destination node has enough space to receive the data). The sending node is left
        empty after this operation.

    Nodes are named by their position: the node named `node-x1-y1` is adjacent to nodes:

        >>> example_grid[1, 1]
        Node(pos=(1, 1), size=8, used=0)
        >>> list(example_grid.adjacent((1, 1)))  # doctest: +ELLIPSIS
        [Node(pos=(0, 1), ...), Node(pos=(2, 1), ...), Node(pos=(1, 0), ...), Node(pos=(1, 2), ...)]

    Before you begin, you need to understand the arrangement of data on these nodes. Even though you
    can only move data between directly connected nodes, you're going to need to rearrange a lot of
    the data to get access to the data you need. Therefore, you need to work out how you might be
    able to shift data around.

    To do this, you'd like to count the number of viable pairs of nodes. A **viable pair** is any
    two nodes (A,B), **regardless of whether they are directly connected**, such that:

      - Node A is **not** empty (its `Used` is not zero).
      - Nodes A and B are **not the same** node.
      - The data on node A (its `Used`) would fit on node B (its `Avail`).

        >>> list(example_grid.viable_pairs())  # doctest: +NORMALIZE_WHITESPACE
        [(Node(pos=(0, 0), size=10, used=8),  Node(pos=(1, 1), size=8, used=0)),
         (Node(pos=(0, 1), size=11, used=6),  Node(pos=(1, 1), size=8, used=0)),
         (Node(pos=(1, 0), size=9,  used=7),  Node(pos=(1, 1), size=8, used=0)),
         (Node(pos=(1, 2), size=11, used=7),  Node(pos=(1, 1), size=8, used=0)),
         (Node(pos=(2, 0), size=10, used=6),  Node(pos=(1, 1), size=8, used=0)),
         (Node(pos=(2, 1), size=9,  used=8),  Node(pos=(1, 1), size=8, used=0)),
         (Node(pos=(2, 2), size=9,  used=6),  Node(pos=(1, 1), size=8, used=0))]


    How many viable pairs of nodes are there?

        >>> part_1(example_grid)
        part 1: there are 7 viable pairs
        7
    """

    result = sum(1 for _ in grid.viable_pairs())
    print(f"part 1: there are {result} viable pairs")
    return result


def part_2(grid: 'Grid'):
    """
    Now that you have a better understanding of the grid, it's time to get to work.

    Your goal is to gain access to the data which begins in the node with `y=0` and the highest `x`
    (that is, the node in the top-right corner).

    For example, suppose you have the following grid:

        >>> example_grid = Grid.from_file(data_path(__file__, 'example.txt'))
        >>> print(example_grid)
        Filesystem            Size  Used  Avail  Use%
        /dev/grid/node-x0-y0   10T    8T     2T   80%
        /dev/grid/node-x0-y1   11T    6T     5T   54%
        /dev/grid/node-x0-y2   32T   28T     4T   87%
        /dev/grid/node-x1-y0    9T    7T     2T   77%
        /dev/grid/node-x1-y1    8T    0T     8T    0%
        /dev/grid/node-x1-y2   11T    7T     4T   63%
        /dev/grid/node-x2-y0   10T    6T     4T   60%
        /dev/grid/node-x2-y1    9T    8T     1T   88%
        /dev/grid/node-x2-y2    9T    6T     3T   66%

    In this example, you have a storage grid 3 nodes wide and 3 nodes tall:

        >>> example_grid.width, example_grid.height
        (3, 3)
        >>> len(example_grid)
        9

    The node you can access directly, `node-x0-y0`, is almost full:

        >>> example_grid.accessible_node
        Node(pos=(0, 0), size=10, used=8)

    The node containing the data you want to access, `node-x2-y0` (because it has `y=0` and the
    highest `x` value), contains `6` terabytes of data - enough to fit on your node, if only you
    could make enough space to move it there.

        >>> example_grid.target_data_node
        Node(pos=(2, 0), size=10, used=6)

    Fortunately, `node-x1-y1` looks like it has enough free space to enable you to move some of this
    data around. In fact, it seems like all of the nodes have enough space to hold any node's data
    (except `node-x0-y2`, which is much larger, very full, and not moving any time soon). So,
    initially, the grid's capacities and connections look like this:

        >>> example_grid.print_sizes_schema()
        ( 8T/10T) --   7T/ 9T  -- [ 6T/10T]
            |            |            |
          6T/11T  --   0T/ 8T  --   8T/ 9T
            |            |            |
         28T/32T  --   7T/11T  --   6T/ 9T

    The node you can access directly is in parentheses; the data you want starts in the node marked
    by square brackets.

    In this example, most of the nodes are interchangable: they're full enough that no other node's
    data would fit, but small enough that their data could be moved around. Let's draw these nodes
    as `.`. The exceptions are the empty node, which we'll draw as `_`, and the very large, very
    full node, which we'll draw as `#`. Let's also draw the goal data as `G`. Then, it looks like
    this:

        >>> example_grid.print_data_schema()
        (.) .  G
         .  _  .
         #  .  .

    The goal is to move the data in the top right, `G`, to the node in parentheses. To do this, we
    can issue some commands to the grid and rearrange the data:

    Move data from `node-x1-y0` to `node-x1-y1`, leaving node `node-x1-y0` empty:

        >>> (grid_1 := example_grid.move_data(source=(1, 0), target=(1, 1))).print_data_schema()
        (.) _  G
         .  .  .
         #  .  .

    Move the goal data from `node-x2-y0` to `node-x1-y0`:

        >>> (grid_2 := grid_1.move_data((2, 0), (1, 0))).print_data_schema()
        (.) G  _
         .  .  .
         #  .  .

    At this point, we're quite close. However, we have no deletion command, so we have to move some
    more data around. So, next, we move the data from `node-x2-y1` to `node-x2-y0`:

        >>> (grid_3 := grid_2.move_data((2, 1), (2, 0))).print_data_schema()
        (.) G  .
         .  .  _
         #  .  .

    Move the data from `node-x1-y1` to `node-x2-y1`:

        >>> (grid_4 := grid_3.move_data((1, 1), (2, 1))).print_data_schema()
        (.) G  .
         .  _  .
         #  .  .

    Move the data from `node-x0-y1` to `node-x1-y1`:

        >>> (grid_5 := grid_4.move_data((0, 1), (1, 1))).print_data_schema()
        (.) G  .
         _  .  .
         #  .  .

    Next, we can free up space on our node by moving the data from `node-x0-y0` to `node-x0-y1`:

        >>> (grid_6 := grid_5.move_data((0, 0), (0, 1))).print_data_schema()
        (_) G  .
         .  .  .
         #  .  .

    Finally, we can access the goal data by moving the it from `node-x1-y0` to `node-x0-y0`:

        >>> (grid_7 := grid_6.move_data((1, 0), (0, 0))).print_data_schema()
        (G) _  .
         .  .  .
         #  .  .

    So, after `7` steps, we've accessed the data we want. Unfortunately, each of these moves takes
    time, and we need to be efficient:

    **What is the fewest number of steps** required to move your goal data to `node-x0-y0`?

        >>> part_2(example_grid)
        part 2: takes 7 steps to reach the data in node-x2-y0
        7
    """

    if len(grid.nodes) <= 20:
        steps, _ = access_target_data(grid)
    else:
        steps = access_target_data_shortcut(grid)

    print(f"part 2: takes {steps} steps to reach the data in {grid.target_data_node.name}")
    return steps


Pos = tuple[int, int]


class Node:
    def __init__(self, pos: Pos, size: int, used: int):
        assert size > 0
        assert size >= used

        self.pos = pos
        self.size = size
        self.used = used

    def __repr__(self):
        return f'{type(self).__name__}(pos={self.pos!r}, size={self.size!r}, used={self.used!r})'

    def __str__(self):
        return self.name

    @classmethod
    def from_str(cls, line: str) -> Self:
        # '/dev/grid/node-x0-y2  85T  73T  12T  85%'
        name, size_str, used_str, avail_str, _ = [p for p in line.strip().split(' ') if p]
        x, y = parse_line(name, "/dev/grid/node-x$-y$")

        pos = (int(x), int(y))
        size = int(size_str.rstrip('T'))
        used = int(used_str.rstrip('T'))
        avail = int(avail_str.rstrip('T'))
        assert size == used + avail

        return cls(pos, size, used)

    @property
    def name(self) -> str:
        return f'node-x{self.x}-y{self.y}'

    @property
    def path(self) -> str:
        return f'/dev/grid/{self.name}'

    @property
    def available(self) -> int:
        return self.size - self.used

    @property
    def used_perc(self) -> int:
        return int(100 * self.used / self.size)

    @property
    def x(self) -> int:
        return self.pos[0]

    @property
    def y(self) -> int:
        return self.pos[1]

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.pos == other.pos

    def __hash__(self):
        return hash(self.pos)


class Grid:
    def __init__(self, nodes: Iterable[Node], target_data_pos: Pos = None):
        self.nodes = {node.pos: node for node in nodes}
        self.rect = Rect.with_all(self.nodes.keys())
        assert self.rect.area == len(self.nodes)

        if target_data_pos:
            assert target_data_pos in self.rect
            self.target_data_pos = target_data_pos
        else:
            self.target_data_pos = self.rect.top_right

        self.empty_node_pos = single_value(
            pos
            for pos, node in self.nodes.items()
            if node.used == 0
        )

        self._key = self._create_hash_key()

    def __repr__(self) -> str:
        return f'{type(self).__name__}({list(self.nodes.values())!r})'

    def _create_hash_key(self) -> tuple:
        # only the shape, location of target data and location of empty node matter
        if self.target_data_pos == self.accessible_node.pos:
            # and if target data is at (0,0), empty node matters no more!
            empty_node_pos = (-1, -1)
        else:
            empty_node_pos = self.empty_node_pos

        return (self.width, self.height, self.target_data_pos, empty_node_pos)

    def __hash__(self) -> int:
        return hash(self._key)

    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and self._key == other._key

    @property
    def width(self) -> int:
        return self.rect.width

    @property
    def height(self) -> int:
        return self.rect.height

    def __len__(self) -> int:
        return len(self.nodes)

    def __getitem__(self, pos: Pos) -> Node:
        return self.nodes[pos]

    @property
    def accessible_node_pos(self) -> Pos:
        return self.rect.top_left

    @property
    def accessible_node(self) -> Node:
        return self[self.accessible_node_pos]

    @property
    def target_data_node(self) -> Node:
        return self[self.target_data_pos]

    @property
    def empty_node(self) -> Node:
        return self[self.empty_node_pos]

    def adjacent(self, node: Node | Pos) -> Iterable[Node]:
        if isinstance(node, Node):
            pos = node.pos
        elif isinstance(node, tuple):
            pos = node
        else:
            raise TypeError(type(node))

        x, y = pos
        for dx, dy in ((-1, 0), (+1, 0), (0, -1), (0, +1)):
            try:
                yield self[x + dx, y + dy]
            except KeyError:
                pass

    def viable_pairs(self) -> Iterable[tuple[Node, Node]]:
        return (
            (node_a, node_b)
            for node_a in self.nodes.values()
            for node_b in self.nodes.values()
            # Node A is **not** empty (its `Used` is not zero).
            if node_a.used > 0
            # Nodes A and B are **not the same** node.
            if node_a != node_b
            # The data on node A (its `Used`) would fit on node B (its `Avail`).
            if node_a.used <= node_b.available
        )

    def move_data(self, source: Pos | Node, target: Pos | Node) -> Self:
        source_node: Node = source if isinstance(source, Node) else self[source]
        target_node: Node = target if isinstance(target, Node) else self[target]

        assert source_node is self[source_node.pos], f"{source_node!r} != {self[source_node.pos]!r}"
        assert target_node is self[target_node.pos]

        assert source_node != target_node
        assert target_node.used == 0  # target is empty
        assert source_node.used > 0  # source is not empty
        assert source_node.used <= target_node.size  # target can fit the data
        assert target_node in self.adjacent(source_node)  # nodes are connected

        def new_used(node: Node) -> int:
            if node == source_node:
                assert node.used > 0
                return 0  # data moved out of source
            elif node == target_node:
                assert node.used == 0, f"{node!r} == {target_node!r}"
                return source_node.used  # data moved from source into target
            else:
                return node.used

        new_nodes = (
            type(node)(node.pos, size=node.size, used=new_used(node))
            for node in self.nodes.values()
        )

        if self.target_data_pos == source_node.pos:
            new_data_pos = target_node.pos
        else:
            new_data_pos = self.target_data_pos

        return type(self)(new_nodes, new_data_pos)

    def __str__(self) -> str:
        header = "Filesystem            Size  Used  Avail  Use%"
        lines = (
            f'{node.path} {node.size:4}T {node.used:4}T {node.available:5}T {node.used_perc:4}%'
            for node in self.nodes.values()
        )
        return header + "\n" + "\n".join(lines)

    def print_sizes_schema(self) -> None:
        def node_str(node: Node) -> str:
            if node == self.accessible_node:
                p_l, p_r = "(", ")"
            elif node == self.target_data_node:
                p_l, p_r = "[", "]"
            else:
                p_l, p_r = " ", " "

            return f"{p_l}{node.used:2}T/{node.size:2}T{p_r}"

        lines_sep = "        ".join("    |" for _ in range(self.width))

        for y in self.rect.range_y():
            if y > 0:
                print(lines_sep)
            print(" -- ".join(node_str(self[x, y]) for x in self.rect.range_x()).rstrip())

    def print_data_schema(self) -> None:
        def is_large_and_full(node: Node) -> bool:
            return any(node.used > node_adj.size for node_adj in self.adjacent(node))

        def node_str(node: Node) -> str:
            if node == self.accessible_node:
                p_l, p_r = "(", ")"
            else:
                p_l, p_r = " ", " "

            if not node.used:
                char = "_"
            elif node == self.target_data_node:
                char = "G"
            elif is_large_and_full(node):
                char = "#"
            else:
                char = "."

            return p_l + char + p_r

        for y in self.rect.range_y():
            print("".join(node_str(self[x, y]) for x in self.rect.range_x()).rstrip())

    @classmethod
    def from_file(cls, fn: str) -> Self:
        return cls.from_lines(open(fn))

    @classmethod
    def from_text(cls, text: str) -> Self:
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        lines = iter(lines)
        assert "Filesystem" in next(lines)  # header
        return cls(Node.from_str(line) for line in lines)


Move = tuple[Pos, Pos]


def access_target_data(grid: Grid) -> tuple[int, list[Move]]:
    # TODO: optimize!
    def possible_moves(current_grid: Grid) -> Iterable[tuple[Grid, Move, int]]:
        target = current_grid.empty_node
        return (
            (current_grid.move_data(source, target), (source.pos, target.pos), 1)
            for source in current_grid.adjacent(target)
            if 0 < source.used <= target.size
        )

    return shortest_path(
        start=grid,
        target=Grid(
            nodes=grid.nodes.values(),  # whatever
            target_data_pos=grid.accessible_node.pos
        ),
        edges=possible_moves,
    )


def access_target_data_shortcut(grid: Grid) -> int:
    t_x = max(x for x, y in grid.nodes if y == 0)
    empty_node = next(node for node in grid.nodes.values() if node.used == 0)
    e_x, e_y = empty_node.pos
    return (
        # move empty to (0, ey) because of barrier with hole at x=0,
        e_y
        # then move empty to (tx-1, 0),
        + e_x + (t_x - 1)
        # then move tx left by shuffling to x=1
        + 5 * (t_x - 1)
        # then one final step
        + 1
    )


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    grid = Grid.from_file(input_path)
    # grid_.print_data_schema()
    result_1 = part_1(grid)
    result_2 = part_2(grid)
    return result_1, result_2


if __name__ == '__main__':
    main()
