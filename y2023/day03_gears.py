"""
Advent of Code 2023
Day 3: Gear Ratios
https://adventofcode.com/2023/day/3
"""

import math
from typing import Iterable

from common.file import relative_path

Pos = tuple[int, int]
Numbers = dict[Pos, int]
Symbols = dict[Pos, str]
Schematic = tuple[Numbers, Symbols]
Gear = tuple[int, int]


def part_1(schematic: Schematic) -> int:
    """
    You and the Elf eventually reach a gondola lift station; he says the gondola lift will take you
    up to the water source, but this is as far as he can bring you. You go inside.

    It doesn't take long to find the gondolas, but there seems to be a problem: they're not moving.

    "Aaah!"

    You turn around to see a slightly-greasy Elf with a wrench and a look of surprise. "Sorry,
    I wasn't expecting anyone! The gondola lift isn't working right now; it'll still be a while
    before I can fix it." You offer to help.

    The engineer explains that an engine part seems to be missing from the engine, but nobody can
    figure out which one. If you can **add up all the part numbers** in the engine schematic, it
    should be easy to work out which part is missing.

    The engine schematic (your puzzle input) consists of a visual representation of the engine.
    There are lots of numbers and symbols you don't really understand, but apparently **any number
    adjacent to a symbol**, even diagonally, is a "part number" and should be included in your sum.
    (Periods (`·`) do not count as a symbol.)

    Here is an example engine schematic:

        >>> numbers_, symbols_ = schematic_from_text('''
        ...     467··114··
        ...     ···*······
        ...     ··35··633·
        ...     ······#···
        ...     617*······
        ...     ·····+·58·
        ...     ··592·····
        ...     ······755·
        ...     ···$·*····
        ...     ·664·598··
        ... ''')
        >>> numbers_  # doctest: +NORMALIZE_WHITESPACE
        {(2, 0): 467, (7, 0): 114, (3, 2):  35, (8, 2): 633, (2, 4): 617,
         (8, 5):  58, (4, 6): 592, (8, 7): 755, (3, 9): 664, (7, 9): 598}
        >>> symbols_
        {(3, 1): '*', (6, 3): '#', (3, 4): '*', (5, 5): '+', (3, 8): '$', (5, 8): '*'}

    In this schematic, two numbers are **not** part numbers because they are not adjacent to
    a symbol: `114` (top right) and `58` (middle right).

        >>> [num for pos, num in numbers_.items() if not is_part_number(num, pos, symbols_)]
        [114, 58]

    Every other number is adjacent to a symbol and so **is** a part number. Their sum is **`4361`**.

        >>> sum(num for pos, num in numbers_.items() if is_part_number(num, pos, symbols_))
        4361

    Of course, the actual engine schematic is much larger.
    **What is the sum of all of the part numbers in the engine schematic?**

        >>> part_1((numbers_, symbols_))
        part 1: part numbers sum up to 4361
        4361
    """

    numbers, symbols = schematic
    result = sum(num for pos, num in numbers.items() if is_part_number(num, pos, symbols))

    print(f"part 1: part numbers sum up to {result}")
    return result


