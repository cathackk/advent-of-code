"""
Advent of Code 2025
Day 4: Printing Department
https://adventofcode.com/2025/day/4
"""

from collections import Counter
from typing import Iterable, Iterator

from common.canvas import Canvas
from common.file import relative_path
from common.iteration import ilen

Pos = tuple[int, int]


def part_1(rolls: set[Pos]) -> int:
    """
    You ride the escalator down to the printing department. They're clearly getting ready for
    Christmas; they have lots of large rolls of paper everywhere, and there's even a massive printer
    in the corner (to handle the really big print jobs).

    Decorating here will be easy: they can make their own decorations. What you really need is a way
    to get further into the North Pole base while the elevators are offline.

    "Actually, maybe we can help with that," one of the Elves replies when you ask for help. "We're
    pretty sure there's a cafeteria on the other side of the back wall. If we could break through
    the wall, you'd be able to keep moving. It's too bad all of our forklifts are so busy moving
    those big rolls of paper around."

    If you can optimize the work the forklifts are doing, maybe they would have time to spare to
    break through the wall.

    The rolls of paper (`@`) are arranged on a large grid; the Elves even have a helpful diagram
    (your puzzle input) indicating where everything is located.

    For example:

        >>> example = rolls_from_text('''
        ...     ..@@.@@@@.
        ...     @@@.@.@.@@
        ...     @@@@@.@.@@
        ...     @.@@@@..@.
        ...     @@.@@@@.@@
        ...     .@@@@@@@.@
        ...     .@.@.@.@@@
        ...     @.@@@.@@@@
        ...     .@@@@@@@@.
        ...     @.@.@@@.@.
        ... ''')
        >>> len(example)
        71

    The forklifts can only access a roll of paper if there are **fewer than four rolls of paper** in
    the eight adjacent positions. If you can figure out which rolls of paper the forklifts can
    access, they'll spend less time looking and more time breaking down the wall to the cafeteria.

    In this example, there are **`13`** rolls of paper that can be accessed by a forklift (marked
    with `x`):

        >>> accessible = list(accessible_rolls(example))
        >>> len(accessible)
        13
        >>> draw_rolls(example, highlighted=accessible)
        ··xx·xx@x·
        x@@·@·@·@@
        @@@@@·x·@@
        @·@@@@··@·
        x@·@@@@·@x
        ·@@@@@@@·@
        ·@·@·@·@@@
        x·@@@·@@@@
        ·@@@@@@@@·
        x·x·@@@·x·

    Consider your complete diagram of the paper roll locations.
    **How many rolls of paper can be accessed by a forklift?**

        >>> part_1(example)
        part 1: you can access 13 rolls of paper
        13
    """

    result = ilen(accessible_rolls(rolls))

    print(f"part 1: you can access {result} rolls of paper")
    return result


