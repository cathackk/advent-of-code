"""
Advent of Code 2024
Day 20: Race Condition
https://adventofcode.com/2024/day/20
"""

from typing import Iterable, Self

from common.canvas import Canvas
from common.file import relative_path
from common.graph import shortest_path
from common.heading import Heading
from common.iteration import minmax, unique
from common.rect import Rect


def part_1(race: 'Racetrack', threshold: int = 100) -> int:
    r"""
    The Historians are quite pixelated again. This time, a massive, black building looms over you -
    you're right outside (y2017/day24_bridge.py) the CPU!

    While The Historians get to work, a nearby program sees that you're idle and challenges you to
    **a race**. Apparently, you've arrived just in time for the frequently-held **race condition**
    festival!

    The race takes place on a particularly long and twisting code path; programs compete to see who
    can finish in **the fewest picoseconds**. The winner even gets their very own mutex!

    They hand you a **map of the racetrack** (your puzzle input). For example:

        >>> example = Racetrack.from_text('''
        ...     ###############
        ...     #...#...#.....#
        ...     #.#.#.#.#.###.#
        ...     #S#...#.#.#...#
        ...     #######.#.#.###
        ...     #######.#.#...#
        ...     #######.#.###.#
        ...     ###..E#...#...#
        ...     ###.#######.###
        ...     #...###...#...#
        ...     #.#####.#.###.#
        ...     #.#...#.#.#...#
        ...     #.#.#.#.#.#.###
        ...     #...#...#...###
        ...     ###############
        ... ''')
        >>> example.bounds.shape
        (15, 15)

    The map consists of track (`.`) - including the **start** (`S`) and **end** (`E`) positions
    (both of which also count as track) - and **walls** (`#`).

        >>> example.start
        (1, 3)
        >>> example.end
        (5, 7)

    When a program runs through the racetrack, it starts at the start position. Then, it is allowed
    to move up, down, left, or right; each such move takes **1 picosecond**. The goal is to reach
    the end position as quickly as possible. In this example racetrack, the fastest time is `84`
    picoseconds.

        >>> example.track[(5, 7)]
        84

    Because there is only a single path from the start to the end and the programs all go the same
    speed, the races used to be pretty boring.

        >>> len(example.track)
        85

    To make things more interesting, they introduced a new rule to the races: programs are allowed
    to **cheat**.

    The rules for cheating are very strict. **Exactly once** during a race, a program may **disable
    collision** for up to **2 picoseconds**. This allows the program to **pass through walls** as if
    they were regular track. At the end of the cheat, the program must be back on normal track
    again; otherwise, it will receive a segmentation fault and get disqualified.

    So, a program could complete the course in 72 picoseconds (saving **12 picoseconds**)
    by cheating for the two moves marked `1` and `2`:

        >>> example.draw(cheat=[(7, 1), (8, 1), (9, 1)])
        ###############
        #...#...12....#
        #.#.#.#.#.###.#
        #S#...#.#.#...#
        #######.#.#.###
        #######.#.#...#
        #######.#.###.#
        ###..E#...#...#
        ###.#######.###
        #...###...#...#
        #.#####.#.###.#
        #.#...#.#.#...#
        #.#.#.#.#.#.###
        #...#...#...###
        ###############
        >>> example.cheat_value((8, 1))
        12

    Or, a program could complete the course in 64 picoseconds (saving **20 picoseconds**)
    by cheating for the two moves marked `1` and `2`:

        >>> example.draw(cheat=[(9, 7), (10, 7), (11, 7)])
        ###############
        #...#...#.....#
        #.#.#.#.#.###.#
        #S#...#.#.#...#
        #######.#.#.###
        #######.#.#...#
        #######.#.###.#
        ###..E#...12..#
        ###.#######.###
        #...###...#...#
        #.#####.#.###.#
        #.#...#.#.#...#
        #.#.#.#.#.#.###
        #...#...#...###
        ###############
        >>> example.cheat_value((10, 7))
        20

    This cheat saves **38 picoseconds**:

        >>> example.draw(cheat=[(8, 7), (8, 8), (8, 9)])
        ###############
        #...#...#.....#
        #.#.#.#.#.###.#
        #S#...#.#.#...#
        #######.#.#.###
        #######.#.#...#
        #######.#.###.#
        ###..E#...#...#
        ###.####1##.###
        #...###.2.#...#
        #.#####.#.###.#
        #.#...#.#.#...#
        #.#.#.#.#.#.###
        #...#...#...###
        ###############
        >>> example.cheat_value((8, 8))
        38

    This cheat saves **64 picoseconds** and takes the program directly to the end:

        >>> example.draw(cheat=[(7, 7), (6, 7), (5, 7)])
        ###############
        #...#...#.....#
        #.#.#.#.#.###.#
        #S#...#.#.#...#
        #######.#.#.###
        #######.#.#...#
        #######.#.###.#
        ###..21...#...#
        ###.#######.###
        #...###...#...#
        #.#####.#.###.#
        #.#...#.#.#...#
        #.#.#.#.#.#.###
        #...#...#...###
        ###############
        >>> example.cheat_value((6, 7))
        64

    Each cheat has a distinct **start position** (the position where the cheat is activated, just
    before the first move that is allowed to go through walls) and **end position**; cheats are
    uniquely identified by their start position and end position.

    In this example, the total number of cheats (grouped by the amount of time they save) are
    as follows (time saved to number of cheats):

        >>> from common.iteration import sorted_counter
        >>> sorted_counter(example.all_cheat_values())
        {2: 14, 4: 14, 6: 2, 8: 4, 10: 2, 12: 3, 20: 1, 36: 1, 38: 1, 40: 1, 64: 1}

    You aren't sure what the conditions of the racetrack will be like, so to give yourself as many
    options as possible, you'll need a list of the best cheats.
    **How many cheats would save you at least 100 picoseconds?**

        >>> part_1(example, threshold=12)  # 12 picoseconds in this smaller example
        part 1: to save at least 12 picoseconds, there are 8 cheats
        8
    """

    result = sum(1 for save in race.all_cheat_values() if save >= threshold)

    print(f"part 1: to save at least {threshold} picoseconds, there are {result} cheats")
    return result


