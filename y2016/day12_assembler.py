"""
Advent of Code 2016
Day 12: Leonardo's Monorail
https://adventofcode.com/2016/day/12
"""

from meta.aoc_tools import data_path
from y2016 import assembunny


def part_1(tape: assembunny.Tape) -> int:
    """
    You finally reach the top floor of this building: a garden with a slanted glass ceiling. Looks
    like there are no more stars to be had.

    While sitting on a nearby bench amidst some tiger lilies, you manage to decrypt some of
    the files you extracted from the servers downstairs.

    According to these documents, Easter Bunny HQ isn't just this building - it's a collection of
    buildings in the nearby area. They're all connected by a local monorail, and there's another
    building not far from here! Unfortunately, being night, the monorail is currently not operating.

    You remotely connect to the monorail control systems and discover that the boot sequence expects
    a password. The password-checking logic (your puzzle input) is easy to extract, but the code it
    uses is strange: it's assembunny code designed for the new computer you just assembled. You'll
    have to execute the code and get the password.

    The assembunny code you've extracted operates on four registers (`a`, `b`, `c`, and `d`) that
    start at `0` and can hold any integer. However, it seems to make use of only a few instructions:

      - `cpy x y` **copies** `x` (either an integer or the value of a register) into register `y`.
      - `inc x` **increases** the value of register `x` by one.
      - `dec x` **decreases** the value of register `x` by one.
      - `jnz x y` **jumps** to an instruction `y` away (positive means forward; negative means
        backward), but only if `x` is not zero.

    The `jnz` instruction moves relative to itself: an offset of `-1` would continue at the previous
    instruction, while an offset of `2` would skip over the next instruction.

    For example:

        >>> (example_tape := assembunny.Tape.from_text('''
        ...     cpy 41 a
        ...     inc a
        ...     inc a
        ...     dec a
        ...     jnz a 2
        ...     dec a
        ... '''))  # doctest: +NORMALIZE_WHITESPACE
        Tape([Command('cpy', 41, 'a'), Command('inc', 'a'), Command('inc', 'a'),
              Command('dec', 'a'), Command('jnz', 'a', 2), Command('dec', 'a')])

    The above code would set register `a` to 41, increase its value by `2`, decrease its value by
    `1`, and then skip the last `dec a` (because `a` is not zero, so the `jnz a 2` skips it),
    leaving register `a` at `42`. When you move past the last instruction, the program halts.

        >>> assembunny.run(example_tape)['a']
        42

    After executing the assembunny code in your puzzle input, **what value is left in
    register `a`**?

        >>> part_1(example_tape)
        part 1: a = 42
        42
    """
    result = assembunny.run(tape)['a']
    print(f"part 1: a = {result}")
    return result


def part_2(tape: assembunny.Tape) -> int:
    """
    As you head down the fire escape to the monorail, you notice it didn't start; register `c` needs
    to be initialized to the position of the ignition key.

    If you instead **initialize register `c` to be `1`**, what value is now left in register `a`?

        >>> example_tape = assembunny.Tape.from_file(data_path(__file__, 'example.txt'))
        >>> assembunny.run(example_tape)['a']
        41
        >>> assembunny.run(example_tape, c=1)['a']
        42

        >>> part_2(example_tape)
        part 2: a = 42
        42
    """

    result = assembunny.run(tape, c=1, optimized=True)['a']
    print(f"part 2: a = {result}")
    return result


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    tape = assembunny.Tape.from_file(input_path)
    result_1 = part_1(tape)
    result_2 = part_2(tape)
    return result_1, result_2


if __name__ == '__main__':
    main()
