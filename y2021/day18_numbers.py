"""
Advent of Code 2021
Day 18: Snailfish
https://adventofcode.com/2021/day/18
"""

from itertools import chain
from typing import Iterable
from typing import Optional

from common.utils import relative_path
from common.utils import zip1


def part_1(numbers: list['Number']) -> int:
    """
    Snailfish numbers aren't like regular numbers. Instead, every snailfish number is a **pair** -
    an ordered list of two elements. Each element of the pair can be either a regular number or
    another pair.

    Pairs are written as `[x,y]`, where `x` and `y` are the elements within the pair. Here are some
    example snailfish numbers, one snailfish number per line:

        >>> ns1 = Number.many_from_text('''
        ...
        ...     [1,2]
        ...     [[1,2],3]
        ...     [9,[8,7]]
        ...     [[1,9],[8,5]]
        ...     [[[[1,2],[3,4]],[[5,6],[7,8]]],9]
        ...     [[[9,[3,8]],[[0,9],6]],[[[3,7],[4,9]],3]]
        ...     [[[[1,3],[5,3]],[[1,3],[8,7]]],[[[4,9],[6,9]],[[8,2],[7,3]]]]
        ...
        ... ''')
        >>> print(ns1[0])
        [1,2]
        >>> print(ns1[1])
        [[1,2],3]
        >>> print(ns1[6])
        [[[[1,3],[5,3]],[[1,3],[8,7]]],[[[4,9],[6,9]],[[8,2],[7,3]]]]

    # Addition

    This snailfish homework is about **addition**. To add two snailfish numbers, form a pair from
    the left and right parameters of the addition operator. For example, `[1,2]` + `[[3,4],5]`
    becomes `[[1,2],[[3,4],5]]`.

        >>> print(Number.from_str('[1,2]') + Number.from_str('[[3,4],5]'))
        [[1,2],[[3,4],5]]

    There's only one problem: **snailfish numbers must always be reduced**, and the process of
    adding two snailfish numbers can result in snailfish numbers that need to be **reduced**.

    ## Reduction

    To **reduce a snailfish number**, you must repeatedly do the first action in this list that
    applies to the snailfish number:

      - If any pair is **nested inside four pairs**, the leftmost such pair **explodes**.
      - If any regular number is **10 or greater**, the leftmost such regular number **splits**.

    Once no action in the above list applies, the snailfish number is reduced.

    During reduction, at most one action applies, after which the process returns to the top of
    the list of actions. For example, if **split** produces a pair that meets the **explode**
    criteria, that pair **explodes** before other **splits** occur.

    ### Exploding

    To **explode** a pair, the pair's left value is added to the first regular number to the left of
    the exploding pair (if any), and the pair's right value is added to the first regular number to
    the right of the exploding pair (if any). Exploding pairs will always consist of two regular
    numbers. Then, the entire exploding pair is replaced with the regular number `0`.

    Here are some examples of a single explode action:

        >>> print(Number.from_str('[[[[[9,8],1],2],3],4]').exploded())
        [[[[0,9],2],3],4]

    ^^ The `9` has no regular number to its left, so it is not added to any regular number.

        >>> print(Number.from_str('[7,[6,[5,[4,[3,2]]]]]').exploded())
        [7,[6,[5,[7,0]]]]

    ^^ The `2` has no regular number to its right, and so it is not added to any regular number.

        >>> print(Number.from_str('[[6,[5,[4,[3,2]]]],1]').exploded())
        [[6,[5,[7,0]]],3]

        >>> print(e1 := Number.from_str('[[3,[2,[1,[7,3]]]],[6,[5,[4,[3,2]]]]]').exploded())
        [[3,[2,[8,0]]],[9,[5,[4,[3,2]]]]]

    ^^ The pair `[3,2]` is unaffected because the pair `[7,3]` is further to the left; `[3,2]` would
    explode on the next action:

        >>> print(e1.exploded())
        [[3,[2,[8,0]]],[9,[5,[7,0]]]]

    ### Splitting

    To **split** a regular number, replace it with a pair; the left element of the pair should be
    the regular number divided by two and rounded **down**, while the right element of the pair
    should be the regular number divided by two and rounded **up**.

        >>> print(Number.singular_from_int(10).split())
        [5,5]
        >>> print(Number.singular_from_int(11).split())
        [5,6]
        >>> print(Number.singular_from_int(12).split())
        [6,6]

    ## Reduction continued

    Here is the process of finding the reduced result for two example numbers:

        >>> a = Number.from_str('[[[[4,3],4],4],[7,[[8,4],9]]]')
        >>> b = Number.from_str('[1,1]')
        >>> with Explain('reduction'):
        ...     c = a + b
        after addition: [[[[[4,3],4],4],[7,[[8,4],9]]],[1,1]]
        after explode:  [[[[0,7],4],[7,[[8,4],9]]],[1,1]]
        after explode:  [[[[0,7],4],[15,[0,13]]],[1,1]]
        after split:    [[[[0,7],4],[[7,8],[0,13]]],[1,1]]
        after split:    [[[[0,7],4],[[7,8],[0,[6,7]]]],[1,1]]
        after explode:  [[[[0,7],4],[[7,8],[6,0]]],[8,1]]

    Once no reduce actions apply, the snailfish number that remains is the actual result of
    the addition operation:

        >>> print(c)
        [[[[0,7],4],[[7,8],[6,0]]],[8,1]]

    # Sum

    The homework assignment involves adding up a **list of snailfish numbers** (your puzzle input).
    The snailfish numbers are each listed on a separate line. Add the first snailfish number and
    the second, then add that result and the third, then add that result and the fourth, and so on
    until all numbers in the list have been used once.

    For example:

        >>> ns2 = Number.many_from_text('''
        ...     [1,1]
        ...     [2,2]
        ...     [3,3]
        ...     [4,4]
        ... ''')
        >>> print(sum(ns2))
        [[[[1,1],[2,2]],[3,3]],[4,4]]

        >>> print(sum(Number.many_from_text('''
        ...     [1,1]
        ...     [2,2]
        ...     [3,3]
        ...     [4,4]
        ...     [5,5]
        ... ''')))
        [[[[3,0],[5,3]],[4,4]],[5,5]]

        >>> print(sum(Number.many_from_text('''
        ...     [1,1]
        ...     [2,2]
        ...     [3,3]
        ...     [4,4]
        ...     [5,5]
        ...     [6,6]
        ... ''')))
        [[[[5,0],[7,4]],[5,5]],[6,6]]

    Here's a slightly larger example:

        >>> ns3 = Number.many_from_text('''
        ...     [[[0,[4,5]],[0,0]],[[[4,5],[2,6]],[9,5]]]
        ...     [7,[[[3,7],[4,3]],[[6,3],[8,8]]]]
        ...     [[2,[[0,8],[3,4]]],[[[6,7],1],[7,[1,6]]]]
        ...     [[[[2,4],7],[6,[0,5]]],[[[6,8],[2,8]],[[2,1],[4,5]]]]
        ...     [7,[5,[[3,8],[1,4]]]]
        ...     [[2,[2,2]],[8,[8,1]]]
        ...     [2,9]
        ...     [1,[[[9,3],9],[[9,0],[0,7]]]]
        ...     [[[5,[7,4]],7],1]
        ...     [[[[4,2],2],6],[8,7]]
        ... ''')

    The final sum is found after adding up the above snailfish numbers:

        >>> with Explain('addition'):
        ...     ns3_sum = sum(ns3)
          [[[0,[4,5]],[0,0]],[[[4,5],[2,6]],[9,5]]]
        + [7,[[[3,7],[4,3]],[[6,3],[8,8]]]]
        = [[[[4,0],[5,4]],[[7,7],[6,0]]],[[8,[7,7]],[[7,9],[5,0]]]]
        <BLANKLINE>
          [[[[4,0],[5,4]],[[7,7],[6,0]]],[[8,[7,7]],[[7,9],[5,0]]]]
        + [[2,[[0,8],[3,4]]],[[[6,7],1],[7,[1,6]]]]
        = [[[[6,7],[6,7]],[[7,7],[0,7]]],[[[8,7],[7,7]],[[8,8],[8,0]]]]
        <BLANKLINE>
          [[[[6,7],[6,7]],[[7,7],[0,7]]],[[[8,7],[7,7]],[[8,8],[8,0]]]]
        + [[[[2,4],7],[6,[0,5]]],[[[6,8],[2,8]],[[2,1],[4,5]]]]
        = [[[[7,0],[7,7]],[[7,7],[7,8]]],[[[7,7],[8,8]],[[7,7],[8,7]]]]
        <BLANKLINE>
          [[[[7,0],[7,7]],[[7,7],[7,8]]],[[[7,7],[8,8]],[[7,7],[8,7]]]]
        + [7,[5,[[3,8],[1,4]]]]
        = [[[[7,7],[7,8]],[[9,5],[8,7]]],[[[6,8],[0,8]],[[9,9],[9,0]]]]
        <BLANKLINE>
          [[[[7,7],[7,8]],[[9,5],[8,7]]],[[[6,8],[0,8]],[[9,9],[9,0]]]]
        + [[2,[2,2]],[8,[8,1]]]
        = [[[[6,6],[6,6]],[[6,0],[6,7]]],[[[7,7],[8,9]],[8,[8,1]]]]
        <BLANKLINE>
          [[[[6,6],[6,6]],[[6,0],[6,7]]],[[[7,7],[8,9]],[8,[8,1]]]]
        + [2,9]
        = [[[[6,6],[7,7]],[[0,7],[7,7]]],[[[5,5],[5,6]],9]]
        <BLANKLINE>
          [[[[6,6],[7,7]],[[0,7],[7,7]]],[[[5,5],[5,6]],9]]
        + [1,[[[9,3],9],[[9,0],[0,7]]]]
        = [[[[7,8],[6,7]],[[6,8],[0,8]]],[[[7,7],[5,0]],[[5,5],[5,6]]]]
        <BLANKLINE>
          [[[[7,8],[6,7]],[[6,8],[0,8]]],[[[7,7],[5,0]],[[5,5],[5,6]]]]
        + [[[5,[7,4]],7],1]
        = [[[[7,7],[7,7]],[[8,7],[8,7]]],[[[7,0],[7,7]],9]]
        <BLANKLINE>
          [[[[7,7],[7,7]],[[8,7],[8,7]]],[[[7,0],[7,7]],9]]
        + [[[[4,2],2],6],[8,7]]
        = [[[[8,7],[7,7]],[[8,6],[7,7]]],[[[0,7],[6,6]],[8,7]]]
        <BLANKLINE>
        >>> print(ns3_sum)
        [[[[8,7],[7,7]],[[8,6],[7,7]]],[[[0,7],[6,6]],[8,7]]]

    # Magnitude

    To check whether it's the right answer, the snailfish teacher only checks the **magnitude** of
    the final sum. The magnitude of a pair is 3 times the magnitude of its left element plus 2 times
    the magnitude of its right element. The magnitude of a regular number is just that number.

    For example, the magnitude of `[9,1]` is `3*9 + 2*1 = 29`:

        >>> abs(Number.from_str('[9,1]'))
        29

    The magnitude of `[1,9]` is `3*1 + 2*9 = 21`:

        >>> abs(Number.from_str('[1,9]'))
        21

    Magnitude calculations are recursive: the magnitude of `[[9,1],[1,9]]` is `3*29 + 2*21 = 129`:

        >>> abs(Number.from_str('[[9,1],[1,9]]'))
        129

    Here are a few more magnitude examples:

        >>> abs(Number.from_str('[[1,2],[[3,4],5]]'))
        143
        >>> abs(Number.from_str('[[[[0,7],4],[[7,8],[6,0]]],[8,1]]'))
        1384
        >>> abs(Number.from_str('[[[[1,1],[2,2]],[3,3]],[4,4]]'))
        445
        >>> abs(Number.from_str('[[[[3,0],[5,3]],[4,4]],[5,5]]'))
        791
        >>> abs(Number.from_str('[[[[5,0],[7,4]],[5,5]],[6,6]]'))
        1137
        >>> abs(Number.from_str('[[[[8,7],[7,7]],[[8,6],[7,7]]],[[[0,7],[6,6]],[8,7]]]'))
        3488

    # Homework

    So, given this example homework assignment:

        >>> homework = Number.many_from_text('''
        ...     [[[0,[5,8]],[[1,7],[9,6]]],[[4,[1,2]],[[1,4],2]]]
        ...     [[[5,[2,8]],4],[5,[[9,9],0]]]
        ...     [6,[[[6,2],[5,6]],[[7,6],[4,7]]]]
        ...     [[[6,[0,7]],[0,9]],[4,[9,[9,0]]]]
        ...     [[[7,[6,4]],[3,[1,3]]],[[[5,5],1],9]]
        ...     [[6,[[7,3],[3,2]]],[[[3,8],[5,7]],4]]
        ...     [[[[5,4],[7,7]],8],[[8,3],8]]
        ...     [[9,3],[[9,9],[6,[4,9]]]]
        ...     [[2,[[7,7],7]],[[5,8],[[9,3],[0,2]]]]
        ...     [[[[5,2],5],[8,[3,7]]],[[5,[7,5]],[4,4]]]
        ... ''')

    The final sum is:

        >>> print(homework_sum := sum(homework))
        [[[[6,6],[7,6]],[[7,7],[7,0]]],[[[7,7],[7,7]],[[7,8],[9,9]]]]

    The magnitude of this final sum is:

        >>> abs(homework_sum)
        4140

    Add up all of the snailfish numbers from the homework assignment in the order they appear.
    **What is the magnitude of the final sum?**

        >>> part_1(homework)
        part 1: magnitude of the final sum is 4140
        4140
    """

    result = abs(sum(numbers))

    print(f"part 1: magnitude of the final sum is {result}")
    return result


