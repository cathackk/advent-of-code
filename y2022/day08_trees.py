"""
Advent of Code 2022
Day 8: Treetop Tree House
https://adventofcode.com/2022/day/8
"""
import math
from itertools import count
from typing import Iterable

from common.file import relative_path
from common.heading import Heading
from common.iteration import dgroupby_pairs
from common.iteration import maxk


def part_1(heights: list[list[int]]) -> int:
    """
    The expedition comes across a peculiar patch of tall trees all planted carefully in a grid.
    The Elves explain that a previous expedition planted these trees as a reforestation effort.
    Now, they're curious if this would be a good location for a tree house.

    First, determine whether there is enough tree cover here to keep a tree house **hidden**. To do
    this, you need to count the number of trees that are **visible from outside the grid** when
    looking directly along a row or column.

    The Elves have already launched a quadcopter to generate a map with the height of each tree
    (your puzzle input). For example:

        >>> hs = heights_from_text('''
        ...     30373
        ...     25512
        ...     65332
        ...     33549
        ...     35390
        ... ''')
        >>> hs
        [[3, 0, 3, 7, 3], [2, 5, 5, 1, 2], [6, 5, 3, 3, 2], [3, 3, 5, 4, 9], [3, 5, 3, 9, 0]]

    Each tree is represented as a single digit whose value is its height, where `0` is the shortest
    and `9` is the tallest.

    A tree is **visible** if all of the other trees between it and an edge of the grid are
    **shorter** than it. Only consider trees in the same row or column; that is, only look up, down,
    left, or right from any given tree.

    All of the trees around the edge of the grid are **visible** - since they are already on the
    edge, there are no trees to block the view. In this example, that only leaves the **interior
    nine trees** to consider:

        >>> visible = visibility_from_outside_dict(hs)

      - The top-left `5` is visible from the left and top. (It isn't visible from the right or
        bottom since other trees of height `5` are in the way.)

        >>> visible[(1, 1)]
        [Heading.NORTH, Heading.WEST]

      - The top-middle `5` is visible from the top and right.

        >>> visible[(2, 1)]
        [Heading.NORTH, Heading.EAST]

      - The top-right `1` is not visible from any direction; for it to be visible, there would need
        to only be trees of height `0` between it and an edge.

        >>> (3, 1) in visible
        False

      - The left-middle `5` is visible, but only from the right.

        >>> visible[(1, 2)]
        [Heading.EAST]

      - The center `3` is not visible from any direction; for it to be visible, there would need to
        be only trees of at most height 2 between it and an edge.

        >>> (2, 2) in visible
        False

      - The right-middle `3` is visible from the right.

        >>> visible[(3, 2)]
        [Heading.EAST]

      - In the bottom row, the middle `5` is visible, but the `3` and `4` are not.

        >>> [(x, 3) in visible for x in (1, 2, 3)]
        [False, True, False]

    With 16 trees visible on the edge and another 5 visible in the interior, a total of **21** trees
    are visible in this arrangement.

        >>> len(visible)
        21

    Consider your map; **how many trees are visible from outside the grid?**

        >>> part_1(hs)
        part 1: 21 trees are visible from outside
        21
    """

    result = len(visibility_from_outside_dict(heights))

    print(f"part 1: {result} trees are visible from outside")
    return result


