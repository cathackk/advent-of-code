"""
Advent of Code 2020
Day 18: Operation Order
https://adventofcode.com/2020/day/18
"""

from enum import Enum
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Tuple
from typing import Union


def part_1(expressions: Iterable['Expr']) -> int:
    """
    The homework (your puzzle input) consists of a series of expressions that consist of addition
    (`+`), multiplication (`*`), and parentheses (`(...)`). Just like normal math, parentheses
    indicate that the expression inside must be evaluated before it can be used by the surrounding
    expression. Addition still finds the sum of the numbers on both sides of the operator, and
    multiplication still finds the product.

    However, the rules of *operator* precedence have changed. Rather than evaluating multiplication
    before addition, the operators have the *same precedence*, and are evaluated left-to-right
    regardless of the order in which they appear.

    For example, the steps to evaluate the expression `1 + 2 * 3 + 4 * 5 + 6` are as follows:

        ```
        1 + 2 * 3 + 4 * 5 + 6
          3   * 3 + 4 * 5 + 6
              9   + 4 * 5 + 6
                 13   * 5 + 6
                     65   + 6
                           71
        ```

        >>> evaluate_1('1 + 2 * 3 + 4 * 5 + 6')
        71

    Parentheses can override this order; for example, here is what happens if parentheses are added
    to form `1 + (2 * 3) + (4 * (5 + 6))`:

        ```
        1 + (2 * 3) + (4 * (5 + 6))
        1 +    6    + (4 * (5 + 6))
             7      + (4 * (5 + 6))
             7      + (4 *   11   )
             7      +     44
                    51
        ```

        >>> evaluate_1('1 + (2 * 3) + (4 * (5 + 6))')
        51

    Here are a few more examples:

        >>> evaluate_1('2 * 3 + (4 * 5)')
        26
        >>> evaluate_1('5 + (8 * 3 + 9 + 3 * 4 * 3)')
        437
        >>> evaluate_1('5 * 9 * (7 * 3 * 3 + 9 * 3 + (8 + 6 * 4))')
        12240
        >>> evaluate_1('((2 + 4 * 9) * (6 + 9 * 8 + 6) + 6) + 2 + 4 * 2')
        13632

    Before you can help with the homework, you need to understand it yourself. *Evaluate the
    expression on each line of the homework; what is the sum of the resulting values?*

        >>> part_1(Expr.load_from_text('''
        ...     1 + 2 * 3 + 4 * 5 + 6
        ...     2 * 3 + (4 * 5)
        ...     5 + (8 * 3 + 9 + 3 * 4 * 3)
        ... '''))
        part 1: sum of all evaluated expressions is 534
        534
    """

    result = sum(
        expr.evaluate(Precedence.SAME)
        for expr in expressions
    )

    print(f"part 1: sum of all evaluated expressions is {result}")
    return result


def part_2(expressions: Iterable['Expr']) -> int:
    """
    You manage to answer the child's questions and they finish part 1 of their homework, but get
    stuck when they reach the next section: *advanced* math.

    Now, addition and multiplication have *different* precedence levels, but they're not the ones
    you're familiar with. Instead, addition is evaluated *before* multiplication.

    For example, the steps to evaluate the expression `1 + 2 * 3 + 4 * 5 + 6` are now as follows:

        ```
        1 + 2 * 3 + 4 * 5 + 6
          3   * 3 + 4 * 5 + 6
          3   *   7   * 5 + 6
          3   *   7   *  11
             21       *  11
                 231
        ```

        >>> evaluate_2('1 + 2 * 3 + 4 * 5 + 6')
        231

    Here are the other examples from above:

        >>> evaluate_2('1 + (2 * 3) + (4 * (5 + 6))')
        51
        >>> evaluate_2('2 * 3 + (4 * 5)')
        46
        >>> evaluate_2('5 + (8 * 3 + 9 + 3 * 4 * 3)')
        1445
        >>> evaluate_2('5 * 9 * (7 * 3 * 3 + 9 * 3 + (8 + 6 * 4))')
        669060
        >>> evaluate_2('((2 + 4 * 9) * (6 + 9 * 8 + 6) + 6) + 2 + 4 * 2')
        23340

    *What do you get if you add up the results of evaluating the homework problems using these new
    rules?*

        >>> part_2(Expr.load_from_text('''
        ...     1 + 2 * 3 + 4 * 5 + 6
        ...     2 * 3 + (4 * 5)
        ...     5 + (8 * 3 + 9 + 3 * 4 * 3)
        ... '''))
        part 2: sum of all evaluated (addition first) expressions is 1722
        1722
    """

    result = sum(
        expr.evaluate(Precedence.ADDITION_FIRST)
        for expr in expressions
    )

    print(f"part 2: sum of all evaluated (addition first) expressions is {result}")
    return result


def evaluate_1(line: str) -> int:
    return Expr.parse(line).evaluate(Precedence.SAME)


def evaluate_2(line: str) -> int:
    return Expr.parse(line).evaluate(Precedence.ADDITION_FIRST)


class Precedence(Enum):
    SAME = 1
    ADDITION_FIRST = 2


