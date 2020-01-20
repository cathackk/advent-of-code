import math

from utils import gcd2
from utils import sgn


class XY:
    __slots__ = ['x', 'y']
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'{type(self).__name__}({self.x}, {self.y})'

    def __iter__(self):
        yield self.x
        yield self.y

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return isinstance(other, type(self)) and tuple(self) == tuple(other)

    def __gt__(self, other):
        return isinstance(other, type(self)) and tuple(self) > tuple(other)


class Vector(XY):
    def __str__(self):
        return f'({self.x}, {self.y})'

    def __add__(self, other: 'Vector') -> 'Vector':
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, k: int) -> 'Vector':
        return Vector(self.x * k, self.y * k)

    def __floordiv__(self, k: int) -> 'Vector':
        return Vector(self.x // k, self.y // k)

    def is_null(self) -> bool:
        return self.x == 0 and self.y == 0

    def normalize(self) -> 'Vector':
        if self.is_null():
            raise ZeroDivisionError(f"cannot normalize vector {self}")
        elif self.x == 0 or self.y == 0:
            return Vector(sgn(self.x), sgn(self.y))
        else:
            return self // gcd2(self.x, self.y)

    def angle(self) -> float:
        angle = math.atan2(self.x, -self.y)
        if angle < 0:
            angle += 2*math.pi
        return angle


class Point(XY):
    def __str__(self):
        return f'[{self.x}, {self.y}]'

    def __add__(self, other: Vector) -> 'Point':
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: XY) -> Vector:
        return Vector(self.x - other.x, self.y - other.y)
