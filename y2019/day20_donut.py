"""
Advent of Code 2019
Day 20: Donut Maze
https://adventofcode.com/2019/day/20
"""

from enum import Enum
from itertools import groupby
from typing import Iterable, Self

from common.graph import shortest_path
from common.iteration import dgroupby_pairs
from common.rect import Rect
from meta.aoc_tools import data_path


def part_1(maze: 'Maze') -> int:
    """
    You notice a strange pattern on the surface of Pluto and land nearby to get a closer look. Upon
    closer inspection, you realize you've come across one of the famous space-warping mazes of the
    long-lost Pluto civilization!

    Because there isn't much space on Pluto, the civilization that used to live here thrived by
    inventing a method for folding spacetime. Although the technology is no longer understood, mazes
    like this one provide a small glimpse into the daily life of an ancient Pluto citizen.

    This maze is shaped like a donut. Portals along the inner and outer edge of the donut can
    instantly teleport you from one side to the other. For example:


        >>> example_1 = Maze.from_text('''
        ...              A
        ...              A
        ...       #######.#########
        ...       #######.........#
        ...       #######.#######.#
        ...       #######.#######.#
        ...       #######.#######.#
        ...       #####  B    ###.#
        ...     BC...##  C    ###.#
        ...       ##.##       ###.#
        ...       ##...DE  F  ###.#
        ...       #####    G  ###.#
        ...       #########.#####.#
        ...     DE..#######...###.#
        ...       #.#########.###.#
        ...     FG..#########.....#
        ...       ###########.#####
        ...                  Z
        ...                  Z
        ... ''')
        >>> example_1.labels  # doctest: +NORMALIZE_WHITESPACE
        {(7, 0): 'AA', (0, 6): 'BC', (7, 4): 'BC', (4, 8): 'DE', (9, 10): 'FG', (0, 11): 'DE',
         (0, 13): 'FG', (11, 14): 'ZZ'}
        >>> example_1.start
        (7, 0)
        >>> example_1.target
        (11, 14)
        >>> example_1.portals  # doctest: +NORMALIZE_WHITESPACE
        {(0, 6): ((7, 4), -1), (0, 11): ((4, 8), -1), (0, 13): ((9, 10), -1),
         (4, 8): ((0, 11), 1), (7, 4): ((0, 6), 1), (9, 10): ((0, 13), 1)}

    This map of the maze shows solid walls (`#`) and open passages (`.`). Every maze on Pluto has
    a start (the open tile next to `AA`) and an end (the open tile next to `ZZ`). Mazes on Pluto
    also have portals; this maze has three pairs of portals: `BC`, `DE`, and `FG`. When on an open
    tile next to one of these labels, a single step can take you to the other tile with the same
    label. (You can only walk on `.` tiles; labels and empty space are not traversable.)

    One path through the maze doesn't require any portals. Starting at `AA`, you could go down 1,
    right 8, down 12, left 4, and down 1 to reach `ZZ`, a total of `26` steps.

    However, there is a shorter path: You could walk from `AA` to the inner `BC` portal (4 steps),
    warp to the outer `BC` portal (1 step), walk to the inner `DE` (6 steps), warp to the outer `DE`
    (1 step), walk to the outer `FG` (4 steps), warp to the inner `FG` (1 step), and finally walk to
    `ZZ` (6 steps). In total, this is only **23** steps.

        >>> length_1, path_1 = solve_maze(example_1)
        >>> length_1
        23
        >>> path_1  # doctest: +NORMALIZE_WHITESPACE
        [(SOUTH, 4), (WARP, 1),
         (EAST, 2), (SOUTH, 2), (EAST, 2), (WARP, 1),
         (EAST, 1), (SOUTH, 2), (WEST, 1), (WARP, 1),
         (SOUTH, 1), (EAST, 2), (SOUTH, 3)]

    Here is a larger example:

        >>> example_2 = Maze.from_text('''
        ...                       A
        ...                       A
        ...      #################.#############
        ...      #.#...#...................#.#.#
        ...      #.#.#.###.###.###.#########.#.#
        ...      #.#.#.......#...#.....#.#.#...#
        ...      #.#########.###.#####.#.#.###.#
        ...      #.............#.#.....#.......#
        ...      ###.###########.###.#####.#.#.#
        ...      #.....#        A   C    #.#.#.#
        ...      #######        S   P    #####.#
        ...      #.#...#                 #......VT
        ...      #.#.#.#                 #.#####
        ...      #...#.#               YN....#.#
        ...      #.###.#                 #####.#
        ...    DI....#.#                 #.....#
        ...      #####.#                 #.###.#
        ...    ZZ......#               QG....#..AS
        ...      ###.###                 #######
        ...    JO..#.#.#                 #.....#
        ...      #.#.#.#                 ###.#.#
        ...      #...#..DI             BU....#..LF
        ...      #####.#                 #.#####
        ...    YN......#               VT..#....QG
        ...      #.###.#                 #.###.#
        ...      #.#...#                 #.....#
        ...      ###.###    J L     J    #.#.###
        ...      #.....#    O F     P    #.#...#
        ...      #.###.#####.#.#####.#####.###.#
        ...      #...#.#.#...#.....#.....#.#...#
        ...      #.#####.###.###.#.#.#########.#
        ...      #...#.#.....#...#.#.#.#.....#.#
        ...      #.###.#####.###.###.#.#.#######
        ...      #.#.........#...#.............#
        ...      #########.###.###.#############
        ...               B   J   C
        ...               U   P   P
        ... ''')

    Here, `AA` has no direct path to `ZZ`, but it does connect to `AS` and `CP`. By passing through
    `AS`, `QG`, `BU`, and `JO`, you can reach `ZZ` in **58** steps.

        >>> length_2, path_2 = solve_maze(example_2)
        >>> length_2
        58
        >>> path_2  # doctest: +NORMALIZE_WHITESPACE
        [(SOUTH, 1), (WEST, 4), (SOUTH, 2), (EAST, 2), (SOUTH, 3), (WARP, 1),
         (WEST, 1), (NORTH, 2), (WEST, 4), (SOUTH, 2), (WEST, 1), (WARP, 1),
         (WEST, 1), (SOUTH, 2), (WEST, 4), (NORTH, 4), (WEST, 1), (WARP, 1),
         (NORTH, 1), (EAST, 2), (NORTH, 5), (WARP, 1),
         (EAST, 1), (SOUTH, 2), (EAST, 2), (NORTH, 4), (WEST, 3)]

    In your maze, **how many steps does it take to get from the open tile marked `AA` to the open
    tile marked `ZZ`?**

        >>> part_1(example_2)
        part 1: shortest path through maze takes 58 steps
        58
    """

    result, _ = solve_maze(maze)

    print(f"part 1: shortest path through maze takes {result} steps")
    return result


