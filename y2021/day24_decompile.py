"""
Advent of Code 2021
Day 24: Arithmetic Logic Unit
https://adventofcode.com/2021/day/24
"""

import itertools
from enum import Enum
from typing import Any
from typing import Generator
from typing import Iterable


def part_1(program: 'Program') -> int:
    """
    Magic smoke starts leaking from the submarine's arithmetic logic unit (ALU). Without the ability
    to perform basic arithmetic and logic functions, the submarine can't produce cool patterns with
    its Christmas lights!

    It also can't navigate. Or run the oxygen system.

    Don't worry, though - you **probably** have enough oxygen left to give you enough time to build
    a new ALU.

    The ALU is a four-dimensional processing unit: it has integer variables `w`, `x`, `y`, and `z`.
    These variables all start with the value `0`. The ALU also supports **six instructions**:

      - `inp a` - Read an input value and write it to variable `a`.
      - `add a b` - Add the value of `a` to the value of `b`, then store the result in variable `a`.
      - `mul a b` - Multiply the value of `a` by the value of `b`, then store the result in `a`.
      - `div a b` - Divide the value of `a` by the value of `b`, truncate the result to an integer,
                    then store the result in variable `a`.
      - `mod a b` - Divide the value of `a` by the value of `b`, then store the remainder in `a`.
                    (This is also called the modulo operation.)
      - `eql a b` - If the value of `a` and `b` are equal, then store the value `1` in variable `a`.
                    Otherwise, store the value `0` in variable `a`.

    In all of these instructions, `a` and `b` are placeholders; `a` will always be the variable
    where the result of the operation is stored (one of `w`, `x`, `y`, or `z`), while `b` can be
    either a variable or a number. Numbers can be positive or negative, but will always be integers.

    The ALU has no jump instructions; in an ALU program, every instruction is run exactly once in
    order from top to bottom. The program halts after the last instruction has finished executing.

    (Program authors should be especially cautious; attempting to execute `div` with `b=0` or
    attempting to execute mod with `a<0` or `b<=0` will cause the program to crash and might even
    damage the ALU. These operations are never intended in any serious ALU program.)

    For example, here is an ALU program which takes an input number, negates it, and stores it in
    `x`:

        >>> negate = Program.from_text('''
        ...     inp x
        ...     mul x -1
        ... ''', return_from='x')
        >>> negate(10)
        -10
        >>> negate(-2)
        2

    Here is an ALU program which takes two input numbers, then sets `z` to `1` if the second input
    number is three times larger than the first input number, or sets `z` to `0` otherwise:

        >>> is_three_times = Program.from_text('''
        ...     inp z
        ...     inp x
        ...     mul z 3
        ...     eql z x
        ... ''', return_from='z')
        >>> is_three_times(5, 5)
        0
        >>> is_three_times(5, 15)
        1
        >>> is_three_times(10, 15)
        0

    Here is an ALU program which takes a non-negative integer as input, converts it into binary, and
    stores the lowest (1's) bit in `z`, the second-lowest (2's) bit in `y`, the third-lowest (4's)
    bit in `x`, and the fourth-lowest (8's) bit in `w`:


        >>> four_bits = Program.from_text('''
        ...     inp w
        ...     add z w
        ...     mod z 2
        ...     div w 2
        ...     add y w
        ...     mod y 2
        ...     div w 2
        ...     add x w
        ...     mod x 2
        ...     div w 2
        ...     mod w 2
        ... ''')
        >>> four_bits(10)
        (1, 0, 1, 0)
        >>> four_bits(15)
        (1, 1, 1, 1)
        >>> four_bits(253)
        (1, 1, 0, 1)

    Once you have built a replacement ALU, you can install it in the submarine, which will immedia-
    tely resume what it was doing when the ALU failed: validating the submarine's **model number**.
    To do this, the ALU will run the MOdel Number Automatic Detector program (MONAD, your puzzle
    input).

        >>> monad = Program.from_file('data/24-input-2.txt', return_from='z')

    Submarine model numbers are always **fourteen-digit numbers** consisting only of digits `1`
    through `9`. The digit `0` **cannot** appear in a model number.

    When MONAD checks a hypothetical fourteen-digit model number, it uses fourteen separate `inp`
    instructions, each expecting a **single digit** of the model number in order of most to least
    significant. (So, to check the model number `13579246899999`, you would give `1` to the first
    `inp` instruction, `3` to the second `inp` instruction, `5` to the third `inp` instruction, and
    so on.) This means that when operating MONAD, each input instruction should only ever be given
    an integer value of at least `1` and at most `9`.

    Then, after MONAD has finished running all of its instructions, it will indicate that the model
    number was **valid** by leaving a `0` in variable `z`. However, if the model number was invalid,
    it will leave some other non-zero value in `z`.

    MONAD imposes additional, mysterious restrictions on model numbers, and legend says the last
    copy of the MONAD documentation was eaten by a tanuki. You'll need to **figure out what MONAD
    does** some other way.

    To enable as many submarine features as possible, find the largest valid fourteen-digit model
    number that contains no `0` digits. **What is the largest model number accepted by MONAD?**

        >>> part_1(monad)
        part 1: largest model number is 59996912981939
        59996912981939
    """

    result = max(all_monad_solutions(extract_monad_variables(program)))

    print(f"part 1: largest model number is {result}")
    return result


