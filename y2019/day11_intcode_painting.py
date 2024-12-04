"""
Advent of Code 2019
Day 11: Space Police
https://adventofcode.com/2019/day/11
"""

from enum import Enum
from typing import Self

from common import ocr
from common.heading import Heading
from common.rect import Rect
from meta.aoc_tools import data_path
from y2019.intcode import load_tape, Machine, Tape


def part_1(tape: Tape) -> int:
    """
    On the way to Jupiter, you're pulled over by the **Space Police**.

    "Attention, unmarked spacecraft! You are in violation of Space Law! All spacecraft must have
    a clearly visible **registration identifier**! You have 24 hours to comply or be sent to Space
    Jail!"

    Not wanting to be sent to Space Jail, you radio back to the Elves on Earth for help. Although it
    takes almost three hours for their reply signal to reach you, they send instructions for how to
    power up the **emergency hull painting robot** and even provide a small Intcode program (your
    puzzle input) that will cause it to paint your ship appropriately.

    There's just one problem: you don't have an emergency hull painting robot.

    You'll need to build a new emergency hull painting robot. The robot needs to be able to move
    around on the grid of square panels on the side of your ship, detect the color of its current
    panel, and paint its current panel **black** or **white**. (All of the panels are currently
    **black**.)

    The Intcode program will serve as the brain of the robot. The program uses input instructions to
    access the robot's camera: provide `0` if the robot is over a **black** panel or `1` if the
    robot is over a **white** panel. Then, the program will output two values:

      - First, it will output a value indicating the **color to paint the panel** the robot is over:
        `0` means to paint the panel **black**, and `1` means to paint the panel **white**.
      - Second, it will output a value indicating the **direction the robot should turn**: `0` means
        it should turn **left 90 degrees**, and `1` means it should turn **right 90 degrees**.

    After the robot turns, it should always move **forward exactly one panel**. The robot starts
    facing **up**.

    The robot will continue running for a while like this and halt when it is finished drawing. Do
    not restart the Intcode computer inside the robot during this process.

    For example, suppose the robot is about to start running. Drawing black panels as `·`, white
    panels as `#`, and the robot pointing the direction it is facing (`< ^ > v`), the initial state
    and region near the robot looks like this:

        >>> rob = Robot()
        >>> rob.draw_grid(region := Rect((-2, -2), (2, 2)))
        ·····
        ·····
        ··^··
        ·····
        ·····

    The panel under the robot (not visible here because a `^` is shown instead) is also black, and
    so any input instructions at this point should be provided `0`.

        >>> rob.current_color()
        Color.BLACK

    Suppose the robot eventually outputs `1` (paint white) and then `0` (turn left). After taking
    these actions and moving forward one panel, the region now looks like this:

        >>> rob.make_step(Color.WHITE, Direction.LEFT)
        >>> rob.draw_grid(region)
        ·····
        ·····
        ·<#··
        ·····
        ·····

    Input instructions should still be provided `0`. Next, the robot might output `0` (paint black)
    and then `0` (turn left):

        >>> rob.make_step(Color.BLACK, Direction.LEFT)
        >>> rob.draw_grid(region)
        ·····
        ·····
        ··#··
        ·v···
        ·····

    After more outputs (`1,0`, `1,0`):

        >>> rob.make_step(Color.WHITE, Direction.LEFT)
        >>> rob.make_step(Color.WHITE, Direction.LEFT)
        >>> rob.draw_grid(region)
        ·····
        ·····
        ··^··
        ·##··
        ·····

    The robot is now back where it started, but because it is now on a white panel, input
    instructions should be provided `1`.

        >>> rob.current_color()
        Color.WHITE

    After several more outputs (`0,1`, `1,0`, `1,0`), the area looks like this:

        >>> rob.make_step(Color.BLACK, Direction.RIGHT)
        >>> rob.make_step(Color.WHITE, Direction.LEFT)
        >>> rob.make_step(Color.WHITE, Direction.LEFT)
        >>> rob.draw_grid(region)
        ·····
        ··<#·
        ···#·
        ·##··
        ·····

    Before you deploy the robot, you should probably have an estimate of the area it will cover:
    specifically, you need to know the **number of panels it paints at least once**, regardless of
    color. In the example above, the robot painted **6 panels** at least once. (It painted its
    starting panel twice, but that panel is still only counted once; it also never painted the panel
    it ended on.)

        >>> len(rob.grid)
        6

    Build a new emergency hull painting robot and run the Intcode program on it.
    **How many panels does it paint at least once?**

        >>> example_steps = [(1, 0), (0, 0), (1, 0), (1, 0), (0, 1), (1, 0), (1, 0)]
        >>> example_tape = [v for c, d in example_steps for v in [3, 1, 104, c, 104, d]] + [99]
        >>> part_1(example_tape)
        part 1: robot painted total 6 panels
        6
    """

    result = len(Robot().run(tape).grid)

    print(f"part 1: robot painted total {result} panels")
    return result


