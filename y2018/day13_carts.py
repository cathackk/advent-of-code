"""
Advent of Code 2018
Day 13: Mine Cart Madness
https://adventofcode.com/2018/day/13
"""

from enum import Enum
from itertools import count
from typing import Iterable
from typing import Iterator
from typing import NamedTuple

from common.heading import Heading
from common.iteration import single_value
from common.rect import Pos
from common.rect import Rect
from common.utils import ro
from meta.aoc_tools import data_path


def part_1(carts_map: 'Map') -> str:
    r"""
    A crop of this size requires significant logistics to transport produce, soil, fertilizer, and
    so on. The Elves are very busy pushing things around in **carts** on some kind of rudimentary
    system of tracks they've come up with.

    Seeing as how cart-and-track systems don't appear in recorded history for another 1000 years,
    the Elves seem to be making this up as they go along. They haven't even figured out how to avoid
    collisions yet.

    You map out the tracks (your puzzle input) and see where you can help.

    Tracks consist of straight paths (`|` and `-`), curves (`/` and `\`), and intersections (`+`).
    Curves connect exactly two perpendicular pieces of track; for example, this is a closed loop:

        /----\
        |    |
        |    |
        \----/

    Intersections occur when two perpendicular paths cross. At an intersection, a cart is capable of
    turning left, turning right, or continuing straight. Here are two loops connected by two
    intersections:

        /-----\
        |     |
        |  /--+--\
        |  |  |  |
        \--+--/  |
           |     |
           \-----/

    Several **carts** are also on the tracks. Carts always face either up (`^`), down (`v`), left
    (`<`), or right (`>`). (On your initial map, the track under each cart is a straight path
    matching the direction the cart is facing.)

    Each time a cart has the option to turn (by arriving at any intersection), it turns **left** the
    first time, goes **straight** the second time, turns **right** the third time, and then repeats
    those directions starting again with left the fourth time, straight the fifth time, and so on.
    This process is independent of the particular intersection at which the cart has arrived - that
    is, the cart has no per-intersection memory.

    Carts all move at the same speed; they take turns moving a single step at a time. They do this
    based on their **current location**: carts on the top row move first (acting from left to
    right), then carts on the second row move (again from left to right), then carts on the third
    row, and so on. Once each cart has moved one step, the process repeats; each of these loops is
    called a **tick**.

    For example, suppose there are two carts on a straight track:

        |  |  |  |  |
        v  |  |  |  |
        |  v  v  |  |
        |  |  |  v  X
        |  |  ^  ^  |
        ^  ^  |  |  |
        |  |  |  |  |

    First, the top cart moves. It is facing down (`v`), so it moves down one square. Second, the
    bottom cart moves. It is facing up (`^`), so it moves up one square. Because all carts have
    moved, the first tick ends. Then, the process repeats, starting with the first cart. The first
    cart moves down, then the second cart moves up - right into the first cart, colliding with it!
    (The location of the crash is marked with an `X`.) This ends the second and last tick.

    Here is a longer example:

        >>> example_map = Map.from_file('data/13-example-1.txt')
        >>> example_map.run(draw=True)
        /->-\
        |   |  /----\
        | /-+--+-\  |
        | | |  | v  |
        \-+-/  \-+--/
          \------/
        <BLANKLINE>
        /-->\
        |   |  /----\
        | /-+--+-\  |
        | | |  | |  |
        \-+-/  \->--/
          \------/
        <BLANKLINE>
        /---v
        |   |  /----\
        | /-+--+-\  |
        | | |  | |  |
        \-+-/  \-+>-/
          \------/
        <BLANKLINE>
        /---\
        |   v  /----\
        | /-+--+-\  |
        | | |  | |  |
        \-+-/  \-+->/
          \------/
        <BLANKLINE>
        /---\
        |   |  /----\
        | /->--+-\  |
        | | |  | |  |
        \-+-/  \-+--^
          \------/
        <BLANKLINE>
        /---\
        |   |  /----\
        | /-+>-+-\  |
        | | |  | |  ^
        \-+-/  \-+--/
          \------/
        <BLANKLINE>
        /---\
        |   |  /----\
        | /-+->+-\  ^
        | | |  | |  |
        \-+-/  \-+--/
          \------/
        <BLANKLINE>
        /---\
        |   |  /----<
        | /-+-->-\  |
        | | |  | |  |
        \-+-/  \-+--/
          \------/
        <BLANKLINE>
        /---\
        |   |  /---<\
        | /-+--+>\  |
        | | |  | |  |
        \-+-/  \-+--/
          \------/
        <BLANKLINE>
        /---\
        |   |  /--<-\
        | /-+--+-v  |
        | | |  | |  |
        \-+-/  \-+--/
          \------/
        <BLANKLINE>
        /---\
        |   |  /-<--\
        | /-+--+-\  |
        | | |  | v  |
        \-+-/  \-+--/
          \------/
        <BLANKLINE>
        /---\
        |   |  /<---\
        | /-+--+-\  |
        | | |  | |  |
        \-+-/  \-<--/
          \------/
        <BLANKLINE>
        /---\
        |   |  v----\
        | /-+--+-\  |
        | | |  | |  |
        \-+-/  \<+--/
          \------/
        <BLANKLINE>
        /---\
        |   |  /----\
        | /-+--v-\  |
        | | |  | |  |
        \-+-/  ^-+--/
          \------/
        <BLANKLINE>
        /---\
        |   |  /----\
        | /-+--+-\  |
        | | |  X |  |
        \-+-/  \-+--/
          \------/

    After following their respective paths for a while, the carts eventually crash. To help prevent
    crashes, you'd like to know **the location of the first crash**. Locations are given in `X,Y`
    coordinates, where the furthest left column is `X=0` and the furthest top row is `Y=0`:

        >>> example_map.draw(collisions=[(7, 3)], coordinates=True)
                   111
         0123456789012
        0/---\
        1|   |  /----\
        2| /-+--+-\  |
        3| | |  X |  |
        4\-+-/  \-+--/
        5  \------/

    In this example, the location of the first crash is **`7,3`**.

        >>> part_1(Map.from_file('data/13-example-1.txt'))
        part 1: first collision happens after 14 ticks at 7,3
        '7,3'
    """

    carts_map = carts_map.copy()
    tick, (collision_x, collision_y) = next(carts_map.collisions())
    result = f"{collision_x},{collision_y}"

    print(f"part 1: first collision happens after {tick} ticks at {result}")
    return result


