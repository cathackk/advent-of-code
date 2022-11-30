"""
Advent of Code 2018
Day 16: Chronal Classification
https://adventofcode.com/2018/day/16
"""

from dataclasses import dataclass
from typing import Iterable
from typing import Iterator

from common.file import relative_path
from common.iteration import ilen
from common.iteration import single_value
from common.text import parse_line
from common.text import ParseError


def part_1(samples: Iterable['Sample']) -> int:
    """
    As you see the Elves defend their hot chocolate successfully, you go back to falling through
    time. This is going to become a problem.

    If you're ever going to return to your own time, you need to understand how this device on your
    wrist works. You have a little while before you reach your next destination, and with a bit of
    trial and error, you manage to pull up a programming manual on the device's tiny screen.

    According to the manual, the device has four registers (numbered `0` through `3`) that can be
    manipulated by instructions containing one of 16 opcodes. The registers start with the value
    `0`.

    Every instruction consists of four values: an **opcode**, two **inputs** (named `A` and `B`),
    and an **output** (named `C`), in that order. The opcode specifies the behavior of the
    instruction and how the inputs are interpreted. The output, `C`, is always treated as
    a register.

    In the opcode descriptions below, if something says **"value `A`"**, it means to take the number
    given as `A` **literally**. (This is also called an "immediate" value.) If something says
    **"register `A`"**, it means to use the number given as `A` to read from (or write to) the
    **register with that number**. So, if the opcode `addi` adds register `A` and value `B`, storing
    the result in register `C`, and the instruction `addi 0 7 3` is encountered, it would add `7` to
    the value contained by register `0` and store the sum in register `3`, never modifying registers
    `0`, `1`, or `2` in the process.

    Many opcodes are similar except for how they interpret their arguments. The opcodes fall into
    seven general categories:

    Addition:

      - `addr` (add register) stores into register `C` the result of adding register `A` and
        register `B`.
      - `addi` (add immediate) stores into register `C` the result of adding register `A` and
        value `B`.

    Multiplication:

      - `mulr` (multiply register) stores into register `C` the result of multiplying register `A`
        and register `B`.
      - `muli` (multiply immediate) stores into register `C` the result of multiplying register `A`
        and value `B`.

    Bitwise AND:

      - `banr` (bitwise AND register) stores into register `C` the result of the bitwise AND of
        register `A` and register `B`.
      - `bani` (bitwise AND immediate) stores into register `C` the result of the bitwise AND of
        register `A` and value `B`.

    Bitwise OR:

      - `borr` (bitwise OR register) stores into register `C` the result of the bitwise OR of
        register `A` and register `B`.
      - `bori` (bitwise OR immediate) stores into register `C` the result of the bitwise OR of
        register `A` and value `B`.

    Assignment:

      - `setr` (set register) copies the contents of register `A` into register `C`.
        (Input `B` is ignored.)
      - `seti` (set immediate) stores value `A` into register `C`. (Input `B` is ignored.)

    Greater-than testing:

      - `gtir` (greater-than immediate/register) sets register `C` to `1` if value `A` is greater
        than register `B`. Otherwise, register `C` is set to `0`.
      - `gtri` (greater-than register/immediate) sets register `C` to `1` if register `A` is greater
        than value `B`. Otherwise, register `C` is set to `0`.
      - `gtrr` (greater-than register/register) sets register `C` to `1` if register `A` is greater
        than register `B`. Otherwise, register `C` is set to `0`.

    Equality testing:

      - `eqir` (equal immediate/register) sets register `C` to `1` if value `A` is equal to
        register `B`. Otherwise, register `C` is set to `0`.
      - `eqri` (equal register/immediate) sets register `C` to `1` if register `A` is equal to
        value `B`. Otherwise, register `C` is set to `0`.
      - `eqrr` (equal register/register) sets register `C` to `1` if register `A` is equal to
        register `B`. Otherwise, register `C` is set to `0`.

    Unfortunately, while the manual gives the **name** of each opcode, it doesn't seem to indicate
    the **number**. However, you can monitor the CPU to see the contents of the registers before and
    after instructions are executed to try to work them out. Each opcode has a number from `0`
    through `15`, but the manual doesn't say which is which. For example, suppose you capture the
    following sample:

        >>> example_sample = Sample.from_text('''
        ...     Before: [3, 2, 1, 1]
        ...     9 2 1 2
        ...     After:  [3, 2, 2, 1]
        ... ''')
        >>> example_sample
        Sample(before=[3, 2, 1, 1], instr=Instr(opnum=9, a=2, b=1, c=2), after=[3, 2, 2, 1])

    This sample shows the effect of the instruction `9 2 1 2` on the registers. Before the
    instruction is executed, register `0` has value `3`, register `1` has value `2`, and registers
    `2` and `3` have value `1`. After the instruction is executed, register `2`'s value becomes `2`.

    The instruction itself, `9 2 1 2`, means that opcode `9` was executed with `A=2`, `B=1`, and
    `C=2`. Opcode `9` could be any of the 16 opcodes listed above, but only three of them behave in
    a way that would cause the result shown in the sample:

      - Opcode `9` could be `mulr`: register `2` (which has a value of `1`) times register `1`
        (which has a value of `2`) produces `2`, which matches the value stored in the output
        register, register `2`.
      - Opcode `9` could be `addi`: register `2` (which has a value of `1`) plus value `1` produces
        `2`, which matches the value stored in the output register, register `2`.
      - Opcode `9` could be `seti`: value `2` matches the value stored in the output register,
        register `2`; the number given for `B` is irrelevant.

        >>> list(example_sample.possible_opcodes())
        ['addi', 'mulr', 'seti']

    None of the other opcodes produce the result captured in the sample. Because of this, the sample
    above **behaves like three opcodes**.

    You collect many of these samples (the first section of your puzzle input). The manual also
    includes a small test program (the second section of your puzzle input) - you can **ignore it
    for now**.

    Ignoring the opcode numbers, **how many samples in your puzzle input behave like three or more
    opcodes?**

        >>> part_1([example_sample])
        part 1: there are 1 samples with at least three possible opcodes
        1
    """

    three_or_more = ilen(
        sample for sample in samples
        if ilen(sample.possible_opcodes()) >= 3
    )
    print(f"part 1: there are {three_or_more} samples with at least three possible opcodes")
    return three_or_more


