"""
Advent of Code 2024
Day 7: Bridge Repair
https://adventofcode.com/2024/day/7
"""

from typing import Iterable

from tqdm import tqdm

from common.file import relative_path
from common.text import parse_line


def part_1(equations: Iterable['Equation']) -> int:
    """
    The Historians take you to a familiar rope bridge (y2022/day09_rope.py) over a river in
    the middle of a jungle. The Chief isn't on this side of the bridge, though; maybe he's on
    the other side?

    When you go to cross the bridge, you notice a group of engineers trying to repair it.
    (Apparently, it breaks pretty frequently.) You won't be able to cross until it's fixed.

    You ask how long it'll take; the engineers tell you that it only needs final calibrations, but
    some young elephants were playing nearby and **stole all the operators** from their calibration
    equations! They could finish the calibrations if only someone could determine which test values
    could possibly be produced by placing any combination of operators into their calibration
    equations (your puzzle input).

    For example:

        >>> example_equations = equations_from_text('''
        ...     190: 10 19
        ...     3267: 81 40 27
        ...     83: 17 5
        ...     156: 15 6
        ...     7290: 6 8 6 15
        ...     161011: 16 10 13
        ...     192: 17 8 14
        ...     21037: 9 7 18 13
        ...     292: 11 6 16 20
        ... ''')
        >>> example_equations  # doctest: +ELLIPSIS
        [(190, [10, 19]), (3267, [81, 40, 27]), (83, [17, 5]), (156, [15, 6]), ...]
        >>> len(example_equations)
        9

    Each line represents a single equation. The test value appears before the colon on each line;
    it is your job to determine whether the remaining numbers can be combined with operators to
    produce the test value.

    Operators are **always evaluated left-to-right**, **not** according to precedence rules.
    Furthermore, numbers in the equations cannot be rearranged. Glancing into the jungle, you can
    see elephants holding two different types of operators: **add (`+`)** and **multiply (`*`)**.

    Only three of the above equations can be made true by inserting operators:

      - `190: 10 19` has only one position that accepts an operator: between `10` and `19`.
        Choosing `+` would give `29`, but choosing `*` would give the test value:

        >>> list(solutions(example_equations[0]))
        [['*']]
        >>> print_solutions(example_equations[0])
        190 = 10 * 19

      - `3267: 81 40 27` has two positions for operators. Of the four possible configurations of
        the operators, **two** cause the right side to match the test value when evaluated
        left-to-right:

        >>> list(solutions(example_equations[1]))
        [['+', '*'], ['*', '+']]
        >>> print_solutions(example_equations[1])
        3267 = 81 + 40 * 27
        3267 = 81 * 40 + 27

      - `292: 11 6 16 20` can be solved in exactly one way:

        >>> print_solutions(example_equations[-1])
        292 = 11 + 6 * 16 + 20

    The engineers just need the **total calibration result**, which is the sum of the test values
    from just the equations that could possibly be true. In the above example, the sum of the test
    values for the three equations listed above is:

        >>> sum(equation[0] for equation in solvables(example_equations))
        3749

    Determine which equations could possibly be true. **What is their total calibration result?**

        >>> part_1(example_equations)
        part 1: 3 equations can be true; their total calibration result is 3749
        3749
    """

    solvable_equations = list(solvables(equations))
    result = sum(test_value for test_value, _ in solvable_equations)

    print(
        f"part 1: "
        f"{len(solvable_equations)} equations can be true; "
        f"their total calibration result is {result}"
    )
    return result


