from typing import Iterable
from typing import List


def swap_positions(s: str, a: int, b: int) -> str:
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
    assert 0 <= a < len(s)
    assert 0 <= b < len(s)
    if a > b:
        a, b = b, a

    if a != b:
        return s[:a] + s[b] + s[a+1:b] + s[a] + s[b+1:]
    else:
        return s


def swap_letters(s: str, a: str, b: str) -> str:
    """
    >>> swap_letters('abcde', 'a', 'd')
    'dbcae'
    """
    assert len(a) == 1
    assert len(b) == 1
    ia = s.index(a)
    ib = s.index(b)
    return swap_positions(s, ia, ib)


def rotate_left(s: str, n: int) -> str:
    """
    >>> rotate_left('abcde', 2)
    'cdeab'
    >>> rotate_left('abcde', -1)
    'eabcd'
    >>> rotate_left('xyz', 5)
    'zxy'
    """
    n = n % len(s)
    return s[n:] + s[:n]


def rotate_right(s: str, n: int) -> str:
    return rotate_left(s, -n)


def rotate_by_letter(s: str, c: str) -> str:
    """
    >>> rotate_by_letter('abcde', 'b')
    'deabc'
    >>> rotate_by_letter('abcdefg', 'd')
    'defgabc'
    >>> rotate_by_letter('abcdefg', 'e')
    'bcdefga'
    """
    pos = s.index(c)
    steps = pos + (2 if pos >= 4 else 1)
    return rotate_right(s, steps)


def reverse_substring(s: str, a: int, b: int) -> str:
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
    assert 0 <= a < len(s)
    assert 0 <= b < len(s)
    assert a <= b

    if a == 0:
        return s[b::-1] + s[b+1:]
    elif a != b:
        return s[:a] + s[b:a-1:-1] + s[b+1:]
    else:
        return s


def move(s: str, a: int, b: int) -> str:
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
    assert 0 <= a < len(s)
    assert 0 <= b < len(s)
    if a < b:
        return s[:a] + s[a+1:b+1] + s[a] + s[b+1:]
    elif a > b:
        return s[:b] + s[a] + s[b:a] + s[a+1:]
    else:
        return s


class Command:
    def __init__(self, instr: str, arg1, arg2=None):
        self.instr = instr
        self.arg1 = arg1
        self.arg2 = arg2

    def __repr__(self):
        args = f'{self.arg1!r}, {self.arg2!r}' if self.arg2 is not None else repr(self.arg1)
        return f'{type(self).__name__}({args})'

    def __str__(self):
        if self.instr == 'swap_pos':
            return f"swap position {self.arg1} with position {self.arg2}"
        elif self.instr == 'swap_letter':
            return f"swap letter {self.arg1} with letter {self.arg2}"
        elif self.instr == 'rot_steps':
            return f"rotate {self.arg1} {self.arg2} step"
        elif self.instr == 'rot_letter':
            return f"rotate based on position of letter {self.arg1}"
        elif self.instr == 'reverse':
            return f"reverse positions {self.arg1} through {self.arg2}"
        elif self.instr == 'move':
            return f"move position {self.arg1} to position {self.arg2}"
        else:
            raise KeyError(self.instr)

    def apply(self, s: str) -> str:
        if self.instr == 'swap_pos':
            return swap_positions(s, self.arg1, self.arg2)
        elif self.instr == 'swap_letter':
            return swap_letters(s, self.arg1, self.arg2)
        elif self.instr == 'rot_steps':
            if self.arg1 == 'left':
                return rotate_left(s, self.arg2)
            else:
                return rotate_right(s, self.arg2)
        elif self.instr == 'rot_letter':
            return rotate_by_letter(s, self.arg1)
        elif self.instr == 'reverse':
            return reverse_substring(s, self.arg1, self.arg2)
        elif self.instr == 'move':
            return move(s, self.arg1, self.arg2)
        else:
            raise KeyError(self.instr)

    def unapply(self, s: str) -> str:
        if self.instr == 'swap_pos':
            # symmetric -> same as apply
            return swap_positions(s, self.arg1, self.arg2)
        elif self.instr == 'swap_letter':
            # symmetric -> same as apply
            return swap_letters(s, self.arg1, self.arg2)
        elif self.instr == 'rot_steps':
            # apply the other direction
            if self.arg1 == 'left':
                return rotate_right(s, self.arg2)
            else:
                return rotate_left(s, self.arg2)
        elif self.instr == 'rot_letter':
            # ¯\_(ツ)_/¯
            return next(
                rs for rs in (
                    rotate_left(s, k)
                    for k in range(len(s))
                ) if rotate_by_letter(rs, self.arg1) == s
            )
        elif self.instr == 'reverse':
            # symmetric -> same as apply
            return reverse_substring(s, self.arg1, self.arg2)
        elif self.instr == 'move':
            # reverse args
            return move(s, self.arg2, self.arg1)
        else:
            raise KeyError(self.instr)

    @classmethod
    def parse(cls, line: str) -> 'Command':
        line = line.strip()

        if line.startswith("swap position "):
            # swap position 4 with position 0
            arg1, _, _, arg2 = line[14:].split(' ')
            return cls('swap_pos', int(arg1), int(arg2))

        elif line.startswith("swap letter "):
            # swap letter d with letter b
            arg1, _, _, arg2 = line[12:].split(' ')
            return cls('swap_letter', arg1, arg2)

        elif line.startswith("rotate left ") or line.startswith("rotate right "):
            # rotate left 1 step
            arg1, arg2, _ = line[7:].split(' ')
            return cls('rot_steps', arg1, int(arg2))

        elif line.startswith("rotate based on position of letter "):
            # rotate based on position of letter b
            arg1 = line[-1]
            return cls('rot_letter', arg1)

        elif line.startswith("reverse positions "):
            # reverse positions 0 through 4
            arg1, _, arg2 = line[18:].split(' ')
            return cls('reverse', int(arg1), int(arg2))

        elif line.startswith("move position "):
            # move position 1 to position 4
            arg1, _, _, arg2 = line[14:].split(' ')
            return cls('move', int(arg1), int(arg2))

        else:
            raise ValueError(line)

    @classmethod
    def load(cls, fn: str) -> List['Command']:
        return [cls.parse(line) for line in open(fn)]


