"""
Advent of Code 2016
Day 21: Scrambled Letters and Hash
https://adventofcode.com/2016/day/21
"""

from typing import Iterable

from common.text import parse_line
from common.file import relative_path


def part_1(commands: Iterable['Command'], password: str = 'abcdefgh') -> str:
    r"""
    The computer system you're breaking into uses a weird scrambling function to store its
    passwords. It shouldn't be much trouble to create your own scrambled password so you can add it
    to the system; you just have to implement the scrambler.

    The scrambling function is a series of operations (the exact list is provided in your puzzle
    input). Starting with the password to be scrambled, apply each operation in succession to the
    string. The individual operations behave as follows:

      - `swap position X with position Y` means that the letters at indexes `X` and `Y` (counting
        from `0`) should be **swapped**.
      - `swap letter X with letter Y` means that the letters `X` and `Y` should be **swapped**
        (regardless of where they appear in the string).
      - `rotate left/right X steps` means that the whole string should be **rotated**; for example,
        one right rotation would turn `abcd` into `dabc`.
      - `rotate based on position of letter X` means that the whole string should be rotated to the
        **right** based on the **index** of letter `X` (counting from `0`) as determined **before**
        this instruction does any rotations. Once the index is determined, rotate the string to the
        right one time, plus a number of times equal to that index, plus one additional time if the
        index was at least 4.
      - reverse positions `X` through `Y` means that the span of letters at indexes `X` through `Y`
        (including the letters at `X` and `Y`) should be **reversed in order**.
      - `move position X to position Y` means that the letter which is at index `X` should be
        **removed** from the string, then **inserted** such that it ends up at index `Y`.

    For example, suppose you start with `abcde` and perform the following operations:

        >>> apply("swap position 4 with position 0", 'abcde')
        'ebcda'
        >>> apply("swap letter d with letter b", _)
        'edcba'
        >>> apply("reverse positions 0 through 4", _)
        'abcde'
        >>> apply("rotate left 1 step", _)
        'bcdea'
        >>> apply("move position 1 to position 4", _)
        'bdeac'
        >>> apply("move position 3 to position 0", _)
        'abdec'
        >>> apply("rotate based on position of letter b", _)
        'ecabd'
        >>> apply("rotate based on position of letter d", _)
        'decab'

    After these steps, the resulting scrambled password is `decab`.

    Now, you just need to generate a new scrambled password and you can access the system. Given the
    list of scrambling operations in your puzzle input, **what is the result of scrambling
    `abcdefgh`**?

        >>> example_commands = commands_from_file('data/21-example.txt')
        >>> print("\n".join(str(cmd) for cmd in example_commands))
        swap position 4 with position 0
        swap letter d with letter b
        reverse positions 0 through 4
        rotate left 1 step
        move position 1 to position 4
        move position 3 to position 0
        rotate based on position of letter b
        rotate based on position of letter d
        >>> part_1(example_commands, password='abcde')
        part 1: scrambled password is 'decab'
        'decab'
    """

    scrambled = scramble(password, commands)
    print(f"part 1: scrambled password is {scrambled!r}")
    return scrambled


def part_2(commands: Iterable['Command'], scrambled: str = 'fbgdceah') -> str:
    """
    You scrambled the password correctly, but you discover that you can't actually modify the
    password file on the system. You'll need to un-scramble one of the existing passwords by
    reversing the scrambling process.

    What is the un-scrambled version of the scrambled password `fbgdceah`?

        >>> example_commands = commands_from_file('data/21-example.txt')
        >>> part_2(example_commands, 'decab')
        part 2: unscrambled password is 'abcde'
        'abcde'
    """

    password = unscramble(scrambled, commands)
    assert scramble(password, commands) == scrambled
    print(f"part 2: unscrambled password is {password!r}")
    return password


def swap_positions(string: str, pos_1: int, pos_2: int) -> str:
    """
        >>> swap_positions('ahoj', 0, 3)
        'jhoa'
        >>> swap_positions('ahoj', 3, 0)
        'jhoa'
        >>> swap_positions('hello', 1, 2)
        'hlelo'
        >>> swap_positions('hello', 2, 1)
        'hlelo'
        >>> swap_positions('abcde', 2, 2)
        'abcde'
    """

    assert 0 <= pos_1 < len(string)
    assert 0 <= pos_2 < len(string)

    if pos_1 == pos_2:
        return string

    if pos_1 > pos_2:
        pos_1, pos_2 = pos_2, pos_1

    return string[:pos_1] + string[pos_2] + string[pos_1+1:pos_2] + string[pos_1] + string[pos_2+1:]