def part_2(equations: Iterable['Equation']) -> int:
    """
    The engineers seem concerned; the total calibration result you gave them is nowhere close to
    being within safety tolerances. Just then, you spot your mistake: some well-hidden elephants are
    holding a **third type of operator**.

    The concatenation operator (`||`) combines the digits from its left and right inputs into
    a single number. For example, `12 || 345` would become `12345`:

        >>> evaluate(12, 345, '||')
        12345

    All operators are still evaluated left-to-right.

    Now, apart from the three equations that could be made true using only addition and
    multiplication, the above example has three more equations that can be made true by inserting
    operators:

        >>> example_equations = equations_from_file('data/07-example.txt')
        >>> extended_operators = ('+', '*', '||')
        >>> print_solutions(example_equations[3], extended_operators)
        156 = 15 || 6
        >>> print_solutions(example_equations[4], extended_operators)
        7290 = 6 * 8 || 6 * 15
        >>> print_solutions(example_equations[6], extended_operators)
        192 = 17 || 8 + 14

    Adding up all six test values (the three that could be made before using only `+` and `*` plus
    the new three that can now be made by also using `||`) produces the new **total calibration
    result** of:

        >>> sum(eq[0] for eq in solvables(example_equations, extended_operators))
        11387

    Using your new knowledge of elephant hiding spots, determine which equations could possibly be
    true. **What is their total calibration result?**

        >>> part_2(example_equations)
        part 2: 6 equations can be true; their total calibration result is 11387
        11387
    """

    solvable_equations = list(solvables(equations, ops=('+', '*', '||')))
    result = sum(test_value for test_value, _ in solvable_equations)

    print(
        f"part 2: "
        f"{len(solvable_equations)} equations can be true; "
        f"their total calibration result is {result}"
    )
    return result


Equation = tuple[int, list[int]]
Op = str
Solution = list[Op]

BASIC_OPS = ('+', '*')


def solvables(equations: Iterable[Equation], ops: Iterable[Op] = BASIC_OPS) -> Iterable[Equation]:
    equations_list = list(equations)
    ops_tuple = tuple(ops)
    return tqdm(
        (eq for eq in equations_list if is_solvable(eq, ops_tuple)),
        total=len(equations_list),
        unit=" equations",
        desc="solving equations",
        delay=1.0,
    )


def is_solvable(equation: Equation, ops: tuple[Op, ...] = BASIC_OPS) -> bool:
    return any(solutions(equation, ops))


def solutions(equation: Equation, ops: tuple[Op, ...] = BASIC_OPS) -> Iterable[Solution]:
    test_value, nums = equation

    if len(nums) == 1:
        if test_value == nums[0]:
            yield []
        return

    a, b, *tail = nums
    for op in ops:
        c = evaluate(a, b, op)
        for solution in solutions((test_value, [c] + tail), ops):
            yield [op] + solution


def evaluate(a: int, b: int, op: str) -> int:
    match op:
        case '+':
            return a + b
        case '*':
            return a * b
        case '||':
            return int(str(a) + str(b))
        case _:
            raise ValueError(f"unsupported operator {op!r}")


def print_solutions(equation: Equation, ops: tuple[Op, ...] = BASIC_OPS) -> None:
    # only used in doctests
    test_value, nums = equation
    for solution in solutions(equation, ops):
        assert len(solution) == len(nums) - 1
        print(
            f"{test_value} = " +
            " ".join(f"{num} {op}" for num, op in zip(nums, solution)) +
            f" {nums[-1]}"
        )


def equations_from_file(fn: str) -> list[Equation]:
    return list(equations_from_lines(open(relative_path(__file__, fn))))


def equations_from_text(text: str) -> list[Equation]:
    return list(equations_from_lines(text.strip().splitlines()))


def equations_from_lines(lines: Iterable[str]) -> Iterable[Equation]:
    for line in lines:
        test_value, nums_str = parse_line(line, '$: $')
        yield int(test_value), [int(num) for num in nums_str.split()]


def main(input_fn: str = 'data/07-input.txt') -> tuple[int, int]:
    equations = equations_from_file(input_fn)
    result_1 = part_1(equations)
    result_2 = part_2(equations)
    return result_1, result_2


if __name__ == '__main__':
    main()
