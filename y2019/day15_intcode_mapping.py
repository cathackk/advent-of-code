"""
Advent of Code 2019
Day 15: Oxygen System
https://adventofcode.com/2019/day/15
"""

from enum import Enum
from typing import Callable, Iterable

from tqdm import tqdm

from common.heading import Heading
from common.rect import Rect
from meta.aoc_tools import data_path
from y2019.intcode import load_tape, Machine, Tape


def part_1(sensor: 'Sensor') -> int:
    """
    Out here in deep space, many things can go wrong. Fortunately, many of those things have
    indicator lights. Unfortunately, one of those lights is lit: the oxygen system for part of the
    ship has failed!

    According to the readouts, the oxygen system must have failed days ago after a rupture in oxygen
    tank two; that section of the ship was automatically sealed once oxygen levels went dangerously
    low. A single remotely-operated **repair droid** is your only option for fixing the oxygen
    system.

    The Elves' care package included an Intcode program (your puzzle input) that you can use to
    remotely control the repair droid. By running that program, you can direct the repair droid to
    the oxygen system and fix the problem.

    The remote control program executes the following steps in a loop forever:

      - Accept a **movement command** via an input instruction.
      - Send the movement command to the repair droid.
      - Wait for the repair droid to finish the movement operation.
      - Report on the **status** of the repair droid via an output instruction.

    Only four **movement commands** are understood:

        >>> HEADING_CODES
        {Heading.NORTH: 1, Heading.SOUTH: 2, Heading.WEST: 3, Heading.EAST: 4}

    Any other command is invalid. The movements differ in direction, but not in distance: in a long
    enough east-west hallway, a series of commands like `4,4,4,4,3,3,3,3` would leave the repair
    droid back where it started.

    The repair droid can reply with any of the following **status codes**:

      - `0`: The repair droid hit a wall. Its position has not changed.
      - `1`: The repair droid has moved one step in the requested direction.
      - `2`: The repair droid has moved one step in the requested direction; its new position is
             the location of the oxygen system.

    You don't know anything about the area around the repair droid, but you can figure it out by
    watching the status codes.

    For example, we can draw the area using `D` for the droid, `█` for walls, `·` for locations the
    droid can traverse, `<`, for the starting position, and `░` for unexplored locations. Then, the
    initial state looks like this:


        >>> dr = Droid(dummy_sensor())
        >>> dr.draw_plan(region := Rect((-3, -2), (2, 2)))
        ░░░░░░
        ░░░░░░
        ░░░D░░
        ░░░░░░
        ░░░░░░

    To make the droid go north, send it `1`. If it replies with `0`, you know that location is
    a wall and that the droid didn't move:

        >>> dr.move(Heading.NORTH)
        Tile.WALL
        >>> dr.draw_plan(region)
        ░░░░░░
        ░░░█░░
        ░░░D░░
        ░░░░░░
        ░░░░░░

    To move east, send `4`; a reply of `1` means the movement was successful:

        >>> dr.move(Heading.EAST)
        Tile.FLOOR
        >>> dr.draw_plan(region)
        ░░░░░░
        ░░░█░░
        ░░░<D░
        ░░░░░░
        ░░░░░░

    Then, perhaps attempts to move north, south, and east are all met with replies of `0`:

        >>> dr.move(Heading.NORTH)
        Tile.WALL
        >>> dr.move(Heading.SOUTH)
        Tile.WALL
        >>> dr.move(Heading.EAST)
        Tile.WALL
        >>> dr.draw_plan(region)
        ░░░░░░
        ░░░██░
        ░░░<D█
        ░░░░█░
        ░░░░░░

    Now, you know the repair droid is in a dead end. Backtrack with `3` (which you already know will
    get a reply of `1` because you already know that location is open):

        >>> dr.move(Heading.WEST)
        Tile.FLOOR
        >>> dr.draw_plan(region)
        ░░░░░░
        ░░░██░
        ░░░D·█
        ░░░░█░
        ░░░░░░

    Then, perhaps west gets a reply of `0`, south gets a reply of `1`, south again gets a reply of
    `0`, and then west gets a reply of `2`:

        >>> dr.move(Heading.WEST)
        Tile.WALL
        >>> dr.move(Heading.SOUTH)
        Tile.FLOOR
        >>> dr.move(Heading.SOUTH)
        Tile.WALL
        >>> dr.move(Heading.WEST)
        Tile.OXYGEN
        >>> dr.draw_plan(region)
        ░░░░░░
        ░░░██░
        ░░█<·█
        ░░D·█░
        ░░░█░░

    Now, because of the reply of `2`, you know you've found the **oxygen system**! In this example,
    it was only **2** moves away from the repair droid's starting position.

        >>> dr.current_distance()
        2

    **What is the fewest number of movement commands** required to move the repair droid from its
    starting position to the location of the oxygen system?

        >>> part_1(dummy_sensor())
        part 1: oxygen can be reached in 2 steps
        2
    """

    result = Droid(sensor).find_oxygen()

    print(f"part 1: oxygen can be reached in {result} steps")
    return result


