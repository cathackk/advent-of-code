"""
Advent of Code 2024
Day 4: Ceres Search
https://adventofcode.com/2024/day/4
"""

from typing import Iterable, Self

from common.file import relative_path
from common.rect import Rect


def part_1(grid: 'Grid', word: str = 'XMAS') -> int:
    """
    "Looks like the Chief's not here. Next!" One of The Historians pulls out a device and pushes
    the only button on it. After a brief flash, you recognize the interior of the Ceres monitoring
    station (y2019/day10_asteroids.py)!

    As the search for the Chief continues, a small Elf who lives on the station tugs on your shirt;
    she'd like to know if you could help her with her **word search** (your puzzle input). She only
    has to find one word: `XMAS`.

    This word search allows words to be horizontal, vertical, diagonal, written backwards, or even
    overlapping other words. It's a little unusual, though, as you don't merely need to find one
    instance of `XMAS` - you need to find **all of them**. Here are a few ways `XMAS` might appear,
    where irrelevant characters have been replaced with `·`:

        ··X···
        ·SAMX·
        ·A··A·
        XMAS·S
        ·X····

    The actual word search will be full of letters instead. For example:

        >>> example = Grid.from_text('''
        ...     MMMSXXMASM
        ...     MSAMXMSMSA
        ...     AMXSXMAAMM
        ...     MSAMASMSMX
        ...     XMASAMXAMM
        ...     XXAMMXXAMA
        ...     SMSMSASXSS
        ...     SAXAMASAAA
        ...     MAMMMXMMMM
        ...     MXMXAXMASX
        ... ''')
        >>> example.bounds.shape
        (10, 10)

    In this word search, `XMAS` occurs a total of **`18`** times:

        >>> example.count_word('XMAS')
        18

    Here's the same word search again, but where letters not involved in any `XMAS` have been
    replaced with `·`:

        >>> example.visualize_word('XMAS')
        ····XXMAS·
        ·SAMXMS···
        ···S··A···
        ··A·A·MS·X
        XMASAMX·MM
        X·····XA·A
        S·S·S·S·SS
        ·A·A·A·A·A
        ··M·M·M·MM
        ·X·X·XMASX

    Take a look at the little Elf's word search. **How many times does `XMAS` appear?**

        >>> part_1(example)
        part 1: word 'XMAS' appears 18 times
        18
    """

    result = grid.count_word(word)

    print(f"part 1: word {word!r} appears {result} times")
    return result


def part_2(grid: 'Grid', cross: str = 'MAS') -> int:
    """
    The Elf looks quizzically at you. Did you misunderstand the assignment?

    Looking for the instructions, you flip over the word search to find that this isn't actually
    an **`XMAS`** puzzle; it's an **`X-MAS`** puzzle in which you're supposed to find two `MAS` in
    the shape of an `X`. One way to achieve that is like this:

        M·S
        ·A·
        M·S

    Irrelevant characters have again been replaced with · in the above diagram. Within the `X`, each
    `MAS` can be written forwards or backwards.

    Here's the same example from before, but this time all of the `X-MAS`es have been kept instead:

        >>> example = Grid.from_file('data/04-example.txt')
        >>> example.visualize_crosses('MAS')
        ·M·S······
        ··A··MSMS·
        ·M·S·MAA··
        ··A·ASMSM·
        ·M·S·M····
        ··········
        S·S·S·S·S·
        ·A·A·A·A··
        M·M·M·M·M·
        ··········

    In this example, an `X-MAS` appears **`9`** times:

        >>> example.count_crosses('MAS')
        9

    Flip the word search from the instructions back over to the word search side and try again.
    **How many times does an `X-MAS` appear?**

        >>> part_2(example)
        part 2: the 'X-MAS' cross appears 9 times
        9
    """

    result = grid.count_crosses(cross)

    print(f"part 2: the 'X-{cross}' cross appears {result} times")
    return result


Pos = tuple[int, int]
Row = Iterable[Pos]

#               →        ↘        ↓         ↙         ←        ↖        ↑         ↗
DIRECTIONS = [(+1, 0), (+1, +1), (0, +1), (-1, +1), (-1, 0), (-1, -1), (0, -1), (+1, -1)]


class Grid:

    def __init__(self, chars: Iterable[tuple[Pos, str]]) -> None:
        self.chars = dict(chars)
        self.bounds = Rect.with_all(self.chars)

    @classmethod
    def from_file(cls, fn: str) -> Self:
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_text(cls, text: str) -> Self:
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        return cls(
            ((x, y), char)
            for y, line in enumerate(lines)
            for x, char in enumerate(line.strip())
        )

    def match_word(self, word: str, pos_0: Pos, direction: tuple[int, int]) -> list[Pos] | None:
        x_0, y_0 = pos_0
        dx, dy = direction

        pos_buffer: list[Pos] = []
        for k, word_char in enumerate(word):
            pos_k = (x_0 + dx * k, y_0 + dy * k)
            if pos_k not in self.chars or self.chars[pos_k] != word_char:
                return None
            pos_buffer.append(pos_k)

        return pos_buffer

    def find_word(self, word: str) -> Iterable[list[Pos]]:
        assert word

        for pos in self.bounds:
            if self.chars[pos] != word[0]:
                continue
            yield from (
                matched
                for direction in DIRECTIONS
                if (matched := self.match_word(word, pos, direction))
            )

    def count_word(self, word: str) -> int:
        return sum(1 for _ in self.find_word(word))

    def find_crosses(self, cross: str) -> Iterable[tuple[Pos, ...]]:
        m, a, s = cross
        return (
            ((x, y), (x-1, y-1), (x-1, y+1), (x+1, y-1), (x+1, y+1))
            for x in range(self.bounds.left_x + 1, self.bounds.right_x)
            for y in range(self.bounds.top_y + 1, self.bounds.bottom_y)
            if self.chars[(x, y)] == a
            if (self.chars[(x-1, y-1)], self.chars[(x+1, y+1)]) in ((m, s), (s, m))
            if (self.chars[(x-1, y+1)], self.chars[(x+1, y-1)]) in ((m, s), (s, m))
        )

    def count_crosses(self, cross: str) -> int:
        return sum(1 for _ in self.find_crosses(cross))

    def _visualize(self, mask: set[Pos]) -> None:
        print(
            '\n'.join(
                ''.join(
                    self.chars[(x, y)] if (x, y) in mask else '·'
                    for x in self.bounds.range_x()
                )
                for y in self.bounds.range_y()
            )
        )

    def visualize_word(self, word: str) -> None:
        self._visualize(mask={pos for found in self.find_word(word) for pos in found})

    def visualize_crosses(self, cross: str) -> None:
        self._visualize(mask={pos for found in self.find_crosses(cross) for pos in found})


def main(input_fn: str = 'data/04-input.txt') -> tuple[int, int]:
    grid = Grid.from_file(input_fn)
    result_1 = part_1(grid)
    result_2 = part_2(grid)
    return result_1, result_2


if __name__ == '__main__':
    main()
