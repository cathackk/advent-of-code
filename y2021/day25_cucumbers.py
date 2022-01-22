"""
Advent of Code 2021
Day 25: Sea Cucumber
https://adventofcode.com/2021/day/25
"""

from itertools import count
from typing import Iterable

from tqdm import tqdm

from common.file import relative_path


def part_1(initial_map: 'Map') -> int:
    """
    There are two herds of sea cucumbers sharing the same region; one always moves east (`>`), while
    the other always moves south (`v`). Each location can contain at most one sea cucumber; the
    remaining locations are empty (`.`). The submarine helpfully generates a map of the situation
    (your puzzle input). For example:

        >>> sea_floor = Map.from_text('''
        ...
        ...     v...>>.vv>
        ...     .vv>>.vv..
        ...     >>.>v>...v
        ...     >>v>>.>.v.
        ...     v>v.vv.v..
        ...     >.>>..v...
        ...     .vv..>.>v.
        ...     v.v..>>v.v
        ...     ....v..v.>
        ...
        ... ''')
        >>> sea_floor.width, sea_floor.height
        (10, 9)

    Every **step**, the sea cucumbers in the east-facing herd attempt to move forward one location,
    then the sea cucumbers in the south-facing herd attempt to move forward one location. When
    a herd moves forward, every sea cucumber in the herd first simultaneously considers whether
    there is a sea cucumber in the adjacent location it's facing (even another sea cucumber facing
    the same direction), and then every sea cucumber facing an empty location simultaneously moves
    into that location.

    So, in a situation like this:

        >>> mini_0 = Map.from_text('...>>>>>...')
        >>> print(mini_0)
        ···>>>>>···

    After one step, only the rightmost sea cucumber would have moved:

        >>> print(mini_1 := mini_0.step())
        ···>>>>·>··

    After the next step, two sea cucumbers move:

        >>> print(mini_1.step())
        ···>>>·>·>·

    During a single step, the east-facing herd moves first, then the south-facing herd moves.
    So, given this situation:

        >>> small_0 = Map.from_text('''
        ...
        ...     ..........
        ...     .>v....v..
        ...     .......>..
        ...     ..........
        ...
        ... ''')

    After a single step, of the sea cucumbers on the left, only the south-facing sea cucumber has
    moved (as it wasn't out of the way in time for the east-facing cucumber on the left to move),
    but both sea cucumbers on the right have moved (as the east-facing sea cucumber moved out of the
    way of the south-facing sea cucumber):

        >>> print(small_0.step())
        ··········
        ·>········
        ··v····v>·
        ··········

    Due to **strong water currents** in the area, sea cucumbers that move off the right edge of the
    map appear on the left edge, and sea cucumbers that move off the bottom edge of the map appear
    on the top edge. Sea cucumbers always check whether their destination location is empty before
    moving, even if that destination is on the opposite side of the map:

        >>> medium = Map.from_file('data/25-example-medium.txt')
        >>> _ = run(medium, steps_limit=4, log=True)
        Initial state:
        ···>···
        ·······
        ······>
        v·····>
        ······>
        ·······
        ··vvv··
        -------
        After 1 step:
        ··vv>··
        ·······
        >······
        v·····>
        >······
        ·······
        ····v··
        -------
        After 2 steps:
        ····v>·
        ··vv···
        ·>·····
        ······>
        v>·····
        ·······
        ·······
        -------
        After 3 steps:
        ······>
        ··v·v··
        ··>v···
        >······
        ··>····
        v······
        ·······
        -------
        After 4 steps:
        >······
        ··v····
        ··>·v··
        ·>·v···
        ···>···
        ·······
        v······

    To find a safe place to land your submarine, the sea cucumbers need to stop moving. Again
    consider the first example:

        >>> s = run(sea_floor, log=list(range(6)) + list(range(10, 60, 10)) + list(range(55, 60)))
        Initial state:
        v···>>·vv>
        ·vv>>·vv··
        >>·>v>···v
        >>v>>·>·v·
        v>v·vv·v··
        >·>>··v···
        ·vv··>·>v·
        v·v··>>v·v
        ····v··v·>
        ----------
        After 1 step:
        ····>·>v·>
        v·v>·>v·v·
        >v>>··>v··
        >>v>v>·>·v
        ·>v·v···v·
        v>>·>vvv··
        ··v···>>··
        vv···>>vv·
        >·v·v··v·v
        ----------
        After 2 steps:
        >·v·v>>··v
        v·v·>>vv··
        >v>·>·>·v·
        >>v>v·>v>·
        ·>··v····v
        ·>v>>·v·v·
        v····v>v>·
        ·vv··>>v··
        v>·····vv·
        ----------
        After 3 steps:
        v>v·v>·>v·
        v···>>·v·v
        >vv>·>v>··
        >>v>v·>·v>
        ··>····v··
        ·>·>v>v··v
        ··v··v>vv>
        v·v··>>v··
        ·v>····v··
        ----------
        After 4 steps:
        v>··v·>>··
        v·v·>·>·v·
        >vv·>>·v>v
        >>·>··v>·>
        ··v>v···v·
        ··>>·>vv··
        >·v·vv>v·v
        ·····>>vv·
        vvv>···v··
        ----------
        After 5 steps:
        vv>···>v>·
        v·v·v>·>v·
        >·v·>·>·>v
        >v>·>··v>>
        ··v>v·v···
        ··>·>>vvv·
        ·>···v>v··
        ··v·v>>v·v
        v·v·>···v·
        ----------
        ...
        ----------
        After 10 steps:
        ··>··>>vv·
        v·····>>·v
        ··v·v>>>v>
        v>·>v·>>>·
        ··v>v·vv·v
        ·v·>>>·v··
        v·v··>v>··
        ··v···>v·>
        ·vv··v>vv·
        ----------
        ...
        ----------
        After 20 steps:
        v>·····>>·
        >vv>·····v
        ·>v>v·vv>>
        v>>>v·>v·>
        ····vv>v··
        ·v·>>>vvv·
        ··v··>>vv·
        v·v···>>·v
        ··v·····v>
        ----------
        ...
        ----------
        After 30 steps:
        ·vv·v··>>>
        v>···v···>
        >·v>·>vv·>
        >v>·>·>v·>
        ·>··v·vv··
        ··v>··>>v·
        ····v>··>v
        v·v···>vv>
        v·v···>vvv
        ----------
        ...
        ----------
        After 40 steps:
        >>v>v··v··
        ··>>v··vv·
        ··>>>v·>·v
        ··>>>>vvv>
        v·····>···
        v·v···>v>>
        >vv·····v>
        ·>v···v·>v
        vvv·v··v·>
        ----------
        ...
        ----------
        After 50 steps:
        ··>>v>vv·v
        ··v·>>vv··
        v·>>v>>v··
        ··>>>>>vv·
        vvv····>vv
        ··v····>>>
        v>·······>
        ·vv>····v>
        ·>v·vv·v··
        ----------
        ...
        ----------
        After 55 steps:
        ··>>v>vv··
        ··v·>>vv··
        ··>>v>>vv·
        ··>>>>>vv·
        v······>vv
        v>v····>>v
        vvv···>··>
        >vv·····>·
        ·>v·vv·v··
        ----------
        After 56 steps:
        ··>>v>vv··
        ··v·>>vv··
        ··>>v>>vv·
        ··>>>>>vv·
        v······>vv
        v>v····>>v
        vvv····>·>
        >vv······>
        ·>v·vv·v··
        ----------
        After 57 steps:
        ··>>v>vv··
        ··v·>>vv··
        ··>>v>>vv·
        ··>>>>>vv·
        v······>vv
        v>v····>>v
        vvv·····>>
        >vv······>
        ·>v·vv·v··
        ----------
        After 58 steps:
        ··>>v>vv··
        ··v·>>vv··
        ··>>v>>vv·
        ··>>>>>vv·
        v······>vv
        v>v····>>v
        vvv·····>>
        >vv······>
        ·>v·vv·v··

    In this example, the sea cucumbers stop moving after **`58`** steps.

        >>> s
        58

    Find somewhere safe to land your submarine. **What is the first step on which no sea cucumbers
    move?**

        >>> part_1(sea_floor)
        part 1: sea cucumbers stop moving after 58 steps
        58
    """

    result = run(initial_map)

    print(f"part 1: sea cucumbers stop moving after {result} steps")
    return result


