from typing import Generator
from typing import Iterable

from common.utils import until_repeat


def realloc(nums: Iterable[int]) -> Generator[tuple[int, ...], None, None]:
    nums = list(nums)
    assert len(nums) > 0

    yield tuple(nums)

    while True:

        max_index = max(range(len(nums)), key=lambda n: nums[n])
        count = nums[max_index]
        nums[max_index] = 0

        head = max_index
        while count > 0:
            head = (head + 1) % len(nums)
            nums[head] += 1
            count -= 1

        yield tuple(nums)


def test_realloc_until_repeat():
    steps = list(until_repeat(realloc([0, 2, 7, 0])))
    assert steps == [
        (0, 2, 7, 0),
        (2, 4, 1, 2),
        (3, 1, 2, 3),
        (0, 2, 3, 4),
        (1, 3, 4, 1)
    ]


if __name__ == '__main__':
    g = realloc([4, 1, 15, 12, 0, 9, 9, 5, 5, 8, 7, 3, 14, 5, 12, 3])
    steps1 = sum(1 for _ in until_repeat(g))
    print(f"part 1: {steps1} steps until repeat")
    steps2 = sum(1 for _ in until_repeat(g))
    print(f"part 2: {steps2} steps to repeat once again")
