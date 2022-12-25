"""
Advent of Code 2022
Day 24: Blizzard Basin
https://adventofcode.com/2022/day/24
"""
from enum import Enum
from functools import lru_cache
from typing import Iterable

from common.file import relative_path
from common.graph import shortest_path2
from common.iteration import dgroupby_pairs
from common.math import mod1
from common.rect import Rect


def part_1(map_: 'Map') -> int:
    """
    With everything replanted for next year (and with elephants and monkeys to tend the grove),
    you and the Elves leave for the extraction point.

    Partway up the mountain that shields the grove is a flat, open area that serves as the
    extraction point. It's a bit of a climb, but nothing the expedition can't handle.

    At least, that would normally be true; now that the mountain is covered in snow, things have
    become more difficult than the Elves are used to.

    As the expedition reaches a valley that must be traversed to reach the extraction site, you find
    that strong, turbulent winds are pushing small blizzards of snow and sharp ice around the
    valley. It's a good thing everyone packed warm clothes! To make it across safely, you'll need to
    find a way to avoid them.

    Fortunately, it's easy to see all of this from the entrance to the valley, so you make a map of
    the valley and the **blizzards** (your puzzle input). For example:

        >>> map_simple = Map.from_text('''
        ...     #.#####
        ...     #.....#
        ...     #>....#
        ...     #.....#
        ...     #...v.#
        ...     #.....#
        ...     #####.#
        ... ''')
        >>> map_simple.bounds
        Rect((1, 1), (5, 5))
        >>> map_simple.width, map_simple.height
        (5, 5)
        >>> map_simple.entrance, map_simple.exit
        ((1, 0), (5, 6))

    The walls of the valley are drawn as `#`; everything else is ground. Clear ground - where there
    is currently no blizzard - is drawn as `.`. Otherwise, blizzards are drawn with an arrow
    indicating their direction of motion: up (`^`), down (`v`), left (`<`), or right (`>`).

        >>> map_simple.init_blizzards
        {(1, 2): Direction.RIGHT, (4, 4): Direction.DOWN}

    The above map includes two blizzards, one moving right (`>`) and one moving down (`v`). In one
    minute, each blizzard moves one position in the direction it is pointing:

        >>> map_simple.draw(minute=1)
        #·#####
        #·····#
        #·>···#
        #·····#
        #·····#
        #···v·#
        #####·#

    Due to conservation of blizzard energy, as a blizzard reaches the wall of the valley, a new
    blizzard forms on the opposite side of the valley moving in the same direction. After another
    minute, the bottom downward-moving blizzard has been replaced with a new downward-moving
    blizzard at the top of the valley instead:

        >>> map_simple.draw(minute=2)
        #·#####
        #···v·#
        #··>··#
        #·····#
        #·····#
        #·····#
        #####·#

    Because blizzards are made of tiny snowflakes, they pass right through each other. After another
    minute, both blizzards temporarily occupy the same position, marked `2`:

        >>> map_simple.draw(minute=3)
        #·#####
        #·····#
        #···2·#
        #·····#
        #·····#
        #·····#
        #####·#

    After another minute, the situation resolves itself, giving each blizzard back its personal
    space:

        >>> map_simple.draw(minute=4)
        #·#####
        #·····#
        #····>#
        #···v·#
        #·····#
        #·····#
        #####·#

    Finally, after yet another minute, the rightward-facing blizzard on the right is replaced with
    a new one on the left facing the same direction:

        >>> map_simple.draw(minute=5)
        #·#####
        #·····#
        #>····#
        #·····#
        #···v·#
        #·····#
        #####·#

    This process repeats at least as long as you are observing it, but probably forever.

    Here is a more complex example:

        >>> map_complex = Map.from_text('''
        ...     #.######
        ...     #>>.<^<#
        ...     #.<..<<#
        ...     #>v.><>#
        ...     #<^v^^>#
        ...     ######.#
        ... ''')
        >>> map_complex.bounds
        Rect((1, 1), (6, 4))
        >>> map_complex.entrance, map_complex.exit
        ((1, 0), (6, 5))

    Your expedition begins in the only non-wall position in the top row and needs to reach the only
    non-wall position in the bottom row. On each minute, you can **move** up, down, left, or right,
    or you can wait in place. You and the blizzards act **simultaneously**, and you cannot share
    a position with a blizzard.

    In the above example, the fastest way to reach your goal requires **18** steps. Drawing the
    position of the expedition as `E`, one way to achieve this is:

        >>> path = map_complex.shortest_path()
        >>> len(path)
        18
        >>> map_complex.draw_traversal(path)
        Initial state:
        #E######
        #>>·<^<#
        #·<··<<#
        #>v·><>#
        #<^v^^>#
        ######·#
        Minute 1, move down:
        #·######
        #E>3·<·#
        #<··<<·#
        #>2·22·#
        #>v··^<#
        ######·#
        Minute 2, move down:
        #·######
        #·2>2··#
        #E^22^<#
        #·>2·^>#
        #·>··<·#
        ######·#
        Minute 3, wait:
        #·######
        #<^<22·#
        #E2<·2·#
        #><2>··#
        #··><··#
        ######·#
        Minute 4, move up:
        #·######
        #E<··22#
        #<<·<··#
        #<2·>>·#
        #·^22^·#
        ######·#
        Minute 5, move right:
        #·######
        #2Ev·<>#
        #<·<··<#
        #·^>^22#
        #·2··2·#
        ######·#
        Minute 6, move right:
        #·######
        #>2E<·<#
        #·2v^2<#
        #>··>2>#
        #<····>#
        ######·#
        Minute 7, move down:
        #·######
        #·22^2·#
        #<vE<2·#
        #>>v<>·#
        #>····<#
        ######·#
        Minute 8, move left:
        #·######
        #·<>2^·#
        #·E<<·<#
        #·22··>#
        #·2v^2·#
        ######·#
        Minute 9, move up:
        #·######
        #<E2>>·#
        #·<<·<·#
        #>2>2^·#
        #·v><^·#
        ######·#
        Minute 10, move right:
        #·######
        #·2E·>2#
        #<2v2^·#
        #<>·>2·#
        #··<>··#
        ######·#
        Minute 11, wait:
        #·######
        #2^E^2>#
        #<v<·^<#
        #··2·>2#
        #·<··>·#
        ######·#
        Minute 12, move down:
        #·######
        #>>·<^<#
        #·<E·<<#
        #>v·><>#
        #<^v^^>#
        ######·#
        Minute 13, move down:
        #·######
        #·>3·<·#
        #<··<<·#
        #>2E22·#
        #>v··^<#
        ######·#
        Minute 14, move right:
        #·######
        #·2>2··#
        #·^22^<#
        #·>2E^>#
        #·>··<·#
        ######·#
        Minute 15, move right:
        #·######
        #<^<22·#
        #·2<·2·#
        #><2>E·#
        #··><··#
        ######·#
        Minute 16, move right:
        #·######
        #·<··22#
        #<<·<··#
        #<2·>>E#
        #·^22^·#
        ######·#
        Minute 17, move down:
        #·######
        #2·v·<>#
        #<·<··<#
        #·^>^22#
        #·2··2E#
        ######·#
        Minute 18, move down:
        #·######
        #>2·<·<#
        #·2v^2<#
        #>··>2>#
        #<····>#
        ######E#

    **What is the fewest number of minutes required to avoid the blizzards and reach the goal?**

        >>> part_1(map_complex)
        part 1: goal can be reached in 18 steps
        18
    """

    result = len(map_.shortest_path())

    print(f"part 1: goal can be reached in {result} steps")
    return result