def swap_letters(string: str, letter_1: str, letter_2: str) -> str:
    """
        >>> swap_letters('abcde', 'a', 'd')
        'dbcae'
    """

    assert len(letter_1) == 1
    assert len(letter_2) == 1
    index_1 = string.index(letter_1)
    index_2 = string.index(letter_2)
    return swap_positions(string, index_1, index_2)


def rotate_left(string: str, n: int) -> str:
    """
        >>> rotate_left('abcde', 2)
        'cdeab'
        >>> rotate_left('abcde', -1)
        'eabcd'
        >>> rotate_left('xyz', 5)
        'zxy'
    """

    n = n % len(string)
    return string[n:] + string[:n]


def rotate_right(string: str, n: int) -> str:
    return rotate_left(string, -n)


def rotate_by_letter(string: str, letter: str) -> str:
    """
        >>> rotate_by_letter('abcde', 'b')
        'deabc'
        >>> rotate_by_letter('abcdefg', 'd')
        'defgabc'
        >>> rotate_by_letter('abcdefg', 'e')
        'bcdefga'
    """
    index = string.index(letter)
    steps = index + (2 if index >= 4 else 1)
    return rotate_right(string, steps)


def reverse_substring(string: str, pos_1: int, pos_2: int) -> str:
    """
        >>> reverse_substring('abcdef', 1, 3)
        'adcbef'
        >>> reverse_substring('abcdef', 1, 4)
        'aedcbf'
        >>> reverse_substring('abcdef', 0, 4)
        'edcbaf'
        >>> reverse_substring('abcdef', 1, 5)
        'afedcb'
        >>> reverse_substring('abcd', 0, 3)
        'dcba'
        >>> reverse_substring('abcd', 1, 1)
        'abcd'
    """

    assert 0 <= pos_1 < len(string)
    assert 0 <= pos_2 < len(string)
    assert pos_1 <= pos_2

    if pos_1 == 0:
        return string[pos_2::-1] + string[pos_2 + 1:]
    elif pos_1 != pos_2:
        return string[:pos_1] + string[pos_2:pos_1 - 1:-1] + string[pos_2 + 1:]
    else:
        return string


def move(string: str, pos_1: int, pos_2: int) -> str:
    """
        >>> move('abcde', 1, 3)
        'acdbe'
        >>> move('abcde', 0, 1)
        'bacde'
        >>> move('abcde', 0, 4)
        'bcdea'
        >>> move('abcde', 3, 1)
        'adbce'
        >>> move('abcde', 4, 0)
        'eabcd'
        >>> move('abcde', 4, 3)
        'abced'
        >>> move('abcde', 2, 2)
        'abcde'
    """

    assert 0 <= pos_1 < len(string)
    assert 0 <= pos_2 < len(string)
    if pos_1 < pos_2:
        return string[:pos_1] + string[pos_1 + 1:pos_2 + 1] + string[pos_1] + string[pos_2 + 1:]
    elif pos_1 > pos_2:
        return string[:pos_2] + string[pos_1] + string[pos_2:pos_1] + string[pos_1 + 1:]
    else:
        return string


