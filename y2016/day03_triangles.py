from typing import Iterable


Triangle = tuple[int, int, int]


def load_triangles(fn: str) -> Iterable[Triangle]:
    for line in open(fn):
        yield tuple(int(v) for v in line.strip().split() if v)


def load_triangles_vertically(fn: str) -> Iterable[Triangle]:
    buffer = []
    for line in open(fn):
        buffer.append(tuple(int(v) for v in line.strip().split() if v))
        if len(buffer) == 3:
            yield from zip(*buffer)
            buffer.clear()


def is_valid(triangle: Triangle):
    a, b, c = triangle
    return a < b + c and b < c + a and c < a + b


def part_1(fn: str) -> int:
    valids = sum(1 for t in load_triangles(fn) if is_valid(t))
    print(f"part 1: {valids} valid triangles")
    return valids


def part_2(fn: str) -> int:
    valids = sum(1 for t in load_triangles_vertically(fn) if is_valid(t))
    print(f"part 2: {valids} valid triangles")
    return valids


if __name__ == '__main__':
    _fn = "data/03-input.txt"
    part_1(_fn)
    part_2(_fn)