def part_2(schematic: Schematic) -> int:
    """
    The engineer finds the missing part and installs it in the engine! As the engine springs
    to life, you jump in the closest gondola, finally ready to ascend to the water source.

    You don't seem to be going very fast, though. Maybe something is still wrong? Fortunately,
    the gondola has a phone labeled "help", so you pick it up and the engineer answers.

    Before you can explain the situation, she suggests that you look out the window. There stands
    the engineer, holding a phone in one hand and waving with the other. You're going so slowly that
    you haven't even left the station. You exit the gondola.

    The missing part wasn't the only issue - one of the gears in the engine is wrong. A **gear** is
    any `*` symbol that is adjacent to **exactly two part numbers**. Its **gear ratio** is the
    result of multiplying those two numbers together.

    This time, you need to find the gear ratio of every gear and add them all up so that
    the engineer can figure out which gear needs to be replaced.

    Consider the same engine schematic again:

        >>> schematic_ = schematic_from_text('''
        ...     467··114··
        ...     ···*······
        ...     ··35··633·
        ...     ······#···
        ...     617*······
        ...     ·····+·58·
        ...     ··592·····
        ...     ······755·
        ...     ···$·*····
        ...     ·664·598··
        ... ''')

    In this schematic, there are **two** gears.

        >>> gears = list(find_gears(schematic_))
        >>> len(gears)
        2

    The first is in the top left; it has part numbers `467` and `35`, so its gear ratio is `16345`.

        >>> gears[0]
        (467, 35)
        >>> math.prod(gears[0])
        16345

    The second gear is in the lower right; its gear ratio is `451490`.

        >>> gears[1]
        (755, 598)
        >>> math.prod(gears[1])
        451490

    (The `*` adjacent to 617 is **not** a gear because it is only adjacent to one part number.)

    Adding up all of the gear ratios produces **`467835`**.

        >>> sum(math.prod(gear) for gear in gears)
        467835

    What is the sum of all of the gear ratios in your engine schematic?

        >>> part_2(schematic_)
        part 2: gear ratios sum up to 467835
        467835
    """

    result = sum(math.prod(gear) for gear in find_gears(schematic))

    print(f"part 2: gear ratios sum up to {result}")
    return result


def is_part_number(number: int, right_pos: Pos, symbols: Symbols) -> bool:
    num_x2, num_y = right_pos
    num_x1 = num_x2 - len(str(number)) + 1
    adjacent_positions = (
        (x, y)
        for y in range(num_y - 1, num_y + 2)
        for x in range(num_x1 - 1, num_x2 + 2)
        if x not in range(num_x1, num_x2 + 1) or y != num_y
    )
    return any(pos in symbols for pos in adjacent_positions)


def find_gears(schematic: Schematic) -> Iterable[Gear]:
    numbers_right, symbols = schematic
    assert all(1 <= len(str(num)) <= 3 for num in numbers_right.values())

    numbers_left = {
        (x - len(str(number)) + 1, y): number
        for (x, y), number in numbers_right.items()
    }

    def adjacent_numbers(pos_0: Pos) -> Iterable[int]:
        x_0, y_0 = pos_0
        adj_positions = (
            (x, y)
            for y in range(y_0 - 1, y_0 + 2)
            for x in range(x_0 - 1, x_0 + 2)
            if x != x_0 or y != y_0
        )

        yielded_nums: set[int] = set()

        for x, y in adj_positions:
            adj_num = numbers_left.get((x, y)) or numbers_right.get((x, y))
            if adj_num and adj_num not in yielded_nums:
                yield adj_num
                yielded_nums.add(adj_num)

    asterisk_positions = (pos for pos, symbol in symbols.items() if symbol == '*')

    for x, y in asterisk_positions:
        try:
            num_1, num_2 = tuple(adjacent_numbers((x, y)))
            yield num_1, num_2
        except ValueError:
            pass


def schematic_from_file(fn: str) -> Schematic:
    return schematic_from_lines(open(relative_path(__file__, fn)))


def schematic_from_text(text: str) -> Schematic:
    return schematic_from_lines(text.strip().splitlines())


def schematic_from_lines(lines: Iterable[str]) -> Schematic:
    numbers: dict[Pos, int] = {}
    symbols: dict[Pos, str] = {}

    for y, line in enumerate(lines):
        for x, char in enumerate(line.strip()):
            if char.isdigit():
                digit = int(char)
                prev_digit = numbers.pop((x-1, y), 0)
                numbers[(x, y)] = prev_digit * 10 + digit

            elif char not in ('.', '·'):
                symbols[(x, y)] = char

    return numbers, symbols


def main(input_fn: str = 'data/03-input.txt') -> tuple[int, int]:
    schematic = schematic_from_file(input_fn)
    result_1 = part_1(schematic)
    result_2 = part_2(schematic)
    return result_1, result_2


if __name__ == '__main__':
    main()
