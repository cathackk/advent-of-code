"""
Advent of Code 2021
Day 22: Reactor Reboot
https://adventofcode.com/2021/day/22
"""

import math
from collections import Counter
from itertools import chain
from typing import Iterable
from typing import Iterator
from typing import Optional

from tqdm import tqdm

from common.rect import Rect
from common.utils import parse_line
from common.utils import relative_path
from common.utils import separate
from common.utils import zip1


def part_1(steps: Iterable['Step']) -> int:
    """
    Operating at these extreme ocean depths has overloaded the submarine's reactor; it needs to be
    rebooted.

    The reactor core is made up of a large 3-dimensional grid made up entirely of cubes, one cube
    per integer 3-dimensional coordinate (`x,y,z`). Each cube can be either **on** or **off**; at
    the start of the reboot process, they are all **off**.

        >>> reactor = Set3D()

    To reboot the reactor, you just need to set all of the cubes to either **on** or **off** by
    following a list of **reboot steps** (your puzzle input). Each step specifies a cuboid (the set
    of all cubes that have coordinates which fall within ranges for `x`, `y`, and `z`) and whether
    to turn all of the cubes in that cuboid **on** or **off**.

    For example, given these reboot steps:

        >>> reboot_steps = steps_from_text('''
        ...     on x=10..12,y=10..12,z=10..12
        ...     on x=11..13,y=11..13,z=11..13
        ...     off x=9..11,y=9..11,z=9..11
        ...     on x=10,y=10,z=10
        ... ''')
        >>> len(reboot_steps)
        4

    The first step turns **on** a 3x3x3 cuboid consisting of 27 cubes:

        >>> print(step_1 := reboot_steps[0])
        on x=10..12,y=10..12,z=10..12
        >>> step_1
        Step(light_on=True, cuboid=Cuboid((10, 10, 10), (12, 12, 12)))
        >>> step_1.run(reactor)
        27
        >>> reactor.draw()
           10 -> x
        10 333
         ↓ 333
         y 333

    The second step turns **on** a 3x3x3 cuboid that overlaps with the first. As a result, only 19
    additional cubes turn on; the rest are already on from the previous step:

        >>> print(step_2 := reboot_steps[1])
        on x=11..13,y=11..13,z=11..13
        >>> step_2.run(reactor)
        19
        >>> reactor.draw()
           10 -> x
        10 333·
         ↓ 3443
         y 3443
           ·333

    The third step turns **off** a 3x3x3 cuboid that overlaps partially with some cubes that are on,
    ultimately turning off 8 cubes:

        >>> print(step_3 := reboot_steps[2])
        off x=9..11,y=9..11,z=9..11
        >>> step_3.run(reactor)
        -8
        >>> reactor.draw()
           10 -> x
        10 113·
         ↓ 1243
         y 3443
           ·333

    The final step turns **on** a single cube, `10,10,10`.

        >>> print(step_4 := reboot_steps[3])
        on x=10,y=10,z=10
        >>> step_4.run(reactor)
        1
        >>> reactor.draw()
           10 -> x
        10 213·
         ↓ 1243
         y 3443
           ·333

    After this last step, **`39`** cubes are **on**.

        >>> len(reactor)
        39

    The initialization procedure only uses cubes that have `x`, `y`, and `z` positions of at least
    `-50` and at most `50`. For now, ignore cubes outside this region.

    Here is a larger example:

        >>> reboot_steps_2 = steps_from_file('data/22-example.txt')
        >>> len(reboot_steps_2)
        22

    The last two steps are fully outside the initialization procedure area; all other steps are
    fully within it.

        >>> reboot_steps_2_filtered = list(filter(Step.is_within_starting_area, reboot_steps_2))
        >>> len(reboot_steps_2_filtered)
        20

    After executing these steps in the initialization procedure region, 590784 cubes are on.

        >>> Step.run_all(reboot_steps_2_filtered)
        590784

    Execute the reboot steps. Afterward, considering only cubes in the region
    `x=-50..50,y=-50..50,z=-50..50`, **how many cubes are on?**

        >>> part_1(reboot_steps_2)
        part 1: 590784 cubes are on
        590784
    """

    result = Step.run_all(step for step in steps if step.is_within_starting_area())

    print(f"part 1: {result} cubes are on")
    return result


