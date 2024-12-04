"""
Advent of Code 2023
Day 10: Pipe Maze
https://adventofcode.com/2023/day/10
"""

from dataclasses import dataclass
from typing import Iterable, Self

from common.file import relative_path
from common.heading import Heading
from common.iteration import ilen
from common.rect import Rect


def part_1(maze: 'Maze') -> int:
    """
    You use the hang glider to ride the hot air from Desert Island all the way up to the floating
    metal island. This island is surprisingly cold and there definitely aren't any thermals to glide
    on, so you leave your hang glider behind.

    You wander around for a while, but you don't find any people or animals. However, you do
    occasionally find signposts labeled "Hot Springs" pointing in a seemingly consistent direction;
    maybe you can find someone at the hot springs and ask them where the desert-machine parts are
    made.

    The landscape here is alien; even the flowers and trees are made of metal. As you stop to admire
    some metal grass, you notice something metallic scurry away in your peripheral vision and jump
    into a big pipe! It didn't look like any animal you've ever seen; if you want a better look,
    you'll need to get ahead of it.

    Scanning the area, you discover that the entire field you're standing on is densely packed with
    pipes; it was hard to tell at first because they're the same metallic silver color as the
    "ground". You make a quick sketch of all of the surface pipes you can see (your puzzle input).

    The pipes are arranged in a two-dimensional grid of **tiles**:

      - `|` is a **vertical pipe** connecting north and south.
      - `-` is a **horizontal pipe** connecting east and west.
      - `L` is a **90-degree bend** connecting north and east.
      - `J` is a **90-degree bend** connecting north and west.
      - `7` is a **90-degree bend** connecting south and west.
      - `F` is a **90-degree bend** connecting south and east.
      - `.` is **ground**; there is no pipe in this tile.
      - `S` is the **starting position** of the animal; there is a pipe on this tile,
        but your sketch doesn't show what shape the pipe has.

    Based on the acoustics of the animal's scurrying, you're confident the pipe that contains
    the animal is **one large, continuous loop**.

    For example, here is a square loop of pipe:

        .....
        .F-7.
        .|.|.
        .L-J.
        .....

    If the animal had entered this loop in the northwest corner, the sketch would instead look like
    this:

        >>> maze_1 = Maze.from_text('''
        ...     .....
        ...     .S-7.
        ...     .|.|.
        ...     .L-J.
        ...     .....
        ... ''')
        >>> maze_1.start_pos
        (1, 1)
        >>> maze_1.tiles  # doctest: +NORMALIZE_WHITESPACE
        {(1, 1): 'F', (2, 1): '-', (3, 1): '7',
         (1, 2): '|',              (3, 2): '|',
         (1, 3): 'L', (2, 3): '-', (3, 3): 'J'}

    In the above diagram, the S tile is still a 90-degree `F` bend: you can tell because of how the
    adjacent pipes connect to it.

        >>> maze_1.start_tile
        'F'

    Unfortunately, there are also many pipes that **aren't connected to the loop**!
    This sketch shows the same loop as above:

        >>> maze_2 = Maze.from_text('''
        ...     -L|F7
        ...     7S-7|
        ...     L|7||
        ...     -L-J|
        ...     L|-JF
        ... ''')
        >>> maze_2.start_pos
        (1, 1)
        >>> len(maze_2.tiles)
        25
        >>> maze_2.start_tile
        'F'

    In the above diagram, you can still figure out which pipes form the main loop: they're the ones
    connected to `S`, pipes those pipes connect to, pipes **those** pipes connect to, and so on.
    Every pipe in the main loop connects to its two neighbors (including `S`, which will have
    exactly two pipes connecting to it, and which is assumed to connect back to those two pipes).

        >>> list(maze_2.trace_loop())
        [(1, 1), (2, 1), (3, 1), (3, 2), (3, 3), (2, 3), (1, 3), (1, 2)]
        >>> [maze_2.tile(pos) for pos in _]
        ['F', '-', '7', '|', 'J', '-', 'L', '|']

    Here is a sketch that contains a slightly more complex main loop:

        >>> maze_3 = Maze.from_text('''
        ...     ..F7.
        ...     .FJ|.
        ...     SJ.L7
        ...     |F--J
        ...     LJ...
        ... ''')
        >>> maze_3.start_pos
        (0, 2)
        >>> len(maze_3.tiles)
        16
        >>> ilen(maze_3.trace_loop())
        16

    Here's the same example sketch with the extra, non-main-loop pipe tiles also shown:

        >>> maze_4 = Maze.from_text('''
        ...     7-F7-
        ...     .FJ|7
        ...     SJLL7
        ...     |F--J
        ...     LJ.LJ
        ... ''')
        >>> maze_3.start_pos == maze_4.start_pos
        True
        >>> maze_3 == maze_4
        False
        >>> list(maze_3.trace_loop()) == list(maze_4.trace_loop())
        True

    If you want to **get out ahead of the animal**, you should find the tile in the loop that is
    **farthest** from the starting position. Because the animal is in the pipe, it doesn't make
    sense to measure this by direct distance. Instead, you need to find the tile that would take
    the longest number of steps **along the loop** to reach from the starting point - regardless of
    which way around the loop the animal went.

    In the first example with the square loop, you can count the distance each tile in the loop is
    from the starting point like this:

        >>> draw_distances(maze_1, margin=1)
        ·····
        ·012·
        ·1·3·
        ·234·
        ·····

    In this example, the farthest point from the start is **`4`** steps away.

        >>> farthest_distance(maze_1)
        4

    Here's the more complex loop again with the distances for each tile on that loop:

        >>> draw_distances(maze_3)
        ··45·
        ·236·
        01·78
        14567
        23···
        >>> farthest_distance(maze_3)
        8

    Find the single giant loop starting at `S`. **How many steps along the loop does it take to get
    from the starting position to the point farthest from the starting position?**

        >>> part_1(maze_3)
        part 1: it takes 8 steps to reach the farthest point
        8
    """

    result = farthest_distance(maze)

    print(f"part 1: it takes {result} steps to reach the farthest point")
    return result


