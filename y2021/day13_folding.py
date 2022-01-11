"""
Advent of Code 2021
Day 13: Transparent Origami
https://adventofcode.com/2021/day/13
"""

from typing import Iterable

from common.rect import Rect
from common.utils import parse_line
from common.utils import relative_path


def part_1(dots: set['Pos'], first_instruction: 'Instruction') -> int:
    """
    You reach another volcanically active part of the cave. It would be nice if you could do some
    kind of thermal imaging so you could tell ahead of time which caves are too hot to safely enter.

    Fortunately, the submarine seems to be equipped with a thermal camera! When you activate it,
    you are greeted with:

        > Congratulations on your purchase! To activate this infrared thermal imaging camera system,
        > please enter the code found on page 1 of the manual.

    Apparently, the Elves have never used this feature. To your surprise, you manage to find
    the manual; as you go to open it, page 1 falls out. It's a large sheet of transparent paper!
    The transparent paper is marked with random dots and includes instructions on how to fold it up
    (your puzzle input). For example:

        >>> example_dots, example_instructions = input_from_text('''
        ...
        ...     6,10
        ...     0,14
        ...     9,10
        ...     0,3
        ...     10,4
        ...     4,11
        ...     6,0
        ...     6,12
        ...     4,1
        ...     0,13
        ...     10,12
        ...     3,4
        ...     3,0
        ...     8,4
        ...     1,10
        ...     2,14
        ...     8,10
        ...     9,0
        ...
        ...     fold along y=7
        ...     fold along x=5
        ...
        ... ''')

    The first section is a list of dots on the transparent paper. `0,0` represents the top-left
    coordinate. The first value, `x`, increases to the right. The second value, `y`, increases
    downward. So, the coordinate `3,0` is to the right of `0,0`, and the coordinate `0,7` is below
    `0,0`. The coordinates in this example form the following pattern, where `█` is a dot on
    the paper and `·` is an empty, unmarked position:

        >>> draw(example_dots)
        ···█··█··█·
        ····█······
        ···········
        █··········
        ···█····█·█
        ···········
        ···········
        ···········
        ···········
        ···········
        ·█····█·██·
        ····█······
        ······█···█
        █··········
        █·█········

    Then, there is a list of **fold instructions**. Each instruction indicates a line on the trans-
    parent paper and wants you to fold the paper **up** (for horizontal `y=...` lines) or **left**
    (for vertical `x=...` lines). In this example, the first fold instruction is:

        >>> print(instr1 := example_instructions[0])
        fold along y=7

    Which designates the line formed by all of the positions where `y` is `7`, marked here with `-`:

        >>> draw(example_dots, instruction=instr1)
        ···█··█··█·
        ····█······
        ···········
        █··········
        ···█····█·█
        ···········
        ···········
        -----------
        ···········
        ···········
        ·█····█·██·
        ····█······
        ······█···█
        █··········
        █·█········

    Because this is a horizontal line, fold the bottom half **up**. Some of the dots might end up
    overlapping after the fold is complete, but dots will never appear exactly on a fold line.
    The result of doing this fold looks like this:

        >>> dots1 = fold(example_dots, instr1)
        >>> draw(dots1)
        █·██··█··█·
        █···█······
        ······█···█
        █···█······
        ·█·█··█·███

    Now, only 17 dots are visible.

        >>> len(dots1)
        17

    Notice, for example, the two dots in the bottom left corner before the transparent paper is
    folded; after the fold is complete, those dots appear in the top left corner (at `0,0` and
    `0,1`). Because the paper is transparent, the dot just below them in the result (at `0,3`)
    remains visible, as it can be seen through the transparent paper.

    Also notice that some dots can end up **overlapping**; in this case, the dots merge together and
    become a single dot.

    The second fold instruction is:

        >>> print(instr2 := example_instructions[1])
        fold along x=5

    Which indicates this line:

        >>> draw(dots1, instr2)
        █·██·|█··█·
        █···█|·····
        ·····|█···█
        █···█|·····
        ·█·█·|█·███

    Because this is a vertical line, fold **left**:

        >>> dots2 = fold(dots1, instr2)
        >>> draw(dots2)
        █████
        █···█
        █···█
        █···█
        █████

    The instructions made a square!

    The transparent paper is pretty big, so for now, focus on just completing the first fold.
    After the first fold in the example above, **`17`** dots are visible - dots that end up overlap-
    ping after the fold is completed count as a single dot.

    **How many dots are visible after completing just the first fold instruction on your transparent
    paper?**

        >>> part_1(example_dots, example_instructions[0])
        part 1: after first folding, there are 17 dots visible
        17
    """

    result = len(fold(dots, first_instruction))

    print(f"part 1: after first folding, there are {result} dots visible")
    return result