def part_2(carts_map: 'Map') -> str:
    r"""
    There isn't much you can do to prevent crashes in this ridiculous system. However, by predicting
    the crashes, the Elves know where to be in advance and **instantly remove the two crashing
    carts** the moment any crash occurs.

    They can proceed like this for a while, but eventually, they're going to run out of carts. It
    could be useful to figure out where the last cart that **hasn't** crashed will end up.

    For example:

        >>> example_map = Map.from_file('data/13-example-2.txt')
        >>> example_map.run(draw=True)
        />-<\
        |   |
        | /<+-\
        | | | v
        \>+</ |
          |   ^
          \<->/
        <BLANKLINE>
        /-X-\
        |   |
        | v-+-\
        | | | |
        \-X-/ X
          |   |
          ^---^
        <BLANKLINE>
        /---\
        |   |
        | /-+-\
        | v | |
        \-+-/ |
          ^   ^
          \---/
        <BLANKLINE>
        /---\
        |   |
        | /-+-\
        | | | |
        \-X-/ ^
          |   |
          \---/

    After four very expensive crashes, a tick ends with only one cart remaining; its final location
    is 6,4.

        >>> single_value(example_map.carts)
        (6, 4)

    **What is the location of the last cart** at the end of the first tick where it is the only cart
    left?

        >>> part_2(Map.from_file('data/13-example-2.txt'))
        part 2: last remaining cart is at 6,4
        '6,4'
    """

    carts_map = carts_map.copy()
    carts_map.run()  # run until last cart remains
    last_cart_x, last_cart_y = single_value(carts_map.carts)
    result = f"{last_cart_x},{last_cart_y}"

    print(f"part 2: last remaining cart is at {result}")
    return result


heading_chars = {
    Heading.NORTH: '^',
    Heading.EAST:  '>',
    Heading.SOUTH: 'v',
    Heading.WEST:  '<'
}
c2h = {c: h for h, c in heading_chars.items()}
north_south = {Heading.NORTH, Heading.SOUTH}
east_west = {Heading.EAST, Heading.WEST}


class Turn(Enum):
    LEFT = 0
    STRAIGHT = 1
    RIGHT = 2

    def following(self) -> 'Turn':
        return Turn((self.value + 1) % 3)

    def turn(self, heading: Heading) -> Heading:
        if self is Turn.LEFT:
            return heading.left()
        elif self is Turn.STRAIGHT:
            return heading
        elif self is Turn.RIGHT:
            return heading.right()
        else:
            raise KeyError(self)


class Cart(NamedTuple):
    pos: Pos
    heading: Heading
    next_turn: Turn = Turn.LEFT

    def moved(self, *, pos: Pos = None, heading: Heading = None, next_turn: Turn = None):
        return type(self)(
            pos=pos or self.pos,
            heading=heading or self.heading,
            next_turn=next_turn or self.next_turn
        )

    def __str__(self):
        return heading_chars[self.heading]