def part_2(race: 'Racetrack', threshold: int = 100) -> int:
    """
    The programs seem perplexed by your list of cheats. Apparently, the two-picosecond cheating rule
    was deprecated several milliseconds ago! The latest version of the cheating rule permits
    a single cheat that instead lasts at most **20 picoseconds**.

    Now, in addition to all the cheats that were possible in just two picoseconds, many more cheats
    are possible. This six-picosecond cheat saves 76 picoseconds:

        >>> example = Racetrack.from_file('data/20-example.txt')
        >>> cheat_1 = [(1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (2, 7), (3, 7)]
        >>> example.draw(cheat_1)
        ###############
        #...#...#.....#
        #.#.#.#.#.###.#
        #S#...#.#.#...#
        #1#####.#.#.###
        #2#####.#.#...#
        #3#####.#.###.#
        #456.E#...#...#
        ###.#######.###
        #...###...#...#
        #.#####.#.###.#
        #.#...#.#.#...#
        #.#.#.#.#.#.###
        #...#...#...###
        ###############
        >>> example.long_cheat_value(cheat_1)
        76

    Because this cheat has the same start and end positions as the one above, it's the **same
    cheat**, even though the path taken during the cheat is different:

        >>> cheat_2 = [(1, 3), (2, 3), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7)]
        >>> cheat_1[0] == cheat_2[0] and cheat_1[-1] == cheat_2[-1]
        True
        >>> example.draw(cheat_2)
        ###############
        #...#...#.....#
        #.#.#.#.#.###.#
        #S12..#.#.#...#
        ###3###.#.#.###
        ###4###.#.#...#
        ###5###.#.###.#
        ###6.E#...#...#
        ###.#######.###
        #...###...#...#
        #.#####.#.###.#
        #.#...#.#.#...#
        #.#.#.#.#.#.###
        #...#...#...###
        ###############
        >>> example.long_cheat_value(cheat_2)
        76

    Cheats don't need to use all 20 picoseconds; cheats can last any amount of time up to and
    including 20 picoseconds (but can still only end when the program is on normal track). Any cheat
    time not used is lost; it can't be saved for another cheat later.

    You'll still need a list of the best cheats, but now there are even more to choose between. Here
    are the quantities of cheats in this example that save **50 picoseconds or more**:

        >>> from common.iteration import sorted_counter
        >>> sorted_counter(val for val in example.all_long_cheat_values() if val >= 50)
        ... # doctest: +NORMALIZE_WHITESPACE
        {50: 32, 52: 31, 54: 29, 56: 39, 58: 25, 60: 23, 62: 20,
         64: 19, 66: 12, 68: 14, 70: 12, 72: 22, 74: 4, 76: 3}

    Find the best cheats using the updated cheating rules. How many cheats would save you at least 100 picoseconds?

        >>> part_2(example, threshold=50)
        part 2: to save at least 50 picoseconds, there are 285 long cheats
        285
    """

    result = sum(1 for save in race.all_long_cheat_values() if save >= threshold)

    print(f"part 2: to save at least {threshold} picoseconds, there are {result} long cheats")
    return result


