"""
Advent of Code 2022
Day 22: Monkey Map
https://adventofcode.com/2022/day/22
"""

import math
from textwrap import dedent
from typing import Iterable

from common.heading import Heading
from common.iteration import last
from common.iteration import minmax
from common.rect import Rect
from common.text import line_groups
from meta.aoc_tools import data_path


def part_1(board: 'Board', path: 'Path') -> int:
    """
    The monkeys take you on a surprisingly easy trail through the jungle. They're even going in
    roughly the right direction according to your handheld device's Grove Positioning System.

    As you walk, the monkeys explain that the grove is protected by a **force field**. To pass
    through the force field, you have to enter a password; doing so involves tracing a specific
    **path** on a strangely-shaped board.

    At least, you're pretty sure that's what you have to do; the elephants aren't exactly fluent in
    monkey.

    The monkeys give you notes that they took when they last saw the password entered (your puzzle
    input).

    For example:

        >>> b, p = input_from_text('''
        ...             ...#
        ...             .#..
        ...             #...
        ...             ....
        ...     ...#.......#
        ...     ........#...
        ...     ..#....#....
        ...     ..........#.
        ...             ...#....
        ...             .....#..
        ...             .#......
        ...             ......#.
        ...
        ...     10R5L5R10L4R5L5
        ... ''')

    The first half of the monkeys' notes is a **map of the board**. It comprises a set of **open
    tiles** (on which you can move, drawn `.`) and **solid walls** (tiles which you cannot enter,
    drawn `#`).

        >>> b.tiles  # doctest: +ELLIPSIS
        {(9, 1): '.', (10, 1): '.', (11, 1): '.', (12, 1): '#', (9, 2): '.', (10, 2): '#', ...}

    The second half is a description of **the path you must follow**. It consists of alternating
    numbers and letters:

      - A **number** indicates the **number of tiles to move** in the direction you are facing.
        If you run into a wall, you stop moving forward and continue with the next instruction.
      - A **letter** indicates whether to turn 90 degrees **clockwise** (`R`) or **counterclock-
        wise** (`L`). Turning happens in-place; it does not change your current tile.

    So, a path like `10R5` means "go forward 10 tiles, then turn clockwise 90 degrees, then go
    forward 5 tiles".

        >>> p
        [10, 'R', 5, 'L', 5, 'R', 10, 'L', 4, 'R', 5, 'L', 5]

    You begin the path in the leftmost open tile of the top row of tiles. Initially, you are facing
    **to the right** (from the perspective of how the map is drawn).

        >>> b.initial_standing()
        ((9, 1), Heading.EAST)

    If a movement instruction takes you off of the map, you **wrap around** to the other side of
    the board. In other words, if your next tile is off of the board, you should instead look in
    the direction opposite of your current facing as far as you can until you find the opposite
    edge of the board, then reappear there.

    For example, if you are at `A` and facing to the right, the tile in front of you is marked `B`;
    if you are at `C` and facing down, the tile in front of you is marked `D`:

        >>> pos_b, heading_b = b.neighbor(pos_a := (12, 7), Heading.EAST)
        >>> pos_b, heading_b
        ((1, 7), Heading.EAST)
        >>> pos_d, heading_d = b.neighbor(pos_c := (6, 8), Heading.SOUTH)
        >>> pos_d, heading_d
        ((6, 5), Heading.SOUTH)
        >>> b.draw(highlight={pos_a: 'A', pos_b: 'B', pos_c: 'C', pos_d: 'D'})
                ···#
                ·#··
                #···
                ····
        ···#·D·····#
        ········#···
        B·#····#···A
        ·····C····#·
                ···#····
                ·····#··
                ·#······
                ······#·


    It is possible for the next tile (after wrapping around) to be a **wall**; this still counts as
    there being a wall in front of you, and so movement stops before you actually wrap to the other
    side of the board.

    By drawing the last facing you had with an arrow on each tile you visit, the full path taken by
    the above example looks like this:

        >>> b.draw(path=p)
                →→↓#
                ·#↓·
                #·↓·
                ··↓·
        ···#···↓··↓#
        →→→↓···→#·→→
        ··#↓···#····
        ···→→→→↓··#·
                ···#····
                ·····#··
                ·#······
                ······#·

    To finish providing the password to this strange input device, you need to determine numbers for
    your final **row, column, and facing** as your final position appears from the perspective of
    the original map. Rows start from 1 at the top and count downward; columns start from 1 at the
    left and count rightward. (In the above example, row 1, column 1 refers to the empty space with
    no tile on it in the top-left corner.) Facing is `0` for right (→), `1` for down (↓), `2` for
    left (←), and `3` for up (↑). The **final password** is the sum of 1000 times the row, 4 times
    the column, and the facing.

    In the above example, the final row is `6`, the final column is `8`, and the final facing is
    `0`. So, the final password is `1000 * 6 + 4 * 8 + 0`: **`6032`**.

        >>> b.final_standing(p)
        ((8, 6), Heading.EAST)
        >>> final_password(*_)
        6032

    Follow the path given in the monkeys' notes. **What is the final password?**

        >>> part_1(b, p)
        part 1: final position is (8, 6) facing EAST -> password is 6032
        6032
    """

    final_pos, final_heading = board.final_standing(path)
    result = final_password(final_pos, final_heading)

    print(
        f"part 1: final position is {final_pos} facing {final_heading.name} "
        f"-> password is {result}"
    )
    return result