class Operator(Enum):
    ADD = '+'
    MULTIPLY = '*'

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)


Value = Union[int, 'Expr']
ExprPart = Tuple[Operator, Value]


class Expr:
    """
        >>> e1 = Expr.parse('1 + 1')
        >>> e1
        Expr(('+', 1), ('+', 1))
        >>> print(e1)
        (1 + 1)
        >>> e1.evaluate(Precedence.SAME)
        2
        >>> e1.evaluate(Precedence.ADDITION_FIRST)
        2

        >>> e2 = Expr.parse('2 * 3 + 4')
        >>> e2
        Expr(('+', 2), ('*', 3), ('+', 4))
        >>> print(e2)
        (2 * 3 + 4)
        >>> e2.evaluate(Precedence.SAME)
        10
        >>> e2.evaluate(Precedence.ADDITION_FIRST)
        14

        >>> e3 = Expr.parse('2 + 3 * 4')
        >>> e3
        Expr(('+', 2), ('+', 3), ('*', 4))
        >>> print(e3)
        (2 + 3 * 4)
        >>> e3.evaluate(Precedence.SAME)
        20
        >>> e3.evaluate(Precedence.ADDITION_FIRST)
        20

        >>> e4 = Expr.parse('(2 * 3) + (4 * 5)')
        >>> e4
        Expr(('+', Expr(('+', 2), ('*', 3))), ('+', Expr(('+', 4), ('*', 5))))
        >>> print(e4)
        ((2 * 3) + (4 * 5))
        >>> e4.evaluate(Precedence.SAME)
        26
        >>> e4.evaluate(Precedence.ADDITION_FIRST)
        26

        >>> e5 = Expr.parse('(1 + 1) * (2 * 2) + (3 * 3 + 3)')
        >>> e5
        Expr(('+', Expr(('+', 1), ('+', 1))), ('*', Expr(('+', 2), ('*', 2))), \
('+', Expr(('+', 3), ('*', 3), ('+', 3))))
        >>> print(e5)
        ((1 + 1) * (2 * 2) + (3 * 3 + 3))
        >>> e5.evaluate(Precedence.SAME)
        20
        >>> e5.evaluate(Precedence.ADDITION_FIRST)
        44
    """

    def __init__(self, parts: Iterable[ExprPart]):
        self.parts = list(parts)
        assert len(self.parts) > 0
        assert self.parts[0][0] is Operator.ADD

    def __repr__(self):
        parts_repr = ', '.join(repr(part) for part in self.parts)
        return f'{type(self).__name__}({parts_repr})'

    def __str__(self):
        return f"({self.parts[0][1]} " + " ".join(
            f"{op} {value}"
            for op, value in self.parts[1:]
        ) + ")"

    def evaluate(self, prec: Precedence) -> int:
        def eval_(value: Value):
            if isinstance(value, Expr):
                return value.evaluate(prec)
            else:
                return int(value)

        if prec is Precedence.SAME:
            result = 0
            for op, val in self.parts:
                if op is Operator.ADD:
                    result += eval_(val)
                elif op is Operator.MULTIPLY:
                    result *= eval_(val)
            return result

        elif prec is Precedence.ADDITION_FIRST:
            prod = 1
            current_sum = 0
            for op, val in self.parts:
                if op is Operator.ADD:
                    current_sum += eval_(val)
                elif op is Operator.MULTIPLY:
                    prod *= current_sum
                    current_sum = eval_(val)
            return prod * current_sum

        else:
            raise ValueError(f"unsupported precedence {prec}")

    @classmethod
    def parse(cls, line: str):
        tokens = line.strip().replace('(', '( ').replace(')', ' )').split(' ')
        return cls.from_symbols(iter(tokens))

    @classmethod
    def from_symbols(cls, symbols: Iterator[str]):
        parts: List[ExprPart] = []

        op = Operator.ADD

        for symbol in symbols:
            match op, symbol:
                case None, '(':
                    raise ValueError("missing operator before subexpression")

                case _, '(':
                    subexpr = cls.from_symbols(symbols)
                    parts.append((op, subexpr))
                    op = None

                case _, ')':
                    return cls(parts)

                case _, '+' | '*':
                    op = Operator(symbol)

                case None, _ if symbol.isdigit():
                    raise ValueError(f"missing operator before int")

                case _, _ if symbol.isdigit():
                    parts.append((op, int(symbol)))
                    op = None

                case _:
                    raise ValueError(f"unknown symbol {symbol!r}")

        return cls(parts)

    @classmethod
    def load_from_file(cls, fn: str) -> List['Expr']:
        return list(cls.load_from_lines(open(fn)))

    @classmethod
    def load_from_text(cls, text: str) -> List['Expr']:
        return list(cls.load_from_lines(text.strip().split("\n")))

    @classmethod
    def load_from_lines(cls, lines: Iterable[str]) -> Iterable['Expr']:
        return (cls.parse(line.strip()) for line in lines)


if __name__ == '__main__':
    exprs_ = Expr.load_from_file('data/18-input.txt')
    part_1(exprs_)
    part_2(exprs_)
