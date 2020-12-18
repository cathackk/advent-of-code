from itertools import chain
from typing import Iterable
from typing import Tuple

from utils import minmax
from utils import product

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


HyperPos = Tuple[int, ...]


def _assert_dimensions_aligned(dim1: int, dim2: int):
    if dim1 != dim2:
        raise ValueError(f"dimensions mismatch: {dim1} vs {dim2}")


class HyperCuboid:
    def __init__(self, corner1: HyperPos, corner2: HyperPos):
        _assert_dimensions_aligned(len(corner1), len(corner2))
        self.corner_min = tuple(min(a, b) for a, b in zip(corner1, corner2))
        self.corner_max = tuple(max(a, b) for a, b in zip(corner1, corner2))

    def __repr__(self):
        return f'{type(self).__name__}({self.corner_min!r}, {self.corner_max!r})'

    @classmethod
    def at_origin(cls, corner: HyperPos):
        origin = tuple(0 for _ in range(len(corner)))
        return cls(origin, corner)

    @classmethod
    def with_all(cls, ps: Iterable[HyperPos]):
        ps = iter(ps)

        try:
            first_pos = next(ps)
        except StopIteration:
            raise ValueError("with_all() arg is an empty sequence")

        min_values, max_values = list(first_pos), list(first_pos)

        for pos in ps:
            _assert_dimensions_aligned(len(first_pos), len(pos))
            for ix, value in enumerate(pos):
                if value < min_values[ix]:
                    min_values[ix] = value
                if value > max_values[ix]:
                    max_values[ix] = value

        return cls(tuple(min_values), tuple(max_values))

    def grow_to_fit(self, ps: Iterable[HyperPos]):
        return type(self).with_all(chain([self.corner_min, self.corner_max], ps))

    @property
    def dimensions(self) -> int:
        return len(self.corner_min)

    @property
    def range_dim(self) -> range:
        return range(self.dimensions)

    @property
    def shape(self) -> Tuple[int, ...]:
        return tuple(self.length(d) for d in self.range_dim)

    def length(self, dim: int) -> int:
        return self.corner_max[dim] - self.corner_min[dim]

    @property
    def volume(self) -> int:
        return product(self.length(d) for d in self.range_dim)

    def range(self, dim: int) -> range:
        return range(self.corner_min[dim], self.corner_max[dim] + 1)

    def slice(self, removed_dimensions: Iterable[int]) -> 'HyperCuboid':
        rds = set(removed_dimensions)
        for dim in rds:
            if not 0 <= dim < self.dimensions:
                raise ValueError(f"dimension out of range: {dim}")

        return type(self)(
            tuple(v for d, v in enumerate(self.corner_min) if d not in rds),
            tuple(v for d, v in enumerate(self.corner_max) if d not in rds)
        )

    def _positions(self, dims: int) -> Iterable[HyperPos]:
        if dims > 0:
            return (
                previous + (pos,)
                for previous in self._positions(dims - 1)
                for pos in self.range(dims - 1)
            )
        else:
            return (),

    def __iter__(self) -> Iterable[HyperPos]:
        return self._positions(self.dimensions)

    def __hash__(self) -> int:
        return hash((self.corner_min, self.corner_max))

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, type(self))
            and self.corner_min == other.corner_min
            and self.corner_max == other.corner_max
        )

    def __contains__(self, item) -> bool:
        if isinstance(item, type(self)):
            _assert_dimensions_aligned(self.dimensions, item.dimensions)
            return all(
                item.corner_min[d] in self.range(d)
                and item.corner_max[d] in self.range(d)
                for d in item.range_dim
            )
        else:
            _assert_dimensions_aligned(self.dimensions, len(item))
            return all(
                v in self.range(d)
                for d, v in enumerate(item)
            )
