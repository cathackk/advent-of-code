"""
Advent of Code 2022
Day 15: Beacon Exclusion Zone
https://adventofcode.com/2022/day/15
"""

import itertools
from typing import Iterable

from tqdm import tqdm

from common.iteration import ilen
from common.maths import sgn
from common.rect import Rect
from common.text import parse_line
from meta.aoc_tools import data_path


def part_1(sensors: list['Sensor'], y: int = 2_000_000) -> int:
    """
    You feel the ground rumble again as the distress signal leads you to a large network of
    subterranean tunnels. You don't have time to search them all, but you don't need to: your pack
    contains a set of deployable **sensors** that you imagine were originally built to locate lost
    Elves.

    The sensors aren't very powerful, but that's okay; your handheld device indicates that you're
    close enough to the source of the distress signal to use them. You pull the emergency sensor
    system out of your pack, hit the big button on top, and the sensors zoom off down the tunnels.

    Once a sensor finds a spot it thinks will give it a good reading, it attaches itself to a hard
    surface and begins monitoring for the nearest signal source **beacon**. Sensors and beacons
    always exist at integer coordinates. Each sensor knows its own position and can **determine the
    position of a beacon precisely**; however, sensors can only lock on to the one beacon **closest
    to the sensor** as measured by the Manhattan distance. (There is never a tie where two beacons
    are the same distance to a sensor.)

    It doesn't take long for the sensors to report back their positions and closest beacons (your
    puzzle input). For example:

        >>> ss = sensors_from_text('''
        ...     Sensor at x=2, y=18: closest beacon is at x=-2, y=15
        ...     Sensor at x=9, y=16: closest beacon is at x=10, y=16
        ...     Sensor at x=13, y=2: closest beacon is at x=15, y=3
        ...     Sensor at x=12, y=14: closest beacon is at x=10, y=16
        ...     Sensor at x=10, y=20: closest beacon is at x=10, y=16
        ...     Sensor at x=14, y=17: closest beacon is at x=10, y=16
        ...     Sensor at x=8, y=7: closest beacon is at x=2, y=10
        ...     Sensor at x=2, y=0: closest beacon is at x=2, y=10
        ...     Sensor at x=0, y=11: closest beacon is at x=2, y=10
        ...     Sensor at x=20, y=14: closest beacon is at x=25, y=17
        ...     Sensor at x=17, y=20: closest beacon is at x=21, y=22
        ...     Sensor at x=16, y=7: closest beacon is at x=15, y=3
        ...     Sensor at x=14, y=3: closest beacon is at x=15, y=3
        ...     Sensor at x=20, y=1: closest beacon is at x=15, y=3
        ... ''')
        >>> len(ss)
        14

    So, consider the sensor at `2,18`; the closest beacon to it is at `-2,15`. For the sensor at
    `9,16`, the closest beacon to it is at `10,16`.

        >>> ss[0]
        Sensor(pos=(2, 18), beacon_pos=(-2, 15))
        >>> ss[1]
        Sensor(pos=(9, 16), beacon_pos=(10, 16))

    Drawing sensors as `S` and beacons as `B`, the above arrangement of sensors and beacons looks
    like this:

        >>> draw_sensors(ss)
                       1    1    2    2
             0    5    0    5    0    5
         0 ····S·······················
         1 ······················S·····
         2 ···············S············
         3 ················SB··········
         4 ····························
         5 ····························
         6 ····························
         7 ··········S·······S·········
         8 ····························
         9 ····························
        10 ····B·······················
        11 ··S·························
        12 ····························
        13 ····························
        14 ··············S·······S·····
        15 B···························
        16 ···········SB···············
        17 ················S··········B
        18 ····S·······················
        19 ····························
        20 ············S······S········
        21 ····························
        22 ·······················B····

    This isn't necessarily a comprehensive map of all beacons in the area, though. Because each
    sensor only identifies its closest beacon, if a sensor detects a beacon, you know there are no
    other beacons that close or closer to that sensor. There could still be beacons that just happen
    to not be the closest beacon to any sensor. Consider the sensor at `8,7`:

        >>> ss[6]
        Sensor(pos=(8, 7), beacon_pos=(2, 10))
        >>> draw_sensors(ss, highlight=ss[6])
                       1    1    2    2
             0    5    0    5    0    5
        -2 ··········#·················
        -1 ·········###················
         0 ····S···#####···············
         1 ·······#######········S·····
         2 ······#########S············
         3 ·····###########SB··········
         4 ····#############···········
         5 ···###############··········
         6 ··#################·········
         7 ·#########S#######S#········
         8 ··#################·········
         9 ···###############··········
        10 ····B############···········
        11 ··S··###########············
        12 ······#########·············
        13 ·······#######··············
        14 ········#####·S·······S·····
        15 B········###················
        16 ··········#SB···············
        17 ················S··········B
        18 ····S·······················
        19 ····························
        20 ············S······S········
        21 ····························
        22 ·······················B····


    This sensor's closest beacon is at `2,10`, and so you know there are no beacons that close or
    closer (in any positions marked `#`).

    None of the detected beacons seem to be producing the distress signal, so you'll need to work
    out where the distress beacon is by working out where it **isn't**. For now, keep things simple
    by counting the positions where a beacon cannot possibly be along just a single row.

    So, suppose you have an arrangement of beacons and sensors like in the example above and, just
    in the row where `y=10`, you'd like to count the number of positions a beacon cannot possibly
    exist. The coverage from all sensors near that row looks like this:

        >>> draw_sensors(ss, highlight='all', bounds=Rect((-4, 9), (26, 11)))
                         1    1    2    2
               0    5    0    5    0    5
         9 ···#########################···
        10 ··####B######################··
        11 ·###S#############·###########·

    In this example, in the row where `y=10`, there are **26** positions where a beacon cannot be
    present.

        >>> ilen(excluded_positions(ss, y=10))
        26

    Consult the report from the sensors you just deployed.
    **In the row where y=2_000_000, how many positions cannot contain a beacon?**

        >>> part_1(ss, y=10)
        part 1: at y=10, there are 26 positions that cannot contain a beacon
        26
    """

    result = ilen(excluded_positions(sensors, y))

    print(f"part 1: at y={y}, there are {result} positions that cannot contain a beacon")
    return result


