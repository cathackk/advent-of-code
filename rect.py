import itertools
import math
from itertools import chain
from typing import Iterable

from utils import minmax

Pos = tuple[int, int]


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
    def shape(self) -> tuple[int, int]:
        return self.width, self.height

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


HyperPos = tuple[int, ...]


class HyperCuboid:
    # TODO: use exclusive corner_max
    def __init__(self, corner1: HyperPos, corner2: HyperPos):
        HyperCuboid._assert_dimensions_aligned(len(corner1), len(corner2))
        self.corner_min = tuple(min(a, b) for a, b in zip(corner1, corner2))
        self.corner_max = tuple(max(a, b) for a, b in zip(corner1, corner2))

    @classmethod
    def unit(cls, dimensions: int):
        origin = tuple(0 for _ in range(dimensions))
        return cls(origin, origin)

    @classmethod
    def at_origin(cls, lengths: HyperPos):
        # TODO: negative length
        return cls(
            corner1=tuple(0 for _ in range(len(lengths))),
            corner2=tuple(v - 1 for v in lengths)
        )

    @classmethod
    def with_all(cls, ps: Iterable[HyperPos]):
        ps = iter(ps)

        try:
            first_pos = next(ps)
        except StopIteration:
            raise ValueError("with_all() arg is an empty sequence")

        min_values, max_values = list(first_pos), list(first_pos)

        for pos in ps:
            HyperCuboid._assert_dimensions_aligned(len(first_pos), len(pos))
            for ix, value in enumerate(pos):
                if value < min_values[ix]:
                    min_values[ix] = value
                if value > max_values[ix]:
                    max_values[ix] = value

        return cls(tuple(min_values), tuple(max_values))

    def grow_to_fit(self, ps: Iterable[HyperPos]):
        return type(self).with_all(chain([self.corner_min, self.corner_max], ps))

    def __len__(self):
        return len(self.corner_min)

    @property
    def range_dim(self) -> range:
        return range(len(self))

    def length(self, dim: int) -> int:
        self._assert_dimension_in_range(dim)
        return self.corner_max[dim] - self.corner_min[dim] + 1

    @property
    def shape(self) -> tuple[int, ...]:
        return tuple(self.length(d) for d in self.range_dim)

    @property
    def volume(self) -> int:
        return math.prod(self.length(d) for d in self.range_dim)

    @property
    def surface(self) -> int:
        inner_volume = math.prod(max(0, self.length(d) - 2) for d in self.range_dim)
        return self.volume - inner_volume

    def corners(self) -> Iterable[HyperPos]:
        # TODO: remove duplicates when any length is 1
        return itertools.product(*zip(self.corner_min, self.corner_max))

    @property
    def corners_count(self) -> int:
        return self.elements_count(0)

    @property
    def edges_count(self) -> int:
        return self.elements_count(1)

    @property
    def faces_count(self) -> int:
        return self.elements_count(2)

    @property
    def cells_count(self) -> int:
        return self.elements_count(3)

    def elements_count(self, dimensions: int):
        if dimensions <= len(self):
            return (2 ** (len(self) - dimensions)) * math.comb(len(self), dimensions)
        else:
            return 0

    def __getitem__(self, dim):
        if isinstance(dim, int):
            # self[0] -> range(x)
            # self[1] -> range(y)
            self._assert_dimension_in_range(dim)
            return range(
                self.corner_min[dim],
                self.corner_max[dim] + 1
            )

        elif isinstance(dim, slice):
            # self[:2] -> range(x) × range(y)
            return type(self)(
                corner1=self.corner_min[dim],
                corner2=self.corner_max[dim]
            )

    def __iter__(self) -> Iterable[HyperPos]:
        return itertools.product(*(self[d] for d in self.range_dim))

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
            self._assert_has_dimensions(len(item))
            return all(
                item.corner_min[d] in self[d]
                and item.corner_max[d] in self[d]
                for d in item.range_dim
            )
        elif hasattr(item, '__len__'):
            self._assert_has_dimensions(len(item))
            return all(
                v in self[d]
                for d, v in enumerate(item)
            )
        else:
            self._assert_has_dimensions(1)
            return item in self[0]

    def __repr__(self):
        if all(v == 0 for v in self.corner_min):
            if all(self.length(d) == 1 for d in self.range_dim):
                return f'{type(self).__name__}.unit({len(self)})'
            else:
                return f'{type(self).__name__}.at_origin({self.shape!r})'
        else:
            return f'{type(self).__name__}({self.corner_min!r}, {self.corner_max!r})'

    @staticmethod
    def _assert_dimensions_aligned(dims1: int, dims2: int):
        if dims1 != dims2:
            raise ValueError(f"dimensions mismatch: {dims1} vs {dims2}")

    def _assert_has_dimensions(self, dims: int):
        if len(self) != dims:
            raise ValueError(f"dimensions mismatch: {dims} (expected {len(self)})")

    def _assert_dimension_in_range(self, dim: int):
        if not 0 <= dim < len(self):
            raise IndexError(f"dimension out of range: {dim} (expected between 0 and {len(self)})")
