"""
Advent of Code 2023
Day 13: Point of Incidence
https://adventofcode.com/2023/day/13
"""

from typing import Iterable, Self

from common.canvas import Canvas
from common.file import relative_path
from common.iteration import maybe_next
from common.rect import Rect
from common.text import line_groups


def part_1(patterns: Iterable['Pattern']) -> int:
    """
    With your help, the hot springs team locates an appropriate spring which launches you neatly and
    precisely up to the edge of **Lava Island**.

    There's just one problem: you don't see any **lava**.

    You **do** see a lot of ash and igneous rock; there are even what look like gray mountains
    scattered around. After a while, you make your way to a nearby cluster of mountains only to
    discover that the valley between them is completely full of large **mirrors**. Most of the
    mirrors seem to be aligned in a consistent way; perhaps you should head in that direction?

    As you move through the valley of mirrors, you find that several of them have fallen from the
    large metal frames keeping them in place. The mirrors are extremely flat and shiny, and many of
    the fallen mirrors have lodged into the ash at strange angles. Because the terrain is all one
    color, it's hard to tell where it's safe to walk or where you're about to run into a mirror.

    You note down the patterns of ash (`.`) and rocks (`#`) that you see as you walk (your puzzle
    input); perhaps by carefully analyzing these patterns, you can figure out where the mirrors are!

    For example:

        >>> p1, p2 = Pattern.from_text('''
        ...     #.##..##.
        ...     ..#.##.#.
        ...     ##......#
        ...     ##......#
        ...     ..#.##.#.
        ...     ..##..##.
        ...     #.#.##.#.
        ...
        ...     #...##..#
        ...     #....#..#
        ...     ..##..###
        ...     #####.##.
        ...     #####.##.
        ...     ..##..###
        ...     #....#..#
        ... ''')

    To find the reflection in each pattern, you need to find a perfect reflection across either
    a horizontal line between two rows or across a vertical line between two columns.

    In the first pattern, the reflection is across a vertical line between two columns; arrows on
    each of the two columns point at the line between the columns:

        >>> p1.column_reflection
        4
        >>> print(format(p1, 'reflection'))
        012345678
            ><
        #·##··##·
        ··#·##·#·
        ##······#
        ##······#
        ··#·##·#·
        ··##··##·
        #·#·##·#·
            ><
        012345678

    In this pattern, the line of reflection is the vertical line between columns 4 and 5. Because
    the vertical line is not perfectly in the middle of the pattern, part of the pattern (column 0)
    has nowhere to reflect onto and can be ignored; every other column has a reflected column within
    the pattern and must match exactly: column 1 matches column 8, column 2 matches 7, 3 matches 6,
    and 4 matches 5.

    The second pattern reflects across a horizontal line instead:

        >>> p2.row_reflection
        3
        >>> print(format(p2, 'reflection'))
        0 #···##··# 0
        1 #····#··# 1
        2 ··##··### 2
        3v#####·##·v3
        4^#####·##·^4
        5 ··##··### 5
        6 #····#··# 6

    This pattern reflects across the horizontal line between rows 3 and 4. Row 0 would reflect with
    a hypothetical row 7, but since that's not in the pattern, row 0 doesn't need to match anything.
    The remaining rows match: row 1 matches row 6, row 2 matches row 5, and row 3 matches row 4.

    To **summarize** your pattern notes, add up **the number of columns** to the left of each
    vertical line of reflection; to that, also add **100 multiplied by the number of rows** above
    each horizontal line of reflection. In the above example, the first pattern's vertical line has
    `5` columns to its left and the second pattern's horizontal line has `4` rows above it, a total
    of **`405`**:

        >>> [p.score() for p in [p1, p2]]
        [5, 400]
        >>> sum(_)
        405

    Find the line of reflection in each of the patterns in your notes.
    **What number do you get after summarizing all of your notes?**

        >>> part_1([p1, p2])
        part 1: summarizing the patterns gives 405
        405
    """

    result = sum(pattern.score() for pattern in patterns)

    print(f"part 1: summarizing the patterns gives {result}")
    return result


def part_2(patterns: Iterable['Pattern']) -> int:
    """
    You resume walking through the valley of mirrors and - **SMACK!** - run directly into one.
    Hopefully nobody was watching, because that must have been pretty embarrassing.

    Upon closer inspection, you discover that every mirror has exactly one **smudge**: exactly one
    `.` or `#` should be the opposite type.

    In each pattern, you'll need to locate and fix the smudge that causes a **different reflection
    line** to be valid. (The old reflection line won't necessarily continue being valid after the
    smudge is fixed.)

    Here's the above example again:

        >>> p1, p2 = Pattern.from_file('data/13-example.txt')
        >>> print(p1)
        #·##··##·
        ··#·##·#·
        ##······#
        ##······#
        ··#·##·#·
        ··##··##·
        #·#·##·#·

    The first pattern's smudge is in the top-left corner.

        >>> smudge_1, cleaned_p1 = locate_smudge(p1)
        >>> smudge_1
        (0, 0)

    If the top-left `#` were instead `.`, it would have a different, horizontal line of reflection:

        >>> print(format(cleaned_p1, 'reflection'))
        0 ··##··##· 0
        1 ··#·##·#· 1
        2v##······#v2
        3^##······#^3
        4 ··#·##·#· 4
        5 ··##··##· 5
        6 #·#·##·#· 6

    With the smudge in the top-left corner repaired, a new horizontal line of reflection between
    rows 2 and 3 now exists. Row 6 has no corresponding reflected row and can be ignored, but every
    other row matches exactly: row 0 matches row 5, row 1 matches row 4, and row 2 matches row 3.

    In the second pattern, the smudge can be fixed by changing the fifth symbol on row 0 from `#`
    to `.`:

        >>> smudge_2, cleaned_p2 = locate_smudge(p2)
        >>> smudge_2
        (4, 0)
        >>> print(format(cleaned_p2, 'reflection'))
        0v#····#··#v0
        1^#····#··#^1
        2 ··##··### 2
        3 #####·##· 3
        4 #####·##· 4
        5 ··##··### 5
        6 #····#··# 6

    Now, the pattern has a different horizontal line of reflection between rows 1 and 2.

    Summarize your notes as before, but instead use the new different reflection lines. In this
    example, the first pattern's new horizontal line has 3 rows above it and the second pattern's
    new horizontal line has 1 row above it, summarizing to the value **`400`**:

        >>> [p.score() for p in (cleaned_p1, cleaned_p2)]
        [300, 100]
        >>> sum(_)
        400

    In each pattern, fix the smudge and find the different line of reflection. **What number do you
    get after summarizing the new reflection line in each pattern in your notes?**

        >>> part_2([p1, p2])
        part 2: after cleaning the smudges, summarizing the patterns gives 400
        400
    """

    result = sum(locate_smudge(pattern)[1].score() for pattern in patterns)

    print(f"part 2: after cleaning the smudges, summarizing the patterns gives {result}")
    return result


