from typing import Iterable
from typing import Set

from utils import count_ones
from y2017.day10_knots import knot_hash


Pos = tuple[int, int]


def disk_rows(seed: str, rows_count: int = 128) -> Iterable[bytes]:
    return [knot_hash(f'{seed}-{r}'.encode()) for r in range(rows_count)]


def neighbors(pos: Pos) -> Iterable[Pos]:
    x, y = pos
    yield x, y-1
    yield x-1, y
    yield x+1, y
    yield x, y+1


def count_regions(seed: str) -> int:
    ones: Set[Pos] = {
        (b*8+x, y)
        for y, row in enumerate(disk_rows(seed))
        for b, byte in enumerate(row)
        for x, bit in enumerate(bin(byte)[2:].zfill(8))
        if bit == '1'
    }

    regions_count = 0
    while ones:
        buffer: list[Pos] = [ones.pop()]

        while buffer:
            pos = buffer.pop()
            for npos in neighbors(pos):
                if npos in ones:
                    ones.remove(npos)
                    buffer.append(npos)

        regions_count += 1

    return regions_count


def test_bits_count():
    assert sum(count_ones(row) for row in disk_rows('flqrgnkx')) == 8108


def test_regions_count():
    assert count_regions('flqrgnkx') == 1242


def part_1(seed: str) -> int:
    ones = sum(count_ones(row) for row in disk_rows(seed))
    print(f"part 1: {ones} ones total")
    return ones


def part_2(seed: str) -> int:
    regions_count = count_regions(seed)
    print(f"part 2: {regions_count} regions total")
    return regions_count


if __name__ == '__main__':
    seed_ = 'hxtvlmkl'
    part_1(seed_)
    part_2(seed_)
