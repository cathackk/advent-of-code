"""
Advent of Code 2017
Day 8: I Heard You Like Registers
https://adventofcode.com/2017/day/8
"""

import operator
from dataclasses import dataclass
from typing import Callable
from typing import Iterable
from typing import Iterator

from common.file import relative_path
from common.iteration import last
from common.text import parse_line


def part_1(instructions: Iterable['Instruction']) -> int:
    """
    You receive a signal directly from the CPU. Because of your recent assistance with jump
    instructions, it would like you to compute the result of a series of unusual register
    instructions.

    Each instruction consists of several parts: the register to modify, whether to increase or
    decrease that register's value, the amount by which to increase or decrease it, and a condition.
    If the condition fails, skip the instruction without modifying the register. The registers all
    start at `0`. The instructions look like this:

        >>> example_instructions = instructions_from_text('''
        ...     b inc 5 if a > 1
        ...     a inc 1 if b < 5
        ...     c dec -10 if a >= 1
        ...     c inc -20 if c == 10
        ... ''')
        >>> example_instructions  # doctest: +NORMALIZE_WHITESPACE
        [Instruction('b', 'inc', 5, Condition('a', '>', 1)),
         Instruction('a', 'inc', 1, Condition('b', '<', 5)),
         Instruction('c', 'dec', -10, Condition('a', '>=', 1)),
         Instruction('c', 'inc', -20, Condition('c', '==', 10))]

    These instructions would be processed as follows:

        >>> run = run_instructions(example_instructions)

      - Because `a` starts at `0`, it is not greater than `1`, and so `b` is not modified:

        >>> next(run)
        RunState(head=0, cond_eval=False, registers={})

      - `a` is increased by `1` (to `1`) because `b` is less than `5` (it is `0`):

        >>> next(run)
        RunState(head=1, cond_eval=True, registers={'a': 1})

      - `c` is decreased by `-10` (to `10`) because `a` is now greater than or equal to `1`
        (it is `1`):

        >>> next(run)
        RunState(head=2, cond_eval=True, registers={'a': 1, 'c': 10})

      - `c` is increased by `-20` (to `-10`) because `c` is equal to `10`:

        >>> next(run)
        RunState(head=3, cond_eval=True, registers={'a': 1, 'c': -10})

    After this process, the largest value in any register is `1`.

    You might also encounter `<=` (less than or equal to) or `!=` (not equal to). However, the CPU
    doesn't have the bandwidth to tell you what all the registers are named, and leaves that to you
    to determine.

    **What is the largest value in any register** after completing the instructions in your puzzle
    input?

        >>> part_1(example_instructions)
        part 1: largest value in registers is a=1
        1
    """

    final_registers = last(run_instructions(instructions)).registers
    max_value, max_reg = max((val, reg) for reg, val in final_registers.items())

    print(f"part 1: largest value in registers is {max_reg}={max_value}")
    return max_value


def part_2(instructions: list['Instruction']) -> int:
    """
    To be safe, the CPU also needs to know **the highest value held in any register during this
    process** so that it can decide how much memory to allocate to these operations. For example, in
    the above instructions, the highest value ever held was `10` (in register `c` after the third
    instruction was evaluated).

        >>> example_instructions = instructions_from_file('data/08-example.txt')
        >>> part_2(example_instructions)
        part 2: largest value in registers at any moment was c=10
        10
    """

    max_value, max_reg = max(
        (val, reg)
        for state in run_instructions(instructions)
        for reg, val in state.registers.items()
    )

    print(f"part 2: largest value in registers at any moment was {max_reg}={max_value}")
    return max_value


class Condition:
    def __init__(self, reg: str, op: str, value: int):
        self.reg = reg
        self.op = op
        self.value = value

    OPERATORS: dict[str, Callable[[int, int], bool]] = {
        '==': operator.eq,
        '!=': operator.ne,
        '>': operator.gt,
        '>=': operator.ge,
        '<': operator.lt,
        '<=': operator.le
    }

    def evaluate(self, registers: dict[str, int]) -> bool:
        return self.OPERATORS[self.op](registers.get(self.reg, 0), self.value)

    def __repr__(self):
        return f'{type(self).__name__}({self.reg!r}, {self.op!r}, {self.value!r})'

    def __str__(self):
        return f"{self.reg} {self.op} {self.value}"

    @classmethod
    def from_str(cls, line: str) -> 'Condition':
        # a >= 1
        reg, op, val = parse_line(line, "$ $ $")
        return cls(reg, op, int(val))


class Instruction:
    def __init__(self, reg: str, command: str, value: int, condition: Condition):
        self.reg = reg
        self.command = command
        self.value = value
        self.condition = condition

    @property
    def inc_value(self) -> int:
        if self.command == 'inc':
            return self.value
        elif self.command == 'dec':
            return -self.value
        else:
            raise KeyError(self.command)

    def __repr__(self):
        return (
            f'{type(self).__name__}('
            f'{self.reg!r}, {self.command!r}, {self.value!r}, {self.condition!r}'
            f')'
        )

    def __str__(self):
        return f"{self.reg} {self.command} {self.value} if {self.condition}"

    @classmethod
    def from_str(cls, line: str) -> 'Instruction':
        # c dec -10 if a >= 1
        reg, cmd, val, cond = parse_line(line, "$ $ $ if $")
        return cls(reg, cmd, int(val), Condition.from_str(cond))


@dataclass(frozen=True)
class RunState:
    head: int
    cond_eval: bool
    registers: dict[str, int]


def run_instructions(instructions: Iterable[Instruction]) -> Iterator[RunState]:
    registers: dict[str, int] = {}

    for head, instr in enumerate(instructions):
        cond_eval = instr.condition.evaluate(registers=registers)
        if cond_eval:
            current_value = registers.get(instr.reg, 0)
            new_value = current_value + instr.inc_value
            registers[instr.reg] = new_value

        yield RunState(head, cond_eval, dict(registers))


def instructions_from_text(text: str) -> list[Instruction]:
    return list(instructions_from_lines(text.strip().splitlines()))


def instructions_from_file(fn: str) -> list[Instruction]:
    return list(instructions_from_lines(open(relative_path(__file__, fn))))


def instructions_from_lines(lines: Iterable[str]) -> Iterable[Instruction]:
    return (Instruction.from_str(line.strip()) for line in lines)


if __name__ == '__main__':
    instructions_ = instructions_from_file('data/08-input.txt')
    part_1(instructions_)
    part_2(instructions_)
