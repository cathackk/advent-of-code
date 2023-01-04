"""
Advent of Code 2016
Day 17: Two Steps Forward
https://adventofcode.com/2016/day/17
"""

from enum import Enum
from typing import Iterable

from common.graph import shortest_path
from common.md5 import md5
from common.rect import Rect
from meta.aoc_tools import data_path


def part_1(password: str) -> str:
    """
    You're trying to access a secure vault protected by a `4x4` grid of small rooms connected by
    doors. You start in the top-left room (marked `S`), and you can access the vault (marked `V`)
    once you reach the bottom-right room:

        #########
        #S| | | #
        #-#-#-#-#
        # | | | #
        #-#-#-#-#
        # | | | #
        #-#-#-#-#
        # | | |
        ####### V

    Fixed walls are marked with `#`, and doors are marked with `-` or `|`.

    The doors in your **current room** are either open or closed (and locked) based on the
    hexadecimal MD5 hash of a passcode (your puzzle input) followed by a sequence of uppercase
    characters representing the **path you have taken so far** (`U` for up, `D` for down,
    `L` for left, and `R` for right).

        >>> list(Direction.from_path('UDLR'))
        [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]

    Only the first four characters of the hash are used; they represent, respectively, the doors
    **up, down, left, and right** from your current position. Any `b`, `c`, `d`, `e`, or `f` means
    that the corresponding door is **open**; any other character (any number or `a`) means that the
    corresponding door is **closed and locked**.

    To access the vault, all you need to do is reach the bottom-right room; reaching this room opens
    the vault and all doors in the maze.

    For example, suppose the passcode is `hijkl`. Initially, you have taken no steps, and so your
    path is empty: you simply find the MD5 hash of `hijkl` alone. The first four characters of this
    hash are `ced9`, which indicate that up is open (`c`), down is open (`e`), left is open (`d`),
    and right is closed and locked (`9`). Because you start in the top-left corner, there are no
    "up" or "left" doors to be open, so your only choice is **down**:

        >>> dict(Room().neighbors(password='hijkl'))
        {'D': Room('D', (0, 1))}

    Next, having gone only one step (down, or `D`), you find the hash of `hijklD`. This produces
    `f2bc`, which indicates that you can go back up, left (but that's a wall), or right:

        >>> dict(Room('D').neighbors('hijkl'))
        {'U': Room('DU', (0, 0)), 'R': Room('DR', (1, 1))}

    Going right means hashing `hijklDR` to get `5745` - all doors closed and locked:

        >>> dict(Room('DR').neighbors('hijkl'))
        {}

    However, going **up** instead is worthwhile: even though it returns you to the room you started
    in, your path would then be `DU`, opening a **different set of doors**. After going DU (and then
    hashing `hijklDU` to get `528e`), only the right door is open:

        >>> dict(Room('DU').neighbors('hijkl'))
        {'R': Room('DUR', (1, 0))}

    After going `DUR`, all doors lock:

        >>> dict(Room('DUR').neighbors('hijkl'))
        {}

    Fortunately, your actual passcode is not `hijkl`. Passcodes actually used by Easter Bunny Vault
    Security do allow access to the vault if you know the right path. For example:

        >>> find_shortest_path('ihgpwlah')
        'DDRRRD'
        >>> find_shortest_path('kglvqrro')
        'DDUDRLRRUDRD'
        >>> find_shortest_path('ulqzkmiv')
        'DRURDRUDDLLDLUURRDULRLDUUDDDRR'

    Given your vault's passcode, **what is the shortest path** (the actual path, not just the
    length) to reach the vault?

        >>> part_1('ihgpwlah')
        part 1: shortest path to reach the vault is 'DDRRRD'
        'DDRRRD'
    """

    path = find_shortest_path(password)
    print(f"part 1: shortest path to reach the vault is {path!r}")
    return path


