import math
from typing import Iterator, Self

from common.math import gcd2, sgn
from common.mixin import Orderable


class XY(Orderable):
    __slots__ = ['x', 'y']

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.x!r}, {self.y!r})'

    def __iter__(self) -> Iterator[int]:
        yield self.x
        yield self.y


class Vector(XY):
    def __str__(self) -> str:
        return f'({self.x}, {self.y})'

    def __add__(self, other: Self) -> Self:
        return type(self)(self.x + other.x, self.y + other.y)

    def __mul__(self, k: int) -> Self:
        return type(self)(self.x * k, self.y * k)

    def __floordiv__(self, k: int) -> Self:
        return type(self)(self.x // k, self.y // k)

    def is_null(self) -> bool:
        return self.x == 0 and self.y == 0

    def normalize(self) -> Self:
        if self.is_null():
            raise ZeroDivisionError(f"cannot normalize vector {self}")

        if self.x == 0 or self.y == 0:
            return type(self)(sgn(self.x), sgn(self.y))
        else:
            return self // gcd2(self.x, self.y)

    def angle(self) -> float:
        angle = math.atan2(self.x, -self.y)
        if angle < 0:
            angle += 2 * math.pi
        return angle


class Point(XY):
    def __str__(self) -> str:
        return f'[{self.x}, {self.y}]'

    def __add__(self, other: Vector) -> Self:
        return type(self)(self.x + other.x, self.y + other.y)

    def __sub__(self, other: XY) -> Vector:
        return Vector(self.x - other.x, self.y - other.y)
