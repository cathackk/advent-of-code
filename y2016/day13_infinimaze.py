from itertools import count
from typing import Iterable


Pos = tuple[int, int]


def is_wall(seed: int, pos: Pos):
    x, y = pos
    if x >= 0 and y >= 0:
        n = x*x + 3*x + 2*x*y + y + y*y + seed
        return sum(int(b) for b in bin(n)[2:]) % 2 == 1
    else:
        return True


def neighbors(pos: Pos) -> Iterable[Pos]:
    x, y = pos
    yield x + 1, y
    yield x - 1, y
    yield x, y + 1
    yield x, y - 1


def find_path(seed: int, start: Pos, end: Pos) -> int:
    visited: set[Pos] = set()
    to_visit: set[Pos] = {start}

    for distance in count(0):
        if end in to_visit:
            return distance
        visited.update(to_visit)
        to_visit = {
            npos
            for pos in to_visit
            for npos in neighbors(pos)
            if npos not in visited and not is_wall(seed, npos)
        }


def flood(seed: int, start: Pos, max_distance: int) -> int:
    visited: set[Pos] = set()
    to_visit: set[Pos] = {start}

    for distance in range(max_distance+1):
        visited.update(to_visit)
        to_visit = {
            npos
            for pos in to_visit
            for npos in neighbors(pos)
            if npos not in visited and not is_wall(seed, npos)
        }
    return len(visited)


def part_1(seed: int) -> int:
    start = (1, 1)
    end = (31, 39)
    dist = find_path(seed, start, end)
    print(f"part 1: distance from {start} to {end} is {dist}")
    return dist


def part_2(seed: int) -> int:
    steps = 50
    flooded = flood(seed, start=(1, 1), max_distance=steps)
    print(f"part 2: can reach {flooded} tiles in {steps} steps")
    return flooded


if __name__ == '__main__':
    seed_ = 1364
    part_1(seed_)
    part_2(seed_)