Pos = tuple[int, int]


class Racetrack:
    def __init__(self, track: Iterable[Pos], start: Pos, end: Pos):
        # position to index of the tile on the track (picoseconds to reach it without cheating)
        self.track = {start: 0}

        self.start = start
        self.end = end

        self.track.update(
            (pos, index)
            for index, pos in enumerate(Racetrack._trace_track(track, self.start, self.end))
        )

        self.bounds = Rect.with_all(self.track).grow_by(1, 1)

    @staticmethod
    def _trace_track(track: Iterable[Pos], start: Pos, end: Pos) -> Iterable[Pos]:
        track_set = set(track)
        assert start in track_set
        assert end in track_set

        def edges(pos: Pos) -> Iterable[tuple[Pos, Pos, int]]:
            return (
                (npos, npos, 1)
                for heading in Heading
                if (npos := pos + heading) in track_set
            )

        length, path = shortest_path(start, end, edges)
        assert length == len(path)
        # the path leads through all the track positions == there is only one path through
        assert length == len(track_set) - 1
        return [start] + path

    def cheat_value(self, cheat: Pos) -> int:
        assert cheat not in self.track
        first_visit, last_visit = minmax(
            self.track[npos]
            for heading in Heading
            if (npos := cheat + heading) in self.track
        )
        return last_visit - first_visit - 2

    def long_cheat_value(self, cheat: Iterable[Pos]) -> int:
        cheat_start, *_, cheat_end = cheat
        normal_length = self.track[cheat_end] - self.track[cheat_start]
        assert normal_length > 0
        cheat_length = manhattan_distance(cheat_start, cheat_end)
        return normal_length - cheat_length

    def all_cheat_values(self) -> Iterable[int]:
        reachable_walls = (
            npos
            for pos in self.track
            for heading in Heading
            if (npos := pos + heading) not in self.track
        )
        return (
            save
            for wall in unique(reachable_walls)
            if (save := self.cheat_value(wall)) > 0
        )

    def all_long_cheat_values(self, max_length: int = 20) -> Iterable[int]:
        return (
            save
            for cheat_start in self.track
            for cheat_end, cheat_length in manhattan_iter(cheat_start, max_length)
            if cheat_end in self.track
            if (normal_length := self.track[cheat_end] - self.track[cheat_start]) > 0
            if (save := normal_length - cheat_length) > 0
        )

    def draw(self, cheat: Iterable[Pos] = ()) -> None:
        c = Canvas(bounds=self.bounds)
        c.draw_many((pos, '.') for pos in self.track)
        c.draw(self.start, 'S')
        c.draw(self.end, 'E')
        c.draw_many((pos, n if n else None) for n, pos in enumerate(cheat))
        print(c.render(empty_char='#'))

    @classmethod
    def from_file(cls, fn: str) -> Self:
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_text(cls, text: str) -> Self:
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        track: list[Pos] = []
        start: Pos | None = None
        end: Pos | None = None

        for y, line in enumerate(lines):
            for x, char in enumerate(line.strip()):
                if char != '#':
                    track.append((x, y))
                if char == 'S':
                    start = (x, y)
                elif char == 'E':
                    end = (x, y)

        assert start is not None
        assert end is not None
        return cls(track, start, end)


def manhattan_distance(pos_1: Pos, pos_2: Pos) -> int:
    x_1, y_1 = pos_1
    x_2, y_2 = pos_2
    return abs(x_1 - x_2) + abs(y_1 - y_2)


def manhattan_iter(pos: Pos, max_distance: int) -> Iterable[tuple[Pos, int]]:
    """
        >>> c = Canvas()
        >>> c.draw_many(manhattan_iter((0, 0), max_distance=3))
        >>> print(c)
           3
          323
         32123
        3210123
         32123
          323
           3
    """
    assert max_distance >= 0
    x, y = pos
    return (
        ((x + dx, y + dy), abs(dx) + abs(dy))
        for dy in range(-max_distance, max_distance + 1)
        for dx in range(-(max_distance - abs(dy)), (max_distance - abs(dy)) + 1)
    )


def main(input_fn: str = 'data/20-input.txt') -> tuple[int, int]:
    race = Racetrack.from_file(input_fn)
    result_1 = part_1(race)
    result_2 = part_2(race)
    return result_1, result_2


if __name__ == '__main__':
    main()
