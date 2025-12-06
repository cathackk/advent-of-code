"""
Advent of Code 2025
Day 6: Trash Compactor
https://adventofcode.com/2025/day/6
"""

from math import prod
from typing import Iterable, Literal

from common.file import relative_path
from common.iteration import zip1

Problem = tuple[list[str], Literal['+', '*']]


def part_1(problems: Iterable[Problem]) -> int:
    """
    After helping the Elves in the kitchen, you were taking a break and helping them re-enact
    a movie scene when you over-enthusiastically jumped into the garbage chute!

    A brief fall later, you find yourself in a garbage smasher. Unfortunately, the door's been
    magnetically sealed.

    As you try to find a way out, you are approached by a family of cephalopods! They're pretty sure
    they can get the door open, but it will take some time. While you wait, they're curious if you
    can help the youngest cephalopod with her math homework.

    Cephalopod math doesn't look that different from normal math. The math worksheet (your puzzle
    input) consists of a list of **problems**; each problem has a group of numbers that need to
    either be either **added** (`+`) or **multiplied** (`*`) together.

    However, the problems are arranged a little strangely; they seem to be presented next to each
    other in a very long horizontal list. For example:

        >>> example = problems_from_text('''
        ...     123 328  51 64
        ...      45 64  387 23
        ...       6 98  215 314
        ...     *   +   *   +
        ... ''')
        >>> example  # doctest: +NORMALIZE_WHITESPACE
        [(['123', ' 45', '  6'], '*'),
         (['328', '64 ', '98 '], '+'),
         ([' 51', '387', '215'], '*'),
         (['64 ', '23 ', '314'], '+')]

    Each problem's numbers are arranged vertically; at the bottom of the problem is the symbol for
    the operation that needs to be performed. Problems are separated by a full column of only
    spaces. The left/right alignment of numbers within each problem can be ignored.

    So, this worksheet contains four problems:

        >>> results = [solve(p, print_formula=True) for p in example]
        123 * 45 * 6 = 33210
        328 + 64 + 98 = 490
        51 * 387 * 215 = 4243455
        64 + 23 + 314 = 401
        >>> results
        [33210, 490, 4243455, 401]

    To check their work, cephalopod students are given the **grand total** of adding together all of
    the answers to the individual problems. In this worksheet, the grand total is:

        >>> sum(results)
        4277556

    Of course, the actual worksheet is **much** wider. You'll need to make sure to unroll it
    completely so that you can read the problems clearly.

    Solve the problems on the math worksheet. **What is the grand total found by adding together all
    of the answers to the individual problems?**

        >>> part_1(example)
        part 1: the grand total of all problems is 4277556
        4277556
    """

    result = sum(solve(problem) for problem in problems)

    print(f"part 1: the grand total of all problems is {result}")
    return result


def part_2(problems: Iterable[Problem]) -> int:
    """
    The big cephalopods come back to check on how things are going. When they see that your grand
    total doesn't match the one expected by the worksheet, they realize they forgot to explain how
    to read cephalopod math.

    Cephalopod math is written **right-to-left in columns**. Each number is given in its own column,
    with the most significant digit at the top and the least significant digit at the bottom.
    (Problems are still separated with a column consisting only of spaces, and the symbol at
    the bottom of the problem is still the operator to use.)

    Here's the example worksheet again:

        >>> example = problems_from_text('''
        ...     123 328  51 64
        ...      45 64  387 23
        ...       6 98  215 314
        ...     *   +   *   +
        ... ''')

    Reading the problems right-to-left one column at a time, the problems are now quite different:

        >>> results = [solve(p, transposed=True, print_formula=True) for p in example]
        1 * 24 * 356 = 8544
        369 + 248 + 8 = 625
        32 * 581 * 175 = 3253600
        623 + 431 + 4 = 1058
        >>> results
        [8544, 625, 3253600, 1058]

    Now, the grand total is:

        >>> sum(results)
        3263827

    Solve the problems on the math worksheet again. **What is the grand total found by adding
    together all of the answers to the individual problems?**

        >>> part_2(example)
        part 2: the grand total is actually 3263827
        3263827
    """

    result = sum(solve(problem, transposed=True) for problem in problems)

    print(f"part 2: the grand total is actually {result}")
    return result


def solve(problem: Problem, transposed: bool = False, print_formula: bool = False) -> int:
    nums_str, op = problem

    if transposed:
        nums = [int(''.join(col)) for col in zip(*nums_str)]
    else:
        nums = [int(num) for num in nums_str]

    if op == '+':
        result = sum(nums)
    elif op == '*':
        result = prod(nums)
    else:
        raise KeyError(op)

    if print_formula:
        print(f" {op} ".join(str(num) for num in nums), "=", result)

    return result


def problems_from_file(fn: str) -> list[Problem]:
    return list(problems_from_lines(open(relative_path(__file__, fn))))


def problems_from_text(text: str) -> list[Problem]:
    return list(problems_from_lines(text.strip('\n').splitlines()))


def problems_from_lines(lines: Iterable[str]) -> Iterable[Problem]:
    # strip and justify trailing whitespace
    lines = [line.rstrip() for line in lines]
    max_length = max(len(line) for line in lines)
    lines = [line.ljust(max_length) for line in lines]

    # split lines along the last line containing operators
    splits = [pos for pos, char in enumerate(lines[-1]) if char in ('+', '*')] + [max_length + 1]
    lines_split = [[line[start:stop-1] for start, stop in zip1(splits)] for line in lines]

    # each column has N-1 numbers and 1 operator
    return (
        (list(col[:-1]), col[-1].strip())
        for col in zip(*lines_split)
    )


def main(input_fn: str = 'data/06-input.txt') -> tuple[int, int]:
    problems = problems_from_file(input_fn)
    result_1 = part_1(problems)
    result_2 = part_2(problems)
    return result_1, result_2


if __name__ == '__main__':
    main()