def part_2(maze: 'Maze') -> int:
    """
    Strangely, the exit isn't open when you reach it. Then, you remember: the ancient Plutonians
    were famous for building **recursive spaces**.

    The marked connections in the maze aren't portals: they **physically connect** to a larger or
    smaller copy of the maze. Specifically, the labeled tiles around the inside edge actually
    connect to a smaller copy of the same maze, and the smaller copy's inner labeled tiles connect
    to yet a **smaller** copy, and so on.

    When you enter the maze, you are at the outermost level; when at the outermost level, only the
    outer labels `AA` and `ZZ` function (as the start and end, respectively); all other outer
    labeled tiles are effectively walls. At any other level, `AA` and `ZZ` count as walls, but the
    other outer labeled tiles bring you one level outward.

    Your goal is to find a path through the maze that brings you back to `ZZ` at the outermost level
    of the maze.

    In the first example above, the shortest path is now the loop around the right side. If the
    starting level is `0`, then taking the previously-shortest path would pass through `BC` (to
    level `1`), `DE` (to level `2`), and `FG` (back to level `1`). Because this is not the outermost
    level, `ZZ` is a wall, and the only option is to go back around to `BC`, which would only send
    you even deeper into the recursive maze.

        >>> example_1 = Maze.from_file(data_path(__file__, 'example-1.txt'))
        >>> solve_recursive_maze(example_1)
        (26, [(SOUTH, 1), (EAST, 8), (SOUTH, 12), (WEST, 4), (SOUTH, 1)])

    In the second example above, there is no path that brings you to `ZZ` at the outermost level.

        >>> example_2 = Maze.from_file(data_path(__file__, 'example-2.txt'))
        >>> solve_recursive_maze(example_2)
        Traceback (most recent call last):
        ...
        ValueError: path not found

    Here is a more interesting example:

        >>> example_3 = Maze.from_file(data_path(__file__, 'example-3.txt'))

    One shortest path through the maze is the following:

        >>> length_3, path_3 = solve_recursive_maze(example_3)
        >>> describe_recursive_path(path_3, example_3)
        - Walk from AA to XF (16 steps)
        - Recurse into level 1 through XF (1 step)
        - Walk from XF to CK (10 steps)
        - Recurse into level 2 through CK (1 step)
        - Walk from CK to ZH (14 steps)
        - Recurse into level 3 through ZH (1 step)
        - Walk from ZH to WB (10 steps)
        - Recurse into level 4 through WB (1 step)
        - Walk from WB to IC (10 steps)
        - Recurse into level 5 through IC (1 step)
        - Walk from IC to RF (10 steps)
        - Recurse into level 6 through RF (1 step)
        - Walk from RF to NM (8 steps)
        - Recurse into level 7 through NM (1 step)
        - Walk from NM to LP (12 steps)
        - Recurse into level 8 through LP (1 step)
        - Walk from LP to FD (24 steps)
        - Recurse into level 9 through FD (1 step)
        - Walk from FD to XQ (8 steps)
        - Recurse into level 10 through XQ (1 step)
        - Walk from XQ to WB (4 steps)
        - Return to level 9 through WB (1 step)
        - Walk from WB to ZH (10 steps)
        - Return to level 8 through ZH (1 step)
        - Walk from ZH to CK (14 steps)
        - Return to level 7 through CK (1 step)
        - Walk from CK to XF (10 steps)
        - Return to level 6 through XF (1 step)
        - Walk from XF to OA (14 steps)
        - Return to level 5 through OA (1 step)
        - Walk from OA to CJ (8 steps)
        - Return to level 4 through CJ (1 step)
        - Walk from CJ to RE (8 steps)
        - Return to level 3 through RE (1 step)
        - Walk from RE to IC (4 steps)
        - Recurse into level 4 through IC (1 step)
        - Walk from IC to RF (10 steps)
        - Recurse into level 5 through RF (1 step)
        - Walk from RF to NM (8 steps)
        - Recurse into level 6 through NM (1 step)
        - Walk from NM to LP (12 steps)
        - Recurse into level 7 through LP (1 step)
        - Walk from LP to FD (24 steps)
        - Recurse into level 8 through FD (1 step)
        - Walk from FD to XQ (8 steps)
        - Recurse into level 9 through XQ (1 step)
        - Walk from XQ to WB (4 steps)
        - Return to level 8 through WB (1 step)
        - Walk from WB to ZH (10 steps)
        - Return to level 7 through ZH (1 step)
        - Walk from ZH to CK (14 steps)
        - Return to level 6 through CK (1 step)
        - Walk from CK to XF (10 steps)
        - Return to level 5 through XF (1 step)
        - Walk from XF to OA (14 steps)
        - Return to level 4 through OA (1 step)
        - Walk from OA to CJ (8 steps)
        - Return to level 3 through CJ (1 step)
        - Walk from CJ to RE (8 steps)
        - Return to level 2 through RE (1 step)
        - Walk from RE to XQ (14 steps)
        - Return to level 1 through XQ (1 step)
        - Walk from XQ to FD (8 steps)
        - Return to level 0 through FD (1 step)
        - Walk from FD to ZZ (18 steps)

    This path takes a total of **396** steps to move from `AA` at the outermost layer to `ZZ` at the
    outermost layer.

        >>> length_3
        396

    In your maze, when accounting for recursion, **how many steps does it take to get from the open
    tile marked `AA` to the open tile marked `ZZ`, both at the outermost layer?**

        >>> part_2(example_3)
        part 2: shortest path through recursive maze takes 396 steps
        396
    """

    result, _ = solve_recursive_maze(maze)

    print(f"part 2: shortest path through recursive maze takes {result} steps")
    return result


