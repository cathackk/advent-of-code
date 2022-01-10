"""
Advent of Code 2015
Day 6: Probably a Fire Hazard
https://adventofcode.com/2015/day/6
"""

from typing import Iterable

from common.rect import Pos
from common.rect import Rect
from common.utils import parse_line
from common.utils import relative_path


def part_1(instructions: Iterable['Instruction']) -> int:
    """
    Because your neighbors keep defeating you in the holiday house decorating contest year after
    year, you've decided to deploy one million lights in a 1000x1000 grid.

    Furthermore, because you've been especially nice this year, Santa has mailed you instructions on
    how to display the ideal lighting configuration.

    Lights in your grid are numbered from 0 to 999 in each direction; the lights at each corner are
    at `0,0`, `0,999`, `999,999`, and `999,0`. The instructions include whether to `turn on`,
    `turn off`, or `toggle` various inclusive ranges given as coordinate pairs. Each coordinate pair
    represents opposite corners of a rectangle, inclusive; a coordinate pair like `0,0 through 2,2`
    therefore refers to 9 lights in a 3x3 square. The lights all start turned off.

    To defeat your neighbors this year, all you have to do is set up your lights by doing the
    instructions Santa sent you in order.

    For example:

      - `turn on 0,0 through 999,999` would turn on (or leave on) every light.

        >>> Instruction.from_str('turn on 0,0 through 999,999')
        Instruction('turn on', Rect((0, 0), (999, 999)))

      - `toggle 0,0 through 999,0` would toggle the first line of 1000 lights, turning off the ones
        that were on, and turning on the ones that were off.

        >>> Instruction.from_str('toggle 0,0 through 999,0')
        Instruction('toggle', Rect((0, 0), (999, 0)))

      - `turn off 499,499 through 500,500` would turn off (or leave off) the middle four lights.

        >>> (instr1 := Instruction.from_str('turn off 499,499 through 500,500'))
        Instruction('turn off', Rect((499, 499), (500, 500)))
        >>> instr1.rect.area
        4

    After following the instructions, **how many lights are lit**?

        >>> example = instructions_from_text('''
        ...     turn on 3,3 through 6,7
        ...     turn off 4,5 through 5,6
        ...     toggle 2,2 through 7,8
        ... ''')
        >>> len(example)
        3
        >>> part_1(example)
        part 1: 26 lights are lit
        26
    """

    panel = Panel()
    panel.update(instructions)
    result = panel.lit_count

    print(f"part 1: {result} lights are lit")
    return result


def part_2(instructions: Iterable['Instruction']) -> int:
    """
    You just finish implementing your winning light pattern when you realize you mistranslated
    Santa's message from Ancient Nordic Elvish.

    The light grid you bought actually has individual brightness controls; each light can have
    a brightness of zero or more. The lights all start at zero.

      - The phrase `turn on` actually means that you should increase the brightness of those lights
        by `1`.
      - The phrase `turn off` actually means that you should decrease the brightness of those lights
        by `1`, to a minimum of zero.
      - The phrase `toggle` actually means that you should increase the brightness of those lights
        by `2`.

    What is the **total brightness** of all lights combined after following Santa's instructions?

    For example:

      - `turn on 0,0 through 0,0` would increase the total brightness by `1`.
      - `toggle 0,0 through 999,999` would increase the total brightness by `2000000`.

        >>> example = instructions_from_text('''
        ...     turn on 3,3 through 6,7
        ...     turn off 4,5 through 5,6
        ...     turn off 5,6 through 6,7
        ...     toggle 2,2 through 7,8
        ... ''')
        >>> part_2(example)
        part 2: total brightness is 97
        97
    """

    panel = Panel()
    panel.update(instructions, mode=2)
    result = panel.total_brightness
    print(f"part 2: total brightness is {result}")
    return result


class Instruction:
    def __init__(self, phrase: str, rect: Rect):
        self.phrase = phrase
        self.rect = rect

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.phrase!r}, {self.rect!r})'

    def __str__(self) -> str:
        x1, y1 = self.rect.top_left
        x2, y2 = self.rect.bottom_right
        return f"{self.phrase} {x1},{y1} through {x2},{y2}"

    @classmethod
    def from_str(cls, line: str) -> 'Instruction':
        phrases = ('turn on', 'turn off', 'toggle')
        phrase = next(p for p in phrases if line.startswith(p + ' '))
        rect_str = line[len(phrase):]
        x1, y1, x2, y2 = parse_line(rect_str, '$,$ through $,$')
        return cls(phrase, Rect((int(x1), int(y1)), (int(x2), int(y2))))


class Panel:
    def __init__(self, lights: Iterable[tuple[Pos, int]] = ()):
        self.lights = dict(lights)

    def __getitem__(self, pos: Pos) -> int:
        return self.lights.get(pos, 0)

    def __setitem__(self, pos: Pos, value: int) -> None:
        self.lights[pos] = value

    @property
    def lit_count(self) -> int:
        return sum(1 for brightness in self.lights.values() if brightness > 0)

    @property
    def total_brightness(self) -> int:
        return sum(self.lights.values())

    def update(self, instructions: Iterable[Instruction], mode: int = 1) -> None:
        for instr in instructions:
            self.process(instr, mode=mode)

    def process(self, instr: Instruction, mode: int = 1) -> None:
        assert mode in (1, 2)

        match instr.phrase:
            case 'turn on':
                if mode == 1:
                    self.set_brightness(1, instr.rect)
                else:
                    self.add_brightness(+1, instr.rect)
            case 'turn off':
                if mode == 1:
                    self.set_brightness(0, instr.rect)
                else:
                    self.add_brightness(-1, instr.rect)
            case 'toggle':
                if mode == 1:
                    self.toggle_brightness(instr.rect)
                else:
                    self.add_brightness(+2, instr.rect)
            case _:
                raise ValueError(instr.phrase)

    def set_brightness(self, value: int, rect: Rect) -> None:
        for x, y in rect:
            self[x, y] = value

    def add_brightness(self, value: int, rect: Rect) -> None:
        for x, y in rect:
            self[x, y] = max(self[x, y] + value, 0)

    def toggle_brightness(self, rect: Rect) -> None:
        for x, y in rect:
            self[x, y] = 1 if self[x, y] == 0 else 0


def instructions_from_text(text: str) -> list[Instruction]:
    return list(instructions_from_lines(text.strip().split('\n')))


def instructions_from_file(fn: str) -> list[Instruction]:
    return list(instructions_from_lines(open(relative_path(__file__, fn))))


def instructions_from_lines(lines: Iterable[str]) -> Iterable[Instruction]:
    return (Instruction.from_str(line.strip()) for line in lines)


if __name__ == '__main__':
    instructions_ = instructions_from_file('data/06-input.txt')
    part_1(instructions_)
    part_2(instructions_)
