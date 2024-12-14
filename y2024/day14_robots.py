"""
Advent of Code 2024
Day 14: Restroom Redoubt
https://adventofcode.com/2024/day/14
"""

from collections import Counter
from itertools import count
from math import prod
from typing import Iterable, Self

from common.canvas import Canvas
from common.file import relative_path
from common.iteration import first_repeat
from common.rect import Rect
from common.text import parse_line
from common.xy import Point, Vector


def part_1(robots: 'Robots', seconds: int = 100) -> int:
    """
    One of The Historians needs to use the bathroom; fortunately, you know there's a bathroom near
    an unvisited location on their list, and so you're all quickly teleported directly to the lobby
    of Easter Bunny Headquarters.

    Unfortunately, EBHQ seems to have "improved" bathroom security **again** after your last visit
    (y2016/day02_keypad.py). The area outside the bathroom is swarming with robots!

    To get The Historian safely to the bathroom, you'll need a way to predict where the robots will
    be in the future. Fortunately, they all seem to be moving on the tile floor in predictable
    **straight lines**.

    You make a list (your puzzle input) of all of the robots' current **positions** (`p`) and
    **velocities** (`v`), one robot per line. For example:

        >>> example = Robots.from_text('''
        ...     p=0,4 v=3,-3
        ...     p=6,3 v=-1,-3
        ...     p=10,3 v=-1,2
        ...     p=2,0 v=2,-1
        ...     p=0,0 v=1,3
        ...     p=3,0 v=-2,-2
        ...     p=7,6 v=-1,-3
        ...     p=3,0 v=-1,-2
        ...     p=9,3 v=2,3
        ...     p=7,3 v=-1,2
        ...     p=2,4 v=2,-3
        ...     p=9,5 v=-3,-3
        ... ''')
        >>> example.robots  # doctest: +ELLIPSIS
        [(Point(0, 4), Vector(3, -3)), (Point(6, 3), Vector(-1, -3)), ...]
        >>> len(example.robots)
        12

    Each robot's position is given as `p=x,y` where `x` represents the number of tiles the robot is
    from the left wall and `y` represents the number of tiles from the top wall (when viewed from
    above). So, a position of `p=0,0` means the robot is all the way in the top-left corner.

    Each robot's velocity is given as `v=x,y` where `x` and `y` are given in **tiles per second**.
    Positive `x` means the robot is moving to the **right**, and positive `y` means the robot is
    moving **down**. So, a velocity of `v=1,-2` means that each second, the robot moves `1` tile to
    the right and `2` tiles up.

    The robots outside the actual bathroom are in a space which is `101` tiles wide and `103` tiles
    tall (when viewed from above). However, in this example, the robots are in a space which is only
    `11` tiles wide and `7` tiles tall.

        >>> smaller_bounds = Rect.at_origin(width=11, height=7)
        >>> example.bounds = smaller_bounds

    The robots are good at navigating over/under each other (due to a combination of springs,
    extendable legs, and quadcopters), so they can share the same tile and don't interact with each
    other. Visually, the number of robots on each tile in this example looks like this:

        >>> example.print()
        1·12·······
        ···········
        ···········
        ······11·11
        1·1········
        ·········1·
        ·······1···

    These robots have a unique feature for maximum bathroom security: they can **teleport**. When
    a robot would run into an edge of the space they're in, they instead **teleport to the other
    side**, effectively wrapping around the edges. Here is what robot `p=2,4 v=2,-3` does for
    the first few seconds:

        >>> (robot_10 := example.robots[10])
        (Point(2, 4), Vector(2, -3))
        >>> Robots([robot_10], smaller_bounds).print_movement(seconds=range(6))
        Initial state:
        ···········
        ···········
        ···········
        ···········
        ··1········
        ···········
        ···········
        After 1 second:
        ···········
        ····1······
        ···········
        ···········
        ···········
        ···········
        ···········
        After 2 seconds:
        ···········
        ···········
        ···········
        ···········
        ···········
        ······1····
        ···········
        After 3 seconds:
        ···········
        ···········
        ········1··
        ···········
        ···········
        ···········
        ···········
        After 4 seconds:
        ···········
        ···········
        ···········
        ···········
        ···········
        ···········
        ··········1
        After 5 seconds:
        ···········
        ···········
        ···········
        ·1·········
        ···········
        ···········
        ···········

    The Historian can't wait much longer, so you don't have to simulate the robots for very long.
    Where will the robots be after `100` seconds?

    In the above example, the number of robots on each tile after 100 seconds has elapsed looks like
    this:

        >>> example.print(after_seconds=100)
        ······2··1·
        ···········
        1··········
        ·11········
        ·····1·····
        ···12······
        ·1····1····

    To determine the safest area, count the **number of robots in each quadrant** after 100 seconds.
    Robots that are exactly in the middle (horizontally or vertically) don't count as being in any
    quadrant, so the only relevant robots are:

        >>> example.print(after_seconds=100, quadrants=True)
        ·····|2··1·
        ·····|·····
        1····|·····
        -----+-----
        ·····|·····
        ···12|·····
        ·1···|1····

    In this example, the quadrants contain `1`, `3`, `4`, and `1` robot:

        >>> example.quadrants_counts(after_seconds=100)
        [1, 3, 4, 1]

    Multiplying these together gives a total **safety factor** of **`12`**:

        >>> example.safety_factor(after_seconds=100)
        12

    Predict the motion of the robots in your list within a space which is `101` tiles wide and `103`
    tiles tall. **What will the safety factor be after exactly `100` seconds have elapsed?**

        >>> part_1(example)
        part 1: after 100 seconds, the safety factor will be 12
        12
    """

    result = robots.safety_factor(seconds)

    print(f"part 1: after {seconds} seconds, the safety factor will be {result}")
    return result


