class XYZ:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f'{type(self).__name__}({self.x}, {self.y}, {self.z})'

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def __bool__(self):
        return any(v for v in self)

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return isinstance(other, type(self)) and tuple(self) == tuple(other)

    def __gt__(self, other):
        return isinstance(other, type(self)) and tuple(self) > tuple(other)


class Vector3(XYZ):
    def __str__(self):
        return f'({self.x}, {self.y}, {self.z})'

    def __add__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(*(a + b for a, b in zip(self, other)))

    def __sub__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(*(a - b for a, b in zip(self, other)))

    def __mul__(self, k: int) -> 'Vector3':
        return Vector3(*(v * k for v in self))

    def __floordiv__(self, k: int) -> 'Vector3':
        return Vector3(*(v // k for v in self))

    def is_null(self) -> bool:
        return all(v == 0 for v in self)

    @classmethod
    def null(cls) -> 'Vector3':
        return Vector3(0, 0, 0)


class Point3(XYZ):
    def __str__(self):
        return f'[{self.x}, {self.y}, {self.z}]'

    def to(self, other: 'Point3') -> Vector3:
        return Vector3(*(b - a for a, b in zip(self, other)))

    def __add__(self, other: Vector3) -> 'Point3':
        return Point3(*(a + b for a, b in zip(self, other)))

    def __sub__(self, other: Vector3) -> 'Point3':
        return Point3(*(a - b for a, b in zip(self, other)))