def part_2(sensors: list['Sensor'], bounds=Rect.at_origin(4_000_000, 4_000_000)) -> int:
    """
    Your handheld device indicates that the distress signal is coming from a beacon nearby.
    The distress beacon is not detected by any sensor, but the distress beacon must have `x` and `y`
    coordinates each no lower than `0` and no larger than `4_000_000`.

    To isolate the distress beacon's signal, you need to determine its **tuning frequency**, which
    can be found by multiplying its `x` coordinate by `4_000_000` and then adding its `y` coordinate

    In the example above, the search space is smaller: instead, the `x` and `y` coordinates can each
    be at most `20`. With this reduced search area, there is only a single position that could have
    a beacon: `x=14, y=11`:

        >>> ss = sensors_from_file(data_path(__file__, 'example.txt'))
        >>> find_beacon(ss, bounds=Rect.at_origin(20, 20))
        (14, 11)

    The tuning frequency for this distress beacon is **56000011**:

        >>> tuning_frequency((14, 11))
        56000011

    Find the only possible position for the distress beacon. What is its tuning frequency?

        >>> part_2(ss, Rect.at_origin(20, 20))
        part 2: the beacon is located at x=14, y=11 with tuning frequency 56000011
        56000011
    """

    x, y = find_beacon(sensors, bounds)
    result = tuning_frequency((x, y))

    print(f"part 2: the beacon is located at x={x}, y={y} with tuning frequency {result}")
    return result


Pos = tuple[int, int]


def manhattan_distance(pos_1: Pos, pos_2: Pos) -> int:
    x_1, y_1 = pos_1
    x_2, y_2 = pos_2
    return abs(x_1 - x_2) + abs(y_1 - y_2)


class Sensor:
    def __init__(self, pos: Pos, beacon_pos: Pos):
        self.pos = pos
        self.beacon_pos = beacon_pos
        self.reach = manhattan_distance(self.pos, self.beacon_pos)

        # rectangular sensor bounds (not the diamond!), useful for drawing
        x, y = self.pos
        self.bounds = Rect(
            (x - self.reach, y - self.reach),
            (x + self.reach, y + self.reach),
        )

    def __repr__(self) -> str:
        return f'{type(self).__name__}(pos={self.pos!r}, beacon_pos={self.beacon_pos!r})'

    def is_within_reach(self, pos) -> bool:
        return manhattan_distance(self.pos, pos) <= self.reach

    @classmethod
    def from_line(cls, line: str):
        # Sensor at x=2, y=18: closest beacon is at x=-2, y=15
        line = line.strip()
        s_x, s_y, b_x, b_y = parse_line(line, "Sensor at x=$, y=$: closest beacon is at x=$, y=$")
        return cls((int(s_x), int(s_y)), (int(b_x), int(b_y)))


def excluded_positions(sensors: list[Sensor], y: int) -> Iterable[Pos]:
    bounds = Rect.with_all(
        pos
        for sensor in sensors
        for pos in sensor.bounds.corners()
    )
    assert y in bounds.range_y()

    relevant_beacons = {sensor.beacon_pos for sensor in sensors if sensor.beacon_pos[1] == y}
    relevant_sensors = [sensor for sensor in sensors if y in sensor.bounds.range_y()]

    return (
        pos
        for x in tqdm(bounds.range_x(), delay=1.0, unit=' pos', unit_scale=True)
        if (pos := (x, y)) not in relevant_beacons
        if any(sensor.is_within_reach(pos) for sensor in relevant_sensors)
    )