class Map:
    def __init__(self, tracks: dict[Pos, str], carts: Iterable[Cart]):
        self.tracks = dict(tracks)
        self.carts, collisions = Map._place_carts(carts)
        assert not collisions

    def copy(self) -> 'Map':
        return type(self)(self.tracks, self.carts.values())

    @staticmethod
    def _place_carts(carts: Iterable[Cart]) -> tuple[dict[Pos, Cart], set[Pos]]:
        by_pos: dict[Pos, Cart] = {}
        collisions: set[Pos] = set()

        for cart in carts:
            pos = cart.pos
            if pos not in by_pos and pos not in collisions:
                by_pos[pos] = cart
            elif pos in by_pos:
                # collision!
                collisions.add(pos)
                del by_pos[pos]
            elif pos in collisions:
                # multiple collision!
                pass

        return by_pos, collisions

    def collisions(self, min_carts: int = 2) -> Iterator[tuple[int, Pos]]:
        for tick in count(1):
            step_collisions = self.step()
            for collision in step_collisions:
                yield tick, collision
            if len(self.carts) < min_carts:
                break

    def run(self, min_carts: int = 2, draw: bool = False) -> None:
        if draw:
            self.draw()

        while len(self.carts) >= min_carts:
            collisions = self.step()
            if draw:
                print()
                self.draw(collisions)

    def step(self) -> list[Pos]:
        """ :return: collisions """
        carts_order = sorted(self.carts.values(), key=lambda c: ro(c.pos))

        def collisions() -> Iterable[Pos]:
            for cart in carts_order:
                if cart.pos not in self.carts:
                    # already collided
                    continue
                del self.carts[cart.pos]
                new_cart = self._move_cart(cart)
                if new_cart.pos not in self.carts:
                    self.carts[new_cart.pos] = new_cart
                else:
                    # collision! kill both
                    del self.carts[new_cart.pos]
                    yield new_cart.pos
                    # TODO: multiple collisions?

        return list(collisions())

    def _move_cart(self, cart: Cart) -> Cart:
        heading = cart.heading
        new_pos = heading.move(cart.pos)

        track = self.tracks[new_pos]
        if track == '|':
            assert heading in north_south
            return cart.moved(pos=new_pos)
        elif track == '-':
            assert heading in east_west
            return cart.moved(pos=new_pos)
        elif track == '+':
            new_heading = cart.next_turn.turn(heading)
            new_next_turn = cart.next_turn.following()
            return cart.moved(pos=new_pos, heading=new_heading, next_turn=new_next_turn)
        elif track == '/':
            new_heading = heading.right() if heading in north_south else heading.left()
            return cart.moved(pos=new_pos, heading=new_heading)
        elif track == '\\':
            new_heading = heading.left() if heading in north_south else heading.right()
            return cart.moved(pos=new_pos, heading=new_heading)
        else:
            raise ValueError(track)

    def __str__(self) -> str:
        return self.drawn()

    def drawn(self, collisions: Iterable[Pos] = None, coordinates: bool = False) -> str:
        collisions_set = set(collisions or ())

        def char(pos: Pos) -> str:
            if pos in self.carts:
                return str(self.carts[pos])
            elif pos in collisions_set:
                return 'X'
            elif pos in self.tracks:
                return self.tracks[pos]
            else:
                return ' '

        bounds = Rect.with_all(self.tracks.keys())

        def lines() -> Iterable[str]:
            if coordinates:
                for coordinates_row in zip(*(str(x).rjust(2) for x in bounds.range_x())):
                    yield " " + "".join(coordinates_row)
            for y in bounds.range_y():
                y_coor = str(y) if coordinates else ""
                yield y_coor + "".join(char((x, y)) for x in bounds.range_x()).rstrip()

        return "\n".join(lines())

    def draw(self, collisions: Iterable[Pos] = None, coordinates: bool = False) -> None:
        print(self.drawn(collisions, coordinates))

    @classmethod
    def from_text(cls, text: str) -> 'Map':
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_file(cls, fn: str) -> 'Map':
        return cls.from_lines(open(fn))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Map':
        tracks: dict[Pos, str] = {}
        carts: list[Cart] = []

        for y, line in enumerate(lines):
            for x, c in enumerate(line.rstrip()):
                pos = (x, y)
                if c in '^>v<':
                    carts.append(Cart(pos, heading=c2h[c]))
                    tracks[pos] = '|' if c in '^v' else '-'
                elif c in '|-/\\+':
                    tracks[pos] = c
                elif c == ' ':
                    pass
                else:
                    raise ValueError(c)

        return Map(tracks, carts)


def main(input_path: str = data_path(__file__)) -> tuple[str, str]:
    carts_map = Map.from_file(input_path)
    result_1 = part_1(carts_map)
    result_2 = part_2(carts_map)
    return result_1, result_2


if __name__ == '__main__':
    main()
