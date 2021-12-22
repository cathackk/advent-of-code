"""
Advent of Code 2021
Day 22: Reactor Reboot
https://adventofcode.com/2021/day/22
"""
from typing import Iterable

from rect import HyperCuboid
from utils import parse_line


def part_1(steps: Iterable['Step']) -> int:
    """
    Operating at these extreme ocean depths has overloaded the submarine's reactor; it needs to be
    rebooted.

    The reactor core is made up of a large 3-dimensional grid made up entirely of cubes, one cube
    per integer 3-dimensional coordinate (`x,y,z`). Each cube can be either **on** or **off**; at
    the start of the reboot process, they are all **off**.

        >>> reactor = set()

    To reboot the reactor, you just need to set all of the cubes to either **on** or **off** by
    following a list of **reboot steps** (your puzzle input). Each step specifies a cuboid (the set
    of all cubes that have coordinates which fall within ranges for `x`, `y`, and `z`) and whether
    to turn all of the cubes in that cuboid **on** or **off**.

    For example, given these reboot steps:

        >>> reboot_steps = steps_from_text('''
        ...     on x=10..12,y=10..12,z=10..12
        ...     on x=11..13,y=11..13,z=11..13
        ...     off x=9..11,y=9..11,z=9..11
        ...     on x=10..10,y=10..10,z=10..10
        ... ''')
        >>> len(reboot_steps)
        4

    The first step turns **on** a 3x3x3 cuboid consisting of 27 cubes:

        >>> print(step_1 := reboot_steps[0])
        on x=10..12,y=10..12,z=10..12
        >>> step_1
        Step(on=True, cuboid=HyperCuboid((10, 10, 10), (12, 12, 12)))
        >>> step_1.cuboid.shape
        (3, 3, 3)
        >>> step_1.run(reactor)
        27

    The second step turns **on** a 3x3x3 cuboid that overlaps with the first. As a result, only 19
    additional cubes turn on; the rest are already on from the previous step:

        >>> print(step_2 := reboot_steps[1])
        on x=11..13,y=11..13,z=11..13
        >>> step_2.run(reactor)
        19

    The third step turns **off** a 3x3x3 cuboid that overlaps partially with some cubes that are on,
    ultimately turning off 8 cubes:

        >>> print(step_3 := reboot_steps[2])
        off x=9..11,y=9..11,z=9..11
        >>> step_3.run(reactor)
        -8

    The final step turns **on** a single cube, `10,10,10`.

        >>> print(step_4 := reboot_steps[3])
        on x=10..10,y=10..10,z=10..10
        >>> step_4.run(reactor)
        1

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

        >>> reboot_steps_2_filtered = [s for s in reboot_steps_2 if s.is_within_starting_area()]
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

        >>> Step.run_all(s for s in reboot_steps if s.is_within_starting_area())
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


Pos3 = tuple[int, int, int]


class Step:
    def __init__(self, on: bool, cuboid: HyperCuboid):
        self.on = on
        self.cuboid = cuboid
        assert len(cuboid.shape) == 3  # three-dimensional

    def __repr__(self) -> str:
        return f'{type(self).__name__}(on={self.on!r}, cuboid={self.cuboid!r})'

    def __str__(self) -> str:
        state = 'on' if self.on else 'off'
        (x0, x1), (y0, y1), (z0, z1) = zip(self.cuboid.corner_min, self.cuboid.corner_max)
        return f'{state} x={x0}..{x1},y={y0}..{y1},z={z0}..{z1}'

    @classmethod
    def from_str(cls, line: str) -> 'Step':
        # on x=-22..28,y=-29..23,z=-38..16
        # off x=-48..-32,y=-32..-16,z=-15..-5
        state, x0, x1, y0, y1, z0, z1 = parse_line(line.strip(), '$ x=$..$,y=$..$,z=$..$')
        return cls(
            on=(state == 'on'),
            cuboid=HyperCuboid((int(x0), int(y0), int(z0)), (int(x1), int(y1), int(z1)))
        )

    def run(self, cubes: set[Pos3]) -> int:
        assert self.is_within_starting_area()  # TODO

        len_before = len(cubes)

        if self.on:
            cubes.update(self.cuboid)
        else:
            cubes.difference_update(self.cuboid)

        len_after = len(cubes)
        return len_after - len_before

    @staticmethod
    def run_all(steps: Iterable['Step'], cubes: set[Pos3] = None) -> int:
        if cubes is None:
            cubes = set()

        return sum(step.run(cubes) for step in steps)

    def is_within_starting_area(self, size: int = 50) -> bool:
        return all(v >= -size for v in self.cuboid.corner_min) \
               and all(v <= size for v in self.cuboid.corner_max)


def steps_from_text(text: str) -> list[Step]:
    return list(steps_from_lines(text.strip().split('\n')))


def steps_from_file(fn: str) -> list[Step]:
    return list(steps_from_lines(open(fn)))


def steps_from_lines(lines: Iterable[str]) -> Iterable[Step]:
    return (Step.from_str(line.strip()) for line in lines)


if __name__ == '__main__':
    steps_ = steps_from_file('data/22-input.txt')
    part_1(steps_)
    part_2(steps_)