def find_beacon(sensors: list[Sensor], bounds: Rect) -> Pos:
    """
    Assumption: The beacon must be bordered by two pairs of scanned "diamonds", where each pair of
    these sensor-diamonds must be exactly one position apart:

        #···###·   4####·##
        ##·##2##   ####·###
        ###X###· + ###X####
        ####·#··   ##·#####
        4####···   #·#####5
    """

    # group sensors into adjacent pairs
    pairs = [
        (sensor_1, sensor_2)
        for sensor_1, sensor_2 in itertools.combinations(sensors, 2)
        if manhattan_distance(sensor_1.pos, sensor_2.pos) == sensor_1.reach + sensor_2.reach + 2
    ]

    if len(pairs) < 2:
        raise ValueError('not enough scanner pairs found to extrapolate beacon position')

    def canyon_positions(pair: tuple[Sensor, Sensor]) -> Iterable[Pos]:
        sensor_1, sensor_2 = pair
        if sensor_1.pos > sensor_2.pos:
            sensor_1, sensor_2 = sensor_2, sensor_1

        x_1, y_1 = sensor_1.pos
        x_2, y_2 = sensor_2.pos
        dist_1, dist_2 = sensor_1.reach + 1, sensor_2.reach + 1

        assert manhattan_distance((x_1, y_1), (x_2, y_2)) == dist_1 + dist_2

        dx = x_2 - x_1  # >= 0 because x_1 <= x_2
        dy = y_2 - y_1

        if dist_1 <= dx:
            cx_1, cy_1 = x_1 + dist_1, y_1
            cx_2, cy_2 = x_2 - dist_2, y_2

        elif dist_1 <= abs(dy):
            cx_1, cy_1 = x_1, y_1 + sgn(dy) * dist_1
            cx_2, cy_2 = x_2, y_2 - sgn(dy) * dist_2

        else:
            raise ValueError(dist_1, dx, dy)

        canyon_length = abs(cx_2 - cx_1)
        assert canyon_length == abs(cy_2 - cy_1)
        csx, csy = sgn(cx_2 - cx_1), sgn(cy_2 - cy_1)

        return (
            (cx_1 + step * csx, cy_1 + step * csy)
            for step in range(canyon_length)
        )

    return next(
        pos
        for sensor_pair in pairs
        for pos in canyon_positions(sensor_pair)
        if pos in bounds
        if not any(sensor.is_within_reach(pos) for sensor in sensors)
    )


def tuning_frequency(pos: Pos) -> int:
    x, y = pos
    return 4_000_000 * x + y


def draw_sensors(
    sensors: list[Sensor],
    highlight: Sensor | str | None = None,
    bounds: Rect = None,
) -> None:
    # highlighting logic
    if highlight == 'all':
        highlighted_sensors = set(sensors)
    elif isinstance(highlight, Sensor):
        highlighted_sensors = {highlight}
    else:
        highlighted_sensors = set()

    # auto-bounds
    if not bounds:
        bounds = Rect.with_all(
            pos
            for sensor in sensors
            for pos in (sensor.pos, sensor.beacon_pos)
        ).grow_to_fit(
            corner
            for sensor in highlighted_sensors
            for corner in sensor.bounds.corners()
        )

    # headers
    assert bounds is not None
    max_x_title_length = max(len(str(bounds.left_x)), len(str(bounds.right_x)))
    max_y_title_length = max(len(str(bounds.top_y)), len(str(bounds.bottom_y)))

    # top x header
    def x_digit(x_value: int, digit_: int) -> str:
        return str(x_value).rjust(max_x_title_length)[digit_] if x_value % 5 == 0 else ' '

    for digit in range(max_x_title_length):
        pad = ' ' * (max_y_title_length + 1)
        print(pad + ''.join(x_digit(x, digit) for x in bounds.range_x()).rstrip())

    # cell printing preparation
    drawn_positions = {
        pos: char
        for sensor in sensors
        for pos, char in [(sensor.pos, 'S'), (sensor.beacon_pos, 'B')]
    }

    def char(pos: Pos) -> str:
        if pos in drawn_positions:
            return drawn_positions[pos]
        elif any(sensor.is_within_reach(pos) for sensor in highlighted_sensors):
            return '#'
        else:
            return '·'

    # left y header + cells
    for y in bounds.range_y():
        y_header = str(y).rjust(max_y_title_length) + ' '
        print(y_header + ''.join(char((x, y)) for x in bounds.range_x()))


def sensors_from_file(fn: str) -> list[Sensor]:
    return list(sensors_from_lines(open(fn)))


def sensors_from_text(text: str) -> list[Sensor]:
    return list(sensors_from_lines(text.strip().splitlines()))


def sensors_from_lines(lines: Iterable[str]) -> Iterable[Sensor]:
    return (Sensor.from_line(line) for line in lines)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    sensors = sensors_from_file(input_path)
    result_1 = part_1(sensors)
    result_2 = part_2(sensors)
    return result_1, result_2


if __name__ == '__main__':
    main()
