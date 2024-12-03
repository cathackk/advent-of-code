"""
Advent of Code 2024
Day 3: Mull It Over
https://adventofcode.com/2024/day/3
"""

import re
from itertools import cycle
from typing import Iterable

from common.file import relative_path


def part_1(memory: list[str]) -> int:
    """
    "Our computers are having issues, so I have no idea if we have any Chief Historians in stock!
    You're welcome to check the warehouse, though," says the mildly flustered shopkeeper at the
    North Pole Toboggan Rental Shop (y2020/day02_passwords). The Historians head out to take a look.

    The shopkeeper turns to you. "Any chance you can see why our computers are having issues again?"

    The computer appears to be trying to run a program, but its memory (your puzzle input) is
    **corrupted**. All of the instructions have been jumbled up!

    It seems like the goal of the program is just to **multiply some numbers**. It does that with
    instructions like `mul(X,Y)`, where `X` and `Y` are each 1-3 digit numbers. For instance,
    `mul(44,46)` multiplies `44` by `46` to get a result of `2024`:

        >>> multiply('mul(44,46)')
        2024

    Similarly, `mul(123,4)` would multiply `123` by `4`:

        >>> multiply('mul(123,4)')
        492

    However, because the program's memory has been corrupted, there are also many invalid characters
    that should be **ignored**, even if they look like part of a `mul` instruction. Sequences like
    `mul(4*`, `mul(6,9!`, `?(12,34)`, or `mul ( 2 , 4 )` do nothing:

        >>> multiply('mul(4*')
        Traceback (most recent call last):
        ...
        ValueError: invalid instruction: 'mul(4*'
        >>> multiply('?(12,34)')
        Traceback (most recent call last):
        ...
        ValueError: invalid instruction: '?(12,34)'
        >>> multiply('mul ( 2 , 4 )')
        Traceback (most recent call last):
        ...
        ValueError: invalid instruction: 'mul ( 2 , 4 )'

    For example, consider the following section of corrupted memory:

        >>> example = 'xmul(2,4)%&mul[3,7]!@^do_not_mul(5,5)+mul(32,64]then(mul(11,8)mul(8,5))'
        >>> visualize_instructions(example)
        xmul(2,4)%&mul[3,7]!@^do_not_mul(5,5)+mul(32,64]then(mul(11,8)mul(8,5))
         ^^^^^^^^                    ^^^^^^^^                ^^^^^^^^^^^^^^^^^

    Only the four highlighted sections are real mul instructions:

        >>> list(parse_instructions([example]))
        ['mul(2,4)', 'mul(5,5)', 'mul(11,8)', 'mul(8,5)']

    Adding up the result of each instruction produces **`161`**:

        >>> sum(multiply(instr) for instr in _)
        161

    Scan the corrupted memory for uncorrupted `mul` instructions.
    **What do you get if you add up all of the results of the multiplications?**

        >>> part_1([example])
        part 1: 4 uncorrupted instructions add up to 161
        161
    """

    instructions = list(parse_instructions(memory))
    result = sum(multiply(instr) for instr in instructions)

    print(f"part 1: {len(instructions)} uncorrupted instructions add up to {result}")
    return result


def part_2(memory: list[str]) -> int:
    """
    As you scan through the corrupted memory, you notice that some of the conditional statements are
    also still intact. If you handle some of the uncorrupted conditional statements in the program,
    you might be able to get an even more accurate result.

    There are two new instructions you'll need to handle:

      - The `do()` instruction **enables** future `mul` instructions.
      - The `don't()` instruction **disables** future `mul` instructions.

    Only the **most recent** `do()` or `don't()` instruction applies.
    At the beginning of the program, `mul` instructions are **enabled**.

    For example:

        >>> example, = memory_from_file('data/03-example.txt')
        >>> visualize_enabled_instructions(example)
        xmul(2,4)&mul[3,7]!^don't()_mul(5,5)+mul(32,64](mul(11,8)undo()?mul(8,5))
         ^^^^^^^^           don't() xxxxxxxx            xxxxxxxxx  do() ^^^^^^^^

    This corrupted memory is similar to the example from before, but this time the `mul(5,5)` and
    `mul(11,8)` instructions are **disabled** (`x`) because there is a `don't()` instruction before
    them. The other `mul` instructions function normally, including the one at the end that gets
    **re-enabled** (`^`) by a `do()` instruction:

        >>> list(parse_enabled_instructions([example]))
        ['mul(2,4)', 'mul(8,5)']

    This time, the sum of the results is **`48`**:

        >>> sum(multiply(instr) for instr in _)
        48

    Handle the new instructions.
    **What do you get if you add up all of the results of just the enabled multiplications?**

        >>> part_2([example])
        part 2: 2 uncorrupted and enabled instructions add up to 48
        48
    """

    instructions = list(parse_enabled_instructions(memory))
    result = sum(multiply(instr) for instr in instructions)

    print(f"part 2: {len(instructions)} uncorrupted and enabled instructions add up to {result}")
    return result


RE_MUL = re.compile(r'mul\((\d{1,3}),(\d{1,3})\)')
RE_PART_1 = re.compile(r'mul\(\d{1,3},\d{1,3}\)')
RE_PART_2 = re.compile(r"mul\(\d{1,3},\d{1,3}\)|do\(\)|don't\(\)")


def multiply(instruction: str) -> int:
    matched = re.match(RE_MUL, instruction)
    if not matched:
        raise ValueError(f'invalid instruction: {instruction!r}')

    a, b = matched.groups()
    return int(a) * int(b)


def parse_instructions(memory: list[str]) -> Iterable[str]:
    return (
        m.group()
        for line in memory
        for m in re.finditer(RE_PART_1, line)
    )


def parse_enabled_instructions(memory: list[str]) -> Iterable[str]:
    enabled = True
    for instr in (m.group() for line in memory for m in re.finditer(RE_PART_2, line)):
        match instr:
            case "do()":
                enabled = True
            case "don't()":
                enabled = False
            case _:
                if enabled:
                    yield instr


def visualize_instructions(memory_line: str) -> None:
    highlighted = {
        index
        for m in re.finditer(RE_PART_1, memory_line)
        for index in range(*m.span())
    }
    highlight = ''.join(
        '^' if index in highlighted else ' '
        for index in range(len(memory_line))
    ).rstrip()

    print(memory_line)
    print(highlight)


def visualize_enabled_instructions(memory_line: str) -> None:
    enabled = True
    highlight_buffer: list[str] = []

    def push(chars: str, span: tuple[int, int]) -> None:
        start, stop = span
        while len(highlight_buffer) < start:
            highlight_buffer.append(' ')
        for _, char in zip(range(start, stop), cycle(chars)):
            highlight_buffer.append(char)

    for instr in re.finditer(RE_PART_2, memory_line):
        match instr.group():
            case "do()":
                enabled = True
                push("do()", instr.span())
            case "don't()":
                enabled = False
                push("don't()", instr.span())
            case _:
                push('^' if enabled else 'x', instr.span())

    print(memory_line)
    print(''.join(highlight_buffer))


def memory_from_file(fn: str) -> list[str]:
    return [line.strip() for line in open(relative_path(__file__, fn))]


def main(input_fn: str = 'data/03-input.txt') -> tuple[int, int]:
    memory = memory_from_file(input_fn)
    result_1 = part_1(memory)
    result_2 = part_2(memory)
    return result_1, result_2


if __name__ == '__main__':
    main()