def part_2(program: 'Program') -> int:
    """
    As the submarine starts booting up things like the Retro Encabulator, you realize that maybe
    you don't need all these submarine features after all.

    **What is the smallest model number accepted by MONAD?**

        >>> part_2(Program.from_file('data/24-input-2.txt'))
        part 2: smallest model number is 17241911811915
        17241911811915
    """

    result = min(all_monad_solutions(extract_monad_variables(program)))

    print(f"part 2: smallest model number is {result}")
    return result


class Op(Enum):
    INP = 'inp'
    ADD = 'add'
    MUL = 'mul'
    DIV = 'div'
    MOD = 'mod'
    EQL = 'eql'


class Instr:
    def __init__(self, op: Op, a: str, b: str | int | None):
        self.op = op
        self.a = a
        if b is not None:
            try:
                self.b = int(b)
            except ValueError:
                self.b = str(b)
        else:
            self.b = None

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.op!r}, {self.a!r}, {self.b!r})'

    def __str__(self) -> str:
        if self.b is None:
            return f'{self.op.value} {self.a}'
        else:
            return f'{self.op.value} {self.a} {self.b}'

    def _key(self) -> tuple:
        return self.op, self.a, self.b

    def __eq__(self, other):
        return isinstance(other, type(self)) and self._key() == other._key()

    @classmethod
    def from_str(cls, line: str) -> 'Instr':
        op_str, *args = line.split(' ')
        op = Op(op_str)
        if op == Op.INP:
            assert len(args) == 1
            return cls(op, args[0], None)
        else:
            assert len(args) == 2
            return cls(op, *args)


class Program:
    def __init__(self, instructions: Iterable[Instr], return_from: str = 'wxyz'):
        self.instructions = list(instructions)
        self.return_from = return_from

    @classmethod
    def from_text(cls, text: str, return_from: str = 'wxyz') -> 'Program':
        return cls.from_lines(text.strip().split('\n'), return_from)

    @classmethod
    def from_file(cls, fn: str, return_from: str = 'wxyz') -> 'Program':
        return cls.from_lines(open(fn), return_from)

    @classmethod
    def from_lines(cls, lines: Iterable[str], return_from: str = 'wxyz') -> 'Program':
        return cls(
            instructions=(Instr.from_str(line.strip()) for line in lines),
            return_from=return_from
        )

    def __len__(self) -> int:
        return len(self.instructions)

    def __call__(self, *args):
        g = self.run()
        next(g)
        for arg in args:
            try:
                g.send(arg)
            except StopIteration as exc:
                result = exc.value
                if len(self.return_from) == 0:
                    return None
                elif len(self.return_from) == 1:
                    return result[self.return_from[0]]
                else:
                    return tuple(result[r] for r in self.return_from)

    def run(self) -> Generator[None, Any, dict[str, int]]:
        regs: dict[str, int] = {r: 0 for r in 'wxyz'}

        for instr in self.instructions:
            if instr.op == Op.INP:
                b = yield
            elif isinstance(instr.b, int):
                b = instr.b
            elif isinstance(instr.b, str):
                b = regs[instr.b]
            else:
                raise ValueError(instr)

            match instr.op:
                case Op.INP:
                    regs[instr.a] = b
                case Op.ADD:
                    regs[instr.a] += b
                case Op.MUL:
                    regs[instr.a] *= b
                case Op.DIV:
                    assert regs[instr.a] >= 0
                    assert b > 0
                    regs[instr.a] //= b
                case Op.MOD:
                    assert regs[instr.a] >= 0
                    assert b > 0
                    regs[instr.a] %= b
                case Op.EQL:
                    regs[instr.a] = 1 if regs[instr.a] == b else 0
                case _:
                    raise ValueError(instr.op)

        return regs