def part_2(maze: 'Maze') -> int:
    """
    You quickly reach the farthest point of the loop, but the animal never emerges. Maybe its nest
    is **within the area enclosed by the loop**?

    To determine whether it's even worth taking the time to search for such a nest, you should
    calculate how many tiles are contained within the loop. For example:

        >>> maze_1 = Maze.from_text('''
        ...     ...........
        ...     .S-------7.
        ...     .|F-----7|.
        ...     .||.....||.
        ...     .||.....||.
        ...     .|L-7.F-J|.
        ...     .|..|.|..|.
        ...     .L--J.L--J.
        ...     ...........
        ... ''')

    The above loop encloses merely **four tiles** - the two pairs of `.` in the southwest and
    southeast (marked `@` below). The middle `.` tiles (marked `o` below) are **not** in the loop.
    Here is the same loop again with those regions marked:

        >>> draw_enclosement(maze_1, inside_char='@', outside_char='o', margin=1)
        ···········
        ·S───────┐·
        ·│┌─────┐│·
        ·││ooooo││·
        ·││ooooo││·
        ·│└─┐o┌─┘│·
        ·│@@│o│@@│·
        ·└──┘o└──┘·
        ···········

    In fact, there doesn't even need to be a full tile path to the outside for tiles to count as
    outside the loop - squeezing between pipes is also allowed! Here, `@` is still within the loop
    and *o* is still outside the loop:

        >>> maze_2 = Maze.from_file('data/10-example.txt')
        >>> draw_enclosement(maze_2, inside_char='@', outside_char='o', margin=1)
        ··········
        ·S──────┐·
        ·│┌────┐│·
        ·││oooo││·
        ·││oooo││·
        ·│└─┐┌─┘│·
        ·│@@││@@│·
        ·└──┘└──┘·
        ··········

    In both of the above examples, **`4`** tiles are enclosed by the loop:

        >>> enclosed_count(maze_1)
        4
        >>> enclosed_count(maze_2)
        4

    Here's a larger example:

        >>> maze_3 = Maze.from_text('''
        ...     .F----7F7F7F7F-7....
        ...     .|F--7||||||||FJ....
        ...     .||.FJ||||||||L7....
        ...     FJL7L7LJLJ||LJ.L-7..
        ...     L--J.L7...LJS7F-7L7.
        ...     ....F-J..F7FJ|L7L7L7
        ...     ....L7.F7||L7|.L7L7|
        ...     .....|FJLJ|FJ|F7|.LJ
        ...     ....FJL-7.||.||||...
        ...     ....L---J.LJ.LJLJ...
        ... ''')

    The above sketch has many random bits of ground, some of which are in the loop (`@`) and some of
    which are outside it (`o`):

        >>> draw_enclosement(maze_3, inside_char='@', outside_char='o')
        o┌────┐┌┐┌┐┌┐┌─┐oooo
        o│┌──┐││││││││┌┘oooo
        o││o┌┘││││││││└┐oooo
        ┌┘└┐└┐└┘└┘││└┘@└─┐oo
        └──┘o└┐@@@└┘S┐┌─┐└┐o
        oooo┌─┘@@┌┐┌┘│└┐└┐└┐
        oooo└┐@┌┐││└┐│@└┐└┐│
        ooooo│┌┘└┘│┌┘│┌┐│o└┘
        oooo┌┘└─┐o││o││││ooo
        oooo└───┘o└┘o└┘└┘ooo

    In this larger example, **`8`** tiles are enclosed by the loop:

        >>> enclosed_count(maze_3)
        8

    Any tile that isn't part of the main loop can count as being enclosed by the loop. Here's
    another example with many bits of junk pipe lying around that aren't connected to the main loop
    at all:

        >>> maze_4 = Maze.from_text('''
        ...     FF7FSF7F7F7F7F7F---7
        ...     L|LJ||||||||||||F--J
        ...     FL-7LJLJ||||||LJL-77
        ...     F--JF--7||LJLJ7F7FJ-
        ...     L---JF-JLJ.||-FJLJJ7
        ...     |F|F-JF---7F7-L7L|7|
        ...     |FFJF7L7F-JF7|JL---7
        ...     7-L-JL7||F7|L7F-7F7|
        ...     L.L7LFJ|||||FJL7||LJ
        ...     L7JLJL-JLJLJL--JLJ.L
        ... ''')

    Here are just the tiles that are enclosed by the loop marked with `@`:

        >>> draw_enclosement(maze_4, inside_char='@')
        ┌┌┐┌S┌┐┌┐┌┐┌┐┌┐┌───┐
        └│└┘││││││││││││┌──┘
        ┌└─┐└┘└┘││││││└┘└─┐┐
        ┌──┘┌──┐││└┘└┘@┌┐┌┘─
        └───┘┌─┘└┘@@@@┌┘└┘┘┐
        │┌│┌─┘┌───┐@@@└┐└│┐│
        │┌┌┘┌┐└┐┌─┘┌┐@@└───┐
        ┐─└─┘└┐││┌┐│└┐┌─┐┌┐│
        └·└┐└┌┘│││││┌┘└┐││└┘
        └┐┘└┘└─┘└┘└┘└──┘└┘·└

    In this last example, **`10`** tiles are enclosed by the loop:

        >>> enclosed_count(maze_4)
        10

    Figure out whether you have time to search for the nest by calculating the area within the loop.
    **How many tiles are enclosed by the loop?**

        >>> part_2(maze_4)
        part 2: the loop encloses 10 tiles
        10
    """

    result = enclosed_count(maze)

    print(f"part 2: the loop encloses {result} tiles")
    return result


