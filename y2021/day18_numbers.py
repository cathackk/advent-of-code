"""
Advent of Code 2021
Day 18: Snailfish
https://adventofcode.com/2021/day/18
"""
from abc import ABC
from abc import abstractmethod
from typing import Iterable
from typing import Optional

from utils import eprint


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
        >>> print(ns1[-1])
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

        >>> print(RegularNumber(10).splitted())
        [5,5]
        >>> print(RegularNumber(11).splitted())
        [5,6]
        >>> print(RegularNumber(12).splitted())
        [6,6]

    ## Reduction continued

    Here is the process of finding the reduced result for two example numbers:

        >>> a = Number.from_str('[[[[4,3],4],4],[7,[[8,4],9]]]')
        >>> b = Number.from_str('[1,1]')
        >>> c = Number.add(a, b, explain=True)
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

        >>> ns3_sum = Number.sum(ns3, explain=True)
          [[[0,[4,5]],[0,0]],[[[4,5],[2,6]],[9,5]]]
        + [7,[[[3,7],[4,3]],[[6,3],[8,8]]]]
        = [[[[4,0],[5,4]],[[7,7],[6,0]]],[[8,[7,7]],[[7,9],[5,0]]]]
        + [[2,[[0,8],[3,4]]],[[[6,7],1],[7,[1,6]]]]
        = [[[[6,7],[6,7]],[[7,7],[0,7]]],[[[8,7],[7,7]],[[8,8],[8,0]]]]
        + [[[[2,4],7],[6,[0,5]]],[[[6,8],[2,8]],[[2,1],[4,5]]]]
        = [[[[7,0],[7,7]],[[7,7],[7,8]]],[[[7,7],[8,8]],[[7,7],[8,7]]]]
        + [7,[5,[[3,8],[1,4]]]]
        = [[[[7,7],[7,8]],[[9,5],[8,7]]],[[[6,8],[0,8]],[[9,9],[9,0]]]]
        + [[2,[2,2]],[8,[8,1]]]
        = [[[[6,6],[6,6]],[[6,0],[6,7]]],[[[7,7],[8,9]],[8,[8,1]]]]
        + [2,9]
        = [[[[6,6],[7,7]],[[0,7],[7,7]]],[[[5,5],[5,6]],9]]
        + [1,[[[9,3],9],[[9,0],[0,7]]]]
        = [[[[7,8],[6,7]],[[6,8],[0,8]]],[[[7,7],[5,0]],[[5,5],[5,6]]]]
        + [[[5,[7,4]],7],1]
        = [[[[7,7],[7,7]],[[8,7],[8,7]]],[[[7,0],[7,7]],9]]
        + [[[[4,2],2],6],[8,7]]
        = [[[[8,7],[7,7]],[[8,6],[7,7]]],[[[0,7],[6,6]],[8,7]]]
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


class Number(ABC):
    def __init__(self):
        self.parent: Optional['PairNumber'] = None

    @classmethod
    def from_str(cls, s: str) -> 'Number':
        if not s:
            raise ValueError('empty value')

        if s[0].isdigit():
            impl_cls = RegularNumber
        elif s[0] == '[':
            impl_cls = PairNumber
        else:
            raise ValueError(f'invalid number string: {s!r}')

        return impl_cls.from_str(s)

    @classmethod
    def many_from_text(cls, text: str) -> list['Number']:
        return list(cls.many_from_lines(text.strip().split('\n')))

    @classmethod
    def many_from_file(cls, fn: str) -> list['Number']:
        return list(cls.many_from_lines(open(fn)))

    @classmethod
    def many_from_lines(cls, lines: Iterable[str]) -> Iterable['Number']:
        return (cls.from_str(line.strip()) for line in lines)

    def add(self, right: 'Number', explain: bool = False) -> 'Number':
        result = PairNumber(left=self.copy(), right=right.copy())
        if explain:
            print(f'after addition: {result}')

        # reduce
        while True:
            if result.explode():
                if explain:
                    print(f'after explode:  {result}')
            elif result.split():
                if explain:
                    print(f'after split:    {result}')
            else:
                return result

    def __add__(self, other) -> 'Number':
        if isinstance(other, Number):
            return self.add(right=other)
        else:
            raise TypeError(
                f'unsupported operand type for +: '
                f'{type(self).__name__!r} and {type(other).__name__!r}'
            )

    def __radd__(self, other) -> 'Number':
        if isinstance(other, int) and other == 0:
            # to enable sum(numbers)
            return self
        else:
            raise TypeError(
                f'unsupported operand type for +: '
                f'{type(other).__name__!r} and {type(self).__name__!r}'
            )

    @abstractmethod
    def explode(self, levels_remaining: int = 4) -> bool:
        ...

    def exploded(self) -> Optional['Number']:
        return self if self.explode() else None

    @abstractmethod
    def split(self, limit: int = 10) -> Optional['PairNumber']:
        ...

    def splitted(self) -> Optional['Number']:
        if self.parent:
            return self if self.split() else None
        else:
            return self.split()

    @abstractmethod
    def copy(self) -> 'Number':
        ...

    @staticmethod
    def sum(numbers: Iterable['Number'], explain: bool = False) -> 'Number':
        numbers_iter = iter(numbers)
        result = next(numbers_iter)
        if explain:
            print(f'  {result}')
        for number in numbers_iter:
            result = result + number
            if explain:
                print(f'+ {number}')
                print(f'= {result}')
        return result

    @abstractmethod
    def leftmost_regular(self) -> 'RegularNumber':
        ...

    @abstractmethod
    def rightmost_regular(self) -> 'RegularNumber':
        ...

    @abstractmethod
    def __abs__(self) -> int:
        ...


