from enum import Enum


class Heading(Enum):
    NORTH = ('N', 0, -1)
    EAST = ('E', +1, 0)
    SOUTH = ('S', 0, +1)
    WEST = ('W', -1, 0)

    def __init__(self, letter: str, dx: int, dy: int):
        self.letter = letter
        self.dx = dx
        self.dy = dy

    @classmethod
    def from_letter(cls, letter: str) -> 'Heading':
        try:
            return next(h for h in cls if h.letter == letter)
        except StopIteration:
            raise KeyError(letter)

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

    def move(self, pos: tuple[int, int], distance: int = 1) -> tuple[int, int]:
        x, y = pos
        return (
            x + self.dx * distance,
            y + self.dy * distance
        )
