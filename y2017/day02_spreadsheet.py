from itertools import combinations
from typing import Iterable

Rows = Iterable[list[int]]


def load_rows(fn: str) -> Rows:
    for line in open(fn):
        yield [int(v) for v in line.strip().split('\t')]


def checksum(rows: Rows) -> int:
    return sum(
        max(row) - min(row)
        for row in rows
    )


def divisibles(rows: Rows) -> Iterable[tuple[int, int]]:
    return (
        next(
            (a, b)
            for a, b in combinations(sorted(row, reverse=True), 2)
            if a % b == 0
        )
        for row in rows
    )


def devsum(rows: Rows) -> int:
    return sum(
        a // b
        for a, b in divisibles(rows)
    )


def part_1(rows: Rows) -> int:
    result = checksum(rows)
    print(f"part 1: checksum is {result}")
    return result


def part_2(rows: Rows) -> int:
    result = devsum(rows)
    print(f"part 2: divsum is {result}")
    return result


if __name__ == '__main__':
    rows_ = list(load_rows("data/02-input.txt"))
    part_1(rows_)
    part_2(rows_)
