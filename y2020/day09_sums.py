"""
Advent of Code 2020
Day 9: Encoding Error
https://adventofcode.com/2020/day/9
"""

from typing import Collection, Iterator

from meta.aoc_tools import data_path


def part_1(numbers: list[int], preamble_length: int = 25) -> int:
    """
    The data appears to be encrypted with the eXchange-Masking Addition System (XMAS) which,
    conveniently for you, is an old cypher with an important weakness.

    XMAS starts by transmitting a *preamble* of 25 numbers. After that, each number you receive
    should be the sum of any two of the 25 immediately previous numbers. The two numbers will have
    different values, and there might be more than one such pair.

    For example, suppose your preamble consists of the numbers `1` through `25` in a random order.

        >>> nums = [20,1,17,23,14,10,16,18,4,7,21,11,8,19,3,2,12,13,6,15,24,5,22,25,9]
        >>> len(nums)
        25

    To be valid, the next number must be the sum of two of those numbers:

        - `26` would be a *valid* next number, as it could be `1+25`, `2+24`, or `20+6`.

            >>> find_sum2(26, nums)
            (20, 6)

        - `49` would be a *valid* next number, as it is `24+25`.

            >>> find_sum2(49, nums)
            (24, 25)

        - `100` would *not* be valid; no two of the previous 25 numbers sum to `100`.

            >>> find_sum2(100, nums) is None
            True

        - `50` would also *not* be valid; although `25` appears in the previous 25 numbers, the two
          numbers in the pair must be different.

            >>> find_sum2(50, nums) is None
            True

    Suppose the 26th number is `45`, and the first number (no longer an option, as it is more than
    25 numbers ago) was `20`.

        >>> nums.append(45)
        >>> nums.pop(0)
        20

    Now, for the next number to be valid, there needs to be some pair of numbers among `1`-`19`,
    `21`-`25`, or `45` that add up to it:

        - `26` would still be a *valid* next number, as `1+25` are still within the prev. 25 numbs.

            >>> find_sum2(26, nums)
            (1, 25)

        - `65` would *not* be valid, as no two of the available numbers sum to it.

            >>> find_sum2(65, nums) is None
            True

        - `64` and `66` would both be *valid*, as they are the result of `19+45` and `21+45`.

            >>> find_sum2(64, nums)
            (19, 45)
            >>> find_sum2(66, nums)
            (21, 45)

    Here is a larger example which only considers the previous 5 numbers (and has a preamble of
    length 5):

        >>> nums_2 = [35,20,15,25,47,40,62,55,65,95,102,117,150,182,127,219,299,277,309,576]

    In this example, after the 5-number preamble, almost every number is the sum of two of
    the previous 5 numbers; the only number that does not follow this rule is *`127`*.

        >>> v = validate_xmas(nums_2, preamble_length=5)
        >>> next(v)
        (40, True)
        >>> next(v)
        (62, True)
        >>> next((num, valid) for num, valid in v if not valid)
        (127, False)

    The first step of attacking the weakness in the XMAS data is to find the first number in
    the list (after the preamble) which is not the sum of two of the 25 numbers before it.

        >>> part_1(nums_2, preamble_length=5)
        part 1: first invalid number is 127
        127

    *What is the first number that does not have this property?*
    """

    result = next(
        num
        for num, valid in validate_xmas(numbers, preamble_length)
        if not valid
    )

    print(f"part 1: first invalid number is {result}")
    return result