def part_2(password: str) -> int:
    """
    You're curious how robust this security solution really is, and so you decide to find longer and
    longer paths which still provide access to the vault. You remember that paths always end the
    first time they reach the bottom-right room (that is, they can never pass through it, only end
    in it).

    For example:

        >>> len(find_longest_path('ihgpwlah'))
        370
        >>> len(find_longest_path('kglvqrro'))
        492
        >>> len(find_longest_path('ulqzkmiv'))
        830

    What is the **length of the longest path** that reaches the vault?

        >>> part_2('ihgpwlah')
        part 2: longest path to reach the vault is 370 steps long
        370
    """
    steps = len(find_longest_path(password))
    print(f"part 2: longest path to reach the vault is {steps} steps long")
    return steps


Pos = tuple[int, int]


class Direction(Enum):
    UP = ('U', 0, -1)
    DOWN = ('D', 0, +1)
    LEFT = ('L', -1, 0)
    RIGHT = ('R', +1, 0)

    def __init__(self, letter: str, dx: int, dy: int):
        self.letter = letter
        self.dx = dx
        self.dy = dy

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'

    @classmethod
    def from_letter(cls, letter: str) -> 'Direction':
        try:
            return next(d for d in cls if d.letter == letter)
        except StopIteration as stop:
            raise KeyError(letter) from stop

    @classmethod
    def from_path(cls, path: str) -> Iterable['Direction']:
        return (cls.from_letter(letter) for letter in path)

    def __add__(self, other):
        x, y = other
        return x + self.dx, y + self.dy

    def __radd__(self, other):
        return self + other


BOUNDS = Rect.at_origin(4, 4)


def walk(path: str, start: Pos = BOUNDS.top_left) -> Pos:
    pos = start

    for step in Direction.from_path(path):
        pos += step
        assert pos in BOUNDS

    return pos


class Room():
    def __init__(self, path: str = '', pos: Pos = None):
        self.path = path
        self.pos = pos or walk(path)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.path!r}, {self.pos!r})'

    def is_vault(self) -> bool:
        return self.pos == BOUNDS.bottom_right

    def neighbors(self, password: str) -> Iterable[tuple[str, 'Room']]:
        if self.is_vault():
            # no door open in the vault
            return

        digest = md5(password + self.path)
        open_doors = (
            direction
            for direction, char in zip(Direction, digest[:4])
            if char in 'bcdef'
        )

        for direction in open_doors:
            new_pos = self.pos + direction
            if new_pos not in BOUNDS:
                continue
            yield direction.letter, type(self)(self.path + direction.letter, new_pos)

    def _key(self) -> tuple:
        if self.is_vault():
            # all vault rooms are the same, no matter how you reach them
            return '...', self.pos
        else:
            return self.path, self.pos

    def __hash__(self) -> int:
        return hash(self._key())

    def __eq__(self, other):
        return isinstance(other, type(self)) and self._key() == other._key()


def find_shortest_path(password: str, start: Room = None, end: Room = None) -> str:
    _, path = shortest_path(
        start=start or Room(),
        target=end or Room('...', BOUNDS.bottom_right),
        edges=lambda room: (
            (new_room, direction, 1)
            for direction, new_room in room.neighbors(password)
        )
    )
    return ''.join(path)


def find_longest_path(password: str, start: Room = None, end: Room = None) -> str:
    _, path = shortest_path(
        start=start or Room(),
        target=end or Room('...', BOUNDS.bottom_right),
        edges=lambda room: (
            # to find the **longest** path instead of shortest, we have to hack the Dijkstra a bit:
            # - non-vault rooms have negative distance = go through as many as possible
            # - the vault room has very large distance = pick it only at the last possible moment
            (new_room, direction, 1 << 20 if new_room.is_vault() else -1)
            for direction, new_room in room.neighbors(password)
        )
    )
    return ''.join(path)


def password_from_file(fn: str) -> str:
    return open(fn).readline().strip()


def main(input_path: str = data_path(__file__)) -> tuple[str, int]:
    password = password_from_file(input_path)
    result_1 = part_1(password)
    result_2 = part_2(password)
    return result_1, result_2


if __name__ == '__main__':
    main()
