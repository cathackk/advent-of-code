"""
Advent of Code 2023
Day 17: Clumsy Crucible
https://adventofcode.com/2023/day/17
"""

from dataclasses import dataclass
from typing import Iterable, Self

from common.file import relative_path
from common.graph import shortest_path
from common.heading import Heading
from common.rect import Rect


def part_1(map_: 'Map') -> int:
    """
    The lava starts flowing rapidly once the Lava Production Facility is operational. As you leave,
    the reindeer offers you a parachute, allowing you to quickly reach Gear Island.

    As you descend, your bird's-eye view of Gear Island reveals why you had trouble finding anyone
    on your way up: half of Gear Island is empty, but the half below you is a giant factory city!

    You land near the gradually-filling pool of lava at the base of your new **lavafall**. Lavaducts
    will eventually carry the lava throughout the city, but to make use of it immediately, Elves are
    loading it into large crucibles on wheels.

    The crucibles are top-heavy and pushed by hand. Unfortunately, the crucibles become very
    difficult to steer at high speeds, and so it can be hard to go in a straight line for very long.

    To get Desert Island the machine parts it needs as soon as possible, you'll need to find the
    best way to get the crucible **from the lava pool to the machine parts factory**. To do this,
    you need to minimize **heat loss** while choosing a route that doesn't require the crucible to
    go in a **straight line** for too long.

    Fortunately, the Elves here have a map (your puzzle input) that uses traffic patterns, ambient
    temperature, and hundreds of other parameters to calculate exactly how much heat loss can be
    expected for a crucible entering any particular city block.

    For example:

        >>> example_map = Map.from_text('''
        ...     2413432311323
        ...     3215453535623
        ...     3255245654254
        ...     3446585845452
        ...     4546657867536
        ...     1438598798454
        ...     4457876987766
        ...     3637877979653
        ...     4654967986887
        ...     4564679986453
        ...     1224686865563
        ...     2546548887735
        ...     4322674655533
        ... ''')

    Each city block is marked by a single digit that represents the **amount of heat loss if the
    crucible enters that block**. The starting point, the lava pool, is the top-left city block;
    the destination, the machine parts factory, is the bottom-right city block. (Because you already
    start in the top-left block, you don't incur that block's heat loss unless you leave that block
    and then return to it.)

    Because it is difficult to keep the top-heavy crucible going in a straight line for very long,
    it can move **at most three blocks** in a single direction before it must turn 90 degrees left
    or right. The crucible also can't reverse direction; after entering each city block, it may only
    turn left, continue straight, or turn right.

    One way to minimize **heat loss** is this path:

        >>> example_cost, example_path = minimize_heat_loss(example_map)
        >>> draw_path(example_map, example_path)
        2>>34^>>>1323
        32v>>>35v5623
        32552456v>>54
        3446585845v52
        4546657867v>6
        14385987984v4
        44578769877v6
        36378779796v>
        465496798688v
        456467998645v
        12246868655<v
        25465488877v5
        43226746555v>

    This path never moves more than three consecutive blocks in the same direction and incurs a heat
    loss of only **`102`**:

        >>> example_cost
        102

    Directing the crucible from the lava pool to the machine parts factory, but not moving more than
    three consecutive blocks in the same direction, **what is the least heat loss it can incur?**

        >>> part_1(example_map)
        part 1: minimal heat loss is 102
        102
    """

    result, _ = minimize_heat_loss(map_)

    print(f"part 1: minimal heat loss is {result}")
    return result