def part_2(board: 'Board', path: 'Path') -> int:
    r"""
    As you reach the force field, you think you hear some Elves in the distance. Perhaps they've
    already arrived?

    You approach the strange **input device**, but it isn't quite what the monkeys drew in their
    notes. Instead, you are met with a large **cube**; each of its six faces is a square of 50x50
    tiles.

    To be fair, the monkeys' map **does** have six 50x50 regions on it. If you were to **carefully
    fold the map**, you should be able to shape it into a cube!

    In the example above, the six (smaller, 4x4) faces of the cube are:

            TTTT
            TTTT
            TTTT
            TTTT
    NNNNWWWWSSSS
    NNNNWWWWSSSS
    NNNNWWWWSSSS
    NNNNWWWWSSSS
            BBBBEEEE
            BBBBEEEE
            BBBBEEEE
            BBBBEEEE

    You still start in the same position and with the same facing as before, but the **wrapping**
    rules are different. Now, if you would walk off the board, you instead **proceed around the
    cube**. From the perspective of the map, this can look a little strange. In the above example,
    if you are at `A` and move to the right, you would arrive at `B` facing down; if you are at
    `C` and move down, you would arrive at `D` facing up:

        >>> b, p = input_from_file(data_path(__file__, 'example.txt'))
        >>> c = Cube.fold(b)
        >>> pos_b, heading_b = c.neighbor(pos_a := (12, 6), Heading.EAST)
        >>> pos_b, heading_b
        ((15, 9), Heading.SOUTH)
        >>> pos_d, heading_d = c.neighbor(pos_c := (11, 12), Heading.SOUTH)
        >>> pos_d, heading_d
        ((2, 8), Heading.NORTH)
        >>> c.transitions[(7, 4), Heading.NORTH]
        ((9, 3), Heading.EAST)
        >>> c.draw(highlight={pos_a: 'A', pos_b: 'B', pos_c: 'C', pos_d: 'D'})
                ···#
                ·#··
                #···
                ····
        ···#·······#
        ········#··A
        ··#····#····
        ·D········#·
                ···#··B·
                ·····#··
                ·#······
                ··C···#·

    Walls still block your path, even if they are on a different face of the cube.

        >>> pos_f, heading_f = c.neighbor(pos_e := (7, 5), Heading.NORTH)
        >>> pos_f, heading_f  # doesn't move
        ((7, 5), Heading.NORTH)

    Using the same method of drawing the **last facing you had** with an arrow on each tile you
    visit, the full path taken by the above example now looks like this:

        >>> c.draw(path=p)
                →→↓#
                ·#↓·
                #·↓·
                ··↓·
        ···#··↑···↓#
        ·→→→→→↑·#·→→
        ·↑#····#····
        ·↑········#·
                ···#··↓·
                ·····#↓·
                ·#↓←←←←·
                ··↓···#·

    The final password is still calculated from your final position and facing from the perspective
    of the map. In this example, the final row is `5`, the final column is `7`, and the final facing
    is `3`, so the final password is `1000 * 5 + 4 * 7 + 3` = **`5031`**.

        >>> c.final_standing(p)
        ((7, 5), Heading.NORTH)
        >>> final_password(*_)
        5031

    Fold the map into a cube, then follow the path given in the monkeys' notes.
    **What is the final password?**

        >>> part_2(b, p)
        part 2: final position is (7, 5) facing NORTH -> password is 5031
        5031
    """

    cube = Cube.fold(board)
    final_pos, final_heading = cube.final_standing(path)
    result = final_password(final_pos, final_heading)

    print(
        f"part 2: final position is {final_pos} facing {final_heading.name} "
        f"-> password is {result}"
    )
    return result