def extract_monad_variables(program: Program) -> Iterable[tuple[int, int, int]]:
    """
    The MONAD program consists of 14 blocks, each having 18 instructions that are the same in each
    block save for three constants, named `A`, `B`, and `C` here:

        inp w
        mul x 0
        add x z
        mod x 26
        div z A  <--
        add x B  <--
        eql x w
        eql x 0
        mul y 0
        add y 25
        mul y x
        add y 1
        mul z y
        mul y 0
        add y w
        add y C  <--
        mul y x
        add z y

    These variables have the following values in my input per the 14 block (`i`):

        | i  | A  |  B  | C  |
        |----|----|-----|----|
        |  0 |  1 |  11 |  6 |
        |  1 |  1 |  11 | 12 |
        |  2 |  1 |  15 |  8 |
        |  3 | 26 | -11 |  7 |
        |  4 |  1 |  15 |  7 |
        |  5 |  1 |  15 | 12 |
        |  6 |  1 |  14 |  2 |
        |  7 | 26 |  -7 | 15 |
        |  8 |  1 |  12 |  4 |
        |  9 | 26 |  -6 |  5 |
        | 10 | 26 | -10 | 12 |
        | 11 | 26 | -15 | 11 |
        | 12 | 26 |  -9 | 13 |
        | 13 | 26 |   0 |  7 |

    This method extracts these variables `A`, `B`, and `C`.
    """
    assert len(program) == 14 * 18
    for block_index in range(14):
        block = program.instructions[block_index * 18:(block_index + 1) * 18]
        assert len(block) == 18
        assert block[0] == Instr(Op.INP, 'w', None)
        assert block[1] == Instr(Op.MUL, 'x', 0)
        assert block[2] == Instr(Op.ADD, 'x', 'z')
        assert block[3] == Instr(Op.MOD, 'x', 26)
        instr_a = block[4]  # div z A
        instr_b = block[5]  # add x B
        assert block[6] == Instr(Op.EQL, 'x', 'w')
        assert block[7] == Instr(Op.EQL, 'x', 0)
        assert block[8] == Instr(Op.MUL, 'y', 0)
        assert block[9] == Instr(Op.ADD, 'y', 25)
        assert block[10] == Instr(Op.MUL, 'y', 'x')
        assert block[11] == Instr(Op.ADD, 'y', 1)
        assert block[12] == Instr(Op.MUL, 'z', 'y')
        assert block[13] == Instr(Op.MUL, 'y', 0)
        assert block[14] == Instr(Op.ADD, 'y', 'w')
        instr_c = block[15]  # add y C
        assert block[16] == Instr(Op.MUL, 'y', 'x')
        assert block[17] == Instr(Op.ADD, 'z', 'y')

        # # div z A
        assert instr_a.op == Op.DIV
        assert instr_a.a == 'z'
        value_a = instr_a.b
        assert value_a in (1, 26)
        # add x B
        assert instr_b.op == Op.ADD
        assert instr_b.a == 'x'
        value_b = instr_b.b
        assert (value_a == 26) == (value_b < 9)
        # add y C
        assert instr_c.op == Op.ADD
        assert instr_c.a == 'y'
        value_c = instr_c.b

        yield value_a, value_b, value_c


