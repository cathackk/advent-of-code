"""
Advent of Code 2023
Day 22: Sand Slabs
https://adventofcode.com/2023/day/22
"""

import string
from collections import defaultdict
from functools import cache
from itertools import combinations
from typing import Iterable, Self

from tqdm import tqdm

from common.file import relative_path
from common.iteration import dgroupby_pairs, dgroupby_pairs_set, ilen, single_value
from common.rect import HyperCuboid, Rect
from common.text import parse_line


def part_1(bricks_settled: list['Brick']) -> int:
    """
    Enough sand has fallen; it can finally filter water for Snow Island.

    Well, **almost**.

    The sand has been falling as large compacted **bricks** of sand, piling up to form an impressive
    stack here near the edge of Island Island. In order to make use of the sand to filter water,
    some of the bricks will need to be broken apart - nay, **disintegrated** - back into freely
    flowing sand.

    The stack is tall enough that you'll have to be careful about choosing which bricks to
    disintegrate; if you disintegrate the wrong brick, large portions of the stack could topple,
    which sounds pretty dangerous.

    The Elves responsible for water filtering operations took a **snapshot of the bricks while they
    were still falling** (your puzzle input) which should let you work out which bricks are safe to
    disintegrate. For example:

        >>> example = bricks_from_text('''
        ...     1,0,1~1,2,1
        ...     0,0,2~2,0,2
        ...     0,2,3~2,2,3
        ...     0,0,4~0,2,4
        ...     2,0,5~2,2,5
        ...     0,1,6~2,1,6
        ...     1,1,8~1,1,9
        ... ''')

    Each line of text in the snapshot represents the position of a single brick at the time
    the snapshot was taken. The position is given as two `x,y,z` coordinates - one for each end of
    the brick - separated by a tilde (`~`). Each brick is made up of a single straight line of
    cubes, and the Elves were even careful to choose a time for the snapshot that had all of the
    free-falling bricks at **integer positions above the ground**, so the whole snapshot is aligned
    to a three-dimensional cube grid.

    A line like `2,2,2~2,2,2` means that both ends of the brick are at the same coordinate - in
    other words, that the brick is a single cube:

        >>> b = Brick.from_line('2,2,2~2,2,2')
        >>> b.volume
        1

    Lines like `0,0,10~1,0,10` or `0,0,10~0,1,10` both represent bricks that are **two cubes** in
    volume, both oriented horizontally. The first brick extends in the `x` direction, while the
    second brick extends in the `y` direction.

        >>> Brick.from_line('0,0,10~1,0,10').volume
        2
        >>> Brick.from_line('0,0,10~0,1,10').volume
        2

    A line like `0,0,1~0,0,10` represents a **ten-cube brick** which is oriented **vertically**.
    One end of the brick is the cube located at `0,0,1`, while the other end of the brick is located
    directly above it at `0,0,10`.

        >>> Brick.from_line('0,0,1~0,0,10').volume
        10

    The ground is at `z=0` and is perfectly flat; the lowest `z` value a brick can have is therefore
    `1`. So, `5,5,1~5,6,1` and `0,2,1~0,2,5` are both resting on the ground, but `3,3,2~3,3,3` was
    above the ground at the time of the snapshot.

        >>> Brick.from_line('5,5,1~5,6,1').above_ground()
        0
        >>> Brick.from_line('0,2,1~0,2,5').above_ground()
        0
        >>> Brick.from_line('3,3,2~3,3,3').above_ground()
        1

    Because the snapshot was taken while the bricks were still falling, some bricks will **still be
    in the air**; you'll need to start by figuring out where they will end up. Bricks are magically
    stabilized, so they **never rotate**, even in weird situations like where a long horizontal
    brick is only supported on one end. Two bricks cannot occupy the same position, so a falling
    brick will come to rest upon the first other brick it encounters.

    At the time of the snapshot, from the side so the `x` axis goes left to right, these bricks are
    arranged like this:

        >>> draw_bricks(example, front_axis='x')
         x
        012
        ·G· 9
        ·G· 8
        ··· 7
        FFF 6
        ··E 5 z
        D·· 4
        CCC 3
        BBB 2
        ·A· 1
        --- 0

    Rotating the perspective 90 degrees so the `y` axis now goes left to right, the same bricks are
    arranged like this:

        >>> draw_bricks(example, front_axis='y')
         y
        012
        ·G· 9
        ·G· 8
        ··· 7
        ·F· 6
        EEE 5 z
        DDD 4
        ··C 3
        B·· 2
        AAA 1
        --- 0

    Once all of the bricks fall downward as far as they can go, the stack looks like this, where `?`
    means bricks are hidden behind other bricks at that location:

        >>> example_settled = list(settled(example))
        >>> draw_bricks(example_settled, front_axis='x')
         x
        012
        ·G· 6
        ·G· 5
        FFF 4
        D·E 3 z
        ??? 2
        ·A· 1
        --- 0

    Again from the side:

        >>> draw_bricks(example_settled, front_axis='y')
         y
        012
        ·G· 6
        ·G· 5
        ·F· 4
        ??? 3 z
        B·C 2
        AAA 1
        --- 0

    Now that all of the bricks have settled, it becomes easier to tell which bricks are supporting
    which other bricks:

      - Brick `A` is the only brick supporting bricks `B` and `C`.
      - Brick `B` is one of two bricks supporting brick `D` and brick `E`.
      - Brick `C` is the other brick supporting brick `D` and brick `E`.
      - Brick `D` supports brick `F`.
      - Brick `E` also supports brick `F`.
      - Brick `F` supports brick `G`.
      - Brick `G` isn't supporting any bricks.

      >>> labels_dict(supports(example_settled))
      {'A': ['B', 'C'], 'B': ['D', 'E'], 'C': ['D', 'E'], 'D': ['F'], 'E': ['F'], 'F': ['G']}
      >>> labels_dict(supported_by(example_settled))
      {'G': ['F'], 'F': ['D', 'E'], 'D': ['B', 'C'], 'E': ['B', 'C'], 'B': ['A'], 'C': ['A']}

    Your first task is to figure out **which bricks are safe to disintegrate**. A brick can be
    safely disintegrated if, after removing it, **no other bricks** would fall further directly
    downward. Don't actually disintegrate any bricks - just determine what would happen if, for each
    brick, only that brick were disintegrated. Bricks can be disintegrated even if they're
    completely surrounded by other bricks; you can squeeze between bricks if you need to.

    In this example, the bricks can be disintegrated as follows:

      - Brick `A` cannot be disintegrated safely;
        if it were disintegrated, bricks `B` and `C` would both fall.
      - Brick `B` can be disintegrated;
        the bricks above it (`D` and `E`) would still be supported by brick `C`.
      - Brick `C` can be disintegrated;
        the bricks above it (`D` and `E`) would still be supported by brick `B`.
      - Brick `D` can be disintegrated;
        the brick above it (`F`) would still be supported by brick `E`.
      - Brick `E` can be disintegrated;
        the brick above it (`F`) would still be supported by brick `D`.
      - Brick `F` cannot be disintegrated; the brick above it (`G`) would fall.
      - Brick `G` can be disintegrated; it does not support any other bricks.

      >>> [brick.label for brick in disintegrable(example_settled)]
      ['B', 'C', 'D', 'E', 'G']

    So, in this example, **`5`** bricks can be safely disintegrated.

    Figure how the blocks will settle based on the snapshot. Once they've settled, consider
    disintegrating a single brick; **how many bricks could be safely chosen as the one to get
    disintegrated?**

        >>> part_1(example_settled)
        part 1: 5 bricks can be disintegrated
        5
    """

    result = ilen(disintegrable(bricks_settled))

    print(f"part 1: {result} bricks can be disintegrated")
    return result