Pos = tuple[int, int]


class Step(Enum):
    NORTH = (0, -1)
    SOUTH = (0, +1)
    WEST = (-1, 0)
    EAST = (+1, 0)
    WARP = (0, 0)

    def __init__(self, dx: int, dy: int):
        self.dx = dx
        self.dy = dy

    def add(self, pos: Pos, distance: int = 1) -> Pos:
        x, y = pos
        return x + self.dx * distance, y + self.dy * distance

    def __repr__(self) -> str:
        return self.name


Steps = tuple[Step, int]
Path = list[Steps]


class Maze:

    def __init__(self, floors: Iterable[Pos], labels: dict[Pos, str]):
        self.floors = set(floors)
        self.bounds = Rect.with_all(self.floors)
        self.labels = dict(labels)

        label_to_poss: dict[str, list[Pos]] = dgroupby_pairs(
            (label, pos) for pos, label in self.labels.items()
        )
        (self.start,) = label_to_poss.pop('AA')
        (self.target,) = label_to_poss.pop('ZZ')

        self.portals = self._create_portals(label_to_poss)

    def _create_portals(self, label_to_poss: dict[str, Iterable[Pos]]):
        def is_outer(pos: Pos) -> bool:
            x, y = pos
            return (
                x in (self.bounds.left_x, self.bounds.right_x) or
                y in (self.bounds.top_y, self.bounds.bottom_y)
            )

        def items() -> tuple[Pos, tuple[Pos, int]]:
            for label, (pos_1, pos_2) in label_to_poss.items():
                outer_1, outer_2 = is_outer(pos_1), is_outer(pos_2)
                if not outer_1 and outer_2:
                    direction = +1
                elif outer_1 and not outer_2:
                    direction = -1
                else:
                    assert outer_1 == outer_2
                    descr = "outer" if outer_1 else "inner"
                    raise ValueError(f"both {label!r} portals are {descr}: {pos_1!r}, {pos_2!r}")

                yield pos_1, (pos_2, direction)
                yield pos_2, (pos_1, -direction)

        return dict(sorted(items()))

    @classmethod
    def from_text(cls, text: str) -> Self:
        return cls.from_lines(text.strip('\n').splitlines())

    @classmethod
    def from_file(cls, fn: str) -> Self:
        return cls.from_lines(open(fn))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        floors: set[Pos] = set()
        letters: dict[Pos, str] = {}
        letter_pairs: dict[tuple[Pos, Pos], str] = {}

        for y, line in enumerate(lines):
            for x, char in enumerate(line.rstrip()):
                pos = (x, y)
                if char == '.':
                    floors.add(pos)
                elif char in ('#', ' '):
                    pass
                elif char.isalpha():
                    if (pos_left := (x-1, y)) in letters:
                        letter_left = letters.pop(pos_left)
                        letter_pairs[(pos_left, pos)] = letter_left + char
                    elif (pos_up := (x, y-1)) in letters:
                        letter_up = letters.pop(pos_up)
                        letter_pairs[(pos_up, pos)] = letter_up + char
                    else:
                        letters[pos] = char
                else:
                    raise ValueError(char)

        # all leters were paired
        assert not letters

        # shift to (0, 0)
        bounds = Rect.with_all(floors)
        off_x, off_y = bounds.top_left
        floors = {(x - off_x, y - off_y) for x, y in floors}

        # assign labels to floor tiles
        def neighboring(xy: Pos) -> Iterable[Pos]:
            x_, y_ = xy
            yield x_, y_ - 1
            yield x_, y_ + 1
            yield x_ - 1, y_
            yield x_ + 1, y_

        def neighboring_floor(positions: Iterable[Pos]) -> Pos:
            return next(
                pos1
                for pos0 in positions
                for pos1 in neighboring(pos0)
                if pos1 in floors
            )

        labels = {
            neighboring_floor((x - off_x, y - off_y) for (x, y) in poss): label
            for poss, label in letter_pairs.items()
        }

        return cls(floors, labels)


