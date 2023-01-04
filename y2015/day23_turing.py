"""
Advent of Code 2015
Day 23: Opening the Turing Lock
https://adventofcode.com/2015/day/23
"""

from typing import Final
from typing import Iterable

from meta.aoc_tools import data_path


def part_1(tape: 'Tape'):
    """
    Little Jane Marie just got her very first computer for Christmas from some unknown benefactor.
    It comes with instructions and an example program, but the computer itself seems to be malfunc-
    tioning. She's curious what the program does, and would like you to help her run it.

    The manual explains that the computer supports two registers and six instructions (truly, it
    goes on to remind the reader, a state-of-the-art technology). The registers are named `a` and
    `b`, can hold any non-negative integer, and begin with a value of `0`.

    The instructions are as follows:

      - `hlf r` sets register `r` to **half** its current value
      - `tpl r` sets register `r` to triple its current value
      - `inc r` increments register `r`, adding `1` to it
      - `jmp offset` is a jump; it continues with the instruction offset away relative to itself
      - `jie r, offset` is like `jmp`, but only jumps if register `r` is even ("jump if even")
      - `jio r, offset` is like `jmp`, but only jumps if register `r` is `1` ("jump if one")

    All three jump instructions work with an **offset** relative to that instruction. The offset is
    always written with a prefix `+` or `-` to indicate the direction of the jump (forward or
    backward, respectively). For example, `jmp +1` would simply continue with the next instruction,
    while `jmp +0` would continuously jump back to itself forever.

    The program exits when it tries to run an instruction beyond the ones defined.

    For example, this program sets `a` to `2`, because the `jio` instruction causes it to skip the
    `tpl` instruction:

        >>> example = tape_from_text('''
        ...     inc a
        ...     jio a, +2
        ...     tpl a
        ...     inc a
        ... ''')
        >>> example  # doctest: +NORMALIZE_WHITESPACE
        [Command('inc', reg='a'),
         Command('jio', reg='a', offset=2),
         Command('tpl', reg='a'),
         Command('inc', reg='a')]
        >>> run_tape(example)
        {'a': 2, 'b': 0}

    What is the value in register `b` when the program in your puzzle input is finished executing?

        >>> part_1(example)
        part 1: a = 2, b = 0
        0
    """

    regs = run_tape(tape)
    a, b = regs['a'], regs['b']
    print(f"part 1: a = {a}, b = {b}")
    return b


def part_2(tape: 'Tape'):
    """
    The unknown benefactor is **very** thankful for releasi-- er, helping little Jane Marie with her
    computer. Definitely not to distract you, what is the value in register `b` after the program is
    finished executing if register `a` starts as 1 instead?

        >>> part_2(tape_from_file(data_path(__file__, 'example.txt')))
        part 2: a = 7, b = 0
        0
    """

    regs = run_tape(tape, a=1)
    a, b = regs['a'], regs['b']
    print(f"part 2: a = {a}, b = {b}")
    return b


class Command:
    def __init__(self, op: str, reg: str = None, offset: int = None):
        self.op = op
        self.reg = reg
        self.offset = offset

    __match_args__: Final[tuple] = ('op', 'reg', 'offset')

    def __repr__(self) -> str:
        reg_repr = f', reg={self.reg!r}' if self.reg is not None else ''
        offset_repr = f', offset={self.offset!r}' if self.offset is not None else ''
        return f'{type(self).__name__}({self.op!r}{reg_repr}{offset_repr})'

    def __str__(self) -> str:
        offset_str = f', {self.offset:+}' if self.offset is not None else ''
        return f'{self.op} {self.reg}{offset_str}'

    @classmethod
    def from_str(cls, line: str) -> 'Command':
        """
            >>> Command.from_str('hlf a')
            Command('hlf', reg='a')
            >>> Command.from_str('jmp +3')
            Command('jmp', offset=3)
            >>> Command.from_str('jie b, -2')
            Command('jie', reg='b', offset=-2)
        """
        instr, args_str = line.split(' ', 1)
        args = args_str.split(', ')
        match args:
            case (arg,):
                try:
                    return cls(instr, offset=int(arg))
                except ValueError:
                    return cls(instr, reg=arg)
            case (reg, offset):
                return cls(instr, reg, int(offset))
            case _:
                raise ValueError(line)

        # TODO: remove when mypy realizes this is unreachable
        assert False


Tape = list[Command]


def run_tape(tape: Tape, a: int = 0, b: int = 0) -> dict[str, int]:
    regs = {'a': a, 'b': b}
    head = 0

    while True:
        try:
            command = tape[head]
        except IndexError:
            return regs

        match command:
            case Command('hlf', r, None):
                regs[r] //= 2
            case Command('tpl', r, None):
                regs[r] *= 3
            case Command('inc', r, None):
                regs[r] += 1
            case Command('jmp', None, off):
                head += (off - 1)
            case Command('jie', r, off):
                head += (off - 1) if regs[r] % 2 == 0 else 0
            case Command('jio', r, off):
                head += (off - 1) if regs[r] == 1 else 0
            case other:
                raise ValueError(repr(other))

        head += 1


def tape_from_file(fn: str) -> Tape:
    return list(tape_from_lines(open(fn)))


def tape_from_text(text: str) -> Tape:
    return list(tape_from_lines(text.strip().splitlines()))


def tape_from_lines(lines: Iterable[str]) -> Iterable[Command]:
    return (Command.from_str(line.strip()) for line in lines)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    tape = tape_from_file(input_path)
    result_1 = part_1(tape)
    result_2 = part_2(tape)
    return result_1, result_2


if __name__ == '__main__':
    main()
