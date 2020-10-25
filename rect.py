from itertools import chain
from typing import Iterable
from typing import Tuple

from utils import minmax

Pos = Tuple[int, int]


class Rect:
    def __init__(self, corner1: Pos, corner2: Pos):
        x1, y1 = corner1
        x2, y2 = corner2
        self.top_left = min(x1, x2), min(y1, y2)
        self.bottom_right = max(x1, x2), max(y2, y2)

    def __repr__(self):
        return f'{type(self).__name__}({self.top_left!r}, {self.bottom_right!r})'

    @classmethod
    def at_origin(cls, width: int, height: int):
        return cls((0, 0), (width - 1, height - 1))

    @classmethod
    def with_all(cls, ps: Iterable[Pos]):
        ps = list(ps)
        x_min, x_max = minmax(x for x, _ in ps)
        y_min, y_max = minmax(y for _, y in ps)
        return cls((x_min, y_min), (x_max, y_max))

    def grow_by(self, dx: int = 0, dy: int = 0):
        return type(self)(
            (self.left_x - dx, self.top_y - dy),
            (self.right_x + dx, self.bottom_y + dy)
        )

    def grow_to_fit(self, ps: Iterable[Pos]):
        return type(self).with_all(chain(
            [self.top_left, self.bottom_right],
            ps
        ))

    @property
    def left_x(self) -> int:
        return self.top_left[0]

    @property
    def right_x(self) -> int:
        return self.bottom_right[0]

    @property
    def top_y(self) -> int:
        return self.top_left[1]

    @property
    def bottom_y(self) -> int:
        return self.bottom_right[1]

    @property
    def width(self) -> int:
        return self.right_x - self.left_x + 1

    @property
    def height(self) -> int:
        return self.bottom_y - self.top_y + 1

    @property
    def area(self) -> int:
        return self.width * self.height

    @property
    def circumference(self) -> int:
        return 2 * self.width + 2 * self.height - 4

    def range_x(self) -> range:
        return range(self.left_x, self.right_x + 1)

    def range_y(self) -> range:
        return range(self.top_y, self.bottom_y + 1)

    def border_ps(self) -> Iterable[Pos]:
        # top (left to right)
        for x in range(self.left_x, self.right_x + 1):
            yield x, self.top_y

        # right (top to bottom)
        for y in range(self.top_y + 1, self.bottom_y):
            yield self.right_x, y

        # bottom (right to left)
        if self.bottom_y > self.top_y:
            for x in range(self.right_x, self.left_x - 1, -1):
                yield x, self.bottom_y

        # left (bottom to top)
        if self.left_x < self.right_x:
            for y in range(self.bottom_y - 1, self.top_y, -1):
                yield self.left_x, y

    def __iter__(self) -> Iterable[Pos]:
        return ((x, y) for y in self.range_y() for x in self.range_x())

    def __hash__(self) -> int:
        return hash((self.top_left, self.bottom_right))

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, type(self))
            and self.top_left == other.top_left
            and self.bottom_right == other.bottom_right
        )

    def __contains__(self, item) -> bool:
        if isinstance(item, Rect):
            return (
                item.left_x in self.range_x()
                and item.right_x in self.range_x()
                and item.top_y in self.range_y()
                and item.bottom_y in self.range_y()
            )
        else:
            x, y = item
            return (
                x in self.range_x()
                and y in self.range_y()
            )
