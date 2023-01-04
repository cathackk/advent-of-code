"""
Advent of Code 2018
Day 22: Mode Maze
https://adventofcode.com/2018/day/22
"""

# TODO: remove when solved: https://github.com/PyCQA/pylint/issues/3045
# pylint: disable=unsupported-membership-test

import functools
from dataclasses import dataclass
from enum import Enum
from itertools import groupby
from typing import Any
from typing import Iterable

from common.graph import shortest_path
from common.rect import Rect
from common.text import parse_line
from meta.aoc_tools import data_path


def part_1(cave: 'Cave'):
    """
    This is it, your final stop: the year -483. It's snowing and dark outside; the only light you
    can see is coming from a small cottage in the distance. You make your way there and knock on
    the door.

    A portly man with a large, white beard answers the door and invites you inside. For someone
    living near the North Pole in -483, he must not get many visitors, but he doesn't act surprised
    to see you. Instead, he offers you some milk and cookies.

    After talking for a while, he asks a favor of you. His friend hasn't come back in a few hours,
    and he's not sure where he is. Scanning the region briefly, you discover one life signal in
    a cave system nearby; his friend must have taken shelter there. The man asks if you can go there
    to retrieve his friend.

    The cave is divided into square **regions** which are either dominantly **rocky**, **narrow**,
    or **wet** (called its **type**). Each region occupies exactly one **coordinate** in `X,Y`
    format where `X` and `Y` are integers and zero or greater. (Adjacent regions can be the same
    type.)

    The scan (your puzzle input) is not very detailed: it only reveals the **depth** of the cave
    system and the **coordinates of the target**. However, it does not reveal the type of each
    region. The mouth of the cave is at `0,0`.

    The man explains that due to the unusual geology in the area, there is a method to determine any
    region's type based on its **erosion level**. The erosion level of a region can be determined
    from its **geologic index**. The geologic index can be determined using the first rule that
    applies from the list below:

      - The region at `0,0` (the mouth of the cave) has a geologic index of `0`.
      - The region at the coordinates of the target has a geologic index of `0`.
      - If the region's `Y` coordinate is 0, the geologic index is its `X` coordinate times `16807`.
      - If the region's `X` coordinate is 0, the geologic index is its `Y` coordinate times `48271`.
      - Otherwise, the region's geologic index is the result of multiplying the erosion **levels**
        of the regions at `X-1,Y` and `X,Y-1`.

    A region's **erosion level** is its **geologic index** plus the cave system's **depth**,
    all modulo `20183`. Then:

      - If the erosion level modulo `3` is 0, the region's type is **rocky**.
      - If the erosion level modulo `3` is 1, the region's type is **wet**.
      - If the erosion level modulo `3` is 2, the region's type is **narrow**.

    For example, suppose the cave system's depth is 510 and the target's coordinates are 10,10:

        >>> example_cave = Cave.from_text('''
        ...     depth: 510
        ...     target: 10,10
        ... ''')
        >>> example_cave
        Cave(depth=510, target_pos=(10, 10))

    Using `%` to represent the modulo operator, the cavern would look as follows:

      - At `0,0`, the geologic index is `0`. The erosion level is `(0 + 510) % 20183 = 510`.
        The type is `510 % 3 = 0`, **rocky**:

        >>> example_cave.geologic_index_at((0, 0))
        0
        >>> example_cave.erosion_level_at((0, 0))
        510
        >>> example_cave.region_type_at((0, 0))
        RegionType.ROCKY

      - At `1,0`, because the `Y` coordinate is 0, the geologic index is `1 * 16807 = 16807`.
        The erosion level is `(16807 + 510) % 20183 = 17317`. The type is `17317 % 3 = 1`, **wet**:

        >>> example_cave.geologic_index_at((1, 0))
        16807
        >>> example_cave.erosion_level_at((1, 0))
        17317
        >>> example_cave.region_type_at((1, 0))
        RegionType.WET

      - At `0,1`, because the X coordinate is 0, the geologic index is `1 * 48271 = 48271`.
        The erosion level is `(48271 + 510) % 20183 = 8415`. The type is `8415 % 3 = 0`, **rocky**:

        >>> example_cave.geologic_index_at((0, 1))
        48271
        >>> example_cave.erosion_level_at((0, 1))
        8415
        >>> example_cave.region_type_at((0, 1))
        RegionType.ROCKY

      - At `1,1`, neither coordinate is 0, and it is not the coordinate of the target,
        so the geologic index is the erosion level of `0,1` (`8415`)
        times the erosion level of `1,0` (`17317`), `8415 * 17317 = 145722555`.
        The erosion level is `(145722555 + 510) % 20183 = 1805`.
        The type is `1805 % 3 = 2`, **narrow**.

        >>> example_cave.geologic_index_at((1, 1))
        145722555
        >>> example_cave.erosion_level_at((1, 1))
        1805
        >>> example_cave.region_type_at((1, 1))
        RegionType.NARROW

      - At `10,10`, because they are the target's coordinates, the geologic index is `0`.
        The erosion level is `(0 + 510) % 20183 = 510`. The type is `510 % 3 = 0`, **rocky**.

        >>> example_cave.geologic_index_at((10, 10))
        0
        >>> example_cave.erosion_level_at((10, 10))
        510
        >>> example_cave.region_type_at((10, 10))
        RegionType.ROCKY

    Drawing this same cave system with rocky as `·`, wet as `~`, narrow as `|`, the mouth as `M`,
    the target as `T`, with `0,0` in the top-left corner, `` increasing to the right, and `Y`
    increasing downward, the top-left corner of the map looks like this:

        >>> example_cave.draw(bounds=Rect.at_origin(16, 16))
        M~·|~·|·|~·|~|~·
        ·|~|~|||··|·~···
        ·~~|····||~··|~~
        ~·|····|·~~·|~~·
        ~|··~~···~·|~~··
        ~||·~·~||~|~··|~
        |·~·~~~|||··~··|
        |··~~||~·|~~|~~~
        ·~··~~~··~|·|||·
        ·~~~~~~|||~|~·|~
        ·~~~|~|~~~T~~~||
        ~|||···|~~··|~·|
        ~·~|~·~··~·||~~|
        ||~|~···|~~·~|~~
        |~·~||~~~·|||~~~
        ||·|~~·|·|·||~||

    Before you go in, you should determine the **risk level** of the area. For the rectangle that
    has a top-left corner of region `0,0` and a bottom-right corner of the region containing the
    target, add up the risk level of each individual region: `0` for rocky regions, `1` for wet
    regions, and `2` for narrow regions.

        >>> RegionType.ROCKY.value
        0
        >>> RegionType.WET.value
        1
        >>> RegionType.NARROW.value
        2

    In the cave system above, because the mouth is at `0,0` and the target is at `10,10`, adding up
    the risk level of all regions with an `X` coordinate from 0 to 10 and a `Y` coordinate from 0
    to 10, this total is **114**.

        >>> example_cave.total_risk()
        114

    **What is the total risk level for the smallest rectangle that includes `0,0`
    and the target's coordinates?**

        >>> part_1(example_cave)
        part 1: total risk of the rectangle is 114
        114
    """

    result = cave.total_risk()

    print(f"part 1: total risk of the rectangle is {result}")
    return result