Pos = tuple[int, int]
Tile = str
Tiles = dict[Pos, Tile]
Pipe = tuple[Heading, Heading]


PIPE_HEADINGS: dict[Tile, Pipe] = {
    '|': (Heading.NORTH, Heading.SOUTH),
    '-': (Heading.EAST, Heading.WEST),
    'L': (Heading.NORTH, Heading.EAST),
    'J': (Heading.NORTH, Heading.WEST),
    '7': (Heading.SOUTH, Heading.WEST),
    'F': (Heading.SOUTH, Heading.EAST),
}


@dataclass(frozen=True)
class Maze:
    start_pos: Pos
    tiles: Tiles

    def __contains__(self, pos: Pos) -> bool:
        return pos in self.tiles

    def tile(self, pos: Pos) -> Tile:
        return self.tiles[pos]

    @property
    def start_tile(self) -> Tile:
        return self.tile(self.start_pos)

    def pipe(self, pos: Pos) -> Pipe:
        return PIPE_HEADINGS[self.tile(pos)]

    def trace_loop(self) -> Iterable[Pos]:
        pos = self.start_pos
        heading = self.pipe(pos)[1]  # any heading

        while True:
            yield pos
            pos = heading.move(pos)
            heading = next_heading(heading, self.pipe(pos))

            if pos == self.start_pos:
                break

    @classmethod
    def from_file(cls, fn: str) -> Self:
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_text(cls, text: str) -> Self:
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        tiles = {
            (x, y): tile
            for y, line in enumerate(lines)
            for x, tile in enumerate(line.strip())
            if tile not in ('.', '·')
        }

        # detect the single starting position
        start_pos, = (pos for pos, tile in tiles.items() if tile == 'S')

        # figure out what tile is underneath the `S`
        start_headings = [
            heading
            for heading in Heading
            if (ntile := tiles.get(heading.move(start_pos)))
            if heading.opposite() in PIPE_HEADINGS[ntile]
        ]
        assert len(start_headings) == 2
        start_tile = next(
            tile
            for tile, headings in PIPE_HEADINGS.items()
            if set(headings) == set(start_headings)
        )
        tiles[start_pos] = start_tile

        return cls(start_pos, tiles)