def part_2(steps: Iterable['Step']) -> int:
    """
    Now that the initialization procedure is complete, you can reboot the reactor.

    Starting with all cubes **off**, run all of the **reboot steps** for all cubes in the reactor.

    Consider the following reboot steps:

        >>> reboot_steps = steps_from_file('data/22-larger-example.txt')

    After running the above reboot steps, 2758514936282235 cubes are on:

        >>> Step.run_all(reboot_steps)
        2758514936282235

    Just for fun, 474140 of those are also in the initialization procedure region:

        >>> Step.run_all(filter(Step.is_within_starting_area, reboot_steps))
        474140

    Starting again with all cubes **off**, execute all reboot steps. Afterward, considering all
    cubes, **how many cubes are on?**

        >>> part_2(reboot_steps)
        part 2: 2758514936282235 cubes are on
        2758514936282235
    """

    result = Step.run_all(steps)

    print(f"part 2: {result} cubes are on")
    return result


Pos3D = tuple[int, int, int]


class Cuboid:
    def __init__(self, corner_0: Pos3D, corner_1: Pos3D):
        self.x_0, self.y_0, self.z_0 = corner_0
        self.x_1, self.y_1, self.z_1 = corner_1
        assert self.x_0 <= self.x_1
        assert self.y_0 <= self.y_1
        assert self.z_0 <= self.z_1

    def __repr__(self) -> str:
        corner_0 = self.x_0, self.y_0, self.z_0
        corner_1 = self.x_1, self.y_1, self.z_1
        return f'{type(self).__name__}({corner_0!r}, {corner_1!r})'

    def __str__(self):
        def edge(v_0: int, v_1: int) -> str:
            return f'{v_0}..{v_1}' if v_0 != v_1 else str(v_0)

        return (
            f'x={edge(self.x_0, self.x_1)},'
            f'y={edge(self.y_0, self.y_1)},'
            f'z={edge(self.z_0, self.z_1)}'
        )

    @classmethod
    def from_str(cls, line: str) -> 'Cuboid':
        def parse_edge(edge: str) -> tuple[int, int]:
            if '..' in edge:
                left, right = edge.split('..')
                return int(left), int(right)
            else:
                return int(edge), int(edge)

        e_x, e_y, e_z = parse_line(line.strip(), 'x=$,y=$,z=$')
        x_0, x_1 = parse_edge(e_x)
        y_0, y_1 = parse_edge(e_y)
        z_0, z_1 = parse_edge(e_z)
        return cls(corner_0=(x_0, y_0, z_0), corner_1=(x_1, y_1, z_1))

    @property
    def range_x(self) -> range:
        return range(self.x_0, self.x_1 + 1)

    @property
    def range_y(self) -> range:
        return range(self.y_0, self.y_1 + 1)

    @property
    def range_z(self) -> range:
        return range(self.z_0, self.z_1 + 1)

    def get_range(self, axis: str) -> range:
        if axis == 'x':
            return self.range_x
        elif axis == 'y':
            return self.range_y
        elif axis == 'z':
            return self.range_z
        else:
            raise ValueError(axis)

    @property
    def shape(self) -> tuple[int, int, int]:
        return len(self.range_x), len(self.range_y), len(self.range_z)

    @property
    def volume(self) -> int:
        return math.prod(self.shape)

    def __iter__(self) -> Iterable[Pos3D]:
        return (
            (x, y, z)
            for x in self.range_x
            for y in self.range_y
            for z in self.range_z
        )

    def __contains__(self, other) -> bool:
        if isinstance(other, tuple):
            x, y, z = other
            return x in self.range_x and y in self.range_y and z in self.range_z
        elif isinstance(other, type(self)):
            return other.is_fully_within(self)
        else:
            raise TypeError(type(other))

    def is_fully_within(self, other: 'Cuboid') -> bool:
        return (
            other.x_0 <= self.x_0 and self.x_1 <= other.x_1 and
            other.y_0 <= self.y_0 and self.y_1 <= other.y_1 and
            other.z_0 <= self.z_0 and self.z_1 <= other.z_1
        )

    def is_fully_outside(self, other: 'Cuboid') -> bool:
        return not self.does_intersect(other)

    def does_intersect(self, other: 'Cuboid') -> bool:
        return (
            self.x_0 <= other.x_1 and other.x_0 <= self.x_1 and
            self.y_0 <= other.y_1 and other.y_0 <= self.y_1 and
            self.z_0 <= other.z_1 and other.z_0 <= self.z_1
        )

    def intersect(self, other: 'Cuboid') -> Optional['Cuboid']:
        if not self.does_intersect(other):
            return None

        return type(self)(
            corner_0=(max(self.x_0, other.x_0), max(self.y_0, other.y_0), max(self.z_0, other.z_0)),
            corner_1=(min(self.x_1, other.x_1), min(self.y_1, other.y_1), min(self.z_1, other.z_1))
        )

    def __and__(self, other: 'Cuboid') -> Optional['Cuboid']:
        return self.intersect(other)

    def broken_by(self, other: 'Cuboid') -> Iterable['Cuboid']:
        # break `self` into pieces which are all fully within or fully outside of `other`

        if not self.does_intersect(other):
            return (self,)

        # TODO: reimplement splitting using intersection?

        def edge_split(
            left_self: int, right_self: int, left_other: int, right_other: int
        ) -> list[tuple[int, int]]:

            split_points = [left_self]

            if left_self < left_other <= right_self:
                #    oooo...
                # ss|ssss...
                split_points.append(left_other)

            if left_self <= right_other < right_self:
                # ...oooo
                # ...ssss|ss
                split_points.append(right_other + 1)

            split_points.append(right_self + 1)

            return [(left, right - 1) for left, right in zip1(split_points)]

        x_split = edge_split(self.x_0, self.x_1, other.x_0, other.x_1)
        y_split = edge_split(self.y_0, self.y_1, other.y_0, other.y_1)
        z_split = edge_split(self.z_0, self.z_1, other.z_0, other.z_1)

        cls = type(self)
        # TODO: optimize pieces by joining into larger cuboids
        return (
            cls((x_0, y_0, z_0), (x_1, y_1, z_1))
            for (x_0, x_1) in x_split
            for (y_0, y_1) in y_split
            for (z_0, z_1) in z_split
        )

    def union(self, other: 'Cuboid') -> Iterable['Cuboid']:
        """
            >>> a = Cuboid((1, 1, 1), (4, 5, 6))
            >>> b = Cuboid((3, 4, 5), (7, 7, 7))
            >>> draw(a | b)
              1 -> x
            1 6666···
            ↓ 6666···
            y 6666···
              6677333
              6677333
              ··33333
              ··33333
        """

        # trivial cases
        if other.is_fully_within(self):
            return (self,)
        if self.is_fully_within(other):
            return (other,)
        if self.is_fully_outside(other):
            return self, other

        # break both cuboids
        # -> return pieces from the one which is broken into less pieces
        # -> and return the other cuboid whole
        self_pieces = list(self.broken_by(other))
        other_pieces = list(other.broken_by(self))
        if len(self_pieces) >= len(other_pieces):
            return chain([self], (piece for piece in other_pieces if piece.is_fully_outside(self)))
        else:
            return chain((piece for piece in self_pieces if piece.is_fully_outside(other)), [other])

    def __or__(self, other: 'Cuboid') -> Iterable['Cuboid']:
        return self.union(other)

    def difference(self, other: 'Cuboid') -> Iterable['Cuboid']:
        """
            >>> a = Cuboid((3, 0, 5), (8, 3, 9))
            >>> b = Cuboid((0, 2, 8), (4, 5, 12))
            >>> draw(a - b)
              3 -> x
            0 555555
            ↓ 555555
            y 335555
              335555
        """

        # trivial cases
        if self.is_fully_within(other):
            return []
        if self.is_fully_outside(other):
            return [self]

        return (
            piece
            for piece in self.broken_by(other)
            if piece.is_fully_outside(other)
        )

    def __sub__(self, other: 'Cuboid') -> Iterable['Cuboid']:
        return self.difference(other)