def part_2(dots: set['Pos'], instructions: Iterable['Instruction']) -> None:
    """
    Finish folding the transparent paper according to the instructions. The manual says the code is
    always eight capital letters.

    **What code do you use to activate the infrared thermal imaging camera system?**

        >>> example_dots, example_instructions = input_from_file('data/13-example.txt')
        >>> part_2(example_dots, example_instructions)
        part 2:
        █████
        █   █
        █   █
        █   █
        █████
    """

    print('part 2:')
    draw(fold(dots, *instructions), empty_char=' ')


Pos = tuple[int, int]


class Instruction:
    def __init__(self, x: int = None, y: int = None):
        assert (x is None) != (y is None)
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        arg_repr = f'x={self.x!r}' if self.x is not None else f'y={self.y!r}'
        return f'{type(self).__name__}({arg_repr})'

    def __str__(self) -> str:
        return 'fold along ' + (f'x={self.x}' if self.x is not None else f'y={self.y}')

    @classmethod
    def parse_line(cls, line: str) -> 'Instruction':
        # fold along x=655
        axis, value = parse_line(line, 'fold along $=$')
        return cls(**{axis: int(value)})

    def is_vertical(self) -> bool:
        return self.x is not None

    def is_horizontal(self) -> bool:
        return self.y is not None

    def translated_x(self, x: int) -> int:
        return self.x - abs(x - self.x) if self.x is not None else x

    def translated_y(self, y: int) -> int:
        return self.y - abs(y - self.y) if self.y is not None else y

    def translated(self, pos: Pos) -> Pos:
        x, y = pos
        return self.translated_x(x), self.translated_y(y)

    def is_on_fold(self, pos: Pos) -> bool:
        x, y = pos
        return (self.x == x) if self.x is not None else (self.y == y)


def draw(dots: set[Pos], instruction: Instruction = None, full_char='█', empty_char='·') -> None:
    def char(pos: Pos) -> str:
        if pos in dots:
            return full_char
        elif instruction and instruction.is_on_fold(pos):
            return '|' if instruction.is_vertical() else '-'
        else:
            return empty_char

    bounds = Rect.with_all(dots)
    for y in bounds.range_y():
        print(''.join(char((x, y)) for x in bounds.range_x()))


def fold(dots: set[Pos], *instructions: Instruction) -> set[Pos]:
    for instr in instructions:
        dots = {instr.translated(dot) for dot in dots}
    return dots


Input = tuple[set[Pos], list[Instruction]]


def input_from_text(text: str) -> Input:
    return input_from_lines(text.split('\n'))


def input_from_file(fn: str) -> Input:
    return input_from_lines(open(relative_path(__file__, fn)))


def input_from_lines(lines: Iterable[str]) -> Input:
    def parse_pos(line_: str) -> Pos:
        x, y = line_.strip().split(',')
        return int(x), int(y)

    dots, instructions = set(), []

    for line in lines:
        line = line.strip()
        if line and line[0].isdigit():
            dots.add(parse_pos(line))
        elif line.startswith('fold along'):
            instructions.append(Instruction.parse_line(line))

    assert len(dots) > 0
    assert len(instructions) > 0

    return dots, instructions


if __name__ == '__main__':
    dots_, instructions_ = input_from_file('data/13-input.txt')
    part_1(dots_, instructions_[0])
    part_2(dots_, instructions_)