Pos = tuple[int, int]


class Pattern:
    def __init__(
        self,
        rocks: Iterable[Pos],
        ignored_reflections: tuple[int | None, int | None] = (None, None),
    ):
        self.rocks = set(rocks)
        self.bounds = Rect.with_all(self.rocks)

        ignored_col_reflection, ignored_row_reflection = ignored_reflections
        self.column_reflection = self._find_column_reflection(ignored_col_reflection)
        self.row_reflection = self._find_row_reflection(ignored_row_reflection)

    def _find_column_reflection(self, ignored_x: int | None) -> int | None:
        return maybe_next(
            x
            for x in range(0, self.bounds.right_x)
            if x != ignored_x
            if all(
                ((x_l, y) in self.rocks) == ((x_r, y) in self.rocks)
                for x_l, x_r in zip(
                    range(x, -1, -1),
                    range(x + 1, self.bounds.right_x + 1),
                )
                for y in self.bounds.range_y()
            )
        )

    def _find_row_reflection(self, ignored_y: int | None) -> int | None:
        return maybe_next(
            y
            for y in range(0, self.bounds.bottom_y)
            if y != ignored_y
            if all(
                ((x, y_t) in self.rocks) == ((x, y_b) in self.rocks)
                for y_t, y_b in zip(
                    range(y, -1, -1),
                    range(y + 1, self.bounds.bottom_y + 1)
                )
                for x in self.bounds.range_x()
            )
        )

    @property
    def reflections(self) -> tuple[int | None, int | None]:
        return self.column_reflection, self.row_reflection

    def has_any_reflections(self) -> bool:
        return self.column_reflection is not None or self.row_reflection is not None

    def score(self) -> int:
        score = 0
        if self.row_reflection is not None:
            score += (self.row_reflection + 1) * 100
        if self.column_reflection is not None:
            score += (self.column_reflection + 1)
        return score

    def __str__(self) -> str:
        return format(self)

    def __format__(self, format_spec: str):
        bounds = self.bounds
        canvas = Canvas({pos: '#' if pos in self.rocks else '·' for pos in bounds})

        if format_spec == 'reflection':
            if (refl_x := self.column_reflection) is not None:
                # arrows
                bounds = bounds.grow_by(dy=1)
                canvas.draw_many(
                    ((x, y), char)
                    for x, char in ((refl_x, '>'), (refl_x + 1, '<'))
                    for y in (bounds.top_y, bounds.bottom_y)
                )
                # indices
                bounds = bounds.grow_by(dy=1)
                canvas.draw_many(
                    ((x, y), str(x)[-1])
                    for x in self.bounds.range_x()
                    for y in (bounds.top_y, bounds.bottom_y)
                )

            if (refl_y := self.row_reflection) is not None:
                # arrows
                bounds = bounds.grow_by(dx=1)
                canvas.draw_many(
                    ((x, y), char)
                    for x in (bounds.left_x, bounds.right_x)
                    for y, char in ((refl_y, 'v'), (refl_y + 1, '^'))
                )
                # indices
                bounds = bounds.grow_by(dx=1)
                canvas.draw_many(
                    ((x, y), str(y)[-1])
                    for x in (bounds.left_x, bounds.right_x)
                    for y in self.bounds.range_y()
                )

        return canvas.render(bounds=bounds)

    @classmethod
    def from_file(cls, fn: str) -> list[Self]:
        return list(cls.from_lines(open(relative_path(__file__, fn))))

    @classmethod
    def from_text(cls, text: str) -> list[Self]:
        return list(cls.from_lines(text.strip().splitlines()))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Iterable[Self]:
        return (
            cls(
                (x, y)
                for y, line in enumerate(block)
                for x, char in enumerate(line)
                if char == '#'
            )
            for block in line_groups(lines)
        )


def locate_smudge(pat: Pattern) -> tuple[Pos, Pattern]:
    def flip(pos: Pos) -> Pattern:
        return type(pat)(pat.rocks.symmetric_difference({pos}), pat.reflections)

    return next(
        (pos, new_pat)
        for pos in pat.bounds
        if (new_pat := flip(pos)).has_any_reflections()
        if new_pat.reflections != pat.reflections
    )


def main(input_fn: str = 'data/13-input.txt') -> tuple[int, int]:
    patterns = Pattern.from_file(input_fn)
    result_1 = part_1(patterns)
    result_2 = part_2(patterns)
    return result_1, result_2


if __name__ == '__main__':
    main()