class Set3D:
    """
        >>> s = Set3D([
        ...     Cuboid((0, 0, 0), (5, 5, 3)),
        ...     Cuboid((1, 1, 1), (6, 6, 6)),
        ...     Cuboid((8, 0, 0), (10, 3, 2)),
        ...     Cuboid((9, 5, 6), (9, 5, 7))
        ... ])
        >>> s.draw()
          0 -> x
        0 444444··333
        ↓ 4777776·333
        y 4777776·333
          4777776·333
          4777776····
          4777776··2·
          ·666666····
        >>> s.draw(axis_flat='y')
          0 -> x
        0 666666··444
        ↓ 6777776·444
        z 6777776·444
          6777776····
          ·666666····
          ·666666····
          ·666666··1·
          ·········1·
        >>> s.draw(axis_flat='x')
          0 -> y
        0 999966·
        ↓ 9###776
        z 9###776
          6777776
          ·666666
          ·666666
          ·666676
          ·····1·
    """

    def __init__(self, cuboids: Iterable[Cuboid] = ()):
        self.cuboids = []  # is always kept disjunct
        self.update(cuboids)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.cuboids!r})'

    def __contains__(self, pos: Pos3D) -> bool:
        assert isinstance(pos, tuple)  # "Cuboid in Set3d" not supported
        return any(pos in cuboid for cuboid in self.cuboids)

    def __len__(self) -> int:
        return sum(cuboid.volume for cuboid in self.cuboids)

    def __iter__(self) -> Iterator[Pos3D]:
        return (pos for cuboid in self.cuboids for pos in cuboid)

    def add(self, cuboid: Cuboid) -> None:
        intersects = (
            (index, other)
            for index, other in enumerate(self.cuboids)
            if cuboid.does_intersect(other)
        )
        first_intersect = next(intersects, None)
        if first_intersect:
            index, intersect = first_intersect
            self.cuboids.pop(index)
            self.update(cuboid.union(intersect))
        else:
            self.cuboids.append(cuboid)

    def update(self, added: Iterable[Cuboid]) -> None:
        for cuboid in added:
            self.add(cuboid)

    def remove(self, removed: Cuboid) -> None:
        intersecting, nonintersecting = separate(self.cuboids, removed.does_intersect)

        self.cuboids = nonintersecting
        self.cuboids.extend(
            piece
            for other in intersecting
            for piece in other.difference(removed)
        )

    def draw(self, axis_flat: str = 'z') -> None:
        draw(self.cuboids, axis_flat=axis_flat)


