from typing import Iterable
from typing import Tuple

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

    def range_x(self) -> range:
        return range(self.left_x, self.right_x + 1)

    def range_y(self) -> range:
        return range(self.top_y, self.bottom_y + 1)

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