def part_2(heights: list[list[int]]) -> int:
    """
    Content with the amount of tree cover available, the Elves just need to know the best spot to
    build their tree house: they would like to be able to see a lot of **trees**.

    To measure the viewing distance from a given tree, look up, down, left, and right from that
    tree; stop if you reach an edge or at the first tree that is the same height or taller than
    the tree under consideration. (If a tree is right on the edge, at least one of its viewing
    distances will be zero.)

    The Elves don't care about distant trees taller than those found by the rules above;
    the proposed tree house has large eaves to keep it dry, so they wouldn't be able to see higher
    than the tree house anyway.

        >>> hs = heights_from_text('''
        ...     30373
        ...     25512
        ...     65332
        ...     33549
        ...     35390
        ... ''')

    In the example above, consider the middle 5 in the second row:

      - Looking up, its view is not blocked; it can see **1** tree (of height `3`).
      - Looking right, its view is not blocked; it can see **2** trees.
      - Looking down, its view is blocked eventually; it can see **2** trees
        (one of height `3`, then the tree of height `5` that blocks its view).
      - Looking left, its view is blocked immediately; it can see only **1** tree
        (of height `5`, right next to it).

        >>> visibility_from_tree(hs, (2, 1))
        {Heading.NORTH: 1, Heading.EAST: 2, Heading.SOUTH: 2, Heading.WEST: 1}

    A tree's **scenic score** is found by multiplying together its viewing distance in each of
    the four directions. For this tree, this is **4** (found by multiplying `1 * 1 * 2 * 2`).

        >>> scenic_score(hs, (2, 1))
        4

    However, you can do better: consider the tree of height `5` in the middle of the fourth row:

      - Looking up, its view is blocked at **2** trees (by another tree with a height of `5`).
      - Looking right, its view is blocked at **2** trees (by a massive tree of height `9`).
      - Looking down, its view is not blocked; it can see **1** tree.
      - Looking left, its view is also not blocked; it can see **2** trees.

        >>> visibility_from_tree(hs, (2, 3))
        {Heading.NORTH: 2, Heading.EAST: 2, Heading.SOUTH: 1, Heading.WEST: 2}

    This tree's scenic score is **8** (`2 * 2 * 1 * 2`); this is the ideal spot for the tree house.

        >>> scenic_score(hs, (2, 3))
        8

    Consider each tree on your map. **What is the highest scenic score possible for any tree?**

        >>> part_2(hs)
        part 2: best place for tree house is at (2, 3) with scenic score 8
        8
    """

    forest_width, forest_height = dimensions(heights)
    inner_positions = (
        (x, y) for x in range(1, forest_width - 1) for y in range(1, forest_height - 1)
    )
    best_pos, best_score = maxk(inner_positions, key=lambda pos: scenic_score(heights, pos))

    print(f"part 2: best place for tree house is at {best_pos} with scenic score {best_score}")
    return best_score


Heights = list[list[int]]
Pos = tuple[int, int]


def dimensions(forest: Heights) -> tuple[int, int]:
    width, = set(len(row) for row in forest)
    height = len(forest)
    return width, height


def visibility_from_outside(forest: Heights) -> Iterable[tuple[Pos, Heading]]:
    width, height = dimensions(forest)

    # traversing the forest from outside in each direction
    def positions(looking_from: Heading) -> Iterable[list[Pos]]:
        match looking_from:
            case Heading.NORTH:
                # x, y+
                return ([(x, y) for y in range(height)] for x in range(width))
            case Heading.SOUTH:
                # x, y-
                return ([(x, y) for y in reversed(range(height))] for x in range(width))
            case Heading.WEST:
                # y, x+
                return ([(x, y) for x in range(width)] for y in range(height))
            case Heading.EAST:
                # y, x-
                return ([(x, y) for x in reversed(range(width))] for y in range(height))
            case _:
                raise ValueError(looking_from)

    for heading in Heading:
        # wtf pylint? pylint: disable=not-an-iterable
        for row in positions(heading):
            max_tree_height = -1
            for tree_x, tree_y in row:
                tree_height = forest[tree_y][tree_x]
                if tree_height > max_tree_height:
                    yield (tree_x, tree_y), heading
                    max_tree_height = tree_height


def visibility_from_outside_dict(forest: Heights) -> dict[Pos, list[Heading]]:
    return dgroupby_pairs(visibility_from_outside(forest))


def visibility_from_tree(forest: Heights, pos: Pos) -> dict[Heading, int]:
    x, y = pos
    my_tree_height = forest[y][x]

    def distance(heading: Heading) -> int:
        for dist in count(1):
            current_x, current_y = x + dist * heading.dx, y + dist * heading.dy

            if not (0 <= current_y < len(forest) and 0 <= current_x < len(forest[current_y])):
                # out of bounds
                return dist - 1

            if forest[current_y][current_x] >= my_tree_height:
                # obscured
                return dist

        assert False

    return {heading: distance(heading) for heading in Heading}


def scenic_score(forest: Heights, pos: Pos) -> int:
    return math.prod(visibility_from_tree(forest, pos).values())


def heights_from_file(fn: str) -> Heights:
    return heights_from_lines(open(relative_path(__file__, fn)))


def heights_from_text(text: str) -> Heights:
    return heights_from_lines(text.strip().splitlines())


def heights_from_lines(lines: Iterable[str]) -> Heights:
    return [[int(c) for c in line.strip()] for line in lines]


def main(input_fn: str = 'data/08-input.txt') -> tuple[int, int]:
    heights = heights_from_file(input_fn)
    result_1 = part_1(heights)
    result_2 = part_2(heights)
    return result_1, result_2


if __name__ == '__main__':
    main()