def part_2(map_: 'Map') -> int:
    """
    As the expedition reaches the far side of the valley, one of the Elves looks especially
    dismayed:

    He **forgot his snacks** at the entrance to the valley!

    Since you're so good at dodging blizzards, the Elves humbly request that you go back for his
    snacks. From the same initial conditions, how quickly can you make it from the start to the
    goal, then back to the start, then back to the goal?


    In the above example, the first trip to the goal takes 18 minutes, the trip back to the start
    takes 23 minutes, and the trip back to the goal again takes 13 minutes, for a total time of
    **54** minutes.

        >>> map_complex = Map.from_file('data/24-example.txt')
        >>> path_1, path_2, path_3 = map_complex.shortest_trip(rounds=3)
        >>> len(path_1), len(path_2), len(path_3)
        (18, 23, 13)
        >>> sum(_)
        54

    **What is the fewest number of minutes required to reach the goal, go back to the start, then
    reach the goal again?**

        >>> part_2(map_complex)
        part 2: goal, start, and goal can be reached in 54 steps
        54
    """

    result = sum(len(path) for path in map_.shortest_trip(rounds=3))

    print(f"part 2: goal, start, and goal can be reached in {result} steps")
    return result


Pos = tuple[int, int]


class Direction(Enum):
    UP = (0, -1, '^')
    DOWN = (0, +1, 'v')
    LEFT = (-1, 0, '<')
    RIGHT = (+1, 0, '>')
    WAIT = (0, 0, '.')

    def __init__(self, dx: int, dy: int, char: str):
        self.dx = dx
        self.dy = dy
        self.char = char

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'

    def __str__(self) -> str:
        if self is Direction.WAIT:
            return 'wait'
        else:
            return f'move {self.name.lower()}'

    def __add__(self, other):
        if not isinstance(other, tuple):
            return NotImplemented
        x, y = other
        return x + self.dx, y + self.dy

    __radd__ = __add__

    def is_vertical(self) -> bool:
        return self in (Direction.UP,  Direction.DOWN)

    def is_horizontal(self) -> bool:
        return self in (Direction.LEFT, Direction.RIGHT)

    @classmethod
    def from_char(cls, char: str) -> 'Direction':
        return next(d for d in cls if d.char == char)


Path = list[Direction]