Path = list[int | str]
Pos = tuple[int, int]
Standing = tuple[Pos, Heading]


def add(pos: Pos, heading: Heading, distance: int = 1) -> Pos:
    x, y = pos
    return x + heading.dx * distance, y + heading.dy * distance


class Board:
    def __init__(self, tiles: Iterable[tuple[Pos, str]]):
        self.tiles = dict(tiles)
        self.bounds = Rect.with_all(self.tiles.keys())
        self.transitions = self.create_transitions()

    def create_transitions(self) -> dict[Standing, Standing]:
        transitions: dict[Standing, Standing] = {}
        # assumption: tiles are concave
        for x in self.bounds.range_x():
            min_y, max_y = minmax(y for y in self.bounds.range_y() if (x, y) in self.tiles)
            transitions[(x, min_y - 1), Heading.NORTH] = ((x, max_y), Heading.NORTH)
            transitions[(x, max_y + 1), Heading.SOUTH] = ((x, min_y), Heading.SOUTH)

        for y in self.bounds.range_y():
            min_x, max_x = minmax(x for x in self.bounds.range_x() if (x, y) in self.tiles)
            transitions [(min_x - 1, y), Heading.WEST] = ((max_x, y), Heading.WEST)
            transitions [(max_x + 1, y), Heading.EAST] = ((min_x, y), Heading.EAST)

        return transitions

    def initial_standing(self) -> Standing:
        init_y = self.bounds.top_y
        init_x = next(x for x in self.bounds.range_x() if (x, init_y) in self.tiles)
        assert self.tiles[init_x, init_y] == '.'
        return (init_x, init_y), Heading.EAST

    def neighbor(self, pos: Pos, heading: Heading) -> Standing:
        new_pos, new_heading = add(pos, heading), heading

        if new_pos not in self.tiles:
            new_pos, new_heading = self.transitions[new_pos, new_heading]

        new_tile = self.tiles[new_pos]

        if new_tile == '.':
            # move into space
            return new_pos, new_heading
        elif new_tile == '#':
            # cannot move into wall
            return pos, heading
        else:
            raise ValueError(new_tile)

    def trace_path(self, path: Path) -> Iterable[Standing]:
        pos, heading = self.initial_standing()
        yield pos, heading

        for step in path:
            if step == 'L':
                heading = heading.left()
                yield pos, heading
            elif step == 'R':
                heading = heading.right()
                yield pos, heading
            elif isinstance(step, int):
                for _ in range(step):
                    pos, heading = self.neighbor(pos, heading)
                    yield pos, heading
            else:
                raise ValueError(step)

    def final_standing(self, path: Path) -> Standing:
        return last(self.trace_path(path))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Board':
        return cls(
            tiles=(
                ((x, y), char)
                for y, line in enumerate(lines, start=1)
                for x, char in enumerate(line.rstrip(), start=1)
                if char != ' '
            )
        )

    def draw(self, highlight: dict[Pos, str] = None, path: Path = None) -> None:
        if highlight is None:
            highlight = {}

        if path:
            highlight.update((pos, heading.arrow) for pos, heading in self.trace_path(path))

        def char(pos: Pos) -> str:
            assert highlight is not None
            if pos in highlight:
                return highlight[pos]
            if pos not in self.tiles:
                return ' '
            tile = self.tiles[pos]
            if tile == '.':
                return '·'
            elif tile == '#':
                return '#'
            else:
                raise ValueError(tile)

        for y in self.bounds.range_y():
            print(''.join(char((x, y)) for x in self.bounds.range_x()).rstrip())


Edge = tuple[list[Pos], Heading]