def part_2(bricks_settled: list['Brick']) -> int:
    """
    Disintegrating bricks one at a time isn't going to be fast enough. While it might sound
    dangerous, what you really need is a **chain reaction**.

    You'll need to figure out the best brick to disintegrate. For each brick, determine how many
    **other bricks would fall** if that brick were disintegrated.

    Using the same example as above:

        >>> example = bricks_from_file('data/22-example.txt')
        >>> example_settled = list(settled(example))

      - Disintegrating brick `A` would cause all **`6`** other bricks to fall.
      - Disintegrating brick `F` would cause only **`1`** other brick, `G`, to fall.

        >>> labels_dict(dict(falling_chain(example_settled)))
        {'A': ['B', 'C', 'D', 'E', 'F', 'G'], 'F': ['G']}

    Disintegrating any other brick would cause **no other bricks** to fall. So, in this example,
    the sum of **the number of other bricks that would fall** as a result of disintegrating each
    brick is **`7`**:

        >>> sum(len(falling) for falling in _.values())
        7

    For each brick, determine how many **other bricks** would fall if that brick were disintegrated.
    **What is the sum of the number of other bricks that would fall?**

        >>> part_2(example_settled)
        part 2: total of 7 bricks would fall
        7
    """

    result = sum(len(falling) for _, falling in falling_chain(bricks_settled))

    print(f"part 2: total of {result} bricks would fall")
    return result


