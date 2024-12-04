"""
Advent of Code 2022
Day 10: Cathode-Ray Tube
https://adventofcode.com/2022/day/10
"""

from typing import Iterable, Iterator

from common.ocr import FONT_6X5
from meta.aoc_tools import data_path


def part_1(program: 'Program') -> int:
    """
    You avoid the ropes, plunge into the river, and swim to shore.

    The Elves yell something about meeting back up with them upriver, but the river is too loud to
    tell exactly what they're saying. They finish crossing the bridge and disappear from view.

    Situations like this must be why the Elves prioritized getting the communication system on your
    handheld device working. You pull it out of your pack, but the amount of water slowly draining
    from a big crack in its screen tells you it probably won't be of much immediate use.

    **Unless**, that is, you can design a replacement for the device's video system! It seems to be
    some kind of cathode-ray tube screen and simple CPU that are both driven by a precise **clock
    circuit**. The clock circuit ticks at a constant rate; each tick is called a **cycle**.

    Start by figuring out the signal being sent by the CPU. The CPU has a single register, **`X`**,
    which starts with the value `1`. It supports only two instructions:

      - `addx V` takes **two cycles** to complete. **After** two cycles, the `X` register is
        increased by the value `V`. (`V` can be negative.)
      - `noop` takes **one cycle** to complete. It has no other effect.

    The CPU uses these instructions in a program (your puzzle input) to, somehow, tell the screen
    what to draw.

    Consider the following small program:

        >>> p = program_from_text('''
        ...     noop
        ...     addx 3
        ...     addx -5
        ... ''')
        >>> p
        [('noop', None), ('addx', 3), ('addx', -5)]

    Execution of this program proceeds as follows:

        >>> e = enumerate(execute(p), start=1)

      - At the start of the first cycle, the `noop` instruction begins execution. During the first
        cycle, `X` is `1`. After the first cycle, the `noop` instruction finishes execution, doing
        nothing.

        >>> next(e)
        (1, 1)

      - At the start of the second cycle, the `addx 3` instruction begins execution. During the
        second cycle, `X` is still `1`.

        >>> next(e)
        (2, 1)

      - During the third cycle, `X` is still `1`. After the third cycle, the `addx 3` instruction
        finishes execution, setting `X` to `4`.

        >>> next(e)
        (3, 1)

      - At the start of the fourth cycle, the `addx -5` instruction begins execution. During the
        fourth cycle, `X` is still `4`.

        >>> next(e)
        (4, 4)

      - During the fifth cycle, `X` is still `4`. After the fifth cycle, the `addx -5` instruction
        finishes execution, setting `X` to `-1`.

        >>> next(e)
        (5, 4)
        >>> next(e)
        (6, -1)
        >>> next(e)
        Traceback (most recent call last):
        ...
        StopIteration

    Maybe you can learn something by looking at the value of the `X` register throughout execution.
    For now, consider the **signal strength** (the cycle number multiplied by the value of the `X`
    register) **during** the 20th cycle and every 40 cycles after that (that is, during the 20th,
    60th, 100th, 140th, 180th, and 220th cycles).

    For example, consider this larger program:

        >>> p2 = program_from_file(data_path(__file__, 'example.txt'))
        >>> len(p2)
        146
        >>> p2[:5]
        [('addx', 15), ('addx', -11), ('addx', 6), ('addx', -3), ('addx', 5)]
        >>> p2[-5:]
        [('addx', -6), ('addx', -11), ('noop', None), ('noop', None), ('noop', None)]

    The interesting signal strengths can be determined as follows:

        >>> s2 = screen_center_signal_strengths(execute(p2))

      - During the 20th cycle, reg `X` has value `21`, so the signal strength is `20 * 21 = 420`.
        (The 20th cycle occurs in the middle of the second `addx -1`, so the value of register `X`
        is the starting value, `1`, plus all of the other addx values up to that point:
        `1 + 15 - 11 + 6 - 3 + 5 - 1 - 8 + 13 + 4 = 21`.)

        >>> next(s2)
        420

      - During the 60th cycle, reg `X` has value `19`, so the signal strength is `60 * 19 = 1140`.

        >>> next(s2)
        1140

      - During the 100th cycle, reg `X` has value `18`, so the signal strength is `100 * 18 = 1800`.

        >>> next(s2)
        1800

      - During the 140th cycle, reg `X` has value `21`, so the signal strength is `140 * 21 = 2940`.

        >>> next(s2)
        2940

      - During the 180th cycle, reg `X` has value `16`, so the signal strength is `180 * 16 = 2880`.

        >>> next(s2)
        2880

      - During the 220th cycle, reg `X` has value `18`, so the signal strength is `220 * 18 = 3960`.

        >>> next(s2)
        3960
        >>> next(s2)
        Traceback (most recent call last):
        ...
        StopIteration

    The sum of these signal strengths is **`13140`**.

        >>> sum(screen_center_signal_strengths(execute(p2)))
        13140

    Find the signal strength during the 20th, 60th, 100th, 140th, 180th, and 220th cycles.
    **What is the sum of these six signal strengths?**

        >>> part_1(p2)
        part 1: sum of signal strengths is 13140
        13140
    """

    result = sum(screen_center_signal_strengths(execute(program)))

    print(f"part 1: sum of signal strengths is {result}")
    return result


