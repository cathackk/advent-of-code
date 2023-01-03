from typing import Iterator

from common.mixin import Orderable


class XYZ(Orderable):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.x}, {self.y}, {self.z})'

    def __iter__(self) -> Iterator[int]:
        yield self.x
        yield self.y
        yield self.z

    def __bool__(self) -> bool:
        return any(v for v in self)

    def __format__(self, format_spec: str) -> str:
        labels = False
        if format_spec.endswith("="):
            labels = True
            format_spec = format_spec[:-1]

        left, right = "", ""
        if len(format_spec) >= 2:
            maybe_enclosings = format_spec[0], format_spec[-1]
            if maybe_enclosings in (("(", ")"), ("[", "]"), ("<", ">"), ("{", "}")):
                left, right = maybe_enclosings
                format_spec = format_spec[1:-1]

        x_str = ("x=" if labels else "") + format(self.x, format_spec)
        y_str = ("y=" if labels else "") + format(self.y, format_spec)
        z_str = ("z=" if labels else "") + format(self.z, format_spec)
        return f"{left}{x_str}, {y_str}, {z_str}{right}"


class Vector3(XYZ):
    def __str__(self) -> str:
        return format(self, "()")

    def __add__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(*(a + b for a, b in zip(self, other)))

    def __sub__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(*(a - b for a, b in zip(self, other)))

    def __mul__(self, k: int) -> 'Vector3':
        return Vector3(*(v * k for v in self))

    def __floordiv__(self, k: int) -> 'Vector3':
        return Vector3(*(v // k for v in self))

    def __abs__(self) -> int:
        return sum(abs(v) for v in self)

    def is_null(self) -> bool:
        return all(v == 0 for v in self)

    @classmethod
    def null(cls) -> 'Vector3':
        return Vector3(0, 0, 0)


class Point3(XYZ):
    def __str__(self):
        return format(self, "[]")

    def to(self, other: 'Point3') -> Vector3:
        return Vector3(*(b - a for a, b in zip(self, other)))

    def __add__(self, other: Vector3) -> 'Point3':
        return Point3(*(a + b for a, b in zip(self, other)))

    def __sub__(self, other: Vector3) -> 'Point3':
        return Point3(*(a - b for a, b in zip(self, other)))
