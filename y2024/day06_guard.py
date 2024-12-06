"""
Advent of Code 2024
Day 6: Guard Gallivant
https://adventofcode.com/2024/day/6
"""

from dataclasses import dataclass
from typing import Generator, Iterable, Iterator, Self

from tqdm import tqdm

from common.canvas import Canvas
from common.file import relative_path
from common.heading import Heading
from common.iteration import exhaust
from common.rect import Rect


def part_1(map_: 'Map') -> int:
    """
    The Historians use their fancy device again, this time to whisk you all away to the North Pole
    prototype suit manufacturing lab... in the year 1518 (y2018/day05_polymer.py)! It turns out that
    having direct access to history is very convenient for a group of historians.

    You still have to be careful of time paradoxes, and so it will be important to avoid anyone from
    1518 while The Historians search for the Chief. Unfortunately, a single **guard** is patrolling
    this part of the lab.

    Maybe you can work out where the guard will go ahead of time so that The Historians can search
    safely?

    You start by making a map (your puzzle input) of the situation. For example:

        >>> example_map = Map.from_text('''
        ...     ....#.....
        ...     .........#
        ...     ..........
        ...     ..#.......
        ...     .......#..
        ...     ..........
        ...     .#..^.....
        ...     ........#.
        ...     #.........
        ...     ......#...
        ... ''')
        >>> example_map.bounds.shape
        (10, 10)

    The map shows the current position of the guard with `^` (to indicate the guard is currently
    facing **up** from the perspective of the map):

        >>> example_map.guard
        Guard(pos=(4, 6), heading=Heading.NORTH)

    Any **obstructions** - crates, desks, alchemical reactors, etc. - are shown as `#`:

        >>> sorted(example_map.obstructions)
        [(0, 8), (1, 6), (2, 3), (4, 0), (6, 9), (7, 4), (8, 7), (9, 1)]

    Lab guards in 1518 follow a very strict patrol protocol which involves repeatedly following
    these steps:

      - If there is something directly in front of you, turn **right** 90 degrees.
      - Otherwise, take a step forward.

    Following the above protocol, the guard moves up several times until she reaches an obstacle
    (in this case, a pile of failed suit prototypes):

        >>> print(next_map := example_map.move_guard())
        ····#·····
        ····^····#
        ··········
        ··#·······
        ·······#··
        ··········
        ·#········
        ········#·
        #·········
        ······#···

    Because there is now an obstacle in front of the guard, she turns right before continuing
    straight in her new facing direction:

        >>> print(next_map := next_map.move_guard())
        ····#·····
        ········>#
        ··········
        ··#·······
        ·······#··
        ··········
        ·#········
        ········#·
        #·········
        ······#···

    Reaching another obstacle (a spool of several **very** long polymers), she turns right again and
    continues downward:

        >>> print(next_map := next_map.move_guard())
        ····#·····
        ·········#
        ··········
        ··#·······
        ·······#··
        ··········
        ·#······v·
        ········#·
        #·········
        ······#···

    This process continues for a while, but the guard eventually leaves the mapped area
    (after walking past a tank of universal solvent):

        >>> print(next_map.move_guard_until_out())
        ····#·····
        ·········#
        ··········
        ··#·······
        ·······#··
        ··········
        ·#········
        ········#·
        #·········
        ······#v··

    By predicting the guard's route, you can determine which specific positions in the lab will be
    in the patrol path. **Including the guard's starting position**, the positions visited by
    the guard before leaving the area are marked with an `X`:

        >>> path = set(example_map.trace_guard_path())
        >>> print(example_map.draw(path))
        ····#·····
        ····XXXXX#
        ····X···X·
        ··#·X···X·
        ··XXXXX#X·
        ··X·X·X·X·
        ·#XXXXXXX·
        ·XXXXXXX#·
        #XXXXXXX··
        ······#X··

    In this example, the guard will visit **`41`** distinct positions on your map:

        >>> len(set(pos for pos, _ in path))
        41

    Predict the path of the guard.
    **How many distinct positions will the guard visit before leaving the mapped area?**

        >>> part_1(example_map)
        part 1: the guard visits 41 distinct positions
        41
    """

    result = len(set(pos for pos, _ in map_.trace_guard_path()))

    print(f"part 1: the guard visits {result} distinct positions")
    return result