def part_2(cave: 'Cave') -> int:
    """
    Okay, it's time to go rescue the man's friend.

    As you leave, he hands you some tools: a **torch** and some **climbing gear**. You can't equip
    both tools at once, but you can choose to use **neither**.

    Tools can only be used in certain regions:

      - In **rocky** regions, you can use the **climbing gear** or the **torch**.
        You cannot use **neither** (you'll likely slip and fall).
      - In **wet** regions, you can use the **climbing gear** or **neither** tool.
        You cannot use the **torch** (if it gets wet, you won't have a light source).
      - In **narrow** regions, you can use the **torch** or **neither** tool.
        You cannot use the **climbing gear** (it's too bulky to fit).

    You start at `0,0` (the mouth of the cave) with the **torch equipped** and must reach the target
    coordinates as quickly as possible. The regions with negative `X` or `Y` are solid rock and
    cannot be traversed. The fastest route might involve entering regions beyond the `X` or `Y`
    coordinate of the target.

    You can **move to an adjacent region** (up, down, left, or right; never diagonally) if your
    currently equipped tool allows you to enter that region. Moving to an adjacent region takes
    **one minute**. (For example, if you have the **torch** equipped, you can move between **rocky**
    and **narrow** regions, but cannot enter **wet** regions.)

        >>> Step.UP.cost, Step.DOWN.cost, Step.LEFT.cost, Step.RIGHT.cost
        (1, 1, 1, 1)
        >>> Tool.TORCH.passable_regions
        (RegionType.ROCKY, RegionType.NARROW)
        >>> Tool.CLIMBING_GEAR.passable_regions
        (RegionType.ROCKY, RegionType.WET)
        >>> Tool.NEITHER.passable_regions
        (RegionType.WET, RegionType.NARROW)

    You can **change your currently equipped tool or put both away** if your new equipment would be
    valid for your current region. Switching to using the **climbing gear**, **torch**,
    or **neither** always takes **seven minutes**, regardless of which tools you start with.
    (For example, if you are in a **rocky** region, you can switch from the **torch** to the
    **climbing gear**, but you cannot switch to **neither**.)

        >>> Step.SWITCH_TOOL.cost
        7

        >>> Tool.TORCH.switched(RegionType.ROCKY)
        Tool.CLIMBING_GEAR
        >>> Tool.CLIMBING_GEAR.switched(RegionType.ROCKY)
        Tool.TORCH

        >>> Tool.TORCH.switched(RegionType.NARROW)
        Tool.NEITHER
        >>> Tool.NEITHER.switched(RegionType.NARROW)
        Tool.TORCH

        >>> Tool.CLIMBING_GEAR.switched(RegionType.WET)
        Tool.NEITHER
        >>> Tool.NEITHER.switched(RegionType.WET)
        Tool.CLIMBING_GEAR

    Finally, once you reach the target, you need the **torch** equipped before you can find him in
    the dark. The target is always in a **rocky** region, so if you arrive there with
    **climbing gear** equipped, you will need to spend seven minutes switching to your torch.

    For example, using the same cave system as above, starting in the top left corner (`0,0`) and
    moving to the bottom right corner (the target, `10,10`) as quickly as possible, one possible
    route is as follows, with your current position marked `X`:

        >>> example_cave = Cave.from_file('data/22-example.txt')
        >>> duration, path = example_cave.shortest_path()
        >>> path  # doctest: +NORMALIZE_WHITESPACE
        [DOWN, RIGHT, SWITCH_TOOL, RIGHT, RIGHT, RIGHT, SWITCH_TOOL,
         DOWN, DOWN, DOWN, DOWN, DOWN, DOWN, DOWN, DOWN, RIGHT, DOWN, DOWN, RIGHT,
         DOWN, RIGHT, RIGHT, UP, UP, RIGHT, RIGHT, SWITCH_TOOL]
        >>> example_cave.draw_traversal(path, bounds=Rect.at_origin(16, 16))
        Initially:
        X~·|~·|·|~·|~|~·
        ·|~|~|||··|·~···
        ·~~|····||~··|~~
        ~·|····|·~~·|~~·
        ~|··~~···~·|~~··
        ~||·~·~||~|~··|~
        |·~·~~~|||··~··|
        |··~~||~·|~~|~~~
        ·~··~~~··~|·|||·
        ·~~~~~~|||~|~·|~
        ·~~~|~|~~~T~~~||
        ~|||···|~~··|~·|
        ~·~|~·~··~·||~~|
        ||~|~···|~~·~|~~
        |~·~||~~~·|||~~~
        ||·|~~·|·|·||~||
        Down:
        M~·|~·|·|~·|~|~·
        X|~|~|||··|·~···
        ·~~|····||~··|~~
        ~·|····|·~~·|~~·
        ~|··~~···~·|~~··
        ~||·~·~||~|~··|~
        |·~·~~~|||··~··|
        |··~~||~·|~~|~~~
        ·~··~~~··~|·|||·
        ·~~~~~~|||~|~·|~
        ·~~~|~|~~~T~~~||
        ~|||···|~~··|~·|
        ~·~|~·~··~·||~~|
        ||~|~···|~~·~|~~
        |~·~||~~~·|||~~~
        ||·|~~·|·|·||~||
        Right:
        M~·|~·|·|~·|~|~·
        ·X~|~|||··|·~···
        ·~~|····||~··|~~
        ~·|····|·~~·|~~·
        ~|··~~···~·|~~··
        ~||·~·~||~|~··|~
        |·~·~~~|||··~··|
        |··~~||~·|~~|~~~
        ·~··~~~··~|·|||·
        ·~~~~~~|||~|~·|~
        ·~~~|~|~~~T~~~||
        ~|||···|~~··|~·|
        ~·~|~·~··~·||~~|
        ||~|~···|~~·~|~~
        |~·~||~~~·|||~~~
        ||·|~~·|·|·||~||
        Switch from using the torch to neither tool.
        Right 3:
        M~·|~·|·|~·|~|~·
        ·|~|X|||··|·~···
        ·~~|····||~··|~~
        ~·|····|·~~·|~~·
        ~|··~~···~·|~~··
        ~||·~·~||~|~··|~
        |·~·~~~|||··~··|
        |··~~||~·|~~|~~~
        ·~··~~~··~|·|||·
        ·~~~~~~|||~|~·|~
        ·~~~|~|~~~T~~~||
        ~|||···|~~··|~·|
        ~·~|~·~··~·||~~|
        ||~|~···|~~·~|~~
        |~·~||~~~·|||~~~
        ||·|~~·|·|·||~||
        Switch from using neither tool to the climbing gear.
        Down 8:
        M~·|~·|·|~·|~|~·
        ·|~|~|||··|·~···
        ·~~|····||~··|~~
        ~·|····|·~~·|~~·
        ~|··~~···~·|~~··
        ~||·~·~||~|~··|~
        |·~·~~~|||··~··|
        |··~~||~·|~~|~~~
        ·~··~~~··~|·|||·
        ·~~~X~~|||~|~·|~
        ·~~~|~|~~~T~~~||
        ~|||···|~~··|~·|
        ~·~|~·~··~·||~~|
        ||~|~···|~~·~|~~
        |~·~||~~~·|||~~~
        ||·|~~·|·|·||~||
        Right:
        M~·|~·|·|~·|~|~·
        ·|~|~|||··|·~···
        ·~~|····||~··|~~
        ~·|····|·~~·|~~·
        ~|··~~···~·|~~··
        ~||·~·~||~|~··|~
        |·~·~~~|||··~··|
        |··~~||~·|~~|~~~
        ·~··~~~··~|·|||·
        ·~~~~X~|||~|~·|~
        ·~~~|~|~~~T~~~||
        ~|||···|~~··|~·|
        ~·~|~·~··~·||~~|
        ||~|~···|~~·~|~~
        |~·~||~~~·|||~~~
        ||·|~~·|·|·||~||
        Down 2:
        M~·|~·|·|~·|~|~·
        ·|~|~|||··|·~···
        ·~~|····||~··|~~
        ~·|····|·~~·|~~·
        ~|··~~···~·|~~··
        ~||·~·~||~|~··|~
        |·~·~~~|||··~··|
        |··~~||~·|~~|~~~
        ·~··~~~··~|·|||·
        ·~~~~~~|||~|~·|~
        ·~~~|~|~~~T~~~||
        ~|||·X·|~~··|~·|
        ~·~|~·~··~·||~~|
        ||~|~···|~~·~|~~
        |~·~||~~~·|||~~~
        ||·|~~·|·|·||~||
        Right:
        M~·|~·|·|~·|~|~·
        ·|~|~|||··|·~···
        ·~~|····||~··|~~
        ~·|····|·~~·|~~·
        ~|··~~···~·|~~··
        ~||·~·~||~|~··|~
        |·~·~~~|||··~··|
        |··~~||~·|~~|~~~
        ·~··~~~··~|·|||·
        ·~~~~~~|||~|~·|~
        ·~~~|~|~~~T~~~||
        ~|||··X|~~··|~·|
        ~·~|~·~··~·||~~|
        ||~|~···|~~·~|~~
        |~·~||~~~·|||~~~
        ||·|~~·|·|·||~||
        Down:
        M~·|~·|·|~·|~|~·
        ·|~|~|||··|·~···
        ·~~|····||~··|~~
        ~·|····|·~~·|~~·
        ~|··~~···~·|~~··
        ~||·~·~||~|~··|~
        |·~·~~~|||··~··|
        |··~~||~·|~~|~~~
        ·~··~~~··~|·|||·
        ·~~~~~~|||~|~·|~
        ·~~~|~|~~~T~~~||
        ~|||···|~~··|~·|
        ~·~|~·X··~·||~~|
        ||~|~···|~~·~|~~
        |~·~||~~~·|||~~~
        ||·|~~·|·|·||~||
        Right 2:
        M~·|~·|·|~·|~|~·
        ·|~|~|||··|·~···
        ·~~|····||~··|~~
        ~·|····|·~~·|~~·
        ~|··~~···~·|~~··
        ~||·~·~||~|~··|~
        |·~·~~~|||··~··|
        |··~~||~·|~~|~~~
        ·~··~~~··~|·|||·
        ·~~~~~~|||~|~·|~
        ·~~~|~|~~~T~~~||
        ~|||···|~~··|~·|
        ~·~|~·~·X~·||~~|
        ||~|~···|~~·~|~~
        |~·~||~~~·|||~~~
        ||·|~~·|·|·||~||
        Up 2:
        M~·|~·|·|~·|~|~·
        ·|~|~|||··|·~···
        ·~~|····||~··|~~
        ~·|····|·~~·|~~·
        ~|··~~···~·|~~··
        ~||·~·~||~|~··|~
        |·~·~~~|||··~··|
        |··~~||~·|~~|~~~
        ·~··~~~··~|·|||·
        ·~~~~~~|||~|~·|~
        ·~~~|~|~X~T~~~||
        ~|||···|~~··|~·|
        ~·~|~·~··~·||~~|
        ||~|~···|~~·~|~~
        |~·~||~~~·|||~~~
        ||·|~~·|·|·||~||
        Right 2:
        M~·|~·|·|~·|~|~·
        ·|~|~|||··|·~···
        ·~~|····||~··|~~
        ~·|····|·~~·|~~·
        ~|··~~···~·|~~··
        ~||·~·~||~|~··|~
        |·~·~~~|||··~··|
        |··~~||~·|~~|~~~
        ·~··~~~··~|·|||·
        ·~~~~~~|||~|~·|~
        ·~~~|~|~~~X~~~||
        ~|||···|~~··|~·|
        ~·~|~·~··~·||~~|
        ||~|~···|~~·~|~~
        |~·~||~~~·|||~~~
        ||·|~~·|·|·||~||
        Switch from using the climbing gear to the torch.

    This is tied with other routes as **the fastest way to reach the target: `45` minutes**.
    In it, `21` minutes are spent switching tools (three times, seven minutes each) and the
    remaining `24` minutes are spent moving.

        >>> duration
        45
        >>> sum(step.cost for step in path if step is Step.SWITCH_TOOL)
        21
        >>> sum(step.cost for step in path if step is not Step.SWITCH_TOOL)
        24

    **What is the fewest number of minutes you can take to reach the target?**

        >>> part_2(example_cave)
        part 2: target can be reached in 45 minutes
        45
    """

    result, _ = cave.shortest_path()

    print(f"part 2: target can be reached in {result} minutes")
    return result


