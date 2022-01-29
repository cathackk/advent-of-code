"""
Advent of Code 2017
Day 23: Coprocessor Conflagration
https://adventofcode.com/2017/day/23
"""

import math
from collections import Counter

from common.file import relative_path
from y2016.assembunny import Command
from y2016.assembunny import Tape
from y2016.assembunny import run as assembunny_run
from y2016.assembunny import run_generator as assembunny_run_generator


def part_1(tape: Tape):
    """
    You decide to head directly to the CPU and fix the printer from there. As you get close, you
    find an **experimental coprocessor** doing so much work that the local programs are afraid it
    will halt and catch fire. This would cause serious issues for the rest of the computer, so you
    head in and see what you can do.

    The code it's running seems to be a variant of the kind you saw recently on that tablet. The
    general functionality seems very similar, but some of the instructions are different:

      - `set X Y` **sets** register `X` to the value of `Y`.
      - `sub X Y` **decreases** register `X` by the value of `Y`.
      - `mul X Y` sets register `X` to the result of **multiplying** the value contained in register
        `X` by the value of `Y`.
      - `jnz X Y` **jumps** with an offset of the value of `Y`, but only if the value of `X` is not
        zero. (An offset of `2` skips the next instruction, an offset of `-1` jumps to the previous
        instruction, and so on.)

    Only the instructions listed above are used. The eight registers here, named `a` through `h`,
    all start at `0`.

        >>> example_program = tape_from_text('''
        ...     set e 2
        ...     set f 5
        ...     sub f e
        ...     mul e f
        ...     jnz e 2
        ...     mul f 100
        ... ''')
        >>> example_program  # doctest: +NORMALIZE_WHITESPACE
        Tape([Command('cpy', 2, 'e'), Command('cpy', 5, 'f'), Command('sub', 'e', 'f'),
              Command('mul', 'f', 'e'), Command('jnz', 'e', 2), Command('mul', 100, 'f')])
        >>> run(example_program)
        {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 6, 'f': 3, 'g': 0, 'h': 0}

    The coprocessor is currently set to some kind of **debug mode**, which allows for testing, but
    prevents it from doing any meaningful work.

    If you run the program (your puzzle input), **how many times is the `mul` instruction invoked?**

        >>> part_1(example_program)
        part 1: mul instruction invoked 1 times
        1
    """

    result = run_counting_instr(tape)['mul']
    print(f"part 1: mul instruction invoked {result} times")
    return result


# TODO: use tape
# pylint: disable=unused-argument
def part_2(tape: Tape):
    """
    Now, it's time to fix the problem.

    The **debug mode switch** is wired directly to register `a`. You flip the switch, which makes
    **register `a` now start at `1`** when the program is executed.

    Immediately, the coprocessor begins to overheat. Whoever wrote this program obviously didn't
    choose a very efficient implementation. You'll need to **optimize the program** if it has any
    hope of completing before Santa needs that printer working.

    The coprocessor's ultimate goal is to determine the final value left in register `h` once the
    program completes. Technically, if it had that... it wouldn't even need to run the program.

    After setting register `a` to `1`, if the program were to run to completion, **what value would
    be left in register `h`?**

    TODO: part 2 doctest?
    """

    # TODO: write optimization rules for assembunny??
    # result = run(tape, init_registers={'a': 1})['h']
    result = program_part2()
    print(f"part 2: program finishes with h={result}")
    return result


# TODO: remove after finishing the optimization
# pylint: disable=invalid-name
def program_part1():
    h = 0
    mul = 0

    # set b 57
    # set c b
    # jnz a 2 <- a is always true
    # jnz 1 5
    # skipped: mul b 100
    # skipped: sub b -100_000
    # skipped: set c b
    # skipped: sub c -17_000
    b = 57
    c = 57

    while True:
        # set f 1
        f = 1
        # set d 2
        d = 2

        while True:
            # set e 2
            e = 2

            while True:
                # set g d
                # mul g e
                # sub g b
                g = d * e - b
                mul += 1

                # jnz g 2
                # set f 0
                if g == 0:
                    f = 0

                # sub e -1
                e += 1
                # set g e
                # sub g b
                g = e - b

                # jnz g -8
                if g == 0:
                    break

            # sub d -1
            d += 1
            # set g d
            # sub g b
            g = d - b
            # jnz g -13
            if g == 0:
                break

        # jnz f 2
        # sub h -1
        if f == 0:
            h += 1

        # set g b
        # sub g c
        g = b - c
        # jnz g 2
        # jnz 1 3
        if g == 0:
            return mul

        # sub b -17
        # jnz 1 -23
        b += 17


def program_part2():
    return sum(
        1 for b in range(105_700, 122_700 + 1, 17)
        if any(b % d == 0 for d in range(2, math.ceil(math.sqrt(b))))
    )


def assembunny_compatible_tape(tape: Tape) -> Tape:
    def compatible_command(command: Command) -> Command:
        match command:
            case Command('set', (target, source)):
                return Command('cpy', source, target)
            case Command('sub', (target, source)):
                return Command('sub', source, target)
            case Command('mul', (target, source)):
                return Command('mul', source, target)
            case Command('jnz', _):
                return command
            case _:
                raise ValueError(f"unexpected command {command!r}")

        # TODO: remove when mypy realizes this is unreachable
        assert False

    return type(tape)(compatible_command(cmd) for cmd in tape)


# there are 8 registers instead of the assembunny's default 4
DEFAULT_REGISTERS = {reg: 0 for reg in 'abcdefgh'}


def run(tape: Tape, init_registers: dict[str, int] = None) -> dict[str, int]:
    registers = dict(DEFAULT_REGISTERS)
    if init_registers:
        registers.update(init_registers)
    return assembunny_run(tape, optimized=True, **registers)


def run_counting_instr(tape: Tape) -> Counter[str]:
    return Counter(
        state.command.instr
        for state in assembunny_run_generator(tape, optimized=True, **DEFAULT_REGISTERS)
    )


def tape_from_text(text: str) -> Tape:
    return assembunny_compatible_tape(Tape.from_text(text))


def tape_from_file(fn: str) -> Tape:
    return assembunny_compatible_tape(Tape.from_lines(open(relative_path(__file__, fn))))


if __name__ == '__main__':
    tape_ = tape_from_file('data/23-input.txt')
    part_1(tape_)
    part_2(tape_)