def part_2(tape: Tape) -> str:
    """
    You're not sure what it's trying to paint, but it's definitely not a **registration
    identifier**. The Space Police are getting impatient.

    Checking your external ship cameras again, you notice a white panel marked "emergency hull
    painting robot starting panel". The rest of the panels are **still black**, but it looks like
    the robot was expecting to **start on a white panel**, not a black one.

    Based on the Space Law Space Brochure that the Space Police attached to one of your windows,
    a valid registration identifier is always **eight capital letters**. After starting the robot on
    a single **white panel** instead, **what registration identifier does it paint** on your hull?
    """

    painting = render_grid(Robot({(0, 0): Color.WHITE}).run(tape).grid, char_black=' ')
    # print(painting)
    result = ocr.FONT_6X5.read_string(painting)

    print(f"part 2: robot painted message {result}")
    return result


class Color(Enum):
    BLACK = 0
    WHITE = 1

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class Direction(Enum):
    LEFT = 0
    RIGHT = 1

    def turn(self, heading: Heading) -> Heading:
        if self is Direction.LEFT:
            return heading.left()
        elif self is Direction.RIGHT:
            return heading.right()
        else:
            raise ValueError(self)


Pos = tuple[int, int]
Grid = dict[Pos, Color]


class Robot:
    def __init__(self, grid: Grid = None):
        self.grid = grid or {}
        self.pos = (0, 0)
        self.heading = Heading.NORTH

    def current_color(self) -> Color:
        return self.grid.get(self.pos, Color.BLACK)

    def make_step(self, color_to_paint: Color, direction_to_turn: Direction) -> None:
        # 1. paint
        self.grid[self.pos] = color_to_paint
        # 2. turn
        self.heading = direction_to_turn.turn(self.heading)
        # 3. move
        self.pos = self.heading.move(self.pos)

    def run(self, tape: Tape) -> Self:

        raw_func = Machine(tape).as_function()

        def paint_logic(color_seen: Color) -> tuple[Color, Direction]:
            color_to_paint, direction_to_turn = raw_func(color_seen.value)
            return Color(color_to_paint), Direction(direction_to_turn)

        try:
            while True:
                self.make_step(*paint_logic(self.current_color()))

        except StopIteration:
            return self

    def draw_grid(self, bounds: Rect = None) -> None:
        print(render_grid(self.grid, bounds, overlay={self.pos: self.heading.caret}))


def render_grid(
    grid: Grid,
    bounds: Rect = None,
    overlay: dict[Pos, str] = None,
    char_black: str = '·',
    char_white: str = '#',
    char_empty: str = None,
) -> str:
    if bounds is None:
        bounds = Rect.with_all(grid)

    color_to_char = {
        Color.BLACK: char_black,
        Color.WHITE: char_white,
        None: char_empty or char_black,
    }

    def char(pos: Pos) -> str:
        if overlay and pos in overlay:
            return overlay[pos]
        return color_to_char[grid.get(pos)]

    return "\n".join(
        "".join(char((x, y)) for x in bounds.range_x())
        for y in bounds.range_y()
    )


def main(input_path: str = data_path(__file__)) -> tuple[int, str]:
    tape = load_tape(input_path)
    result_1 = part_1(tape)
    result_2 = part_2(tape)
    return result_1, result_2


if __name__ == '__main__':
    main()
