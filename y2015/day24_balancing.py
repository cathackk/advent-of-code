from typing import Iterable

from utils import following
from utils import ilog
from utils import mink
from utils import product


def subsqs(tsum: int, values: list[int]) -> Iterable[list[int]]:
    if tsum == 0:
        yield []
        return

    for value, others in following(values):
        if value <= tsum:
            for ss in subsqs(tsum - value, others):
                yield [value] + ss


def first_container(weights: list[int], containers_count: int) -> Iterable[list[int]]:
    total_weights = sum(weights)
    assert total_weights % containers_count == 0
    container_weight = total_weights // containers_count

    for container1 in subsqs(container_weight, weights):
        assert sum(container1) == container_weight

        remaining_weights = list(weights)
        for w in container1:
            remaining_weights.remove(w)
        assert sum(remaining_weights) == container_weight * (containers_count - 1)

        if containers_count == 2 or any(first_container(remaining_weights, containers_count-1)):
            yield container1


def best_ps_balance(weights: list[int], containers_count: int) -> tuple[list[int], int]:
    weights = sorted(weights, reverse=True)
    ps, (l, qe) = mink(
        ilog(first_container(weights, containers_count), every=1000),
        key=lambda c: (len(c), product(c))
    )
    return ps, qe


def part_1(weights: list[int]) -> int:
    ps, qe = best_ps_balance(weights, 3)
    print(f"part 1: best balancing has QE={qe} ({ps})")
    return qe


def part_2(weights: list[int]) -> int:
    ps, qe = best_ps_balance(weights, 4)
    print(f"part 2: best balancing has QE={qe} ({ps})")
    return qe


if __name__ == '__main__':
    ws = [int(line) for line in open("data/24-input.txt")]
    part_1(ws)
    part_2(ws)
