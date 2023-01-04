"""
Advent of Code 2016
Day 19: An Elephant Named Joseph
https://adventofcode.com/2016/day/19
"""
from meta.aoc_tools import data_path


def part_1(elf_count: int) -> int:
    """
    The Elves contact you over a highly secure emergency channel. Back at the North Pole, the Elves
    are busy misunderstanding
    [White Elephant parties](https://en.wikipedia.org/wiki/White_elephant_gift_exchange).

    Each Elf brings a present. They all sit in a circle, numbered starting with position `1`. Then,
    starting with the first Elf, they take turns stealing all the presents from the Elf to their
    left. An Elf with no presents is removed from the circle and does not take turns.

    For example, with five Elves (numbered `1` to `5`):

          1
        5   2
         4 3

      - Elf `1` takes Elf `2`'s present.
      - Elf `2` has no presents and is skipped.
      - Elf `3` takes Elf `4`'s present.
      - Elf `4` has no presents and is also skipped.
      - Elf `5` takes Elf `1`'s two presents.
      - Neither Elf `1` nor Elf `2` have any presents, so both are skipped.
      - Elf `3` takes Elf `5`'s three presents.

    So, with **five** Elves, the Elf that sits starting in position `3` gets all the presents.

        >>> elimination_naive(5)
        3

    With the number of Elves given in your puzzle input, **which Elf gets all the presents?**

        >>> part_1(5)
        part 1: winner is elf number 3
        3
    """

    winner = elimination_fast(elf_count)
    print(f"part 1: winner is elf number {winner}")
    return winner


def part_2(elf_count: int) -> int:
    """
    Realizing the folly of their present-exchange rules, the Elves agree to instead steal presents
    from the Elf **directly across the circle**. If two Elves are across the circle, the one on the
    left (from the perspective of the stealer) is stolen from. The other rules remain unchanged:
    Elves with no presents are removed from the circle entirely, and the other elves move in
    slightly to keep the circle evenly spaced.

    For example, with five Elves (again numbered `1` to `5`):

      - The Elves sit in a circle; Elf `1` goes first:
         *1*
        5   2
         4 3

      - Elves `3` and `4` are across the circle; Elf `3`'s present is stolen, being the one to the
        left. Elf `3` leaves the circle, and the rest of the Elves move in:
         *1*          1
        5   2  -->  5   2
         4 -          4

      - Elf `2` steals from the Elf directly across the circle, Elf `5`:
          1         1
        -  *2* -->     2
          4         4

      - Next is Elf `4` who, choosing between Elves `1` and `2`, steals from Elf `1`:

         -          2
            2  -->
        *4*         4

      - Finally, Elf 2 steals from Elf 4:
        *2*
            -->  2
         -

    So, with **five** Elves, the Elf that sits starting in position `2` gets all the presents.

        >>> across_elimination_naive(5)
        2

    With the number of Elves given in your puzzle input, **which Elf now gets all the presents**?

        >>> part_2(5)
        part 2: winner is elf number 2
        2
    """

    winner = across_elimination_fast(elf_count)
    print(f"part 2: winner is elf number {winner}")
    return winner


def elimination_naive(count: int) -> int:
    """
        >>> [elimination_naive(n) for n in range(1, 21)]
        [1, 1, 3, 1, 3, 5, 7, 1, 3, 5, 7, 9, 11, 13, 15, 1, 3, 5, 7, 9]
    """
    assert count > 0
    nums = list(range(1, count+1))
    while len(nums) > 1:
        if len(nums) % 2 == 0:
            nums = nums[::2]
        else:
            nums = nums[-1:] + nums[:-1:2]
    return nums[0]


def elimination_fast(count: int) -> int:
    """
        >>> [elimination_fast(n) for n in range(1, 21)]
        [1, 1, 3, 1, 3, 5, 7, 1, 3, 5, 7, 9, 11, 13, 15, 1, 3, 5, 7, 9]
    """
    assert count > 0
    # take binary form and move first digit to the end
    # 18 = '0b10010' -> '0b00101' = 5
    return int(bin(count)[3:]+'1', 2)


def across_elimination_naive(count: int) -> int:
    """
        >>> [across_elimination_naive(n) for n in range(1, 21)]
        [1, 1, 3, 1, 2, 3, 5, 7, 9, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 13]
        >>> across_elimination_naive(1000)
        271
        >>> across_elimination_naive(1237)
        508
    """
    assert count > 0
    nums = list(range(1, count+1))

    active_index = 0
    while len(nums) > 1:
        across_index = (active_index + len(nums)//2) % len(nums)
        nums.pop(across_index)
        if active_index < across_index:
            active_index += 1
        if active_index >= len(nums):
            active_index -= len(nums)

    return nums[0]


def terc(n) -> str:
    assert n >= 0
    if n == 0:
        return '0'
    digits = []
    while n > 0:
        digits.append(str(n % 3))
        n //= 3
    return ''.join(reversed(digits))


def across_elimination_fast(count: int) -> int:
    """
        >>> [across_elimination_fast(n) for n in range(1, 21)]
        [1, 1, 3, 1, 2, 3, 5, 7, 9, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 13]
        >>> across_elimination_fast(1000)
        271
        >>> across_elimination_fast(1237)
        508
    """

    assert count > 0

    # take tertiary form of n:
    #
    # (1) if it consists of a digit followed by z zeroes,
    #     return 1 followed by z zeroes (aka magnitude)
    #       • 27 = 0t1000 -> 0t1000 = 27;
    #       • 54 = 0t2000 -> 0t1000 = 27
    #
    # (2) if first digit is 1 (n < 2 * magnitude),
    #     return the rest of digits (n - magnitude)
    #       •  48 =  0t1210 ->  0t210 = 21
    #       • 111 = 0t11010 -> 0t1010 = 30
    #
    # (3) if first digit is 2 (n > 2 * magnitude),
    #     return twice the rest of digits plus magnitude (2*n - 3*magnitude)
    #       •  19 =   0t201 -> 2 *  0t01 +   0t100 =   0t102 =  11
    #       • 176 = 0t20112 -> 2 * 0t112 + 0t10000 = 0t11001 = 109

    t = terc(count)
    mag = int('1' + '0'*(len(t)-1), 3)
    if count == mag:
        return mag
    elif count <= 2 * mag:
        return count - mag
    else:
        return 2 * count - 3 * mag


def elf_count_from_file(fn: str) -> int:
    return int(open(fn).readline().strip())


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    elf_count = elf_count_from_file(input_path)
    result_1 = part_1(elf_count)
    result_2 = part_2(elf_count)
    return result_1, result_2


if __name__ == '__main__':
    main()