def part_2(numbers: list['Number']) -> int:
    """
    You notice a second question on the back of the homework assignment:

    What is the largest magnitude you can get from adding only two of the snailfish numbers?

    Note that snailfish addition is **not commutative** - that is, `x + y` and `y + x` can produce
    different results.

    Again considering the last example homework assignment above:

        >>> homework = Number.many_from_file('data/18-example.txt')

    The largest magnitude of the sum of any two snailfish numbers in this list is **`3993`**:

        >>> print(a := homework[8])
        [[2,[[7,7],7]],[[5,8],[[9,3],[0,2]]]]
        >>> print(b := homework[0])
        [[[0,[5,8]],[[1,7],[9,6]]],[[4,[1,2]],[[1,4],2]]]
        >>> print(c := a + b)
        [[[[7,8],[6,6]],[[6,0],[7,7]]],[[[7,8],[8,8]],[[7,9],[0,6]]]]
        >>> abs(c)
        3993

    **What is the largest magnitude of any sum of two different snailfish numbers from the homework
    assignment?**

        >>> part_2(homework)
        part 2: largest magnitude of sum of two different numbers is 3993
        3993
    """

    result = max(
        abs(num1 + num2)
        for num1 in numbers
        for num2 in numbers
        if num1 != num2
    )

    print(f"part 2: largest magnitude of sum of two different numbers is {result}")
    return result


