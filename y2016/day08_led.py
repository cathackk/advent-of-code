"""
Advent of Code 2016
Day 8: Two-Factor Authentication
https://adventofcode.com/2016/day/8
"""

from typing import Iterable

from common import ocr
from common.file import relative_path
from common.rect import Rect
from common.text import parse_line


def part_1(commands: list[str]) -> int:
    """
    You come across a door implementing what you can only assume is an implementation of two-factor
    authentication after a long game of requirements telephone.

    To get past the door, you first swipe a keycard (no problem; there was one on a nearby desk).
    Then, it displays a code on a little screen, and you type that code on a keypad. Then,
    presumably, the door unlocks.

    Unfortunately, the screen has been smashed. After a few minutes, you've taken everything apart
    and figured out how it works. Now you just have to work out what the screen **would** have
    displayed.

    The magnetic strip on the card you swiped encodes a series of instructions for the screen; these
    instructions are your puzzle input. The screen is **`50` pixels wide and `6` pixels tall**, all
    of which start **off**:

        >>> scr = Screen()
        >>> scr.width, scr.height, scr.pixels_on_count
        (50, 6, 0)
        >>> print(scr)
        ··················································
        ··················································
        ··················································
        ··················································
        ··················································
        ··················································

    It is capable of three somewhat peculiar operations:

      - `rect AxB` turns **on** all of the pixels in a rectangle at the top-left of the screen which
        is `A` wide and `B` tall:

        >>> scr.command('rect 20x3')
        >>> print(scr)
        ####################······························
        ####################······························
        ####################······························
        ··················································
        ··················································
        ··················································

      - `rotate row y=A by B` shifts all of the pixels in row `A` (`0` is the top row) **right**
        by `B` pixels. Pixels that would fall off the right end appear at the left end of the row:

        >>> scr.commands('rotate row y=1 by 25', 'rotate row y=2 by 35')
        >>> print(scr)
        ####################······························
        ·························####################·····
        #####······························###############
        ··················································
        ··················································
        ··················································

      - `rotate column x=A by B` shifts all of the pixels in column `A` (`0` is the left column)
        **down** by `B` pixels. Pixels that would fall off the bottom appear at the top of
        the column:

        >>> scr.commands(
        ...     'rotate column x=36 by 1', 'rotate column x=37 by 2', 'rotate column x=38 by 3',
        ...     'rotate column x=39 by 4', 'rotate column x=40 by 5', 'rotate column x=41 by 6'
        ... )
        >>> print(scr)
        ####################···················##·········
        ·························###########····#####·····
        #####······························##····#########
        ····································##············
        ·····································##···········
        ······································##··········

    Here is a simple sequence on a smaller screen:

        >>> scr_small = Screen(7, 3)
        >>> scr_small.command('rect 3x2')
        >>> print(scr_small)
        ###····
        ###····
        ·······
        >>> scr_small.command('rotate column x=1 by 1')
        >>> print(scr_small)
        #·#····
        ###····
        ·#·····
        >>> scr_small.command('rotate row y=0 by 4')
        >>> print(scr_small)
        ····#·#
        ###····
        ·#·····
        >>> scr_small.command('rotate column x=1 by 1')
        >>> print(scr_small)
        ·#··#·#
        #·#····
        ·#·····

    As you can see, this display technology is extremely powerful, and will soon dominate the tiny-
    -code-displaying-screen market. That's what the advertisement on the back of the display tries
    to convince you, anyway.

    There seems to be an intermediate check of the voltage used by the display: after you swipe your
    card, if the screen did work, **how many pixels should be lit**?

        >>> part_1(['rect 3x2', 'rotate row y=0 by 1', 'rect 2x1'])
        part 1: 7 pixels are on
        7
    """

    screen = Screen()
    screen.commands(*commands)
    result = screen.pixels_on_count

    print(f"part 1: {result} pixels are on")
    return result