def part_2(sensor: 'Sensor') -> int:
    """
    You quickly repair the oxygen system; oxygen gradually fills the area.

    Oxygen starts in the location containing the repaired oxygen system. It takes **one minute** for
    oxygen to spread to all open locations that are adjacent to a location that already contains
    oxygen. Diagonal locations are **not** adjacent.

    In the example above, suppose you've used the droid to explore the area fully and have the
    following map (where locations that currently contain oxygen are marked `O`):

        >>> dr = Droid(dummy_sensor())
        >>> plan = dr.fully_explore()
        >>> draw_plan(plan)
        ░██░░░
        █··██░
        █·█··█
        █·O·█░
        ░███░░

    Initially, the only location which contains oxygen is the location of the repaired oxygen
    system. However, after one minute, the oxygen spreads to all open (`·`) locations that are
    adjacent to a location containing oxygen:

        >>> draw_plan(plan_1 := spread_oxygen(plan))
        ░██░░░
        █··██░
        █·█··█
        █OOO█░
        ░███░░

    After a total of two minutes, the map looks like this:

        >>> draw_plan(plan_2 := spread_oxygen(plan_1))
        ░██░░░
        █··██░
        █O█O·█
        █OOO█░
        ░███░░

    After a total of three minutes:

        >>> draw_plan(plan_3 := spread_oxygen(plan_2))
        ░██░░░
        █O·██░
        █O█OO█
        █OOO█░
        ░███░░

    And finally, the whole region is full of oxygen after a total of four minutes:

        >>> draw_plan(spread_oxygen(plan_3))
        ░██░░░
        █OO██░
        █O█OO█
        █OOO█░
        ░███░░

    So, in this example, all locations contain oxygen after **4** minutes.

        >>> oxygen_refill_duration(plan)
        4

    Use the repair droid to get a complete map of the area.
    **How many minutes will it take to fill with oxygen?**

        >>> part_2(dummy_sensor())
        part 2: it takes 4 minutes to fill the area with oxygen
        4
    """

    result = oxygen_refill_duration(Droid(sensor).fully_explore())

    print(f"part 2: it takes {result} minutes to fill the area with oxygen")
    return result


class Tile(Enum):
    WALL = 0
    FLOOR = 1
    OXYGEN = 2

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'

    def __bool__(self) -> bool:
        return bool(self.value)


class Drawing:
    WALL = '█'
    FLOOR = '·'
    OXYGEN = 'O'
    DROID = 'D'
    UNKNOWN = '░'
    ORIGIN = '<'

    @classmethod
    def for_tile(cls, tile: Tile) -> str:
        match tile:
            case Tile.WALL:
                return cls.WALL
            case Tile.FLOOR:
                return cls.FLOOR
            case Tile.OXYGEN:
                return cls.OXYGEN
            case _:
                raise ValueError(tile)


HEADING_CODES = {
    Heading.NORTH: 1,
    Heading.SOUTH: 2,
    Heading.WEST: 3,
    Heading.EAST: 4,
}


Pos = tuple[int, int]
Plan = dict[Pos, Tile]
Sensor = Callable[[Heading], Tile]