def part_2(map_: 'Map') -> int:
    """
    The crucibles of lava simply aren't large enough to provide an adequate supply of lava to
    the machine parts factory. Instead, the Elves are going to upgrade to **ultra crucibles**.

    Ultra crucibles are even more difficult to steer than normal crucibles. Not only do they have
    trouble going in a straight line, but they also have trouble turning!

    Once an ultra crucible starts moving in a direction, it needs to move **a minimum of four
    blocks** in that direction before it can turn (or even before it can stop at the end). However,
    it will eventually start to get wobbly: ultra crucible can move a maximum of **ten consecutive
    blocks** without turning.

    In the above example, an ultra crucible could follow this path to minimize heat loss:

        >>> example_map_1 = Map.from_file('data/17-example.txt')
        >>> cost_1, path_1 = minimize_heat_loss(example_map_1, ultra=True)
        >>> draw_path(example_map_1, path_1)
        2>>>>>>>>1323
        32154535v5623
        32552456v4254
        34465858v5452
        45466578v>>>>
        143859879845v
        445787698776v
        363787797965v
        465496798688v
        456467998645v
        122468686556v
        254654888773v
        432267465553v
        >>> cost_1
        94

    Here's another example:

        >>> example_map_2 = Map.from_text('''
        ...     111111111111
        ...     999999999991
        ...     999999999991
        ...     999999999991
        ...     999999999991
        ... ''')

    Sadly, an ultra crucible would need to take an unfortunate path like this one:

        >>> cost_2, path_2 = minimize_heat_loss(example_map_2, ultra=True)
        >>> draw_path(example_map_2, path_2)
        1>>>>>>>1111
        9999999v9991
        9999999v9991
        9999999v9991
        9999999v>>>>
        >>> cost_2
        71

    Directing the **ultra crucible** from the lava pool to the machine parts factory,
    **what is the least heat loss it can incur?**

        >>> part_2(example_map_1)
        part 2: minimal heat loss with ultra crucible is 94
        94
    """

    result, _ = minimize_heat_loss(map_, ultra=True)

    print(f"part 2: minimal heat loss with ultra crucible is {result}")
    return result


Pos = tuple[int, int]
Path = Iterable[Heading]


class Map:
    def __init__(self, values: Iterable[tuple[Pos, int]]):
        self.values = dict(values)
        self.bounds = Rect.with_all(self.values)
        self.start_pos = self.bounds.top_left
        self.target_pos = self.bounds.bottom_right

    def __getitem__(self, pos: Pos) -> int:
        return self.values[pos]

    def __contains__(self, pos: Pos) -> bool:
        return pos in self.bounds

    def __str__(self) -> str:
        return '\n'.join(
            ''.join(
                str(self[(x, y)])[0]
                for x in self.bounds.range_x()
            )
            for y in self.bounds.range_y()
        )

    @classmethod
    def from_file(cls, fn: str) -> Self:
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_text(cls, text: str) -> Self:
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        return cls(
            ((x, y), int(char))
            for y, line in enumerate(lines)
            for x, char in enumerate(line.strip())
        )


@dataclass(frozen=True)
class State:
    pos: Pos
    heading: Heading | None
    streak: int

    @classmethod
    def initial(cls, start_pos: Pos = (0, 0)) -> Self:
        return cls(start_pos, None, 0)

    def step(self, heading: Heading) -> Self:
        return type(self)(
            pos=heading.move(self.pos),
            heading=heading,
            streak=self.streak + 1 if heading is self.heading else 1
        )


def minimize_heat_loss(map_: Map, ultra: bool = False) -> tuple[int, Path]:
    def next_states(state: State) -> Iterable[tuple[State, Heading, int]]:
        return (
            (new_state, heading, map_[new_state.pos])
            for heading in Heading
            # cannot turn back
            if heading.opposite() is not state.heading
            # max 3 straight (ultra: max 10 straight)
            if not (state.streak >= (10 if ultra else 3) and heading is state.heading)
            # ultra: min 4 straight
            if not (ultra and 1 <= state.streak < 4 and heading is not state.heading)
            # must not leave bounds
            if (new_state := state.step(heading)).pos in map_
        )

    def is_target(state: State) -> bool:
        if ultra and state.streak < 4:
            # ultra: is stopped (streak at least 4)
            return False

        # is at the target position
        return state.pos == map_.target_pos

    return shortest_path(State.initial(map_.start_pos), is_target, next_states)


def draw_path(map_: Map, path: Path) -> None:
    canvas = {pos: str(val) for pos, val in map_.values.items()}
    bounds = map_.bounds

    pos = bounds.top_left
    for step in path:
        pos = step.move(pos)
        canvas[pos] = step.caret

    for y in bounds.range_y():
        print(''.join(canvas[(x, y)] for x in bounds.range_x()))


def main(input_fn: str = 'data/17-input.txt') -> tuple[int, int]:
    map_ = Map.from_file(input_fn)
    result_1 = part_1(map_)
    result_2 = part_2(map_)
    return result_1, result_2


if __name__ == '__main__':
    main()