def part_2(robots: 'Robots', draw_result: bool = False) -> int:
    """
    During the bathroom break, someone notices that these robots seem awfully similar to ones built
    and used at the North Pole. If they're the same type of robots, they should have a hard-coded
    Easter egg: very rarely, most of the robots should arrange themselves into **a picture of
    a Christmas tree**.

    **What is the fewest number of seconds that must elapse for the robots
    to display the Easter egg?**
    """

    result = robots.find_christmas_tree()

    print(f"part 2: a Christmas tree picture appears after {result} seconds")
    if draw_result:
        robots.print(result)

    return result


Robot = tuple[Point, Vector]
DEFAULT_BOUNDS = Rect.at_origin(width=101, height=103)


class Robots:
    def __init__(self, robots: Iterable[Robot], bounds: Rect = DEFAULT_BOUNDS):
        self.robots = list(robots)
        self.bounds = bounds
        assert all(pos in self.bounds for pos, _ in self.robots)

    def robot_positions(self, after_seconds: int) -> Iterable[Point]:
        for pos, vel in self.robots:
            yield Point(
                x=self.bounds.left_x + (pos.x + vel.x * after_seconds) % self.bounds.width,
                y=self.bounds.top_y + (pos.y + vel.y * after_seconds) % self.bounds.height,
            )

    def quadrants_counts(self, after_seconds: int) -> list[int]:
        middle = self.middle_point()

        def quadrant(pos: Point) -> int | None:
            if pos.x == middle.x or pos.y == middle.y:
                return None
            return (pos.x > middle.x) + 2 * (pos.y > middle.y)

        counter = Counter(
            q
            for pos in self.robot_positions(after_seconds)
            if (q := quadrant(pos)) is not None
        )

        return [counter[q] for q in range(4)]

    def middle_point(self) -> Point:
        assert self.bounds.width % 2 == 1
        assert self.bounds.height % 2 == 1
        return Point(
            x=self.bounds.left_x + self.bounds.width // 2,
            y=self.bounds.top_y + self.bounds.height // 2,
        )

    def safety_factor(self, after_seconds: int) -> int:
        return prod(self.quadrants_counts(after_seconds))

    def find_christmas_tree(self) -> int:
        """
        Returns second when all the robots form a "Christmas tree" pattern

        This can be done using several methods:

           1. min safety: find the configuration with the lowest safety factor in given interval
           2. detection of vertical lines
           3. first image where no two robots overlap

        The method number 3 is quite fast and easy to implement:
        """

        try:
            return next(
                second
                for second in count()
                # no position is repeated -> not two robots overlap
                if first_repeat(self.robot_positions(second)) is None
            )
        except StopIteration as stop:
            raise ValueError("no christmas tree found :(") from stop

    def print(self, after_seconds: int = 0, quadrants: bool = False) -> None:
        canvas = Canvas(bounds=self.bounds)
        canvas.draw_many(
            chars=((pos, '1') for pos in self.robot_positions(after_seconds)),
            blending=lambda cur, new: str(int(cur) + int(new))[-1],
        )

        if quadrants:
            middle = self.middle_point()
            canvas.draw_many(
                chars=(((middle.x, y), '|') for y in self.bounds.range_y()),
            )
            canvas.draw_many(
                chars=(((x, middle.y), '-') for x in self.bounds.range_x()),
                blending=lambda cur, new: '+' if cur == '|' else None
            )

        canvas.print(empty_char='·')

    def print_movement(self, seconds: Iterable[int]) -> None:
        # only used in doctests
        for second in seconds:
            if second == 0:
                print("Initial state:")
            elif second == 1:
                print("After 1 second:")
            else:
                print(f"After {second} seconds:")

            self.print(second)

    @classmethod
    def from_file(cls, fn: str, bounds: Rect = DEFAULT_BOUNDS) -> Self:
        return cls.from_lines(open(relative_path(__file__, fn)), bounds)

    @classmethod
    def from_text(cls, text: str, bounds: Rect = DEFAULT_BOUNDS) -> Self:
        return cls.from_lines(text.strip().splitlines(), bounds)

    @classmethod
    def from_lines(cls, lines: Iterable[str], bounds: Rect) -> Self:
        def robots() -> Iterable[Robot]:
            for line in lines:
                # p=10,3 v=-1,2
                p_x, p_y, v_x, v_y = parse_line(line.strip(), 'p=$,$ v=$,$')
                yield Point(p_x, p_y), Vector(v_x, v_y)

        return cls(robots(), bounds)


def main(input_fn: str = 'data/14-input.txt') -> tuple[int, int]:
    robots = Robots.from_file(input_fn)
    result_1 = part_1(robots)
    result_2 = part_2(robots)
    return result_1, result_2


if __name__ == '__main__':
    main()