def aggregate_path(directions: Iterable[Step]) -> Path:
    return [(direction, len(list(group))) for direction, group in groupby(directions)]


def solve_maze(maze: Maze) -> tuple[int, Path]:
    def edges(pos: Pos) -> Iterable[tuple[Pos, Step, int]]:
        yield from (
            (pos1, step, 1)
            for step in (Step.NORTH, Step.SOUTH, Step.WEST, Step.EAST)
            if (pos1 := step.add(pos)) in maze.floors
        )
        if pos in maze.portals:
            pos1, _ = maze.portals[pos]
            yield pos1, Step.WARP, 1

    length, directions = shortest_path(
        start=maze.start,
        target=maze.target,
        edges=edges,
        nodes_count=len(maze.floors),
    )

    return length, aggregate_path(directions)


Pos3 = tuple[Pos, int]


def solve_recursive_maze(maze: Maze, max_level: int = 32) -> tuple[int, Path]:
    level_range = range(max_level + 1)

    def edges(pos: Pos3) -> Iterable[tuple[Pos3, Step, int]]:
        xy, level = pos
        yield from (
            ((xy1, level), step, 1)
            for step in (Step.NORTH, Step.SOUTH, Step.WEST, Step.EAST)
            if (xy1 := step.add(xy)) in maze.floors
        )
        if xy in maze.portals:
            xy1, level_delta = maze.portals[xy]
            if (level1 := level + level_delta) in level_range:
                yield (xy1, level1), Step.WARP, 1

    length, directions = shortest_path(
        start=(maze.start, 0),
        target=(maze.target, 0),
        edges=edges,
    )

    return length, aggregate_path(directions)


def describe_recursive_path(path: Path, maze: Maze) -> None:
    pos = maze.start
    level = 0
    last_label = maze.labels[pos]
    steps_since_label = 0

    for direction, distance in path:

        if direction is not Step.WARP:
            steps_since_label += distance
            pos = direction.add(pos, distance)
            if pos in maze.labels:
                new_label = maze.labels[pos]
                print(f"- Walk from {last_label} to {new_label} ({steps_since_label} steps)")
                last_label = new_label
                steps_since_label = 0

        else:
            assert distance == 1
            pos, level_delta = maze.portals[pos]
            level += level_delta
            verb = "Recurse into" if level_delta > 0 else "Return to"
            print(f"- {verb} level {level} through {last_label} (1 step)")


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    maze = Maze.from_file(input_path)
    result_1 = part_1(maze)
    result_2 = part_2(maze)
    return result_1, result_2


if __name__ == '__main__':
    main()
