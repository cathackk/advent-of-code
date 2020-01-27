from enum import Enum
from itertools import count
from typing import Dict
from typing import Generator
from typing import Iterable
from typing import List
from typing import NamedTuple
from typing import Set
from typing import Tuple

from heading import Heading
from rect import Rect
from utils import exhaust
from utils import ro
from utils import single_value

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


Pos = Tuple[int, int]


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
    def __init__(self, tracks: Dict[Pos, str], carts: Iterable[Cart]):
        self.tracks = dict(tracks)
        self.carts, collisions = Map._place_carts(carts)
        assert not collisions

    @staticmethod
    def _place_carts(carts: Iterable[Cart]) -> Tuple[Dict[Pos, Cart], Set[Pos]]:
        by_pos: Dict[Pos, Cart] = dict()
        collisions: Set[Pos] = set()

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

    def run(self, min_carts: int = 2,) -> Generator[Tuple[int, Pos], None, int]:
        for tick in count(1):
            if len(self.carts) < min_carts:
                return tick
            for col in self.step():
                yield tick, col

    def step(self) -> Iterable[Pos]:
        """ :return: collisions """
        carts_order = sorted(self.carts.values(), key=lambda c: ro(c.pos))
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

    def _move_cart(self, cart: Cart) -> Cart:
        h = cart.heading
        new_pos = h.move(cart.pos)

        track = self.tracks[new_pos]
        if track == '|':
            assert h in north_south
            return cart.moved(pos=new_pos)
        elif track == '-':
            assert h in east_west
            return cart.moved(pos=new_pos)
        elif track == '+':
            new_heading = cart.next_turn.turn(h)
            new_next_turn = cart.next_turn.following()
            return cart.moved(pos=new_pos, heading=new_heading, next_turn=new_next_turn)
        elif track == '/':
            new_heading = h.right() if h in north_south else h.left()
            return cart.moved(pos=new_pos, heading=new_heading)
        elif track == '\\':
            new_heading = h.left() if h in north_south else h.right()
            return cart.moved(pos=new_pos, heading=new_heading)
        else:
            raise ValueError(track)

    def draw(self, collisions: Set[Pos] = None):
        def t(pos: Pos) -> str:
            if pos in self.carts:
                return str(self.carts[pos])
            elif collisions and pos in collisions:
                return 'X'
            elif pos in self.tracks:
                return self.tracks[pos]
            else:
                return ' '

        bounds = Rect.with_all(self.tracks.keys())
        for y in bounds.range_y():
            print(''.join(t((x, y)) for x in bounds.range_x()))
        print()

    @classmethod
    def load(cls, fn: str):
        tracks: Dict[Pos, str] = dict()
        carts: List[Cart] = list()

        for y, line in enumerate(open(fn)):
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


def test_first_collision():
    m = Map.load('data/13-example-1.txt')
    tick, col = next(m.run())
    assert tick == 14
    assert col == (7, 3)


def test_last_remaining():
    m = Map.load('data/13-example-2.txt')
    ticks = exhaust(m.run())
    assert ticks == 4
    last_cart = single_value(list(m.carts.values()))
    assert last_cart.pos == (6, 4)
    assert last_cart.heading == Heading.NORTH


def part_1(fn: str) -> Pos:
    m = Map.load(fn)
    tick, col = next(m.run())
    print(f"part 1: first collision on tick {tick} at pos {col}")
    return col


def part_2(fn: str) -> Pos:
    m = Map.load(fn)
    ticks = exhaust(m.run())
    last_cart = single_value(list(m.carts.values()))
    print(f"part 2: last cart after {ticks} ticks is at {last_cart.pos}")
    return last_cart.pos


if __name__ == '__main__':
    fn_ = 'data/13-input.txt'
    part_1(fn_)
    part_2(fn_)