def part_2(rolls: set[Pos]) -> int:
    """
    Now, the Elves just need help accessing as much of the paper as they can.

    Once a roll of paper can be accessed by a forklift, it can be **removed**. Once a roll of paper
    is removed, the forklifts might be able to access **more** rolls of paper, which they might also
    be able to remove. How many total rolls of paper could the Elves remove if they keep repeating
    this process?

    Starting with the same example as above, here is one way you could remove as many rolls of paper
    as possible, using `x` to indicate that a roll of paper was just removed:

        >>> example = rolls_from_file('data/04-example.txt')
        >>> removable_count = ilen(removable_rolls(example, print_steps=True))
        Initial state:
        ··@@·@@@@·
        @@@·@·@·@@
        @@@@@·@·@@
        @·@@@@··@·
        @@·@@@@·@@
        ·@@@@@@@·@
        ·@·@·@·@@@
        @·@@@·@@@@
        ·@@@@@@@@·
        @·@·@@@·@·
        ---
        Remove 13 rolls of paper:
        ··xx·xx@x·
        x@@·@·@·@@
        @@@@@·x·@@
        @·@@@@··@·
        x@·@@@@·@x
        ·@@@@@@@·@
        ·@·@·@·@@@
        x·@@@·@@@@
        ·@@@@@@@@·
        x·x·@@@·x·
        ---
        Remove 12 rolls of paper:
        ·······x··
        ·@@·x·x·@x
        x@@@@···@@
        x·@@@@··x·
        ·@·@@@@·x·
        ·x@@@@@@·x
        ·x·@·@·@@@
        ··@@@·@@@@
        ·x@@@@@@@·
        ····@@@···
        ---
        Remove 7 rolls of paper:
        x@·····x·
        @@@@···xx
        ·@@@@····
        x·@@@@···
        ·@@@@@@··
        ··@·@·@@x
        ·@@@·@@@@
        ·x@@@@@@·
        ···@@@···
        ---
        Remove 5 rolls of paper:
        ·x·······
        x@@@·····
        ·@@@@····
        ··@@@@···
        ·x@@@@@··
        ··@·@·@@·
        ·x@@·@@@x
        ··@@@@@@·
        ···@@@···
        ---
        Remove 2 rolls of paper:
        x@@····
        @@@@···
        ·@@@@··
        ·@@@@@·
        ·@·@·@@
        ·@@·@@@
        ·@@@@@x
        ··@@@··
        ---
        Remove 1 roll of paper:
        ·@@····
        x@@@···
        ·@@@@··
        ·@@@@@·
        ·@·@·@@
        ·@@·@@@
        ·@@@@@·
        ··@@@··
        ---
        Remove 1 roll of paper:
        x@····
        @@@···
        @@@@··
        @@@@@·
        @·@·@@
        @@·@@@
        @@@@@·
        ·@@@··
        ---
        Remove 1 roll of paper:
        ·x····
        @@@···
        @@@@··
        @@@@@·
        @·@·@@
        @@·@@@
        @@@@@·
        ·@@@··
        ---
        Remove 1 roll of paper:
        x@@···
        @@@@··
        @@@@@·
        @·@·@@
        @@·@@@
        @@@@@·
        ·@@@··

    Stop once no more rolls of paper are accessible by a forklift. In this example, a total of
    **`43`** rolls of paper can be removed:

        >>> removable_count
        43

    Start with your original diagram.
    **How many rolls of paper in total can be removed by the Elves and their forklifts?**

        >>> part_2(example)
        part 2: you can remove 43 rolls of paper
        43
    """

    result = ilen(removable_rolls(rolls))

    print(f"part 2: you can remove {result} rolls of paper")
    return result


def accessible_rolls(rolls: set[Pos]) -> Iterator[Pos]:
    neighbor_count = Counter(
        (x + dx, y + dy)
        for x, y in rolls
        for dx in (-1, 0, +1)
        for dy in (-1, 0, +1)
        if dx or dy
    )

    return (
        roll
        for roll in rolls
        if neighbor_count[roll] < 4
    )


def removable_rolls(rolls: set[Pos], print_steps: bool = False) -> Iterator[Pos]:
    if print_steps:
        print("Initial state:")
        draw_rolls(rolls)

    while True:
        to_remove = list(accessible_rolls(rolls))
        if not to_remove:
            break

        if print_steps:
            print("---")
            noun = "rolls" if len(to_remove) > 1 else "roll"
            print(f"Remove {len(to_remove)} {noun} of paper:")
            draw_rolls(rolls, highlighted=to_remove)

        yield from to_remove
        rolls = rolls.difference(to_remove)


def draw_rolls(rolls: set[Pos], highlighted: Iterable[Pos] = ()) -> None:
    highlighted_set = set(highlighted)
    c = Canvas(
        (roll, 'x' if roll in highlighted_set else '@')
        for roll in rolls
    )
    c.print(empty_char='·')


def rolls_from_file(fn: str) -> set[Pos]:
    return set(rolls_from_lines(open(relative_path(__file__, fn))))


def rolls_from_text(text: str) -> set[Pos]:
    return set(rolls_from_lines(text.strip().splitlines()))


def rolls_from_lines(lines: Iterable[str]) -> Iterator[Pos]:
    return (
        (x, y)
        for y, line in enumerate(lines)
        for x, char in enumerate(line.strip())
        if char == '@'
    )


def main(input_fn: str = 'data/04-input.txt') -> tuple[int, int]:
    rolls = rolls_from_file(input_fn)
    result_1 = part_1(rolls)
    result_2 = part_2(rolls)
    return result_1, result_2


if __name__ == '__main__':
    main()
