from typing import Iterable
from typing import List

from utils import following
from utils import min_all


def generate_fillings(amount: int, containers: Iterable[int]) -> Iterable[List[int]]:
    if amount == 0:
        yield []
        return

    for container, rest_containers in following(containers):
        if container <= amount:
            rest_amount = amount - container
            yield from (
                [container] + subfilling
                for subfilling in generate_fillings(rest_amount, rest_containers)
            )


def load_containers(fn: str) -> Iterable[int]:
    for line in open(fn):
        yield int(line.strip())


def part_1(amount: int, containers: List[int]) -> int:
    combs_count = sum(1 for _ in generate_fillings(amount, containers))
    print(f"part 1: there are {combs_count} combinations to contain {amount} liters of eggnog")
    return combs_count


def part_2(amount: int, containers: List[int]) -> int:
    min_fillings = min_all(generate_fillings(amount, containers), key=lambda s: len(s))
    min_length = len(min_fillings[0])
    min_combs_count = len(min_fillings)
    print(
        f"part 2: there are {min_combs_count} combinations of length {min_length} "
        f"to contain {amount} liters of eggnog"
    )
    return min_combs_count


if __name__ == '__main__':
    in_amount = 150
    in_containers = list(load_containers("data/17-input.txt"))
    part_1(in_amount, in_containers)
    part_2(in_amount, in_containers)