class Step:
    def __init__(self, light_on: bool, cuboid: Cuboid):
        self.light_on = light_on
        self.cuboid = cuboid

    def __repr__(self) -> str:
        return f'{type(self).__name__}(light_on={self.light_on!r}, cuboid={self.cuboid!r})'

    def __str__(self) -> str:
        state = 'on' if self.light_on else 'off'
        return f'{state} {self.cuboid}'

    @classmethod
    def from_str(cls, line: str) -> 'Step':
        # on x=-22..28,y=-29..23,z=-38..16
        # off x=-48..-32,y=-32..-16,z=-15..-5
        state, cuboid = line.split(' ')
        return cls(light_on=(state == 'on'), cuboid=Cuboid.from_str(cuboid))

    def run(self, cubes: Set3D) -> int:
        volume_before = len(cubes)

        if self.light_on:
            cubes.add(self.cuboid)
        else:
            cubes.remove(self.cuboid)

        return len(cubes) - volume_before

    @staticmethod
    def run_all(steps: Iterable['Step'], cubes: Set3D = None) -> int:
        if cubes is None:
            cubes = Set3D()

        return sum(
            step.run(cubes)
            for step in tqdm(steps, unit='step', delay=1.0)
        )

    STARTING_AREA = Cuboid((-50, -50, -50), (50, 50, 50))

    def is_within_starting_area(self) -> bool:
        return self.cuboid.is_fully_within(self.STARTING_AREA)


def draw(cuboids: Iterable[Cuboid], axis_flat: str = 'z') -> None:
    axis_hor, axis_vert = {'x': ('y', 'z'), 'y': ('x', 'z'), 'z': ('x', 'y')}[axis_flat]
    depths = (
        ((h, v), len(cuboid.get_range(axis_flat)))
        for cuboid in cuboids
        for h in cuboid.get_range(axis_hor)
        for v in cuboid.get_range(axis_vert)
    )
    total_depths = Counter()
    for h_v, depth in depths:
        total_depths[h_v] += depth

    def char(pos: tuple[int, int]) -> str:
        val = total_depths[pos]
        if val == 0:
            return '·'
        elif val < 10:
            return str(val)
        else:
            return '#'

    bounds = Rect.with_all(total_depths.keys())
    left_margin = len(str(bounds.top_y)) + 1
    print(' ' * left_margin + f'{bounds.left_x} -> {axis_hor}')  # h_label
    vert_labels = [
        f'{bounds.top_y} ',
        '↓'.rjust(left_margin - 1) + ' ',
        axis_vert.rjust(left_margin - 1) + ' '
    ]

    for vert in bounds.range_y():
        vert_off = vert - bounds.top_y
        vert_label = vert_labels[vert_off] if vert_off < len(vert_labels) else ' ' * left_margin
        print(vert_label + ''.join(char((h, vert)) for h in bounds.range_x()))


def steps_from_text(text: str) -> list[Step]:
    return list(steps_from_lines(text.strip().split('\n')))


def steps_from_file(fn: str) -> list[Step]:
    return list(steps_from_lines(open(relative_path(__file__, fn))))


def steps_from_lines(lines: Iterable[str]) -> Iterable[Step]:
    return (Step.from_str(line.strip()) for line in lines)


if __name__ == '__main__':
    steps_ = steps_from_file('data/22-input.txt')
    part_1(steps_)
    part_2(steps_)