Pos3 = tuple[int, int, int]
Pos2 = tuple[int, int]


class Brick(HyperCuboid):
    def __init__(self, id_: int, corner_1: Pos3, corner_2: Pos3):
        self.id_ = id_
        super().__init__(corner_1, corner_2)

    @property
    def top_z(self) -> int:
        return self.corner_max[2]

    @property
    def bottom_z(self) -> int:
        return self.corner_min[2]

    def above_ground(self) -> int:
        return self.bottom_z - 1

    def fall(self, by: int = 1) -> Self:
        x_1, y_1, z_1 = self.corner_min
        x_2, y_2, z_2 = self.corner_max
        return type(self)(self.id_, (x_1, y_1, z_1 - by), (x_2, y_2, z_2 - by))

    def intersects(self, other: Self) -> bool:
        return all(
            self[axis].start < other[axis].stop and other[axis].start < self[axis].stop
            for axis in range(3)
        )

    def stands_on(self, other: Self) -> bool:
        if not self.bottom_z - 1 == other.top_z:
            return False
        return self.fall(by=1).intersects(other)

    @property
    def label(self) -> str:
        if self.id_ is None:
            return '?'
        return string.ascii_uppercase[self.id_ % len(string.ascii_uppercase)]

    @classmethod
    def from_line(cls, line: str, id_: int = -1) -> Self:
        # '0,2,3~2,2,3'
        x_1, y_1, z_1, x_2, y_2, z_2 = parse_line(line, '$,$,$~$,$,$')
        return cls(
            id_=id_,
            corner_1=(int(x_1), int(y_1), int(z_1)),
            corner_2=(int(x_2), int(y_2), int(z_2)),
        )

    @staticmethod
    def sorted(bricks: Iterable['Brick'], axes: Iterable[str]) -> list['Brick']:
        sort_indices = [('xyz'.index(axis[-1]), -1 if axis[0] == '-' else 1) for axis in axes]

        def key(brick: 'Brick') -> tuple[int, ...]:
            return tuple(
                (brick.corner_min if direction > 0 else brick.corner_max)[axis] * direction
                for axis, direction in sort_indices
            )

        return sorted(bricks, key=key)


def settled(bricks: Iterable[Brick]) -> Iterable[Brick]:
    bricks_sorted = Brick.sorted(bricks, axes=('z',))

    settled_by_top_z: defaultdict[int, list[Brick]] = defaultdict(list)

    for brick in bricks_sorted:
        while True:
            if brick.above_ground() <= 0:
                # already on ground -> stop falling
                break
            if any(brick.stands_on(other) for other in settled_by_top_z[brick.bottom_z - 1]):
                # standing on another brick -> stop falling
                break
            # fall on ...
            brick = brick.fall()

        settled_by_top_z[brick.top_z].append(brick)
        yield brick


def supports(bricks: Iterable[Brick]) -> dict[Brick, list[Brick]]:
    return dgroupby_pairs(
        (brick_bottom, brick_top)
        for brick_bottom, brick_top in combinations(
            # sorted from bottom to top
            Brick.sorted(bricks, axes=('z',)),
            r=2
        )
        if brick_top.stands_on(brick_bottom)
    )


def supported_by(bricks: Iterable[Brick]) -> dict[Brick, list[Brick]]:
    return dgroupby_pairs(
        (brick_top, brick_bottom)
        for (brick_top, brick_bottom) in combinations(
            # sorted from top to bottom
            Brick.sorted(bricks, axes=('-z',)),
            r=2
        )
        if brick_top.stands_on(brick_bottom)
    )