Pos = tuple[int, int]


class RegionType(Enum):
    ROCKY = 0
    WET = 1
    NARROW = 2

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'

    def char(self) -> str:
        match self:
            case RegionType.ROCKY:
                return '·'
            case RegionType.WET:
                return '~'
            case RegionType.NARROW:
                return '|'

        assert False


class Tool(Enum):
    TORCH = 'the torch'
    CLIMBING_GEAR = 'the climbing gear'
    NEITHER = 'neither tool'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'

    def __str__(self) -> str:
        return str(self.value)

    @property
    def passable_regions(self) -> Iterable[RegionType]:
        match self:
            case Tool.TORCH:
                return (RegionType.ROCKY, RegionType.NARROW)
            case Tool.CLIMBING_GEAR:
                return (RegionType.ROCKY, RegionType.WET)
            case Tool.NEITHER:
                return (RegionType.WET, RegionType.NARROW)

        assert False

    def switched(self, region_type: RegionType) -> 'Tool':
        match self, region_type:
            case (Tool.TORCH, RegionType.ROCKY) | (Tool.NEITHER, RegionType.WET):
                return Tool.CLIMBING_GEAR
            case (Tool.CLIMBING_GEAR, RegionType.ROCKY) | (Tool.NEITHER, RegionType.NARROW):
                return Tool.TORCH
            case (Tool.TORCH, RegionType.NARROW) | (Tool.CLIMBING_GEAR, RegionType.WET):
                return Tool.NEITHER
            case _:
                raise ValueError((self, region_type))