class Map:
    def __init__(self, width: int, height: int, init_blizzards: dict[Pos, Direction]):
        self.width, self.height = width, height
        self.bounds = Rect((1, 1), (width, height))
        self.entrance = (1, 0)
        self.exit = (width, height + 1)
        self.init_blizzards = dict(init_blizzards)

    def shortest_path(
        self,
        minute_offset: int = 0,
        reverse: bool = False,
        description: str = "finding shortest path",
    ) -> Path:
        Node = tuple[Pos, int]  # position and time

        start, target = (self.entrance, self.exit) if not reverse else (self.exit, self.entrance)

        def move(pos: Pos, direction: Direction) -> Pos:
            if direction is None:
                return pos
            x, y = pos
            return x + direction.dx, y + direction.dy

        def neighbors(node: Node) -> Iterable[tuple[Node, Direction, int]]:
            pos, minute = node
            blizzards = self.current_blizzards_set(minute + 1)
            return (
                ((npos, minute + 1), dir_, 1)
                for dir_ in Direction
                if (npos := move(pos, dir_)) in (self.entrance, self.exit) or npos in self.bounds
                if npos not in blizzards
            )

        _, path = shortest_path2(
            start=(start, minute_offset),
            is_target=lambda pos_minute: pos_minute[0] == target,
            edges=neighbors,
            description=description,
        )
        return path

    def shortest_trip(self, rounds: int = 3) -> Iterable[Path]:
        minute = 0
        for round_no in range(rounds):
            path = self.shortest_path(
                minute_offset=minute,
                reverse=round_no % 2 == 1,
                description=f"round #{round_no + 1}"
            )
            yield path
            minute += len(path)

    def current_blizzards_set(self, minute: int) -> set[Pos]:
        return (
            self._current_blizzards_horizontal(minute % self.width) |
            self._current_blizzards_vertical(minute % self.height)
        )

    @lru_cache()
    def _current_blizzards_horizontal(self, minute: int) -> set[Pos]:
        return {
            (mod1(x + d.dx * minute, self.width), mod1(y + d.dy * minute, self.height))
            for (x, y), d in self.init_blizzards.items()
            if d.is_horizontal()
        }

    @lru_cache()
    def _current_blizzards_vertical(self, minute: int) -> set[Pos]:
        return {
            (mod1(x + d.dx * minute, self.width), mod1(y + d.dy * minute, self.height))
            for (x, y), d in self.init_blizzards.items()
            if d.is_vertical()
        }

    def new_blizzard_pos(self, init_pos: Pos, direction: Direction, minute: int) -> Pos:
        x, y = init_pos
        return (
            mod1(x + direction.dx * minute, self.width),
            mod1(y + direction.dy * minute, self.height)
        )

    def draw(self, minute: int = 0, highlight: dict[Pos, str] = None) -> None:
        if highlight is None:
            highlight = {}

        blizzards = dgroupby_pairs(
            (self.new_blizzard_pos(init_pos, dir_, minute), dir_)
            for init_pos, dir_ in self.init_blizzards.items()
        )

        def char(pos: Pos) -> str:
            assert highlight is not None
            if pos in highlight:
                return highlight[pos]
            if pos in (self.entrance, self.exit):
                return '·'
            if pos not in self.bounds:
                return '#'
            if pos not in blizzards:
                return '·'

            local_blizzards = blizzards[pos]
            if len(local_blizzards) == 1:
                return local_blizzards[0].char
            else:
                assert len(local_blizzards) <= 4
                return str(len(local_blizzards))

        draw_bounds = self.bounds.grow_by(1, 1)
        for y in draw_bounds.range_y():
            print(''.join(char((x, y)) for x in draw_bounds.range_x()))

    def draw_traversal(self, path: Path) -> None:
        print("Initial state:")
        pos = self.entrance
        self.draw(minute=0, highlight={pos: 'E'})

        for minute, direction in enumerate(path, start=1):
            print(f"Minute {minute}, {direction}:")
            pos += direction
            self.draw(minute=minute, highlight={pos: 'E'})

    @classmethod
    def from_file(cls, fn: str) -> 'Map':
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_text(cls, text) -> 'Map':
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Map':
        blizzards: dict[Pos, Direction] = {}
        width, height = 0, 0

        for y, line in enumerate(lines):
            line = line.strip()
            if y == 0:
                width = len(line) - 2
                assert width >= 3
                assert line == '#.' + '#' * width

            elif line.startswith('###'):
                height = y - 1
                assert height >= 3
                assert line == '#' * width + '.#'

            else:
                assert line.startswith('#') and line.endswith('#')
                blizzards.update(
                    ((x, y), Direction.from_char(char))
                    for x, char in enumerate(line)
                    if char not in ('.', '#')
                )

        return cls(width, height, blizzards)


def main(input_fn: str = 'data/24-input.txt') -> tuple[int, int]:
    map_ = Map.from_file(input_fn)
    result_1 = part_1(map_)
    result_2 = part_2(map_)
    return result_1, result_2


if __name__ == '__main__':
    main()