def part_2(map_: 'Map') -> int:
    """
    While The Historians begin working around the guard's patrol route, you borrow their fancy
    device and step outside the lab. From the safety of a supply closet, you time travel through
    the last few months and record (y2018/day04_guards.py) the nightly status of the lab's guard
    post on the walls of the closet.

    Returning after what seems like only a few seconds to The Historians, they explain that
    the guard's patrol area is simply too large for them to safely search the lab without getting
    caught.

    Fortunately, they are **pretty sure** that adding a single new obstruction **won't** cause
    a time paradox. They'd like to place the new obstruction in such a way that the guard will get
    **stuck in a loop**, making the rest of the lab safe to search.

    To have the lowest chance of creating a time paradox, The Historians would like to know **all**
    of the possible positions for such an obstruction. The new obstruction can't be placed at
    the guard's starting position - the guard is there right now and would notice.

    In the above example, there are only **`6`** different positions where a new obstruction would
    cause the guard to get stuck in a loop. The diagrams of these six situations use `O` to mark the
    new obstruction, `|` to show a position where the guard moves up/down, `-` to show a position
    where the guard moves left/right, and `+` to show a position where the guard moves both up/down
    and left/right.

        >>> example_map = Map.from_file('data/06-example.txt')

    Option one, put a printing press next to the guard's starting position:

        >>> print(example_map.draw_loop(new_obstruction=(3, 6)))
        ····#·····
        ····+---+#
        ····|···|·
        ··#·|···|·
        ····|··#|·
        ····|···|·
        ·#·O^---+·
        ········#·
        #·········
        ······#···

    Option two, put a stack of failed suit prototypes in the bottom right quadrant of the mapped
    area:

        >>> print(example_map.draw_loop(new_obstruction=(6, 7)))
        ····#·····
        ····+---+#
        ····|···|·
        ··#·|···|·
        ··+-+-+#|·
        ··|·|·|·|·
        ·#+-^-+-+·
        ······O·#·
        #·········
        ······#···

    Option three, put a crate of chimney-squeeze prototype fabric next to the standing desk in
    the bottom right quadrant:

        >>> print(example_map.draw_loop(new_obstruction=(7, 7)))
        ····#·····
        ····+---+#
        ····|···|·
        ··#·|···|·
        ··+-+-+#|·
        ··|·|·|·|·
        ·#+-^-+-+·
        ·+----+O#·
        #+----+···
        ······#···

    Option four, put an alchemical retroencabulator near the bottom left corner:

        >>> print(example_map.draw_loop(new_obstruction=(1, 8)))
        ····#·····
        ····+---+#
        ····|···|·
        ··#·|···|·
        ··+-+-+#|·
        ··|·|·|·|·
        ·#+-^-+-+·
        ··|···|·#·
        #O+---+···
        ······#···

    Option five, put the alchemical retroencabulator a bit to the right instead:

        >>> print(example_map.draw_loop(new_obstruction=(3, 8)))
        ····#·····
        ····+---+#
        ····|···|·
        ··#·|···|·
        ··+-+-+#|·
        ··|·|·|·|·
        ·#+-^-+-+·
        ····|·|·#·
        #··O+-+···
        ······#···

    Option six, put a tank of sovereign glue right next to the tank of universal solvent:

        >>> print(example_map.draw_loop(new_obstruction=(7, 9)))
        ····#·····
        ····+---+#
        ····|···|·
        ··#·|···|·
        ··+-+-+#|·
        ··|·|·|·|·
        ·#+-^-+-+·
        ·+----++#·
        #+----++··
        ······#O··

    It doesn't really matter what you choose to use as an obstacle so long as you and The Historians
    can put it into position without the guard noticing. The important thing is having enough
    options that you can find one that minimizes time paradoxes, and in this example, there are
    **`6`** different positions you could choose:

        >>> list(example_map.plan_loops())
        [(3, 6), (6, 7), (3, 8), (1, 8), (7, 7), (7, 9)]
        >>> len(_)
        6

    You need to get the guard stuck in a loop by adding a single new obstruction.
    **How many different positions could you choose for this obstruction?**

        >>> part_2(example_map)
        part 2: the new obstruction can be placed at 6 different positions
        6
    """

    result = sum(1 for _ in map_.plan_loops())

    print(f"part 2: the new obstruction can be placed at {result} different positions")
    return result


Pos = tuple[int, int]


@dataclass(frozen=True)
class Guard:
    pos: Pos
    heading: Heading

    def next_pos(self) -> Pos:
        return self.heading.move(self.pos)

    def make_step(self) -> Self:
        return type(self)(pos=self.next_pos(), heading=self.heading)

    def turn_right(self) -> Self:
        return type(self)(pos=self.pos, heading=self.heading.right())

    def __iter__(self) -> Iterator:
        return iter((self.pos, self.heading))


