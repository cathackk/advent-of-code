from typing import Iterable


def load_dimensions(fn: str = "data/02-input.txt") -> Iterable[tuple[int, int, int]]:
    with open(fn) as f:
        for line in f:
            yield tuple(int(v) for v in line.strip().split('x'))


def paper(l: int, w: int, h: int) -> int:
    lw = l * w
    wh = w * h
    hl = h * l
    smallest = min([lw, wh, hl])
    return 2 * lw + 2 * wh + 2 * hl + smallest


def ribbon(l: int, w: int, h: int) -> int:
    a, b, c = sorted([l, w, h])
    return (2 * a) + (2 * b) + (a * b * c)


def test_paper():
    assert paper(2, 3, 4) == 58
    assert paper(1, 1, 10) == 43


def test_ribbon():
    assert ribbon(2, 3, 4) == 34
    assert ribbon(1, 1, 10) == 14


if __name__ == '__main__':
    dimensions = list(load_dimensions())

    r1 = sum(paper(*d) for d in dimensions)
    print(f"part 1: total paper needed is {r1}")

    r2 = sum(ribbon(*d) for d in dimensions)
    print(f"part 2: total ribbon needed is {r2}")
