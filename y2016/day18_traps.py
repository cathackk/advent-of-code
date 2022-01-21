"""
Advent of Code 2016
Day 18: Like a Rogue
https://adventofcode.com/2016/day/18
"""

from common.file import relative_path


def part_1(first_row: str, height: int = 40) -> int:
    """
    As you enter this room, you hear a loud click! Some of the tiles in the floor here seem to be
    pressure plates for traps, and the trap you just triggered has run out of... whatever it tried
    to do to you. You doubt you'll be so lucky next time.

    Upon closer examination, the traps and safe tiles in this room seem to follow a pattern.
    The tiles are arranged into rows that are all the same width; you take note of the safe tiles
    (`.`) and traps (`^`) in the first row (your puzzle input).

    The type of tile (trapped or safe) in each row is based on the types of the tiles in the same
    position, and to either side of that position, in the previous row. (If either side is off
    either end of the row, it counts as "safe" because there isn't a trap embedded in the wall.)

    For example, suppose you know the first row (with tiles marked by letters) and want to determine
    the next row (with tiles marked by numbers):

        ABCDE
        12345

    The type of tile 2 is based on the types of tiles `A`, `B`, and `C`; the type of tile `5` is
    based on tiles `D`, `E`, and an imaginary "safe" tile. Let's call these three tiles from
    the previous row the **left**, **center**, and **right** tiles, respectively. Then, a new tile
    is a trap only in one of the following situations:

      - Its **left** and **center** tiles are traps, but its **right** tile is not.
      - Its **center** and **right** tiles are traps, but its **left** tile is not.
      - Only its **left** tile is a trap.
      - Only its **right** tile is a trap.

    In any other situation, the new tile is safe.

    Then, starting with the row `..^^.`, you can determine the next row by applying those rules to
    each new tile:

      - The leftmost character on the next row considers the left (nonexistent, so we assume
        "safe"), center (the first `.`, which means "safe"), and right (the second `.`, also "safe")
        tiles on the previous row. Because all of the trap rules require a trap in at least one of
        the previous three tiles, the first tile on this new row is also safe, `.`.
      - The second character on the next row considers its left (`.`), center (`.`), and right (`^`)
        tiles from the previous row. This matches the fourth rule: only the right tile is a trap.
        Therefore, the next tile in this new row is a trap, `^`.
      - The third character considers `.^^`, which matches the second trap rule: its center and
        right tiles are traps, but its left tile is not. Therefore, this tile is also a trap, `^`.
      - The last two characters in this new row match the first and third rules, respectively, and
        so they are both also traps, `^`.

    After these steps, we now know the next row of tiles in the room:

        >>> (row_1 := next_row('..^^.'))
        '.^^^^'

    Then, we continue on to the next row, using the same rules, and get:

        >>> next_row(row_1)
        '^^..^'

    After determining two new rows, our map looks like this:

        >>> draw_map('..^^.', height=3)
        ··^^·
        ·^^^^
        ^^··^

    Here's a larger example with ten tiles per row and ten rows:

        >>> draw_map('.^^.^.^^^^', height=10)
        ·^^·^·^^^^
        ^^^···^··^
        ^·^^·^·^^·
        ··^^···^^^
        ·^^^^·^^·^
        ^^··^·^^··
        ^^^^··^^^·
        ^··^^^^·^^
        ·^^^··^·^^
        ^^·^^^··^^

    In ten rows, this larger example has `38` safe tiles.

    Starting with the map in your puzzle input, in a total of `40` rows (including the starting
    row), **how many safe tiles** are there?

        >>> part_1('.^^.^.^^^^')
        part 1: 185 safe tiles in 40 rows
        185
    """

    safe_tiles = safe_tiles_count(first_row, height)
    print(f"part 1: {safe_tiles} safe tiles in {height} rows")
    return safe_tiles


def part_2(first_row: str, height: int = 400_000) -> int:
    """
    How many safe tiles are there in a total of 400000 rows?

        >>> part_2('.^^.^.^^^^')
        part 2: 1935478 safe tiles in 400000 rows
        1935478
    """

    safe_tiles = safe_tiles_count(first_row, height)
    print(f"part 2: {safe_tiles} safe tiles in {height} rows")
    return safe_tiles


def next_row(row: str) -> str:
    """
        ^^.  -> ^
        .^^  -> ^
        ^..  -> ^
        ..^  -> ^
        else -> .
    =>
        ^?.  -> ^
        .?^  -> ^
        else -> .
    """
    row_padded = '.'+row+'.'
    return ''.join(
        '^' if (row_padded[k] != row_padded[k + 2]) else '.'
        for k in range(len(row))
    )


def safe_tiles_count(first_row: str, height: int) -> int:
    safe_tiles = 0
    row = first_row
    for _ in range(height):
        safe_tiles += sum(1 for c in row if c != '^')
        row = next_row(row)
    return safe_tiles


def draw_map(first_row: str, height: int, safe_char='·', trap_char='^') -> None:
    row = first_row
    for _ in range(height):
        print(row.replace('.', safe_char).replace('^', trap_char))
        row = next_row(row)


def first_row_from_file(fn: str) -> str:
    return open(relative_path(__file__, fn)).readline().strip()


if __name__ == '__main__':
    first_row_ = first_row_from_file('data/18-input.txt')
    part_1(first_row_)
    part_2(first_row_)