def all_monad_solutions(monad_variables: Iterable[tuple[int, int, int]]) -> Iterable[int]:
    """
    The instructions can be rewritten and reorganized into the following Python code:

        w = input()  # inp w
        x = 0        # mul x 0
        x += z       # add x z
        x %= 26      # mod x 26
        z //= A[i]   # div z A
        x += B[i]    # add x B
        x = 1 if x == w else 0  # eql x w
        x = 1 if x == 0 else 0  # eql x 0
        y = 0        # mul y 0
        y += 25      # add y 25
        y *= x       # mul y x
        y += 1       # add y 1
        z *= y       # mul z y
        y = 0        # mul y 0
        y += w       # add y w
        y += C[i]    # add y C
        y *= x       # mul y x
        z += y       # add z y

    ... which is then reducible to:

        for i in range(14):
            w = input()
            x = z % 26
            z = z // A[i]
            x = 0 if x + B[i] == w else 1
            y = 25 * x + 1
            z *= y
            y = (w + C[u]) * x
            z += y

    ... note that `A`s are always either `1` or `26` ...
    ... also change `input()` to `D[i]` == digit for block `i`

        for i in range(14):
            if D[i] == z % 26 + B[i]:
                x = 0
            else:
                x = 1

            if A[i] == 26:
                z = z // 26

            z = z * (25 * x + 1) + (D[i] + C[i]) * x

    ... further reducing to ...

         for i in range(14):
            if D[i] != z % 26 + B[i]:
                z = z * 26 + D[i] + C[i]
            if A[i] == 26:
                z = z // 26

    ... `z` can be thought of as list `Z` with numbers `0` .. `25` (or a number base 26) ...
    ... and `A`s converted to `1`->`False` and `26`->`True` ...

        Z = []
        for i in range(14):
            if D[i] != Z.peek(default=0) + B[i]:
                Z.push(D[i] + C[i])
            if A[i]:
                Z.pop()

    - goal is to have the `Z` stack empty after the last block (`z=0` == valid input)
    - `Z` stack is pushed into based on its last element and `D[i]`
    - in 7 out of 14 blocks the stack is popped (`A[i] = 26`)
    - in the other 7 blocks `B[i]` is set so that it's impossible not to push into the stack
    -> 7 pushes + 7 pops -> in order to have empty stack at the end, we need to use every pop
       and prevent every push possible (preventable if `B[i]` < 9)
    -> the pushes will dictate the value of a "paired" input based on the pops
    -> this way we can pair the 14 values of `D[i]` into 7 pairs, e.g. D[2] == D[3] - 4
    """

    z_stack: list[tuple[int, int]] = []  # (i, C[i])
    d_pair_indexes: list[tuple[int, int]] = []  # (i1, i2) for each pair
    d_values: list[list[tuple[int, int]]] = []  # [(d1, d2), ...] for each pair
    for i, (a, b, c) in enumerate(monad_variables):
        if b >= 9:
            # push is necessary -> store current `i` and the offset-determinant `c`
            z_stack.append((i, c))
        else:
            # push is preventable by having the correct input value `d`
            paired_i, paired_c = z_stack[-1]
            d_pair_indexes.append((i, paired_i))

            offset = -(paired_c + b)
            # offset = 5 -> d1,2 = (1,6), (2,7), (3,8), (4,9)
            # offset =-3 -> d1,2 = (4,1), (5,2), (6,3), (7,4), (8,5), (9,6)
            d1_range = range(1, 10 - offset) if offset >= 0 else range(1 - offset, 10)
            d_values.append([(d1, d1 + offset) for d1 in d1_range])

        if a == 26:
            z_stack.pop()

    # result should be seven pairs
    assert len(d_pair_indexes) == len(d_values) == 7
    # yield each combination of the valid digits
    for ds in itertools.product(*d_values):
        digits = [None] * 14
        for (d1, d2), (d1i, d2i) in zip(ds, d_pair_indexes):
            digits[d1i] = d1
            digits[d2i] = d2
        assert all(digit is not None for digit in digits)
        yield int(''.join(str(digit) for digit in digits))


if __name__ == '__main__':
    program_ = Program.from_file('data/24-input.txt')
    part_1(program_)
    part_2(program_)