def part_2(program: 'Program') -> str:
    """
    It seems like the `X` register controls the horizontal position of a sprite. Specifically, the
    sprite is 3 pixels wide, and the X register sets the horizontal position of the **middle** of
    that sprite. (In this system, there is no such thing as "vertical position": if the sprite's
    horizontal position puts its pixels where the CRT is currently drawing, then those pixels will
    be drawn.)

    You count the pixels on the CRT: 40 wide and 6 high. This CRT screen draws the top row of pixels
    left-to-right, then the row below that, and so on. The left-most pixel in each row is in
    position `0`, and the right-most pixel in each row is in position `39`.

    Like the CPU, the CRT is tied closely to the clock circuit: the CRT draws **a single pixel
    during each cycle**. Representing each pixel of the screen as a `·`, here are the cycles during
    which the first and last pixel in each row (`#`) are drawn:

        Cycle   1 -> #······································# <- Cycle  40
        Cycle  41 -> #······································# <- Cycle  80
        Cycle  81 -> #······································# <- Cycle 120
        Cycle 121 -> #······································# <- Cycle 160
        Cycle 161 -> #······································# <- Cycle 200
        Cycle 201 -> #······································# <- Cycle 240

    So, by carefully timing the CPU instructions and the CRT drawing operations, you should be able
    to determine whether the sprite is visible the instant each pixel is drawn. If the sprite is
    positioned such that one of its three pixels is the pixel currently being drawn, the screen
    produces a **lit** pixel (`#`); otherwise, the screen leaves the pixel **dark** (`·`).

    The first few pixels from the larger example above are drawn as follows:

        >>> p = program_from_file(data_path(__file__, 'example.txt'))
        >>> print(crt_draw(pixels(execute(p))))
        ##··##··##··##··##··##··##··##··##··##··
        ###···###···###···###···###···###···###·
        ####····####····####····####····####····
        #####·····#####·····#####·····#####·····
        ######······######······######······####
        #######·······#######·······#######·····

    Render the image given by your program. **What eight capital letters appear on your CRT?**
    """

    drawing = crt_draw(pixels(execute(program)))
    result = FONT_6X5.read_string(drawing)

    print(f"part 2: CRT displays {result}")
    return result


Instruction = tuple[str, int | None]
Program = list[Instruction]


def execute(program: Program, initial_x: int = 1) -> Iterator[int]:
    x = initial_x

    for instruction in program:
        match instruction:
            case ('noop', None):
                yield x
            case ('addx', value):
                yield x
                yield x
                x += value

    yield x


SPRITE_SIZE = 3
SCREEN_COLS = 40
SCREEN_ROWS = 6


def screen_center_signal_strengths(values: Iterable[int]) -> Iterator[int]:
    return (
        cycle * value
        for cycle, value in enumerate(values, start=1)
        if cycle % SCREEN_COLS == SCREEN_COLS // 2
    )


def pixels(values: Iterable[int]) -> Iterator[bool]:
    assert SPRITE_SIZE % 2 == 1
    delta = SPRITE_SIZE // 2

    return (
        abs(cycle % SCREEN_COLS - value) <= delta
        for cycle, value in enumerate(values)
    )


def crt_draw(pixels_: Iterator[bool], lit: str = '#', dark: str = '·') -> str:
    return '\n'.join(
        ''.join(lit if next(pixels_) else dark for _ in range(SCREEN_COLS))
        for _ in range(SCREEN_ROWS)
    )


def program_from_file(fn: str) -> Program:
    return list(program_from_lines(open(fn)))


def program_from_text(text: str) -> Program:
    return list(program_from_lines(text.strip().splitlines()))


def program_from_lines(lines: Iterable[str]) -> Iterable[Instruction]:
    for line in lines:
        line = line.strip()
        if line == 'noop':
            yield ('noop', None)
        else:
            op, value = line.split()
            yield op, int(value)


def main(input_path: str = data_path(__file__)) -> tuple[int, str]:
    program = program_from_file(input_path)
    result_1 = part_1(program)
    result_2 = part_2(program)
    return result_1, result_2


if __name__ == '__main__':
    main()