def scramble(s: str, commands: Iterable[Command]) -> str:
    for cmd in commands:
        s = cmd.apply(s)
    return s


def unscramble(s: str, commands: Iterable[Command]) -> str:
    for cmd in reversed(commands):
        s = cmd.unapply(s)
    return s

def test_str_ops():
    pwd = "abcde"
    pwd = swap_positions(pwd, 4, 0)
    assert pwd == "ebcda"
    pwd = swap_letters(pwd, 'd', 'b')
    assert pwd == "edcba"
    pwd = reverse_substring(pwd, 0, 4)
    assert pwd == "abcde"
    pwd = rotate_left(pwd, 1)
    assert pwd == "bcdea"
    pwd = move(pwd, 1, 4)
    assert pwd == "bdeac"
    pwd = move(pwd, 3, 0)
    assert pwd == "abdec"
    pwd = rotate_by_letter(pwd, 'b')
    assert pwd == "ecabd"
    pwd = rotate_by_letter(pwd, 'd')
    assert pwd == "decab"


_test_lines = [
    "swap position 4 with position 0",
    "swap letter d with letter b",
    "reverse positions 0 through 4",
    "rotate left 1 step",
    "move position 1 to position 4",
    "move position 3 to position 0",
    "rotate based on position of letter b",
    "rotate based on position of letter d"
]


def test_scramble():
    commands = [Command.parse(line) for line in _test_lines]
    assert scramble("abcde", commands) == "decab"


def test_unscramble():
    commands = [Command.parse(line) for line in _test_lines]
    assert unscramble("decab", commands) == "abcde"


def part_1(password: str, commands: Iterable[Command]) -> str:
    scrambled = scramble(password, commands)
    print(f"part 1: scrambled password is {scrambled!r}")
    return scrambled


def part_2(scrambled: str, commands: Iterable[Command]) -> str:
    password = unscramble(scrambled, commands)
    assert scramble(password, commands) == scrambled
    print(f"part 2: unscrambled password is {password!r}")
    return password


if __name__ == '__main__':
    commands_ = Command.load("data/21-input.txt")
    part_1("abcdefgh", commands_)
    part_2("fbgdceah", commands_)