class Droid:
    def __init__(self, sensor: Sensor, origin: Pos = (0, 0)):
        self.sensor = sensor

        self.current_pos = origin
        self.origin = origin

        self.plan: Plan = {origin: Tile.FLOOR}
        self.distances: dict[Pos, int] = {origin: 0}

    def move(self, direction: Heading) -> Tile:
        tile_detected = self.sensor(direction)

        new_position = direction.move(self.current_pos)
        self.plan[new_position] = tile_detected

        if tile_detected is not Tile.WALL:
            if new_position not in self.distances:
                # assumes there are no loops in the maze!
                self.distances[new_position] = self.distances[self.current_pos] + 1
            self.current_pos = new_position

        return tile_detected

    def current_distance(self) -> int:
        return self.distances[self.current_pos]

    def find_oxygen(self) -> int:
        # traverse through the maze, always tracing the left wall
        # (assumes there are no loops and that no large rooms)

        progress = tqdm(desc="finding oxygen", unit=" steps", delay=1.0)

        # first go north as long as you can until you run into a wall
        direction = Heading.NORTH
        while self.move(direction):
            progress.update()

        # now that there's a wall in the north, turn right to east, and follow the left wall
        while True:
            progress.update()
            match self.move(direction):
                case Tile.WALL:
                    direction = direction.right()
                case Tile.FLOOR:
                    direction = direction.left()
                case Tile.OXYGEN:
                    return self.current_distance()

    def fully_explore(self) -> Plan:
        # similar to find_oxygen(), but don't stop at oxygen,
        # (stop when you're back where you started)

        progress = tqdm(desc="exploring", unit=" steps", delay=1.0)

        direction = Heading.NORTH
        while self.move(direction):
            progress.update()

        start_standing = self.current_pos, direction
        while True:
            progress.update()
            if self.move(direction):
                direction = direction.left()
            else:
                direction = direction.right()
            if (self.current_pos, direction) == start_standing:
                return self.plan

    def draw_plan(self, bounds: Rect = None) -> None:
        draw_plan(
            plan=self.plan,
            bounds=bounds,
            overlay={self.origin: Drawing.ORIGIN, self.current_pos: Drawing.DROID},
        )


def spread_oxygen(plan: Plan) -> Plan:
    return plan | {
        npos: Tile.OXYGEN
        for pos, tile in plan.items()
        if tile is Tile.OXYGEN
        for direction in Heading
        if plan[npos := direction.move(pos)] is Tile.FLOOR
    }


def oxygen_refill_duration(plan: Plan) -> int:
    # flood plan with oxygen, return number of steps needed

    total_floors = sum(1 for tile in plan.values() if tile)
    progress = tqdm(desc="filling with oxygen", unit=" tiles", total=total_floors, delay=1.0)
    minutes = 0
    prev_oxygen = 0

    while True:
        oxygen = sum(1 for tile in plan.values() if tile is Tile.OXYGEN)
        progress.update(oxygen - prev_oxygen)
        prev_oxygen = oxygen
        if oxygen >= total_floors:
            return minutes

        plan = spread_oxygen(plan)
        minutes += 1


def draw_plan(plan: Plan, bounds: Rect = None, overlay: dict[Pos, str] = None) -> None:
    if bounds is None:
        bounds = Rect.with_all(plan)

    def char(pos: Pos) -> str:
        if overlay and pos in overlay:
            return overlay[pos]
        if pos not in plan:
            return Drawing.UNKNOWN
        return Drawing.for_tile(plan[pos])

    for y in bounds.range_y():
        print(''.join(char((x, y)) for x in bounds.range_x()))


def dummy_sensor() -> Sensor:
    class TestSensor:
        """for testing only"""

        def __init__(self, floors: Iterable[Pos], oxygen: Pos):
            self.floors = set(floors)
            self.oxygen = oxygen
            self.current_pos = (0, 0)

        def __call__(self, direction: Heading) -> Tile:
            new_pos = direction.move(self.current_pos)
            if new_pos in self.floors:
                self.current_pos = new_pos
                return Tile.OXYGEN if new_pos == self.oxygen else Tile.FLOOR
            else:
                return Tile.WALL

    return TestSensor(
        # test map:
        # ░██░░░
        # █··██░
        # █·█<·█
        # █·O·█░
        # ░███░░
        floors=[(0, 0), (1, 0), (0, 1), (-1, 1), (-2, 1), (-2, 0), (-2, -1), (-1, -1)],
        oxygen=(-1, 1),
    )


def sensor_from_tape(tape: Tape) -> Sensor:
    raw_func = Machine(tape).as_function_scalar()

    def sensor(heading: Heading) -> Tile:
        return Tile(raw_func(HEADING_CODES[heading]))

    return sensor


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    tape = load_tape(input_path)
    result_1 = part_1(sensor_from_tape(tape))
    result_2 = part_2(sensor_from_tape(tape))
    return result_1, result_2


if __name__ == '__main__':
    main()
