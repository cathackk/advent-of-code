from typing import Generator

from common.heading import Heading


Pos = tuple[int, int]
Map = dict[Pos, str]
Route = tuple[Pos, Heading, int, list[str]]


def load_map(fn: str) -> Map:
    return {
        (x, y): c
        for y, line in enumerate(open(fn))
        for x, c in enumerate(line.rstrip())
        if c != ' '
    }


def routes(rmap: Map) -> Generator[Route, None, None]:
    pos = next((x, y) for (x, y), c in rmap.items() if y == 0 and c == '|')
    heading = Heading.SOUTH

    while True:
        dist = 0
        collected: list[str] = []

        # follow route
        while True:
            pos = heading.move(pos)
            dist += 1
            c = rmap.get(pos)
            if c is None:
                yield heading.move(pos, -1), heading, dist-1, collected
                return
            elif c == '+':
                yield pos, heading, dist, collected
                break
            elif c.isalpha():
                collected.append(c)
            elif c in ('-', '|'):
                pass
            else:
                raise ValueError(f"unsupported char! c={c!r}, at={pos}")

        # turn
        hr, hl = heading.right(), heading.left()
        if (hr.move(pos)) in rmap:
            # turn right
            heading = hr
        elif (hl.move(pos)) in rmap:
            # turn left
            heading = hl
        else:
            raise ValueError(f"nowhere to turn! pos={pos}, heading={heading.name}")


def test_routes():
    rs = routes(load_map("data/19-example.txt"))
    assert next(rs) == ((5, 5), Heading.SOUTH, 5, ['A'])
    assert next(rs) == ((8, 5), Heading.EAST, 3, ['B'])
    assert next(rs) == ((8, 1), Heading.NORTH, 4, [])
    assert next(rs) == ((11, 1), Heading.EAST, 3, [])
    assert next(rs) == ((11, 5), Heading.SOUTH, 4, ['C'])
    assert next(rs) == ((14, 5), Heading.EAST, 3, [])
    assert next(rs) == ((14, 3), Heading.NORTH, 2, ['D'])
    assert next(rs) == ((1, 3), Heading.WEST, 13, ['E', 'F'])
    assert list(rs) == []


def test_collect():
    assert ''.join(
        letter
        for _, _, _, letters in routes(load_map("data/19-example.txt"))
        for letter in letters
    ) == 'ABCDEF'


def test_distance():
    assert sum(dist for _, _, dist, _ in routes(load_map("data/19-example.txt"))) + 1 == 38


def part_1(fn: str) -> str:
    collected = ''.join(
        letter
        for _, _, _, letters in routes(load_map(fn))
        for letter in letters
    )
    print(f"part 1: {collected}")
    return collected


def part_2(fn: str) -> int:
    steps = sum(dist for _, _, dist, _ in routes(load_map(fn))) + 1
    print(f"part 2: {steps} steps total")
    return steps


if __name__ == '__main__':
    fn_ = "data/19-input.txt"
    part_1(fn_)
    part_2(fn_)
