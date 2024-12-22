from enum import Enum
from typing import Iterable, Self


class Heading(Enum):
    NORTH = ('N', 0, -1, "↑", "^")
    EAST = ('E', +1, 0, "→", ">")
    SOUTH = ('S', 0, +1, "↓", "v")
    WEST = ('W', -1, 0, "←", "<")

    def __init__(self, letter: str, dx: int, dy: int, arrow: str, caret: str):
        self.letter = letter
        self.dx = dx
        self.dy = dy
        self.arrow = arrow
        self.caret = caret

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'

    @classmethod
    def from_letter(cls, letter: str) -> Self:
        try:
            return next(h for h in cls if h.letter == letter)
        except StopIteration as stop:
            raise KeyError(letter) from stop

    @classmethod
    def from_caret(cls, caret: str) -> Self:
        try:
            return next(h for h in cls if h.caret == caret)
        except StopIteration as stop:
            raise KeyError(caret) from stop

    def right(self) -> 'Heading':
        return {
            Heading.NORTH: Heading.EAST,
            Heading.EAST: Heading.SOUTH,
            Heading.SOUTH: Heading.WEST,
            Heading.WEST: Heading.NORTH,
        }[self]

    def left(self) -> 'Heading':
        return {
            Heading.NORTH: Heading.WEST,
            Heading.EAST: Heading.NORTH,
            Heading.SOUTH: Heading.EAST,
            Heading.WEST: Heading.SOUTH,
        }[self]

    def opposite(self) -> 'Heading':
        return {
            Heading.NORTH: Heading.SOUTH,
            Heading.EAST: Heading.WEST,
            Heading.SOUTH: Heading.NORTH,
            Heading.WEST: Heading.EAST,
        }[self]

    # TODO: use where available
    def __add__(self, right: Iterable[int]) -> tuple[int, int]:
        x, y = right
        return x + self.dx, y + self.dy

    def __radd__(self, left: Iterable[int]) -> tuple[int, int]:
        return self + left

    def move(self, pos: tuple[int, int], distance: int = 1) -> tuple[int, int]:
        x, y = pos
        return (
            x + self.dx * distance,
            y + self.dy * distance
        )

    @classmethod
    def from_vector(cls, vec: tuple[int, int]) -> Iterable['Heading']:
        match vec:
            case 0, dy if dy < 0:
                return (cls.NORTH for _ in range(abs(dy)))
            case dx, 0 if dx > 0:
                return (cls.EAST for _ in range(dx))
            case 0, dy if dy > 0:
                return (cls.SOUTH for _ in range(dy))
            case dx, 0 if dx < 0:
                return (cls.WEST for _ in range(abs(dx)))
            case _:
                raise ValueError(f"vector must be ortogonal to one axis, got {vec}")
