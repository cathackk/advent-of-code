"""
Advent of Code 2017
Day 19: A Series of Tubes
https://adventofcode.com/2017/day/19
"""

from dataclasses import dataclass
from typing import Iterable
from typing import Iterator

from common.heading import Heading
from meta.aoc_tools import data_path


def part_1(diagram: 'Diagram') -> str:
    """
    Somehow, a network packet got lost and ended up here. It's trying to follow a routing diagram
    (your puzzle input), but it's confused about where to go.

    Its starting point is just off the top of the diagram. Lines (drawn with `|`, `-`, and `+`) show
    the path it needs to take, starting by going down onto the only line connected to the top of the
    diagram. It needs to follow this path until it reaches the end (located somewhere within the
    diagram) and stop there.

    Sometimes, the lines cross over each other; in these cases, it needs to continue going the same
    direction, and only turn left or right when there's no other option. In addition, someone has
    left **letters** on the line; these also don't change its direction, but it can use them to keep
    track of where it's been. For example:

        >>> example_diagram = Diagram.from_text('''
        ...      |
        ...      |  +--+
        ...      A  |  C
        ...  F---|----E|--+
        ...      |  |  |  D
        ...      +B-+  +--+
        ... ''')

    Given this diagram, the packet needs to take the following path:

        >>> routes = example_diagram.routes()

      - Starting at the only line touching the top of the diagram, it must go down, pass through
        `A`, and continue onward to the first `+`:

        >>> next(routes)
        Route(start=(5, 0), heading=Heading.SOUTH, length=5, letters=['A'])

      - Travel right, up, and right, passing through `B` in the process:

        >>> next(routes)
        Route(start=(5, 5), heading=Heading.EAST, length=3, letters=['B'])
        >>> next(routes)
        Route(start=(8, 5), heading=Heading.NORTH, length=4, letters=[])
        >>> next(routes)
        Route(start=(8, 1), heading=Heading.EAST, length=3, letters=[])

      - Continue down (collecting `C`), right, and up (collecting `D`):

        >>> next(routes)
        Route(start=(11, 1), heading=Heading.SOUTH, length=4, letters=['C'])
        >>> next(routes)
        Route(start=(11, 5), heading=Heading.EAST, length=3, letters=[])
        >>> next(routes)
        Route(start=(14, 5), heading=Heading.NORTH, length=2, letters=['D'])

      - Finally, go all the way left through `E` and stopping at `F`:

        >>> next(routes)
        Route(start=(14, 3), heading=Heading.WEST, length=14, letters=['E', 'F'])
        >>> next(routes)
        Traceback (most recent call last):
        ...
        StopIteration

    Following the path to the end, the letters it sees on its path are `ABCDEF`.

    The little packet looks up at you, hoping you can help it find the way. **What letters will it
    see (in the order it would see them) if it follows the path? (The routing diagram is very wide;
    make sure you view it without line wrapping.)

        >>> part_1(example_diagram)
        part 1: letters seen: ABCDEF
        'ABCDEF'
    """

    letters_seen = ''.join(
        letter
        for route in diagram.routes()
        for letter in route.letters
    )

    print(f"part 1: letters seen: {letters_seen}")
    return letters_seen


def part_2(diagram: 'Diagram') -> int:
    r"""
    The packet is curious how many steps it needs to go.

    For example, using the same routing diagram from the example above, the packet would go:

        >>> example_diagram = Diagram.from_file('data/19-example.txt')
        >>> print("\n".join(f"- {route}" for route in example_diagram.routes()))
        - 5 steps down
        - 3 steps right
        - 4 steps up
        - 3 steps right
        - 4 steps down
        - 3 steps right
        - 2 steps up
        - 14 steps left

    This would result in a total of `38` steps.

    **How many steps** does the packet need to go?

        >>> part_2(example_diagram)
        part 2: traversal is 38 steps long
        38
    """

    steps = sum(route.length for route in diagram.routes())
    print(f"part 2: traversal is {steps} steps long")
    return steps


Pos = tuple[int, int]


@dataclass(frozen=True)
class Route:
    start: Pos
    heading: Heading
    length: int
    letters: list[str]

    @property
    def heading_name(self) -> str:
        return {
            Heading.NORTH: "up",
            Heading.EAST: "right",
            Heading.SOUTH: "down",
            Heading.WEST: "left"
        }[self.heading]

    def __str__(self) -> str:
        steps_noun = "step" if self.length == 1 else "steps"
        return f"{self.length} {steps_noun} {self.heading_name}"


class Diagram:
    def __init__(self, locations: Iterable[tuple[Pos, str]] | dict[Pos, str]):
        self.locations: dict[Pos, str] = dict(locations)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.locations!r})'

    def entrance(self) -> tuple[Pos, Heading]:
        # entrance is always on the top, so don't bother scanning the other sides for entrances
        heading = Heading.SOUTH
        try:
            start = next(
                (x, y)
                for (x, y), char in self.locations.items()
                if y == 0
                if char == '|'
            )
            return start, heading

        except StopIteration as stop:
            raise ValueError("unable to find entrance") from stop

    def routes(self) -> Iterator[Route]:

        pos, heading = self.entrance()

        while True:
            # start of one route - a straight line traversed
            route_start = pos
            route_length = 0
            route_letters: list[str] = []

            while True:
                # follow the route step-by-step
                pos = heading.move(pos)
                route_length += 1
                char = self.locations.get(pos)

                if char is None:
                    # end of traversal!
                    yield Route(route_start, heading, route_length, route_letters)
                    return

                elif char == '+':
                    # end of route!
                    yield Route(route_start, heading, route_length, route_letters)
                    break

                elif char.isalpha():
                    # collect a letter
                    route_letters.append(char)

                elif char in ('-', '|'):
                    # go on ...
                    pass

                else:
                    raise ValueError(f"unsupported char! char={char!r}, at={pos!r}")

            # after each route, we need to turn right or left
            if (turn_right := heading.right()).move(pos) in self.locations:
                heading = turn_right
            elif (turn_left := heading.left()).move(pos) in self.locations:
                heading = turn_left
            else:
                raise ValueError(f"nowhere to turn! pos={pos!r}, heading={heading!r}")

    @classmethod
    def from_text(cls, text: str) -> 'Diagram':
        return cls.from_lines(text.strip('\n').splitlines())

    @classmethod
    def from_file(cls, fn: str) -> 'Diagram':
        return cls.from_lines(open(fn))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Diagram':
        return cls(
            ((x, y), char)
            for y, line in enumerate(lines)
            for x, char in enumerate(line.rstrip())
            if char != ' '
        )


def main(input_path: str = data_path(__file__)) -> tuple[str, int]:
    diagram = Diagram.from_file(input_path)
    result_1 = part_1(diagram)
    result_2 = part_2(diagram)
    return result_1, result_2


if __name__ == '__main__':
    main()
