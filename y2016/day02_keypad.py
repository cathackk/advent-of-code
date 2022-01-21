"""
Advent of Code 2016
Day 2: Bathroom Security
https://adventofcode.com/2016/day/2
"""

from typing import Iterable

from common.heading import Heading
from common.rect import Rect
from common.file import relative_path


def part_1(instructions: Iterable['Steps']) -> str:
    """
    You arrive at **Easter Bunny Headquarters** under cover of darkness. However, you left in such
    a rush that you forgot to use the bathroom! Fancy office buildings like this one usually have
    keypad locks on their bathrooms, so you search the front desk for the code.

    "In order to improve security," the document you find says, "bathroom codes will no longer be
    written down. Instead, please memorize and follow the procedure below to access the bathrooms."

    The document goes on to explain that each button to be pressed can be found by starting on
    the previous button and moving to adjacent buttons on the keypad: `U` moves up, `D` moves down,
    `L` moves left, and `R` moves right.

        >>> CODE_TO_HEADING
        {'U': Heading.NORTH, 'D': Heading.SOUTH, 'L': Heading.WEST, 'R': Heading.EAST}

    Each line of instructions corresponds to one button,
    starting at the previous button (or, for the first line, **the "5" button**); press whatever
    button you're on at the end of each line. If a move doesn't lead to a button, ignore it.

    You can't hold it much longer, so you decide to figure out the code as you walk to the bathroom.
    You picture a keypad like this:

        >>> print(KEYPAD_1)
        1 2 3
        4 5 6
        7 8 9

    Suppose your instructions are:

        >>> example_instructions = instructions_from_text('''
        ...     ULL
        ...     RRDDD
        ...     LURDL
        ...     UUUUD
        ... ''')

      - You start at "5" and move up (to "2"), left (to "1"), and left (you can't, and stay on "1"),
        so the first button is `1`.
      - Starting from the previous button ("1"), you move right twice (to "3") and then down three
        times (stopping at "9" after two moves and ignoring the third), ending up with `9`.
      - Continuing from "9", you move left, up, right, down, and left, ending with `8`.
      - Finally, you move up four times (stopping at "2"), then down once, ending with `5`.

    So, in this example, the bathroom code is 1985:

        >>> list(KEYPAD_1.walk(example_instructions))
        ['1', '9', '8', '5']

    Your puzzle input is the instructions from the document you found at the front desk.
    What is the **bathroom code**?

        >>> part_1(example_instructions)
        part 1: bathroom code is 1985
        '1985'
    """
    code = ''.join(KEYPAD_1.walk(instructions))
    print(f"part 1: bathroom code is {code}")
    return code


def part_2(instructions: Iterable['Steps']) -> str:
    """
    You finally arrive at the bathroom (it's a several minute walk from the lobby so visitors can
    behold the many fancy conference rooms and water coolers on this floor) and go to punch in
    the code. Much to your bladder's dismay, the keypad is not at all like you imagined it. Instead,
    you are confronted with the result of hundreds of man-hours of bathroom-keypad-design meetings:

        >>> print(KEYPAD_2)
            1
          2 3 4
        5 6 7 8 9
          A B C
            D

    You still start at "5" and stop when you're at an edge, but given the same instructions as
    above, the outcome is very different:

        >>> example_instructions = instructions_from_file('data/02-example.txt')

      - You start at "5" and don't move at all (up and left are both edges), ending at `5`.
      - Continuing from "5", you move right twice and down three times (through "6", "7", "B", "D",
        "D"), ending at `D`.
      - Then, from "D", you move five more times (through "D", "B", "C", "C", "B"), ending at `B`.
      - Finally, after five more moves, you end at `3`.

    So, given the actual keypad layout, the code would be 5DB3:

        >>> list(KEYPAD_2.walk(example_instructions))
        ['5', 'D', 'B', '3']

    Using the same instructions in your puzzle input, what is the correct **bathroom code**?

        >>> part_2(example_instructions)
        part 2: bathroom code is 5DB3
        '5DB3'
    """
    code = ''.join(KEYPAD_2.walk(instructions))
    print(f"part 2: bathroom code is {code}")
    return code


CODE_TO_HEADING = {
    'U': Heading.NORTH,
    'D': Heading.SOUTH,
    'L': Heading.WEST,
    'R': Heading.EAST
}


Pos = tuple[int, int]
Steps = list[Heading]


class Keypad:
    def __init__(self, keys: Iterable[tuple[Pos, str]]):
        self.keys = dict(keys)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.keys!r})'

    def get(self, pos: Pos, default: str) -> str:
        return self.keys.get(pos, default)

    def __getitem__(self, pos: Pos):
        return self.keys[pos]

    def __contains__(self, pos: Pos):
        return pos in self.keys

    def __str__(self):
        rect = Rect.with_all(self.keys)
        return "\n".join(
            " ".join(self.get((x, y), " ") for x in rect.range_x()).rstrip()
            for y in rect.range_y()
        )

    @classmethod
    def from_str(cls, text: str) -> 'Keypad':
        return cls.from_lines(text.strip("\n").splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Keypad':
        return cls(
            ((x, y), char)
            for y, line in enumerate(lines)
            for x, char in enumerate(line[::2])
            if char != " "
        )

    def position_of(self, key: str) -> Pos:
        return next(pos for pos, k in self.keys.items() if k == key)

    def walk(self, instructions: Iterable[Steps], starting_key: str = '5') -> Iterable[str]:
        pos = self.position_of(starting_key)
        for steps in instructions:
            for step in steps:
                new_pos = step.move(pos)
                if new_pos in self:
                    pos = new_pos

            yield self[pos]


KEYPAD_1 = Keypad.from_str('''
1 2 3
4 5 6
7 8 9
''')

KEYPAD_2 = Keypad.from_str('''
    1   
  2 3 4
5 6 7 8 9
  A B C
    D
''')


def instructions_from_text(text: str) -> list[Steps]:
    return list(instructions_from_lines(text.strip().splitlines()))


def instructions_from_file(fn: str) -> list[Steps]:
    return list(instructions_from_lines(open(relative_path(__file__, fn))))


def instructions_from_lines(lines: Iterable[str]) -> Iterable[Steps]:
    return (
        [CODE_TO_HEADING[char] for char in line.strip()]
        for line in lines
    )


if __name__ == '__main__':
    instructions_ = list(instructions_from_file('data/02-input.txt'))
    part_1(instructions_)
    part_2(instructions_)