def part_2(target: int, numbers: list[int]) -> int:
    """
    The final step in breaking the XMAS encryption relies on the invalid number you just found:
    you must *find a contiguous set of at least two numbers* in your list which sum to the invalid
    number from step 1.

    Again consider the above example:

        >>> nums_2 = [35,20,15,25,47,40,62,55,65,95,102,117,150,182,127,219,299,277,309,576]

    In this list, adding up all of the numbers from `15` through `40` produces the invalid number
    from step 1, `127`. (Of course, the contiguous set of numbers in your actual list might be much
    longer.)

        >>> find_sum_subseq(127, nums_2)
        [15, 25, 47, 40]
        >>> sum(_)
        127

    To find the *encryption weakness*, add together the *smallest* and *largest* number in this
    contiguous range; in this example, these are `15` and `47`, producing *`62`*.

        >>> part_2(127, nums_2)
        part 2: encryption weakness is 62
        62

    *What is the encryption weakness in your XMAS-encrypted list of numbers?*
    """

    subseq = find_sum_subseq(target, numbers)
    assert subseq is not None
    result = min(subseq) + max(subseq)

    print(f"part 2: encryption weakness is {result}")
    return result


def validate_xmas(nums: list[int], preamble_length: int = 25) -> Iterator[tuple[int, bool]]:
    """
    Yields every number from `nums` after first `preamble_length` values, with its validity info:
    the number is considered valid if two distinct numbers among previous `preamble_length` values
    can sum up to it.
    """

    if len(nums) <= preamble_length:
        return

    # let's keep a set of fixed length
    pool = set(nums[:preamble_length])

    for head in range(preamble_length, len(nums)):
        num = nums[head]
        valid = find_sum2(num, pool) is not None
        yield num, valid

        # rotate numbers in pool -> slightly more effective than sliding window above the nums
        pool.remove(nums[head - preamble_length])
        pool.add(num)


def find_sum2(target_sum: int, numbers: Collection[int]) -> tuple[int, int] | None:
    """ Find two values among `numbers` that add up to `target_sum`. """

    for a in numbers:
        b = target_sum - a
        if a != b and b in numbers:
            return a, b

    else:
        return None


def find_sum_subseq(
        target_sum: int,
        numbers: list[int],
        min_length: int = 2
) -> list[int] | None:
    """
    Find subsequence of `numbers` with at least `min_length` values that sum to `target_sum`.
    """

    # in order for this algorithm to work, numbers must be positive:
    assert all(num >= 0 for num in numbers)

    if min_length > len(numbers):
        return None

    # let's have two "pointers" (`start` and `end`) marking bounds of the candidate subsequence
    end = min_length
    # we'll continuously keep sum of the current subsequence, adding and subtracting numbers to it
    current_sum = sum(numbers[:min_length])

    for start in range(len(numbers) - min_length + 1):
        # after moving the `start` pointer, let's either:

        # (1) move the `end` pointer to the right, adding to the "running" sum, until the sum is no
        #     longer lower that `target_sum`, or until we reach the end of `numbers`
        if current_sum < target_sum:
            while current_sum < target_sum and end < len(numbers):
                end += 1
                current_sum += numbers[end - 1]
            if end == len(numbers) - 1:
                # we included all numbers from `start`, and it's still not enough
                # -> we'll never have a larger sum -> give up prematurely
                return None

        # (2) move the `end` pointer to the left, subtracting from the sum, until the sum is no
        #     longer greater than `target_sum`, or until we are too close to the `start` pointer
        elif current_sum > target_sum:
            while current_sum > target_sum and end > start + min_length:
                end -= 1
                current_sum -= numbers[end]

        # are we done?
        if current_sum == target_sum:
            subseq = numbers[start:end]
            assert len(subseq) >= min_length
            assert sum(subseq) == target_sum
            return subseq

        # ... nope -> let's move both pointers one position to the left and continue ...
        current_sum += numbers[end] - numbers[start]
        end += 1

    else:
        # no subsequence of given properties found
        return None


def load_nums(fn: str) -> list[int]:
    """ Load numbers from file, one per line. """
    return [
        int(line_stripped)
        for line in open(fn)
        if (line_stripped := line.strip())
    ]


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    nums = load_nums(input_path)
    result_1 = part_1(nums)
    result_2 = part_2(result_1, nums)
    return result_1, result_2


if __name__ == '__main__':
    main()
