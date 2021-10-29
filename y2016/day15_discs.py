from itertools import count
from typing import Optional


Disc = tuple[int, int]


def fall(discs: list[Disc], time: int) -> Optional[tuple[int, Disc]]:
    for index, (dpos0, dsize) in enumerate(discs):
        dpos = (dpos0 + time + index + 1) % dsize
        if dpos != 0:
            return index, (dpos, dsize)


if __name__ == '__main__':
    discs_1 = [(0, 7), (0, 13), (2, 3), (2, 5), (0, 17), (7, 19)]
    result_1 = next(t for t in count(0) if fall(discs_1, t) is None)
    print(f"part 1: t={result_1}")

    discs_2 = discs_1 + [(0, 11)]
    result_2 = next(t for t in count(0) if fall(discs_2, t) is None)
    print(f"part 2: t={result_2}")