class Map:

    def __init__(self, guard: Guard, obstructions: Iterable[Pos]):
        self.guard = guard
        self.obstructions = set(obstructions)
        self.bounds = Rect.with_all(self.obstructions)
        assert guard.pos in self.bounds
        assert guard.pos not in self.obstructions

    def trace_guard_path(self) -> Generator[Guard, None, bool]:
        # generates guard path
        # returns final value `True` if the guard is stuck in a loop, `False` otherwise

        guard = self.guard
        visited: set[Guard] = set()

        # move the guard, ...
        while True:
            path, left = self._guard_path_single_move(guard)
            guard = path[-1]

            # reporting its path, ...
            yield from path
            visited.update(path)

            # until she leaves the map ...
            if left:
                return False
            # or is stuck in a loop
            if guard.turn_right() in visited:
                return True

    def is_guard_looped(self) -> bool:
        return exhaust(self.trace_guard_path())

    def plan_loops(self) -> Iterable[Pos]:
        tested_positions: set[Pos] = set()

        # follow the guard in the unmodified map
        original_path = list(self.trace_guard_path())
        for guard in tqdm(original_path, desc="placing obstructions", unit=" positions"):

            # only consider positions where the guard doesn't face an existing obstruction
            if (facing_pos := guard.next_pos()) in self.obstructions:
                continue
            # also ignore positions already tested
            if facing_pos in tested_positions:
                continue

            # try placing an obstruction in front of her
            adjusted_map = type(self)(guard, self.obstructions | {facing_pos})
            # ... and check if it now results in a loop
            if adjusted_map.is_guard_looped():
                # if so, then we have one winner!
                yield facing_pos

            # the position is now marked as tested and won't be tested again
            # (otherwise the guard would have already passed it and would re-directed elsewhere)
            tested_positions.add(facing_pos)

    def _guard_path_single_move(self, init_guard: Guard | None = None) -> tuple[list[Guard], bool]:
        # returns:
        # - guard's taken path
        # - `True` if she left the map, `False` otherwise

        # turn the guard if she faces an obstruction, ...
        guard: Guard = init_guard or self.guard
        if guard.next_pos() in self.obstructions:
            guard = guard.turn_right()

        # ... then keep moving her ...
        visited: list[Guard] = []
        while True:
            visited.append(guard)
            next_guard = guard.make_step()
            # ... until she collides with an obstruction or leaves the map
            if next_guard.pos in self.obstructions or next_guard.pos not in self.bounds:
                return visited, next_guard.pos not in self.bounds

            guard = next_guard

    def move_guard(self) -> Self:
        # make a single move with the guard and return the map with her new position
        # (only used in doctests)
        (*_, guard), _ = self._guard_path_single_move()
        return type(self)(guard, self.obstructions)

    def move_guard_until_out(self) -> Self:
        # move the guard until she leaves the map and return the map with her final position
        # (only used in doctests)
        guard = self.guard
        while True:
            (*_, guard), left = self._guard_path_single_move(guard)
            if left:
                return type(self)(guard, self.obstructions)

    @classmethod
    def from_file(cls, fn: str) -> Self:
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_text(cls, text: str) -> Self:
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        guard: Guard | None = None
        obstructions: list[Pos] = []

        pos_chars: Iterable[tuple[Pos, str]] = (
            ((x, y), char)
            for y, line in enumerate(lines)
            for x, char in enumerate(line.strip())
        )

        for pos, char in pos_chars:
            match char:
                case '#':
                    obstructions.append(pos)
                case '^' | '>' | 'v' | '<' as caret:
                    assert guard is None
                    guard = Guard(pos, Heading.from_caret(caret))
                case '.' | '·':
                    pass
                case _:
                    raise ValueError(f"unexpected character: {char!r}")

        assert guard is not None
        assert obstructions

        return cls(guard, obstructions)

    def __str__(self) -> str:
        return self.draw()

    def draw(
        self,
        visited: Iterable[Guard] = (),
        show_directional_paths: bool = False,
        extra: dict[Pos, str] | None = None,
    ) -> str:
        canvas = Canvas(bounds=self.bounds)

        # draw obstructions
        canvas.draw_many((pos, '#') for pos in self.obstructions)

        # draw visited path (directional)
        if show_directional_paths:
            lines = {Heading.NORTH: '|', Heading.SOUTH: '|', Heading.WEST: '-', Heading.EAST: '-'}

            canvas.draw_many(
                ((pos, lines[heading]) for pos, heading in visited),
                blending=lambda a, b: '+' if a != b else None
            )

        # draw guard position
        canvas.draw(self.guard.pos, self.guard.heading.caret)

        # draw visited path (non-directional)
        if not show_directional_paths:
            canvas.draw_many((pos, 'X') for pos, heading in visited)

        # draw any extra chars
        if extra:
            canvas.draw_many(extra)

        return canvas.render(empty_char='·')

    def draw_loop(self, new_obstruction: Pos) -> str:
        # places new obstruction at given position, the draws the loop the guard would make with it
        # (only used in doctests)
        assert new_obstruction not in self.obstructions
        new_map = type(self)(self.guard, self.obstructions | {new_obstruction})
        return new_map.draw(
            visited=new_map.trace_guard_path(),
            show_directional_paths=True,
            extra={new_obstruction: 'O'},
        )


def main(input_fn: str = 'data/06-input.txt') -> tuple[int, int]:
    map_ = Map.from_file(input_fn)
    result_1 = part_1(map_)
    result_2 = part_2(map_)
    return result_1, result_2


if __name__ == '__main__':
    main()
