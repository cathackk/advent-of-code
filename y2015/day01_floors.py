from typing import Iterable


def floors(s: str) -> Iterable[int]:
    current = 0
    yield current
    for c in s:
        current += {'(': +1, ')': -1}[c]
        yield current


if __name__ == '__main__':
    data = open("data/01-input.txt").readline().strip()

    final_floor = list(floors(data))[-1]
    print(f"part 1: final floor is {final_floor}")

    basement_index = next(i for i, f in enumerate(floors(data)) if f < 0)
    print(f"part 2: entering basement at position {basement_index}")