class RegularNumber(Number):
    def __init__(self, value: int):
        super().__init__()
        self.value = value

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.value!r})'

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def from_str(cls, s: str) -> 'RegularNumber':
        return cls(int(s))

    def copy(self) -> 'RegularNumber':
        return type(self)(self.value)

    def explode(self, levels_remaining: int = 4) -> bool:
        return False

    def split(self, limit: int = 10) -> Optional['PairNumber']:
        if self.value < limit:
            return None

        left_value = self.value // 2
        right_value = self.value - left_value
        split_number = PairNumber(left=RegularNumber(left_value), right=RegularNumber(right_value))
        if self.parent:
            self.parent.replace(self, split_number)

        return split_number

    def leftmost_regular(self) -> 'RegularNumber':
        return self

    def rightmost_regular(self) -> 'RegularNumber':
        return self

    def increase(self, by: int) -> None:
        self.value += by

    def __abs__(self) -> int:
        return self.value


class PairNumber(Number):
    def __init__(self, left: Number, right: Number):
        super().__init__()

        self.left = left
        self.right = right

        self.left.parent = self
        self.right.parent = self

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.left!r}, {self.right!r})'

    def __str__(self) -> str:
        return f'[{self.left},{self.right}]'

    @classmethod
    def from_str(cls, s: str) -> 'PairNumber':
        def delimit(text: str, start: int) -> int:
            level = 0
            for i in range(start, len(text)):
                ch = text[i]
                if ch == '[':
                    level += 1
                elif ch == ']':
                    level -= 1
                    if level == -1:
                        return i
                elif ch == ',':
                    if level == 0:
                        return i
            else:
                return -1

        try:
            assert len(s) > 2
            assert s[0] == '['
            assert s[-1] == ']'

            left_start = 1
            left_end = delimit(s, left_start)
            assert left_end > left_start
            assert s[left_end] == ','

            right_start = left_end + 1
            right_end = delimit(s, right_start)
            assert right_end > right_start
            assert s[right_end] == ']'
            assert right_end == len(s) - 1

        except AssertionError as exc:
            raise ValueError(f'invalid pair number string: {s}') from exc

        return cls(
            left=Number.from_str(s[left_start:left_end]),
            right=Number.from_str(s[right_start:right_end])
        )

    def copy(self) -> 'PairNumber':
        return type(self)(left=self.left.copy(), right=self.right.copy())

    def explode(self, levels_remaining: int = 4) -> bool:
        if levels_remaining <= 0 and self.is_regular_pair():
            left_value, right_value = self.regular_pair_values()

            assert self.parent is not None

            if (left_rn := self.parent.left_neighbor_regular(self)):
                left_rn.increase(left_value)

            if (right_rn := self.parent.right_neighbor_regular(self)):
                right_rn.increase(right_value)

            self.parent.replace(self, RegularNumber(0))

            return True

        # not exploding this one, try exploding its children
        return self.left.explode(levels_remaining - 1) or self.right.explode(levels_remaining - 1)

    def split(self, limit: int = 10) -> Optional['PairNumber']:
        return self.left.split(limit) or self.right.split(limit)

    def is_regular_pair(self) -> bool:
        try:
            self.regular_pair_values()
        except TypeError:
            return False
        else:
            return True

    def regular_pair_values(self) -> tuple[int, int]:
        if isinstance(self.left, RegularNumber) and isinstance(self.right, RegularNumber):
            return self.left.value, self.right.value
        else:
            raise TypeError('not a regular pair')

    def replace(self, child: 'Number', with_number: 'Number') -> None:
        with_number.parent = self
        if child is self.left:
            self.left.parent = None
            self.left = with_number
        elif child is self.right:
            self.right.parent = None
            self.right = with_number
        else:
            raise AssertionError(f'{child} not in {self}')

    def left_neighbor_regular(self, child: 'PairNumber') -> RegularNumber | None:
        if child is self.right:
            return self.left.rightmost_regular()
        elif child is self.left:
            return self.parent.left_neighbor_regular(self) if self.parent else None
        else:
            raise AssertionError(f'{child} not in {self}')

    def right_neighbor_regular(self, child: 'PairNumber') -> RegularNumber | None:
        if child is self.left:
            return self.right.leftmost_regular()
        elif child is self.right:
            return self.parent.right_neighbor_regular(self) if self.parent else None
        else:
            raise AssertionError(f'{child} not in {self}')

    def leftmost_regular(self) -> 'RegularNumber':
        return self.left.leftmost_regular()

    def rightmost_regular(self) -> RegularNumber:
        return self.right.rightmost_regular()

    def __abs__(self) -> int:
        return 3 * abs(self.left) + 2 * abs(self.right)


if __name__ == '__main__':
    numbers_ = Number.many_from_file('data/18-input.txt')
    part_1(numbers_)
    part_2(numbers_)