class Cube(Board):
    @classmethod
    def fold(cls, board: Board):
        return cls(board.tiles.items())

    def create_transitions(self) -> dict[Standing, Standing]:
        edges = self.trace_edges()
        edge_pairs = self.pair_edges(edges)

        transitions: dict[Standing, Standing] = {}

        for (poss_1, heading_1), (poss_2, heading_2) in edge_pairs:
            for pos_1, pos_2 in zip(poss_1, reversed(poss_2)):
                transitions[pos_1, heading_1] = (add(pos_2, heading_2, -1), heading_2.opposite())
                transitions[pos_2, heading_2] = (add(pos_1, heading_1, -1), heading_1.opposite())

        return transitions

    def trace_edges(self) -> Iterable[Edge]:
        cube_surface = len(self.tiles)
        assert cube_surface % 6 == 0
        face_area = cube_surface // 6
        edge_len = int(math.sqrt(face_area))
        assert edge_len * edge_len == face_area

        init_pos, init_heading = self.initial_standing()
        init_pos = add(init_pos, init_heading.left())

        pos, heading = init_pos, init_heading
        edges_count = 0

        while True:
            edge_poss = [add(pos, heading, dist) for dist in range(edge_len)]
            outside, inside = heading.left(), heading.right()
            assert all(pos not in self.tiles for pos in edge_poss)
            assert all((x + inside.dx, y + inside.dy) in self.tiles for x, y in edge_poss)
            yield edge_poss, outside
            edges_count += 1

            pos = add(pos, heading, edge_len)
            if pos in self.tiles:
                # inner curve -> one step back and turn outside
                pos = add(pos, heading, -1)
                heading = outside
            elif (pos_inner := add(pos, inside)) not in self.tiles:
                # outer curve -> one step inside and turn inside
                pos = pos_inner
                heading = inside
            else:
                # straight line
                pass

            if pos == init_pos:
                assert heading == init_heading
                # number of outer edges in each cube network is 14
                assert edges_count == 14
                return

    def pair_edges(self, edges: Iterable[Edge]) -> Iterable[tuple[Edge, Edge]]:
        edges = list(edges)

        # TODO: compute properly!
        edge_len = len(edges[0][0])
        if edge_len == 4:
            # example only
            assert [heading for poss, heading in edges] == [
                Heading.NORTH, Heading.EAST, Heading.EAST, Heading.NORTH,
                Heading.EAST, Heading.SOUTH, Heading.SOUTH, Heading.WEST,
                Heading.SOUTH, Heading.SOUTH, Heading.WEST, Heading.NORTH,
                Heading.NORTH, Heading.WEST,
            ]
            pairings = [(0, 11), (1, 4), (2, 3), (5, 10), (6, 9), (7, 8), (12, 13)]
        elif edge_len == 50:
            # real input only
            assert [heading for _, heading in edges] == [
                Heading.NORTH, Heading.NORTH, Heading.EAST, Heading.SOUTH,
                Heading.EAST, Heading.EAST, Heading.SOUTH, Heading.EAST,
                Heading.SOUTH, Heading.WEST, Heading.WEST, Heading.NORTH,
                Heading.WEST, Heading.WEST,
            ]
            pairings = [(0, 9), (1, 8), (2, 5), (3, 4), (6, 7), (10, 13), (11, 12)]
        else:
            raise ValueError(len(edges[0]))

        return ((edges[a], edges[b]) for a, b in pairings)


def final_password(final_pos: Pos, final_heading: Heading) -> int:
    h_val = {Heading.EAST: 0, Heading.SOUTH: 1, Heading.WEST: 2, Heading.NORTH: 3}[final_heading]
    (x, y) = final_pos
    return 1000 * y + 4 * x + h_val


def input_from_file(fn: str) -> tuple[Board, Path]:
    return input_from_lines(open(fn))


def input_from_text(text: str) -> tuple[Board, Path]:
    return input_from_lines(dedent(text.lstrip('\n')).splitlines())


def input_from_lines(lines: Iterable[str]) -> tuple[Board, Path]:
    board_lines, (path_line,) = line_groups(lines, lstrip=False)
    return Board.from_lines(board_lines), list(path_from_line(path_line))


def path_from_line(line: str) -> Iterable[int | str]:
    # '10R5L5R10L4R5L5' -> 10, 'R', 5, 'L', ...
    for index_1, split_1 in enumerate(line.split('L')):
        if index_1:
            yield 'L'
        for index_2, split_2 in enumerate(split_1.split('R')):
            if index_2:
                yield 'R'
            yield int(split_2)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    board, path = input_from_file(input_path)
    result_1 = part_1(board, path)
    result_2 = part_2(board, path)
    return result_1, result_2


if __name__ == '__main__':
    main()