Pos = tuple[int, int]


class Map:

    def __init__(self, width: int, height: int, cucumbers: Iterable[tuple[Pos, str]]):
        self.width = width
        self.height = height
        self.cucumbers = dict(cucumbers)

    def __str__(self) -> str:
        return '\n'.join(
            ''.join(self.cucumbers.get((x, y), '·') for x in range(self.width))
            for y in range(self.height)
        )

    @classmethod
    def from_text(cls, text: str) -> 'Map':
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_file(cls, fn: str) -> 'Map':
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Map':
        lines = [line.strip() for line in lines]
        assert len(lines) > 0
        width, height = len(lines[0]), len(lines)
        assert width > 0
        assert all(width == len(line) for line in lines[1:])  # all lines have the same width

        def parse_chr(c: str) -> str | None:
            if c in ('v', '>'):
                return c
            elif c in ('.', '·'):
                return None
            else:
                raise ValueError(c)

        return Map(
            width=width,
            height=height,
            cucumbers=(
                ((x, y), cucumber)
                for y, line in enumerate(lines)
                for x, ch in enumerate(line)
                if (cucumber := parse_chr(ch))
            )
        )

    def step(self) -> 'Map':
        # 1. move east
        def east(pos: Pos) -> Pos:
            x, y = pos
            return (x + 1) % self.width, y

        moving_east = {
            pos: pos1
            for pos, c in self.cucumbers.items()
            if c == '>'
            if (pos1 := east(pos)) not in self.cucumbers
        }

        cucumbers_moved_east = {
            moving_east.get(pos, pos): c
            for pos, c in self.cucumbers.items()
        }

        # 2. move south
        def south(pos: Pos) -> Pos:
            x, y = pos
            return x, (y + 1) % self.height

        moving_south = {
            pos: pos1
            for pos, c in cucumbers_moved_east.items()
            if c == 'v'
            if (pos1 := south(pos)) not in cucumbers_moved_east
        }

        if not moving_east and not moving_south:
            # no move possible
            raise StopIteration("no move possible")

        return type(self)(
            width=self.width,
            height=self.height,
            cucumbers=(
                (moving_south.get(pos, pos), c)
                for pos, c in cucumbers_moved_east.items()
            )
        )


def run(initial_map: Map, steps_limit: int = None, log: bool | Iterable[int] = False) -> int:
    current_map = initial_map

    last_step_logged = None

    def should_log(step_: int) -> int:
        return log if isinstance(log, bool) else step_ in log

    if should_log(0):
        print("Initial state:")
        print(current_map)
        last_step_logged = 0

    for step in tqdm(count(1), unit="steps", desc="moving cucumbers", delay=1.0):
        try:
            current_map = current_map.step()

        except StopIteration:
            return step

        finally:
            if should_log(step):
                if step - last_step_logged > 1:
                    print("-" * current_map.width)
                    print("...")
                print("-" * current_map.width)
                noun = "step" if step == 1 else "steps"
                print(f"After {step} {noun}:")
                print(current_map)
                last_step_logged = step

        if steps_limit is not None and step >= steps_limit:
            return step

    # unreachable
    assert False


if __name__ == '__main__':
    initial_map_ = Map.from_file('data/25-input.txt')
    part_1(initial_map_)