def next_heading(last_heading: Heading, pipe: Pipe) -> Heading:
    came_from = last_heading.opposite()
    new_heading, = (h for h in pipe if h != came_from)
    return new_heading


def farthest_distance(maze: Maze) -> int:
    return ilen(maze.trace_loop()) // 2


def enclosed_positions(maze: Maze) -> Iterable[Pos]:
    loop = set(maze.trace_loop())
    rect = Rect.with_all(maze.tiles)
    for y in rect.range_y():
        north, south = False, False
        for x in rect.range_x():
            if (pos := (x, y)) in loop:
                pipe = maze.pipe(pos)
                if Heading.NORTH in pipe:
                    north = not north
                if Heading.SOUTH in pipe:
                    south = not south
            elif north and south:
                yield pos


def enclosed_count(maze: Maze) -> int:
    return ilen(enclosed_positions(maze))


def draw_distances(maze: Maze, margin: int = 0) -> None:
    tiles = dict(maze.tiles)
    loop = list(maze.trace_loop())

    for step, pos in enumerate(loop):
        distance = min(step, len(loop) - step)
        tiles[pos] = str(distance)[-1]

    canvas = Rect.with_all(tiles).grow_by(margin, margin)
    for y in canvas.range_y():
        print(''.join(tiles.get((x, y), '·') for x in canvas.range_x()))


PRETTY_PIPES = {
    '|': '│',
    '-': '─',
    'L': '└',
    'J': '┘',
    '7': '┐',
    'F': '┌',
}


def draw_enclosement(
    maze: Maze,
    inside_char: str | None = None,
    outside_char: str | None = None,
    pretty_pipes: bool = True,
    draw_start: bool = True,
    margin: int = 0,
) -> None:

    if pretty_pipes:
        tiles = {
            pos: PRETTY_PIPES.get(tile)
            for pos, tile in maze.tiles.items()
        }
    else:
        tiles = dict(maze.tiles)

    if draw_start:
        tiles[maze.start_pos] = 'S'

    enclosed_set = set(enclosed_positions(maze))

    if inside_char:
        assert len(inside_char) == 1
        tiles.update((pos, inside_char) for pos in enclosed_set)

    if outside_char:
        assert len(outside_char) == 1
        tiles.update(
            (pos, outside_char)
            for pos in Rect.with_all(maze.tiles)
            if pos not in maze.tiles
            if pos not in enclosed_set
        )

    canvas = Rect.with_all(tiles).grow_by(margin, margin)
    for y in canvas.range_y():
        print(''.join(tiles.get((x, y)) or '·' for x in canvas.range_x()))


def main(input_fn: str = 'data/10-input.txt') -> tuple[int, int]:
    maze = Maze.from_file(input_fn)
    result_1 = part_1(maze)
    result_2 = part_2(maze)
    return result_1, result_2


if __name__ == '__main__':
    main()
