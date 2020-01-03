from collections import defaultdict
from enum import Enum
from typing import Dict
from typing import Tuple

from utils import minmax
from xy import Point
from xy import Vector
from y2019.machine import load_tape
from y2019.machine import Machine


class Color(Enum):
    BLACK = 0
    WHITE = 1
    NONE = 99

    def __bool__(self):
        return self != Color.NONE


class Direction(Enum):
    LEFT = 0
    RIGHT = 1


class Heading(Enum):
    NORTH = Vector(0, -1)
    EAST = Vector(1, 0)
    SOUTH = Vector(0, 1)
    WEST = Vector(-1, 0)

    def __init__(self, vector: Vector):
        self.vector = vector

    def turned(self, direction: Direction) -> 'Heading':
        if direction == Direction.LEFT:
            return self.turned_left()
        elif direction == Direction.RIGHT:
            return self.turned_right()

    def turned_right(self) -> 'Heading':
        return {
            Heading.NORTH: Heading.EAST,
            Heading.EAST: Heading.SOUTH,
            Heading.SOUTH: Heading.WEST,
            Heading.WEST: Heading.NORTH
        }[self]

    def turned_left(self) -> 'Heading':
        return {
            Heading.NORTH: Heading.WEST,
            Heading.EAST: Heading.NORTH,
            Heading.SOUTH: Heading.EAST,
            Heading.WEST: Heading.SOUTH
        }[self]


Grid = Dict[Point, Color]


class Robot:
    def __init__(self, machine: Machine, debug: bool = False):
        self.brain = machine.as_function()
        self.pos = Point(0, 0)
        self.heading = Heading.NORTH
        self.debug = debug

    def log(self, message=""):
        if self.debug:
            print(message)

    def evaluate_tile(self, color_seen: Color) -> Tuple[Color, Direction]:
        color_to_paint, direction_to_turn = self.brain(color_seen.value)
        return Color(color_to_paint), Direction(direction_to_turn)

    def paint_on(self, grid: Grid):
        cycle = 0
        try:
            while True:
                cycle += 1
                color_seen = grid[self.pos]
                self.log(
                    f"[T={cycle}] pos={self.pos}, head={self.heading.name}: "
                    f"sees color {color_seen.name}"
                )

                if not color_seen:
                    color_seen = Color.BLACK

                color_to_paint, direction_to_turn = self.evaluate_tile(color_seen)

                # 1. paint
                grid[self.pos] = color_to_paint
                self.log(f">> paints {color_to_paint} to {self.pos}")
                # 2. turn
                self.heading = self.heading.turned(direction_to_turn)
                self.log(f">> turns {direction_to_turn} -> {self.heading}")
                # 3. move
                self.pos += self.heading.vector
                self.log(f">> moves {self.heading} to {self.pos}")
                self.log()
                # draw_grid(grid)
                self.log()

        except StopIteration:
            return


def draw_grid(grid: Grid):
    min_x, max_x = minmax(pos.x for pos in grid.keys())
    min_y, max_y = minmax(pos.y for pos in grid.keys())
    c = {
        Color.BLACK: '.',
        Color.WHITE: '#',
        Color.NONE: ' '
    }
    for y in range(min_y, max_y+1):
        print(''.join(c[grid[Point(x, y)]] for x in range(min_x, max_x+1)))


def part_1():
    robot = Robot(Machine(load_tape('data/11-program.txt')), debug=False)
    grid = defaultdict(lambda: Color.NONE)
    robot.paint_on(grid)
    draw_grid(grid)
    count = sum(1 for color in grid.values() if color)
    print(f"painted on {count} cells")


def part_2():
    robot = Robot(Machine(load_tape('data/11-program.txt')), debug=False)
    grid2 = defaultdict(lambda: Color.NONE)
    grid2[Point(0, 0)] = Color.WHITE
    robot.paint_on(grid2)
    draw_grid(grid2)


if __name__ == '__main__':
    part_1()
    part_2()