ValueLevel = tuple[int, int]


class Number:
    def __init__(self, value_levels: Iterable[ValueLevel]):
        self.value_levels = list(value_levels)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.value_levels!r})'

    @classmethod
    def many_from_text(cls, text: str) -> list['Number']:
        return list(cls.many_from_lines(text.strip().split('\n')))

    @classmethod
    def many_from_file(cls, fn: str) -> list['Number']:
        return list(cls.many_from_lines(open(relative_path(__file__, fn))))

    @classmethod
    def many_from_lines(cls, lines: Iterable[str]) -> Iterable['Number']:
        return (cls.from_str(line.strip()) for line in lines)

    @classmethod
    def from_str(cls, line: str) -> 'Number':
        def vls() -> Iterable[ValueLevel]:
            level = 0
            num_buffer = []
            for ch in line:
                if ch.isdigit():
                    num_buffer.append(ch)
                elif num_buffer:
                    yield int(''.join(num_buffer)), level
                    num_buffer.clear()

                if ch == '[':
                    level += 1
                elif ch == ']':
                    level -= 1

        return cls(vls())

    @classmethod
    def singular_from_int(cls, n: int) -> 'Number':
        return cls([(n, 0)])

    def __str__(self) -> str:
        def chars() -> Iterable[str]:
            states = []
            for value, level in self.value_levels:
                # opening brackets
                while level > len(states):
                    states.append(',')
                    yield '['
                # value
                yield str(value)
                # closing brackets
                while states and states[-1] == ']':
                    yield states.pop()
                # commas
                if states:
                    assert states[-1] == ','
                    yield states.pop()
                    states.append(']')

        return ''.join(chars())

    def __add__(self, other) -> 'Number':
        cls = type(self)
        if not isinstance(other, cls):
            raise TypeError(
                f"unsupported operand type(s) for +: {cls.__name__!r} and {type(other).__name__!r}"
            )

        result = cls(chain(
            ((value, level + 1) for value, level in self.value_levels),
            ((value, level + 1) for value, level in other.value_levels)
        ))

        if Explain.LEVEL == 'reduction':
            print(f'after addition: {result}')

        # reduction
        while True:
            if exploded := result.exploded():
                result = exploded
                if Explain.LEVEL == 'reduction':
                    print(f'after explode:  {result}')
            elif split := result.split():
                result = split
                if Explain.LEVEL == 'reduction':
                    print(f'after split:    {result}')
            else:
                break

        if Explain.LEVEL == 'addition':
            print(f'  {self}')
            print(f'+ {other}')
            print(f'= {result}')
            print()

        return result

    def __radd__(self, other) -> 'Number':
        if isinstance(other, int) and other == 0:
            return self  # support for sum()
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: "
                f"{type(self).__name__!r} and {type(other).__name__!r}"
            )

    def exploded(self, level_limit: int = 4) -> Optional['Number']:
        try:
            left_index, right_index, level, left_value, right_value = next(
                (index, index + 1, l1, v1, v2)
                for index, ((v1, l1), (v2, l2)) in enumerate(zip1(self.value_levels))
                if l1 == l2 > level_limit
            )
        except StopIteration:
            return None

        new_vls = list(self.value_levels)

        def adjust_new_vls(index: int, value_diff: int):
            if index in range(len(new_vls)):
                v1, l1 = new_vls[index]
                new_vls[index] = v1 + value_diff, l1

        adjust_new_vls(left_index - 1, left_value)
        adjust_new_vls(right_index + 1, right_value)

        new_vls[left_index] = (0, level - 1)
        new_vls.pop(right_index)

        return type(self)(new_vls)

    def split(self, value_limit: int = 10) -> Optional['Number']:
        try:
            index, value, level = next(
                (i, v, l)
                for i, (v, l) in enumerate(self.value_levels)
                if v >= value_limit
            )
        except StopIteration:
            return None

        new_value_left = value // 2
        new_value_right = value - new_value_left

        new_vls = list(self.value_levels)
        new_vls[index] = (new_value_left, level + 1)
        new_vls.insert(index + 1, (new_value_right, level + 1))

        return type(self)(new_vls)

    def __abs__(self) -> int:
        stack: list[tuple[str, int]] = []

        def add_to_stack(val: int) -> int | None:
            if not stack:
                return val
            last_state, last_value = stack.pop()
            if last_state == 'L':
                stack.append(('R', last_value + 3 * val))
                return None
            elif last_state == 'R':
                return add_to_stack(last_value + 2 * val)
            else:
                assert False, last_state

        for value, level in self.value_levels:
            while level > len(stack):
                stack.append(('L', 0))
            if (result := add_to_stack(value)) is not None:
                return result


class Explain:
    LEVEL = None

    def __init__(self, level):
        self.level = level
        self.previous_level = None

    def __enter__(self):
        self.previous_level = Explain.LEVEL
        Explain.LEVEL = self.level

    def __exit__(self, exc_type, exc_val, exc_tb):
        Explain.LEVEL = self.previous_level
        return False


if __name__ == '__main__':
    numbers_ = Number.many_from_file('data/18-input.txt')
    part_1(numbers_)
    part_2(numbers_)
