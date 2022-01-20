"""
Advent of Code 2016
Day 23: Safe Cracking
https://adventofcode.com/2016/day/23
"""

from y2016 import assembunny


def part_1(tape: assembunny.Tape):
    """
    This is one of the top floors of the nicest tower in EBHQ. The Easter Bunny's private office is
    here, complete with a safe hidden behind a painting, and who **wouldn't** hide a star in a safe
    behind a painting?

    The safe has a digital screen and keypad for code entry. A sticky note attached to the safe has
    a password hint on it: "eggs". The painting is of a large rabbit coloring some eggs. You see
    `7`.

    When you go to type the code, though, nothing appears on the display; instead, the keypad comes
    apart in your hands, apparently having been smashed. Behind it is some kind of socket - one that
    matches a connector in your prototype computer (day 11)! You pull apart the smashed keypad and
    extract the logic circuit, plug it into your computer, and plug your computer into the safe.

    Now, you just need to figure out what output the keypad would have sent to the safe. You extract
    the assembunny code from the logic chip (your puzzle input).

    The code looks like it uses **almost** the same architecture and instruction set that
    the monorail computer used! You should be able to use the same assembunny interpreter for this
    as you did there, but with one new instruction:

    `tgl x` **toggles** the instruction `x` away (pointing at instructions like `jnz` does: positive
    means forward; negative means backward):

      - For **one-argument** instructions, `inc` becomes `dec`,
        and all other one-argument instructions become `inc`.
      - For **two-argument** instructions, `jnz` becomes `cpy`,
        and all other two-instructions become `jnz`.
      - The arguments of a toggled instruction are **not affected**.
      - If an attempt is made to toggle an instruction outside the program, **nothing happens**.
      - If toggling produces an **invalid instruction** (like `cpy 1 2`) and an attempt is later
        made to execute that instruction, **skip it instead**.
      - If `tgl` toggles **itself** (for example, if `a` is `0`, `tgl a` would target itself and
        become `inc a`), the resulting instruction is not executed until the next time it is
        reached.

    For example, given this program:

        >>> example = assembunny.Tape.from_text('''
        ...     cpy 2 a
        ...     tgl a
        ...     tgl a
        ...     tgl a
        ...     cpy 1 a
        ...     dec a
        ...     dec a
        ... ''')
        >>> run = assembunny.run_generator(example)

      - `cpy 2` a initializes register `a` to `2`.

        >>> next(run)  # doctest: +NORMALIZE_WHITESPACE
        RunState(head=0, command=Command('cpy', 2, 'a'), registers={'a': 2, 'b': 0, 'c': 0, 'd': 0},
                 tape='cpy 2 a; tgl a; tgl a; tgl a; cpy 1 a; dec a; dec a')

      - The first `tgl a` toggles an instruction `a` (`2`) away from it, which changes the third
        `tgl a` into `inc a`.

        >>> next(run)  # doctest: +NORMALIZE_WHITESPACE
        RunState(head=1, command=Command('tgl', 'a'), registers={'a': 2, 'b': 0, 'c': 0, 'd': 0},
                 tape='cpy 2 a; tgl a; tgl a; inc a; cpy 1 a; dec a; dec a')

      - The second `tgl` a also modifies an instruction `2` away from it, which changes the
        `cpy 1 a` into `jnz 1 a`.

        >>> next(run)  # doctest: +NORMALIZE_WHITESPACE
        RunState(head=2, command=Command('tgl', 'a'), registers={'a': 2, 'b': 0, 'c': 0, 'd': 0},
                 tape='cpy 2 a; tgl a; tgl a; inc a; jnz 1 a; dec a; dec a')

      - The fourth line, which is now `inc a`, increments `a` to `3`.

        >>> next(run)  # doctest: +ELLIPSIS
        RunState(head=3, command=Command('inc', 'a'), registers={'a': 3, ...}, tape='...')

      - Finally, the fifth line, which is now `jnz 1 a`, jumps `a` (`3`) instructions ahead,
        skipping the `dec a` instructions.

        >>> next(run)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        RunState(head=4, head_next=7, command=Command('jnz', 1, 'a'), registers={'a': 3, ...}, ...)
        >>> next(run)
        Traceback (most recent call last):
        ...
        StopIteration: (7, {'a': 3, 'b': 0, 'c': 0, 'd': 0})

    In this example, the final value in register `a` is `3`.

        >>> assembunny.run(example, return_from='a')
        3

    The rest of the electronics seem to place the keypad entry (the number of eggs, `7`) in register
    `a`, run the code, and then send the value left in register `a` to the safe.

    **What value** should be sent to the safe?

        >>> part_1(example)
        part 1: result is a=3
        3
    """

    result = assembunny.run(tape, a=7, return_from='a')
    print(f"part 1: result is a={result}")
    return result


def part_2(tape: assembunny.Tape):
    """
    The safe doesn't open, but it **does** make several angry noises to express its frustration.

    You're quite sure your logic is working correctly, so the only other thing is... you check the
    painting again. As it turns out, colored eggs are still eggs. Now you count 12.

    As you run the program with this new input, the prototype computer begins to overheat. You
    wonder what's taking so long, and whether the lack of any instruction more powerful than
    "add one" has anything to do with it. Don't bunnies usually multiply?

    Anyway, what value should actually be sent to the safe?

        >>> example = assembunny.Tape.from_file('data/23-example.txt')
        >>> part_2(example)
        part 2: result is a=720
        720
    """

    result = assembunny.run(tape, a=12, return_from='a', optimized=True)
    print(f"part 2: result is a={result}")
    return result


if __name__ == '__main__':
    tape_ = assembunny.Tape.from_file('data/23-input.txt')
    part_1(tape_)
    part_2(tape_)