def part_2(samples: Iterable['Sample'], program: Iterable['Instr']):
    """
    Using the samples you collected, work out the number of each opcode and execute the test program
    (the second section of your puzzle input).

    **What value is contained in register `0` after executing the test program?**
    """

    opnum_to_opcode = dict(map_opnums_to_opcodes(samples))
    final_registers = run_program(program, opnum_to_opcode)
    result = final_registers[0]

    print(f"part 2: after processing the instructions, register 0 contains value {result}")
    return result


all_ops = {
    'addr': lambda a, b, regs: regs[a] + regs[b],
    'addi': lambda a, b, regs: regs[a] + b,
    'mulr': lambda a, b, regs: regs[a] * regs[b],
    'muli': lambda a, b, regs: regs[a] * b,
    'banr': lambda a, b, regs: regs[a] & regs[b],
    'bani': lambda a, b, regs: regs[a] & b,
    'borr': lambda a, b, regs: regs[a] | regs[b],
    'bori': lambda a, b, regs: regs[a] | b,
    'setr': lambda a, b, regs: regs[a],
    'seti': lambda a, b, regs: a,
    'gtir': lambda a, b, regs: int(a > regs[b]),
    'gtri': lambda a, b, regs: int(regs[a] > b),
    'gtrr': lambda a, b, regs: int(regs[a] > regs[b]),
    'eqir': lambda a, b, regs: int(a == regs[b]),
    'eqri': lambda a, b, regs: int(regs[a] == b),
    'eqrr': lambda a, b, regs: int(regs[a] == regs[b])
}


@dataclass(frozen=True)
class Instr:
    opnum: int
    a: int
    b: int
    c: int

    def __str__(self) -> str:
        return f"{self.opnum} {self.a} {self.b} {self.c}"

    @classmethod
    def from_str(cls, line: str) -> 'Instr':
        opcode, a, b, c = line.strip().split(" ")
        return cls(int(opcode), int(a), int(b), int(c))


@dataclass(frozen=True)
class Sample:
    before: list[int]
    instr: Instr
    after: list[int]

    @classmethod
    def from_text(cls, text: str) -> 'Sample':
        return cls.from_lines(iter(text.strip().splitlines()))

    def __str__(self) -> str:
        return f"Before: {self.before}\n{self.instr}\nAfter:{self.after}"

    @classmethod
    def from_lines(cls, lines: Iterator[str]) -> 'Sample':
        def registers(values: Iterable[str]) -> list[int]:
            return [int(val) for val in values]

        return cls(
            before=registers(parse_line(next(lines).strip(), "Before: [$, $, $, $]")),
            instr=Instr.from_str(next(lines)),
            after=registers(parse_line(next(lines).strip(), "After:  [$, $, $, $]"))
        )

    def possible_opcodes(self) -> Iterable[str]:
        return (
            opcode
            for opcode, op in all_ops.items()
            if op(self.instr.a, self.instr.b, self.before) == self.after[self.instr.c]
        )


def map_opnums_to_opcodes(samples: Iterable[Sample]) -> Iterable[tuple[int, str]]:
    possible_n2c: dict[int, set[str]] = {
        opnum: set(all_ops.keys())
        for opnum in range(len(all_ops))
    }

    for sample in samples:
        possible_n2c[sample.instr.opnum].intersection_update(sample.possible_opcodes())

    while possible_n2c:
        try:
            opnum, opcode = next(
                (n, single_value(cs))
                for n, cs in possible_n2c.items()
                if len(cs) == 1
            )
        except StopIteration as stop:
            raise ValueError("no more matches") from stop

        yield opnum, opcode
        del possible_n2c[opnum]
        for opcodes in possible_n2c.values():
            opcodes.discard(opcode)


def run_program(program: Iterable[Instr], opnum_to_opcode: dict[int, str]) -> list[int]:
    registers = [0, 0, 0, 0]

    for instr in program:
        opcode = opnum_to_opcode[instr.opnum]
        registers[instr.c] = all_ops[opcode](instr.a, instr.b, registers)

    return registers


def input_from_file(fn: str) -> tuple[list[Sample], list[Instr]]:
    return input_from_lines(line.strip() for line in open(relative_path(__file__, fn)))


def input_from_lines(lines: Iterator[str]) -> tuple[list[Sample], list[Instr]]:
    return list(samples_from_lines(lines)), list(program_from_lines(lines))


def samples_from_lines(lines: Iterator[str]) -> Iterable[Sample]:
    while True:
        try:
            yield Sample.from_lines(lines)
            assert next(lines) == ""
        except ParseError:
            assert next(lines) == ""
            break


def program_from_lines(lines: Iterator[str]) -> Iterable[Instr]:
    return (Instr.from_str(line) for line in lines)


if __name__ == '__main__':
    samples_, program_ = input_from_file('data/16-input.txt')
    part_1(samples_)
    part_2(samples_, program_)