def labels_dict(bricks: dict[Brick, list[Brick]]) -> dict[str, list[str]]:
    return {
        brick.label: [other.label for other in others]
        for brick, others in bricks.items()
    }


def disintegrable(bricks_settled: list[Brick]) -> Iterable[Brick]:
    bottom_to_tops = supports(bricks_settled)
    top_to_bottoms = supported_by(bricks_settled)

    return (
        brick
        for brick in bricks_settled
        # all bricks supported by this one have at least one other support
        if all(len(top_to_bottoms[top]) > 1 for top in bottom_to_tops.get(brick, []))
    )


def falling_chain(bricks_settled: list[Brick]) -> Iterable[tuple[Brick, list[Brick]]]:
    top_to_bottoms = supported_by(bricks_settled)

    @cache
    def is_standing(brick: Brick, removed: Brick) -> bool:
        if brick is removed:
            # brick is not standing by definition
            return False
        if not brick.above_ground():
            # brick is standing on the ground
            return True
        # is any other brick, this one is standing at, still standing?
        return any(
            is_standing(bottom, removed)
            for bottom in top_to_bottoms.get(brick, [])
        )

    return (
        (brick_removed, fallen)
        for brick_removed in tqdm(bricks_settled, unit=" bricks", desc="falling bricks", delay=1.0)
        if (
            fallen := [
                other
                for other in bricks_settled
                if other is not brick_removed
                if not is_standing(other, brick_removed)
            ]
        )
    )


def draw_bricks(bricks: Iterable[Brick], front_axis: str = 'x', legend: bool = True) -> None:
    assert front_axis in ('x', 'y')
    bricks_sorted = Brick.sorted(bricks, axes=(('-y', 'x') if front_axis == 'x' else ('x', 'y')))

    # draw brick labels
    def flatten(x: int, y: int, z: int) -> Pos2:
        return ((x if front_axis == 'x' else y), -z)

    canvas_multi = dgroupby_pairs_set(
        (flatten(x, y, z), brick.label)
        for brick in bricks_sorted
        for x, y, z in brick
    )
    canvas = {
        pos_c: (single_value(labels) if len(labels) == 1 else '?')
        for (pos_c, labels) in canvas_multi.items()
    }

    # draw ground
    bounds = Rect.with_all(canvas).grow_by(bottom_y=+1)
    canvas.update(((x_c, bounds.bottom_y), '-') for x_c in bounds.range_x())
    # draw empty spaces
    canvas.update((pos, '·') for pos in bounds if pos not in canvas)

    # draw legend
    if legend:
        legend_bounds = bounds.grow_by(right_x=4, top_y=2)
        # horizontal axis = x/y
        canvas[(bounds.width//2, legend_bounds.top_y)] = front_axis
        canvas.update(((x_c, legend_bounds.top_y + 1), str(x_c)[-1]) for x_c in bounds.range_x())
        # vertical axis = z
        canvas[(legend_bounds.right_x, -(bounds.height-1)//2)] = 'z'
        canvas.update(((legend_bounds.right_x-2, y_c), str(y_c)[-1]) for y_c in bounds.range_y())
        bounds = legend_bounds

    # print!
    for y_c in bounds.range_y():
        print(''.join(canvas.get((x_c, y_c), ' ') for x_c in bounds.range_x()).rstrip())


def bricks_from_file(fn: str) -> list[Brick]:
    return list(bricks_from_lines(open(relative_path(__file__, fn))))


def bricks_from_text(text: str) -> list[Brick]:
    return list(bricks_from_lines(text.strip().splitlines()))


def bricks_from_lines(lines: Iterable[str]) -> Iterable[Brick]:
    return (Brick.from_line(line.strip(), n) for n, line in enumerate(lines))


def main(input_fn: str = 'data/22-input.txt') -> tuple[int, int]:
    bricks = bricks_from_file(input_fn)
    bricks_settled = list(settled(bricks))
    result_1 = part_1(bricks_settled)
    result_2 = part_2(bricks_settled)
    return result_1, result_2


if __name__ == '__main__':
    main()