def part_2(commands: list[str]) -> str:
    """
    You notice that the screen is only capable of displaying capital letters; in the font it uses,
    each letter is 5 pixels wide and 6 tall.

    After you swipe your card, **what code is the screen trying to display?**

        >>> part_2(commands_from_file('data/08-example-large.txt'))
        part 2: the screen shows 'UPOJFLBCEZ'
        █  █ ███   ██    ██ ████ █    ███   ██  ████ ████
        █  █ █  █ █  █    █ █    █    █  █ █  █ █       █
        █  █ █  █ █  █    █ ███  █    ███  █    ███    █
        █  █ ███  █  █    █ █    █    █  █ █    █     █
        █  █ █    █  █ █  █ █    █    █  █ █  █ █    █
         ██  █     ██   ██  █    ████ ███   ██  ████ ████
        'UPOJFLBCEZ'
    """

    screen = Screen()
    screen.commands(*commands)
    result = ocr.FONT_6X5.read_string(str(screen))

    print(f"part 2: the screen shows {result!r}")
    print(format(screen, " █"))
    return result


Pos = tuple[int, int]


class Screen:
    def __init__(self, width: int = 50, height: int = 6, pixels_on: Iterable[Pos] = None):
        self.bounds = Rect.at_origin(width, height)
        self.pixels_on: set[Pos] = set(pixels_on) if pixels_on else set()

    def __repr__(self) -> str:
        tn = type(self).__name__
        return f'{tn}(width={self.width!r}, height={self.height!r}, pixels_on={self.pixels_on!r})'

    def __str__(self) -> str:
        return format(self)

    def __format__(self, format_spec: str) -> str:
        char_off, char_on = tuple(format_spec) or ("·", "#")

        def char(pos: Pos) -> str:
            return char_on if pos in self.pixels_on else char_off

        return "\n".join(
            "".join(char((x, y)) for x in self.bounds.range_x()).rstrip()
            for y in self.bounds.range_y()
        )

    @property
    def width(self) -> int:
        return self.bounds.width

    @property
    def height(self) -> int:
        return self.bounds.height

    @property
    def pixels_on_count(self) -> int:
        return len(self.pixels_on)

    def commands(self, *cmds: str) -> None:
        for cmd in cmds:
            self.command(cmd)

    def command(self, cmd: str) -> None:
        # rect 2x1
        if cmd.startswith("rect "):
            rect_width, rect_height = parse_line(cmd, "rect $x$")
            self.rect(int(rect_width), int(rect_height))

        # rotate row y=0 by 3
        elif cmd.startswith("rotate row"):
            row_y, right = parse_line(cmd, "rotate row y=$ by $")
            self.rotate_row(int(row_y), int(right))

        # rotate column x=8 by 2
        elif cmd.startswith("rotate column"):
            column_x, down = parse_line(cmd, "rotate column x=$ by $")
            self.rotate_column(int(column_x), int(down))

        else:
            raise ValueError(cmd)

    def rect(self, rect_width: int, rect_height: int):
        self.pixels_on.update(
            (x, y)
            for x in range(rect_width)
            for y in range(rect_height)
        )

    def rotate_row(self, row_y: int, right: int):
        self.pixels_on = {
            ((pixel_x + right) % self.width, pixel_y) if pixel_y == row_y else (pixel_x, pixel_y)
            for pixel_x, pixel_y in self.pixels_on
        }

    def rotate_column(self, column_x: int, down: int):
        self.pixels_on = {
            (pixel_x, (pixel_y + down) % self.height) if pixel_x == column_x else (pixel_x, pixel_y)
            for pixel_x, pixel_y in self.pixels_on
        }


def commands_from_file(fn: str) -> list[str]:
    return [line.strip() for line in open(relative_path(__file__, fn))]


if __name__ == '__main__':
    commands_ = commands_from_file('data/08-input.txt')
    part_1(commands_)
    part_2(commands_)