class Step(Enum):
    UP = (0, -1, 1)
    DOWN = (0, +1, 1)
    LEFT = (-1, 0, 1)
    RIGHT = (+1, 0, 1)
    SWITCH_TOOL = (0, 0, 7)

    def __init__(self, dx: int, dy: int, cost: int):
        self.dx, self.dy, self.cost = dx, dy, cost

    def __repr__(self) -> str:
        return self.name

    def __add__(self, pos: Any) -> Pos:
        if not isinstance(pos, tuple):
            return NotImplemented

        x, y = pos
        return x + self.dx, y + self.dy

    __radd__ = __add__


Path = list[Step]


EROSION_MODULO = 20183
GEOLOGICAL_FACTOR_X = 16807
GEOLOGICAL_FACTOR_Y = 48271
ORIGIN = (0, 0)
STARTING_TOOL = Tool.TORCH
FINAL_TOOL = Tool.TORCH


@dataclass(frozen=True)
class Cave:
    depth: int
    target_pos: Pos

    # TODO: remove when pylint starts to understand match-case properly
    # pylint: disable=used-before-assignment
    def geologic_index_at(self, pos: Pos) -> int:
        match pos:
            case (0, 0):
                return 0
            case self.target_pos:
                return 0
            case (x, 0) if x > 0:
                return x * GEOLOGICAL_FACTOR_X
            case (0, y) if y > 0:
                return y * GEOLOGICAL_FACTOR_Y
            case (x, y) if x > 0 and y > 0:
                return self.erosion_level_at((x - 1, y)) * self.erosion_level_at((x, y - 1))

        raise ValueError(pos)

    @functools.lru_cache(maxsize=32_000)
    def erosion_level_at(self, pos: Pos) -> int:
        return (self.geologic_index_at(pos) + self.depth) % EROSION_MODULO

    def region_type_at(self, pos: Pos) -> RegionType:
        return RegionType(self.erosion_level_at(pos) % 3)

    def target_bounds(self) -> Rect:
        return Rect(ORIGIN, self.target_pos)

    def total_risk(self, bounds: Rect = None) -> int:
        return sum(
            self.region_type_at(pos).value
            for pos in (bounds or self.target_bounds())
        )

    def shortest_path(self) -> tuple[int, Path]:
        Node = tuple[Pos, Tool]
        # Edge = Step

        target_x, target_y = self.target_pos
        # optimization: do not go further than 80 right of the target or 3 below the target
        passable_boundaries = Rect(ORIGIN, (target_x + 80, target_y + 3))

        def possible_steps(node: Node) -> Iterable[tuple[Node, Step, int]]:
            pos, tool = node
            for move in [Step.UP, Step.DOWN, Step.LEFT, Step.RIGHT]:
                new_pos = move + pos
                if new_pos not in passable_boundaries:
                    continue
                new_region_type = self.region_type_at(new_pos)
                if new_region_type in tool.passable_regions:
                    yield (new_pos, tool), move, 1

            switched_tool = tool.switched(self.region_type_at(pos))
            yield (pos, switched_tool), Step.SWITCH_TOOL, Step.SWITCH_TOOL.cost

        assert self.region_type_at(ORIGIN) in STARTING_TOOL.passable_regions
        assert self.region_type_at(self.target_pos) in FINAL_TOOL.passable_regions

        return shortest_path(
            start=(ORIGIN, STARTING_TOOL),
            target=(self.target_pos, FINAL_TOOL),
            edges=possible_steps,
        )

    def draw(self, bounds: Rect = None, highlight: dict[Pos, str] = None) -> None:
        if highlight is None:
            highlight = {}

        def char(pos: Pos) -> str:
            assert highlight is not None
            if pos in highlight:
                return highlight[pos]
            elif pos == ORIGIN:
                return 'M'
            elif pos == self.target_pos:
                return 'T'
            elif pos[0] < 0 or pos[1] < 0:
                return '#'
            else:
                return self.region_type_at(pos).char()

        if bounds is None:
            bounds = self.target_bounds().grow_to_fit(highlight.keys())

        for y in bounds.range_y():
            print(''.join(char((x, y)) for x in bounds.range_x()))

    def draw_traversal(self, path: Path, bounds: Rect = None) -> None:
        pos, tool = ORIGIN, STARTING_TOOL
        print("Initially:")
        self.draw(bounds, {pos: 'X'})

        for step, steps_group in groupby(path):
            steps_group_list = list(steps_group)

            if step is Step.SWITCH_TOOL:
                assert len(steps_group_list) == 1
                new_tool = tool.switched(self.region_type_at(pos))
                print(f"Switch from using {tool} to {new_tool}.")
                tool = new_tool

            else:
                for single_step in steps_group_list:
                    pos += single_step
                    assert self.region_type_at(pos) in tool.passable_regions

                step_descr = step.name.title()
                if len(steps_group_list) > 1:
                    step_descr += f" {len(steps_group_list)}"
                print(step_descr + ":")
                self.draw(bounds, {pos: 'X'})

    @classmethod
    def from_text(cls, text: str) -> 'Cave':
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_file(cls, fn: str) -> 'Cave':
        return cls.from_lines(open(fn))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Cave':
        depth_line, target_line = lines
        depth, = parse_line(depth_line.strip(), "depth: $")
        target_x, target_y = parse_line(target_line.strip(), "target: $,$")
        return cls(depth=int(depth), target_pos=(int(target_x), int(target_y)))


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    cave = Cave.from_file(input_path)
    result_1 = part_1(cave)
    result_2 = part_2(cave)
    return result_1, result_2


if __name__ == '__main__':
    main()