class Command:
    def __init__(self, instr: str, arg1, arg2=None):
        self.instr = instr
        self.arg1 = arg1
        self.arg2 = arg2

    __match_args__ = ('instr', 'arg1', 'arg2')

    def __repr__(self):
        args = f'{self.arg1!r}, {self.arg2!r}' if self.arg2 is not None else repr(self.arg1)
        return f'{type(self).__name__}({self.instr!r}, {args})'

    # pylint: disable=invalid-str-returned
    def __str__(self) -> str:
        match self:
            case Command('swap_pos', pos_1, pos_2):
                return f"swap position {pos_1} with position {pos_2}"
            case Command('swap_letter', letter_1, letter_2):
                return f"swap letter {letter_1} with letter {letter_2}"
            case Command('rot_steps', direction, steps):
                return f"rotate {direction} {steps} step"
            case Command('rot_letter', letter, None):
                return f"rotate based on position of letter {letter}"
            case Command('reverse', pos_1, pos_2):
                return f"reverse positions {pos_1} through {pos_2}"
            case Command('move', pos_1, pos_2):
                return f"move position {pos_1} to position {pos_2}"
            case _:
                raise ValueError(self)

    # pylint: disable=too-many-return-statements
    def apply(self, string: str) -> str:
        match self:
            case Command('swap_pos', pos_1, pos_2):
                return swap_positions(string, pos_1, pos_2)
            case Command('swap_letter', letter_1, letter_2):
                return swap_letters(string, letter_1, letter_2)
            case Command('rot_steps', 'left', steps):
                return rotate_left(string, steps)
            case Command('rot_steps', 'right', steps):
                return rotate_right(string, steps)
            case Command('rot_letter', letter):
                return rotate_by_letter(string, letter)
            case Command('reverse', pos_1, pos_2):
                return reverse_substring(string, pos_1, pos_2)
            case Command('move', pos_1, pos_2):
                return move(string, pos_1, pos_2)
            case _:
                raise ValueError(self)

    # pylint: disable=too-many-return-statements
    def unapply(self, string: str) -> str:
        match self:
            case Command('swap_pos', pos_1, pos_2):
                # symmetric -> same as apply
                return swap_positions(string, pos_1, pos_2)
            case Command('swap_letter', letter_1, letter_2):
                # symmetric -> same as apply
                return swap_letters(string, letter_1, letter_2)
            case Command('rot_steps', 'left', steps):
                # rotate right instead
                return rotate_right(string, steps)
            case Command('rot_steps', 'right', steps):
                # rotate left instead
                return rotate_left(string, steps)
            case Command('rot_letter', letter):
                # ¯\_(ツ)_/¯
                return next(
                    rs for rs in (
                        rotate_left(string, k)
                        for k in range(len(string))
                    ) if rotate_by_letter(rs, letter) == string
                )
            case Command('reverse', pos_1, pos_2):
                # symmetric -> same as apply
                return reverse_substring(string, pos_1, pos_2)
            case Command('move', pos_1, pos_2):
                # reverse args, pylint: disable=arguments-out-of-order
                return move(string, pos_2, pos_1)
            case _:
                raise ValueError(repr(self))

    @classmethod
    def from_str(cls, line: str) -> 'Command':
        line = line.strip()

        if line.startswith("swap position "):
            # swap position 4 with position 0
            pos_1, pos_2 = parse_line(line, "swap position $ with position $")
            return cls('swap_pos', int(pos_1), int(pos_2))

        elif line.startswith("swap letter "):
            # swap letter d with letter b
            letter_1, letter_2 = parse_line(line, "swap letter $ with letter $")
            return cls('swap_letter', letter_1, letter_2)

        elif line.startswith("rotate left ") or line.startswith("rotate right "):
            # rotate left 1 step
            direction, steps, _ = parse_line(line, "rotate $ $ step$")
            return cls('rot_steps', direction, int(steps))

        elif line.startswith("rotate based "):
            # rotate based on position of letter b
            letter, = parse_line(line, "rotate based on position of letter $")
            return cls('rot_letter', letter)

        elif line.startswith("reverse positions "):
            # reverse positions 0 through 4
            pos_1, pos_2 = parse_line(line, "reverse positions $ through $")
            return cls('reverse', int(pos_1), int(pos_2))

        elif line.startswith("move position "):
            # move position 1 to position 4
            pos_1, pos_2 = parse_line(line, "move position $ to position $")
            return cls('move', int(pos_1), int(pos_2))

        else:
            raise ValueError(line)


def apply(command: str | Command, string: str) -> str:
    if isinstance(command, str):
        command = Command.from_str(command)

    return command.apply(string)


def unapply(command: str | Command, string: str) -> str:
    if isinstance(command, str):
        command = Command.from_str(command)

    return command.apply(string)


def scramble(string: str, commands: Iterable[Command]) -> str:
    for cmd in commands:
        string = cmd.apply(string)
    return string


def unscramble(string: str, commands: Iterable[Command]) -> str:
    for cmd in reversed(list(commands)):
        string = cmd.unapply(string)
    return string


def commands_from_file(fn: str) -> list[Command]:
    return list(commands_from_lines(open(relative_path(__file__, fn))))


def commands_from_lines(lines: Iterable[str]) -> Iterable[Command]:
    return (Command.from_str(line) for line in lines)


if __name__ == '__main__':
    commands_ = commands_from_file('data/21-input.txt')
    part_1(commands_)
    part_2(commands_)
