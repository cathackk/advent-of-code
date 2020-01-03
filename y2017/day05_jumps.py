from typing import Callable
from typing import Generator
from typing import Iterable
from typing import List


def load_jumps(fn: str) -> List[int]:
    return [int(line) for line in open(fn)]


def go(
        jumps: Iterable[int],
        inc: Callable[[int], int] = lambda x: x + 1
) -> Generator[int, None, List[int]]:
    """
    >>> list(go([0, 3, 0, 1, -3]))
    [0, 1, 4, 1, 5]
    >>> list(go([0, 3, 0, 1, -3], lambda x: x-1 if x >= 3 else x+1))
    [0, 1, 4, 1, 3, 4, 2, 2, 3, 5]
    """

    jumps = list(jumps)
    pos = 0

    while 0 <= pos < len(jumps):
        jump = jumps[pos]
        jumps[pos] = inc(jump)
        pos += jump
        yield pos

    return jumps


def part_1(jumps: List[int]) -> int:
    steps = sum(1 for _ in go(jumps))
    print(f"part 1: it takes {steps} steps to reach the exit")
    return steps


def part_2(jumps: List[int]) -> int:
    steps = sum(1 for _ in go(jumps, lambda x: x-1 if x >= 3 else x+1))
    print(f"part 2: it takes {steps} steps to reach the exit")
    return steps


if __name__ == '__main__':
    jumps_ = load_jumps("data/05-input.txt")
    part_1(jumps_)
    part_2(jumps_)
