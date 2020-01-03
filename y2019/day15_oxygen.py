from enum import Enum
from typing import Callable
from typing import Optional
from typing import Tuple

from machine import load_tape
from machine import Machine
from utils import minmax
from xy import Point
from xy import Vector


class Heading(Enum):
    NORTH = (1, Vector(0, -1))
    SOUTH = (2, Vector(0, +1))
    WEST = (3, Vector(-1, 0))
    EAST = (4, Vector(+1, 0))

    def __init__(self, code: int, vector: Vector):
        self.code = code
        self.vector = vector

    @classmethod
    def from_code(cls, code: int) -> 'Heading':
        return next(h for h in Heading if h.code == code)

    def opposite(self) -> 'Heading':
        return {
            Heading.NORTH: Heading.SOUTH,
            Heading.SOUTH: Heading.NORTH,
            Heading.WEST: Heading.EAST,
            Heading.EAST: Heading.WEST,
        }[self]

    def left(self) -> 'Heading':
        return {
            Heading.NORTH: Heading.WEST,
            Heading.WEST: Heading.SOUTH,
            Heading.SOUTH: Heading.EAST,
            Heading.EAST: Heading.NORTH,
        }[self]

    def right(self) -> 'Heading':
        return {
            Heading.NORTH: Heading.EAST,
            Heading.EAST: Heading.SOUTH,
            Heading.SOUTH: Heading.WEST,
            Heading.WEST: Heading.NORTH,
        }[self]


class Tile(Enum):
    WALL = (0, '#')
    FLOOR = (1, '.')
    OXYGEN = (2, 'O')
    ROBOT = (None, '@')
    ORIGIN = (None, '<')
    UNKNOWN = (None, ' ')

    def __init__(self, code: Optional[int], char: str):
        assert len(char) == 1
        self.code = code
        self.char = char

    @classmethod
    def from_code(cls, code: int) -> 'Tile':
        return next(t for t in Tile if t.code == code)


class Robot:
    def __init__(self, sensor: Callable[[Heading], Tile], pos: Point = Point(0, 0)):
        self.sensor = sensor
        self.pos = pos
        self.last_heading = Heading.NORTH
        self.plan = {pos: Tile.FLOOR}
        self.distances = {pos: 0}
        self.look_around()

    @property
    def current_distance(self) -> int:
        return self.distances[self.pos]

    @property
    def current_tile(self) -> Tile:
        return self.plan[self.pos]

    def step(self) -> Tuple[Heading, Tile, int]:
        heading = self.choose_heading()
        tile = self.move(heading)
        discovered = self.look_around()
        return heading, tile, discovered

    def choose_heading(self) -> Heading:
        h = self.last_heading.left()
        for _ in range(4):
            hpos = self.pos + h.vector
            if self.plan[hpos] != Tile.WALL:
                self.last_heading = h
                return h
            h = h.right()
        else:
            raise ValueError("robot is trapped!")

    def look_around(self) -> int:
        discovered_count = 0

        orig_pos = self.pos
        for look_heading in Heading:
            look_pos = self.pos + look_heading.vector
            if look_pos not in self.plan:
                self.move(look_heading)
                if self.pos != orig_pos:
                    self.move(look_heading.opposite())
                assert self.pos == orig_pos
                discovered_count += 1

        return discovered_count

    def move(self, heading: Heading) -> Tile:
        headed_pos = self.pos + heading.vector
        tile = self.sensor(heading)
        self.plan[headed_pos] = tile
        if tile != Tile.WALL:
            if headed_pos not in self.distances:
                self.distances[headed_pos] = self.distances[self.pos] + 1
            self.pos = headed_pos
        return tile

    def draw_plan(self):
        def tile_at(p: Point) -> Tile:
            if p == self.pos:
                return Tile.ROBOT
            elif p == Point(0, 0):
                return Tile.ORIGIN
            elif p in self.plan:
                return self.plan[p]
            else:
                return Tile.UNKNOWN

        def char_at(x: int, y: int) -> str:
            return tile_at(Point(x, y)).char

        min_x, max_x = minmax(p.x for p in self.plan.keys())
        min_y, max_y = minmax(p.y for p in self.plan.keys())
        for y in range(min_y, max_y+1):
            print(''.join(char_at(x, y) for x in range(min_x, max_x+1)))


def map_maze():
    machine_f = Machine(load_tape("data/15-program.txt")).as_function_scalar()
    sensor = lambda h: Tile.from_code(machine_f(h.code))

    step = 0
    robot = Robot(sensor)
    while True:
        step += 1
        robot.step()
        print(f"[R] {step}: pos={robot.pos}, distance={robot.current_distance}")

        if robot.current_tile == Tile.OXYGEN:
            robot.draw_plan()
            print(
                f"oxygen source located after {step} steps: "
                f"pos={robot.pos}, "
                f"distance={robot.current_distance}"
            )
            print()
            break

    # continue as different "robot"
    step = 0
    oxbot = Robot(sensor, pos=robot.pos)
    while True:
        step += 1
        oxbot.step()
        print(f"[O] {step}: pos={oxbot.pos}, distance={oxbot.current_distance}")

        if oxbot.current_tile == Tile.OXYGEN:
            oxbot.draw_plan()
            max_oxygen_distance = max(oxbot.distances.values())
            print(f"max distance from oxygen source: {max_oxygen_distance}")
            break


if __name__ == '__main__':
    map_maze()
