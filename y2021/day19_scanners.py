"""
Advent of Code 2021
Day 19: Beacon Scanner
https://adventofcode.com/2021/day/19
"""

import itertools
from functools import lru_cache
from typing import Iterable
from typing import Iterator

from tqdm import tqdm

from rect import Rect
from utils import dgroupby_pairs
from utils import maxk
from utils import parse_line
from utils import sgn
from xyz import Vector3


def part_1(report: list['Reading']) -> 'Map':
    """
    As your probe drifted down through this area, it released an assortment of **beacons** and
    **scanners** into the water. It's difficult to navigate in the pitch black open waters of
    the ocean trench, but if you can build a map of the trench using data from the scanners, you
    should be able to safely reach the bottom.

    The beacons and scanners float motionless in the water; they're designed to maintain the same
    position for long periods of time. Each scanner is capable of detecting all beacons in a large
    cube centered on the scanner; beacons that are at most `1000` units away from the scanner in
    each of the three axes (`x`, `y`, and `z`) have their precise position determined relative to
    the scanner. However, scanners cannot detect other scanners. The submarine has automatically
    summarized the relative positions of beacons detected by each scanner (your puzzle input).

    For example, if a scanner is at `x,y,z` coordinates `500,0,-500` and there are beacons at
    `-500,1000,-1500` and `1501,0,-500`, the scanner could report that the first beacon is at
    `-1000,1000,-1000` (relative to the scanner) but would not detect the second beacon at all.

        >>> scanner = Scanner(Vector3(500, 0, -500))
        >>> beacons = [Vector3(-500, 1000, -1500), Vector3(1501, 0, -500)]
        >>> scanner.scan(beacons)
        Reading([Vector3(-1000, 1000, -1000)])

    Unfortunately, while each scanner can report the positions of all detected beacons relative to
    itself, **the scanners do not know their own position**. You'll need to determine the positions
    of the beacons and scanners yourself.

    The scanners and beacons map a single contiguous 3d region. This region can be reconstructed by
    finding pairs of scanners that have overlapping detection regions such that there are **at least
    12 beacons** that both scanners detect within the overlap. By establishing 12 common beacons,
    you can precisely determine where the scanners are relative to each other, allowing you to
    reconstruct the beacon map one scanner at a time.

    For a moment, consider only two dimensions. Suppose you have the following scanner reports:

        >>> reading_2d_0, reading_2d_1 = report_from_text('''
        ...     --- scanner 0 ---
        ...     0,2,0
        ...     4,1,0
        ...     3,3,0
        ...
        ...     --- scanner 1 ---
        ...     -1,-1,0
        ...     -5,0,0
        ...     -2,1,0
        ... ''')
        >>> reading_2d_0
        Reading([Vector3(0, 2, 0), Vector3(4, 1, 0), Vector3(3, 3, 0)])
        >>> reading_2d_1
        Reading([Vector3(-1, -1, 0), Vector3(-5, 0, 0), Vector3(-2, 1, 0)])

    Drawing `x` increasing rightward, `y` increasing downward, scanners as `S`, and beacons as `B`,
    scanner 0 detects this:

        >>> reading_2d_0.draw(z=0)
        S····
        ····B
        B····
        ···B·

    Scanner 1 detects this:

        >>> reading_2d_1.draw(z=0)
        ····B·
        B····S
        ···B··

    For this example, assume scanners only need 3 overlapping beacons. Then, the beacons visible to
    both scanners overlap to produce the following complete map:

        >>> world_map_2d = Map.build([reading_2d_0])
        >>> world_map_2d.scanners
        [Scanner(Vector3(0, 0, 0))]
        >>> sorted(world_map_2d.all_beacons, key=tuple)
        [Vector3(0, 2, 0), Vector3(3, 3, 0), Vector3(4, 1, 0)]
        >>> world_map_2d.place_scanner(reading_2d_1, min_overlaps=3)
        Scanner(Vector3(5, 2, 0))
        >>> world_map_2d.scanners
        [Scanner(Vector3(0, 0, 0)), Scanner(Vector3(5, 2, 0))]
        >>> sorted(world_map_2d.all_beacons, key=tuple)  # no new beacons added (they all overlap)
        [Vector3(0, 2, 0), Vector3(3, 3, 0), Vector3(4, 1, 0)]
        >>> world_map_2d.draw(z=0)
        S·····
        ····B·
        B····S
        ···B··

    Unfortunately, there's a second problem: the scanners also don't know their **rotation or facing
    direction**. Due to magnetic alignment, each scanner is rotated some integer number of 90-degree
    turns around all of the `x`, `y`, and `z` axes. That is, one scanner might call a direction
    positive `x`, while another scanner might call that direction negative `y`. Or, two scanners
    might agree on which direction is positive `x`, but one scanner might be upside-down from
    the perspective of the other scanner. In total, each scanner could be in any of 24 different
    orientations: facing positive or negative `x`, `y`, or `z`, and considering any of four
    directions "up" from that facing.

    For example, here is an arrangement of beacons as seen from a scanner in the same position but
    in different orientations:

        >>> r0, = report_from_text('''
        ...     -1,-1,1
        ...     -2,-2,2
        ...     -3,-3,3
        ...     -2,-3,1
        ...     5,6,-4
        ...     8,0,7
        ... ''')
        >>> (rot1 := Rotation.from_str('x->-x, y->-z, z->-y'))
        Rotation(-1, -3, -2)
        >>> print(r0.rotated(rot1))
        1,-1,1
        2,-2,2
        3,-3,3
        2,-1,3
        -5,4,-6
        -8,-7,0
        >>> print(r0.rotated(Rotation.from_str('x->z, y->y, z->-x')))
        -1,-1,-1
        -2,-2,-2
        -3,-3,-3
        -1,-3,-2
        4,6,5
        -7,0,8
        >>> print(r0.rotated(Rotation.from_str('x->z, y->-y, z->x')))
        1,1,-1
        2,2,-2
        3,3,-3
        1,3,-2
        -4,-6,5
        7,0,8
        >>> print(r0.rotated(Rotation.from_str('x->-z, y->-x, z->y')))
        1,1,1
        2,2,2
        3,3,3
        3,1,2
        -6,-4,-5
        0,7,-8

    By finding pairs of scanners that both see at least 12 of the same beacons, you can assemble
    the entire map. For example, consider the following report:

        >>> example_report = report_from_file('data/19-example.txt')
        >>> [len(reading) for reading in example_report]
        [25, 25, 26, 25, 26]

    Because all coordinates are relative, in this example, all "absolute" positions will be
    expressed relative to scanner 0 (using the orientation of scanner 0 and as if scanner 0 is at
    coordinates `0,0,0`).

        >>> world_map = Map.build(example_report[:1])
        >>> scanner_0, = world_map.scanners
        >>> scanner_0
        Scanner(Vector3(0, 0, 0))
        >>> len(world_map.all_beacons)
        25

    Scanners 0 and 1 have overlapping detection cubes.

        >>> scanner_1 = world_map.place_scanner(example_report[1])
        >>> len(world_map.all_beacons)  # 25 + 25 - 12
        38

    The 12 beacons they both detect (relative to scanner 0) are at the following coordinates:

        >>> print(scanner_0.scan(b for b in world_map.all_beacons if scanner_1.sees(b)))
        -661,-816,-575
        -618,-824,-621
        -537,-823,-458
        -485,-357,347
        -447,-329,318
        -345,-311,381
        390,-675,-793
        404,-588,-901
        423,-701,434
        459,-707,401
        528,-643,409
        544,-627,-890

    These same 12 beacons (in the same order) but from the perspective of scanner 1 are:

        >>> print(scanner_1.scan(b for b in world_map.all_beacons if scanner_0.sees(b)))
        729,430,532
        686,422,578
        605,423,415
        553,889,-390
        515,917,-361
        413,935,-424
        -322,571,750
        -336,658,858
        -355,545,-477
        -391,539,-444
        -460,603,-452
        -476,619,847

    Because of this, scanner 1 must be at position (relative to scanner 0):

        >>> scanner_1
        Scanner(Vector3(68, -1246, -43), Rotation(-1, 2, -3))

    Scanner 4 overlaps with scanner 1:

        >>> scanner_4 = world_map.place_scanner(example_report[4])
        >>> len(world_map.all_beacons)  # 38 + 26 - 12
        52

    The 12 beacons they both detect (relative to scanner 0) are:

        >>> print(
        ...     Reading(sorted(
        ...         set(world_map.fixed_readings[scanner_1]) &
        ...         set(world_map.fixed_readings[scanner_4])
        ...     ))
        ... )
        -739,-1745,668
        -687,-1600,576
        -635,-1737,486
        -485,-357,347
        -447,-329,318
        -345,-311,381
        408,-1815,803
        423,-701,434
        432,-2009,850
        459,-707,401
        528,-643,409
        534,-1912,768

    So, scanner 4 is at position (relative to scanner 0):

        >>> scanner_4
        Scanner(Vector3(-20, -1133, 1061), Rotation(3, -1, -2))

    Following this process, scanners 2 and 3 must be at following positions (relative to scanner 0):

        >>> world_map.place_scanner(example_report[2])
        Scanner(Vector3(1105, -1205, 1229), Rotation(-1, 3, 2))
        >>> world_map.place_scanner(example_report[3])
        Scanner(Vector3(-92, -2380, -20), Rotation(-1, 2, -3))

    The full list of beacons (relative to scanner 0) is:

        >>> print(world_map.full_reading())
        -892,524,684
        -876,649,763
        -838,591,734
        -789,900,-551
        -739,-1745,668
        -706,-3180,-659
        -697,-3072,-689
        -689,845,-530
        -687,-1600,576
        -661,-816,-575
        -654,-3158,-753
        -635,-1737,486
        -631,-672,1502
        -624,-1620,1868
        -620,-3212,371
        -618,-824,-621
        -612,-1695,1788
        -601,-1648,-643
        -584,868,-557
        -537,-823,-458
        -532,-1715,1894
        -518,-1681,-600
        -499,-1607,-770
        -485,-357,347
        -470,-3283,303
        -456,-621,1527
        -447,-329,318
        -430,-3130,366
        -413,-627,1469
        -345,-311,381
        -36,-1284,1171
        -27,-1108,-65
        7,-33,-71
        12,-2351,-103
        26,-1119,1091
        346,-2985,342
        366,-3059,397
        377,-2827,367
        390,-675,-793
        396,-1931,-563
        404,-588,-901
        408,-1815,803
        423,-701,434
        432,-2009,850
        443,580,662
        455,729,728
        456,-540,1869
        459,-707,401
        465,-695,1988
        474,580,667
        496,-1584,1900
        497,-1838,-617
        527,-524,1933
        528,-643,409
        534,-1912,768
        544,-627,-890
        553,345,-567
        564,392,-477
        568,-2007,-577
        605,-1665,1952
        612,-1593,1893
        630,319,-379
        686,-3108,-505
        776,-3184,-501
        846,-3110,-434
        1135,-1161,1235
        1243,-1093,1063
        1660,-552,429
        1693,-557,386
        1735,-437,1738
        1749,-1800,1813
        1772,-405,1572
        1776,-675,371
        1779,-442,1789
        1780,-1548,337
        1786,-1538,337
        1847,-1591,415
        1889,-1729,1762
        1994,-1805,1792

    In total, there are **`79`** beacons.

        >>> len(world_map.all_beacons)
        79

    Assemble the full map of beacons. **How many beacons are there?**

        >>> _ = part_1(example_report)
        part 1: there are 79 beacons
    """

    world = Map.build(report)
    result = len(world.all_beacons)

    print(f"part 1: there are {result} beacons")
    return world


def part_2(world_map: 'Map') -> int:
    """
    Sometimes, it's a good idea to appreciate just how big the ocean is. Using the Manhattan
    distance, how far apart do the scanners get?

    In the above example, scanners 2 (`1105,-1205,1229`) and 3 (`-92,-2380,-20`) are the largest
    Manhattan distance apart. In total, they are `1197 + 1175 + 1249 = 3621` units apart.

        >>> example_report = report_from_file('data/19-example.txt')
        >>> world = Map.build(example_report)
        >>> (s3, s2), d = world.most_distant_scanners()
        >>> s2
        Scanner(Vector3(1105, -1205, 1229), Rotation(-1, 3, 2))
        >>> s3
        Scanner(Vector3(-92, -2380, -20), Rotation(-1, 2, -3))
        >>> d
        3621

    **What is the largest Manhattan distance between any two scanners?**

        >>> part_2(world)
        part 2: largest distance between two scanners is 3621
        3621
    """

    _, distance = world_map.most_distant_scanners()

    print(f"part 2: largest distance between two scanners is {distance}")
    return distance


class Rotation:
    def __init__(self, x_to: int, y_to: int, z_to: int):
        self.x_to = x_to
        self.y_to = y_to
        self.z_to = z_to

        assert abs(self.x_to) in range(1, 4)
        assert abs(self.y_to) in range(1, 4)
        assert abs(self.z_to) in range(1, 4)
        assert abs(self.x_to) != abs(self.y_to)
        assert abs(self.y_to) != abs(self.z_to)
        assert abs(self.z_to) != abs(self.x_to)

        # calculation helpers
        abs_to = (abs(self.x_to), abs(self.y_to), abs(self.z_to))
        sgn_to = (sgn(self.x_to), sgn(self.y_to), sgn(self.z_to))
        self.new_x_from_index = abs_to.index(1)
        self.new_y_from_index = abs_to.index(2)
        self.new_z_from_index = abs_to.index(3)
        self.new_x_sgn = sgn_to[self.new_x_from_index]
        self.new_y_sgn = sgn_to[self.new_y_from_index]
        self.new_z_sgn = sgn_to[self.new_z_from_index]

        # parity "mirrored"
        # 1. each axis swap pair flips parity
        # -> 0 non-matching axes -> 0 swapped pairs -> keep parity
        # -> 2 non-matching axes -> 1 swapped pair  -> FLIP parity
        # -> 3 non-matching axes -> 2 swapped pairs -> keep parity
        non_matching_axes_count = sum(a_orig != a_new for a_orig, a_new in zip((1, 2, 3), abs_to))
        axes_swaps_count = {0: 0, 2: 1, 3: 2}[non_matching_axes_count]
        # 2. each sign change flips parity
        signs_change_count = sum((s == -1) for s in sgn_to)
        self.mirrored = (axes_swaps_count + signs_change_count) % 2 == 1

        # str helpers
        self.x_to_str = Rotation.axis_str(self.x_to)
        self.y_to_str = Rotation.axis_str(self.y_to)
        self.z_to_str = Rotation.axis_str(self.z_to)

    AXES = ('-z', '-y', '-x', '?', 'x', 'y', 'z')

    @staticmethod
    def axis_str(n: int) -> str:
        assert abs(n) in range(1, 4)
        return Rotation.AXES[n + 3]

    @staticmethod
    def axis_from_str(s: str) -> int:
        return Rotation.AXES.index(s) - 3

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.x_to!r}, {self.y_to!r}, {self.z_to!r})'

    def __str__(self) -> str:
        return f'x->{self.x_to_str}, y->{self.y_to_str}, z->{self.z_to_str}'

    @classmethod
    def from_str(cls, line: str) -> 'Rotation':
        sx, sy, sz = parse_line(line, 'x->$, y->$, z->$')
        return cls(
            x_to=cls.axis_from_str(sx),
            y_to=cls.axis_from_str(sy),
            z_to=cls.axis_from_str(sz)
        )

    def apply(self, vector: Vector3):
        """
            >>> Rotation.from_str('x->y, y->z, z->-x').apply(Vector3(5, 6, 7))
            Vector3(-7, 5, 6)
            >>> Rotation.from_str('x->-y, y->x, z->-z').apply(Vector3(10, 5, -9))
            Vector3(5, -10, 9)
        """
        xyz = (vector.x, vector.y, vector.z)
        return type(vector)(
            xyz[self.new_x_from_index] * self.new_x_sgn,
            xyz[self.new_y_from_index] * self.new_y_sgn,
            xyz[self.new_z_from_index] * self.new_z_sgn
        )

    @classmethod
    def all(cls, mirrored: bool = None) -> Iterable['Rotation']:
        return (
            rot
            for x, y, z in itertools.permutations((1, 2, 3))
            for sx in (+1, -1)
            for sy in (+1, -1)
            for sz in (+1, -1)
            if (rot := cls(x * sx, y * sy, z * sz)).mirrored is mirrored or mirrored is None
        )

    def _key(self) -> tuple:
        return self.x_to, self.y_to, self.z_to

    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and self._key() == other._key()

    def __hash__(self) -> int:
        return hash(self._key())


class Reading:
    def __init__(self, beacons: Iterable[Vector3]):
        self.beacons = list(beacons)
        sorted_beacons = sorted(self.beacons, key=tuple)
        self.pairs = dgroupby_pairs(
            ((b2 - b1), (b1, b2))
            for b1, b2 in itertools.combinations(sorted_beacons, 2)
        )

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.beacons!r})'

    def __str__(self) -> str:
        return '\n'.join(','.join(str(v) for v in b) for b in self.beacons)

    def __len__(self) -> int:
        return len(self.beacons)

    def __iter__(self) -> Iterator[Vector3]:
        return iter(self.beacons)

    @lru_cache(maxsize=10_000)
    def rotated(self, rotation: Rotation) -> 'Reading':
        return type(self)(rotation.apply(beacon) for beacon in self)

    def translated(self, vector: Vector3) -> 'Reading':
        return type(self)(beacon + vector for beacon in self)

    @lru_cache(maxsize=10_000)
    def match(
        self, other: 'Reading', min_overlaps: int = 12
    ) -> tuple[Rotation, Vector3, 'Reading'] | None:

        my_beacons_set = set(self.beacons)
        # number of pairs that must be matched
        min_pairs_overlaps = (min_overlaps * (min_overlaps - 1)) // 2

        for rotation in ROTATIONS:
            other_rotated = other.rotated(rotation)
            pairs_overlap = self.pairs.keys() & other_rotated.pairs.keys()
            if len(pairs_overlap) < min_pairs_overlaps:
                continue

            translations = (
                (beacon_self - beacon_other)
                for diff in pairs_overlap
                for beacon_self, _ in self.pairs[diff]
                for beacon_other, _ in other_rotated.pairs[diff]
            )

            for translation in translations:
                other_rotated_translated = other_rotated.translated(translation)
                overlaps = my_beacons_set & set(other_rotated_translated)
                if len(overlaps) >= min_overlaps:
                    return rotation, translation, other_rotated_translated

        # no match found
        return None

    def draw(self, z: int) -> None:
        flat_beacons = {(b.x, b.y) for b in self if b.z == z}
        flat_origin = (0, 0)
        canvas = Rect.with_all(flat_beacons | {flat_origin})

        def ch(pos: tuple[int, int]) -> str:
            if pos == flat_origin:
                return 'S'
            elif pos in flat_beacons:
                return 'B'
            else:
                return '·'

        for y in canvas.range_y():
            print(''.join(ch((x, y)) for x in canvas.range_x()))


ROTATIONS = list(Rotation.all(mirrored=False))
assert len(ROTATIONS) == 24
NO_ROTATION = Rotation(1, 2, 3)


class Scanner:
    DEFAULT_REACH = 1000

    def __init__(self, pos: Vector3, rotation: Rotation = NO_ROTATION, reach: int = DEFAULT_REACH):
        self.pos = pos
        self.rotation = rotation
        self.reach = reach

    def __repr__(self) -> str:
        rotation_repr = f', {self.rotation!r}' if self.rotation != NO_ROTATION else ''
        reach_repr = f', reach={self.reach!r}' if self.reach != self.DEFAULT_REACH else ''
        return f'{type(self).__name__}({self.pos!r}{rotation_repr}{reach_repr})'

    def scan(self, beacons: Iterable[Vector3]) -> Reading:
        return Reading(
            beacon - self.pos
            for beacon in sorted(beacons, key=tuple)
            if self.sees(beacon)
        ).rotated(self.rotation)

    def sees(self, beacon: Vector3) -> bool:
        return all(
            abs(v1 - v2) <= self.reach
            for v1, v2 in zip(self.rotation.apply(self.pos), beacon)
        )


class Map:
    def __init__(self, fixed_readings: Iterable[tuple[Scanner, Reading]] = ()):
        self.fixed_readings = dict(fixed_readings)

    def __repr__(self) -> str:
        return f'{type(self).__name__}(fixed_readings={self.fixed_readings!r})'

    @property
    def scanners(self) -> list[Scanner]:
        return list(self.fixed_readings.keys())

    @classmethod
    def build(cls, readings: Iterable[Reading]) -> 'Map':
        map_ = cls()
        unused_readings = list(readings)

        progress = tqdm(total=len(unused_readings), desc="placing", unit="placed", delay=1.0)

        while unused_readings:
            for reading in unused_readings:
                scanner = map_.place_scanner(reading)
                if scanner is not None:
                    progress.update()
                    unused_readings.remove(reading)
                    break
            else:
                raise StopIteration("no more matches found -> failed to build map")

        return map_

    def place_scanner(self, reading: Reading, min_overlaps: int = 12) -> Scanner | None:
        if not self.fixed_readings:
            # first reading -> trivial
            first_scanner = Scanner(Vector3(0, 0, 0))
            self.fixed_readings[first_scanner] = reading
            return first_scanner

        # try matching the reading to match with any of a fixed reading
        for fixed_reading in self.fixed_readings.values():
            if match := fixed_reading.match(reading, min_overlaps):
                rotation, vector, reading_translated = match
                scanner = Scanner(vector, rotation)
                self.fixed_readings[scanner] = reading_translated
                return scanner
        else:
            # cannot be placed
            return None

    @property
    def all_beacons(self) -> set[Vector3]:
        return {
            beacon
            for reading in self.fixed_readings.values()
            for beacon in reading.beacons
        }

    def full_reading(self) -> Reading:
        return Reading(sorted(self.all_beacons, key=tuple))

    def draw(self, z: int) -> None:
        flat_scanners = {(s.pos.x, s.pos.y) for s in self.scanners if s.pos.z == z}
        flat_beacons = {(b.x, b.y) for b in self.all_beacons if b.z == z}
        canvas = Rect.with_all(flat_scanners | flat_beacons)

        def ch(pos: tuple[int, int]) -> str:
            if pos in flat_scanners:
                return 'S'
            elif pos in flat_beacons:
                return 'B'
            else:
                return '·'

        for y in canvas.range_y():
            print(''.join(ch((x, y)) for x in canvas.range_x()))

    def most_distant_scanners(self) -> tuple[tuple[Scanner, Scanner], int]:
        assert len(self.fixed_readings) >= 2

        def manhattan_distance(scanner_pair: tuple[Scanner, Scanner]) -> int:
            return sum(abs(v) for v in (scanner_pair[0].pos - scanner_pair[1].pos))

        scanner_pairs = ((s1, s2) for s1, s2 in itertools.combinations(self.scanners, 2))
        return maxk(scanner_pairs, key=manhattan_distance)


def report_from_text(text: str) -> list[Reading]:
    return list(report_from_lines(text.strip().split('\n')))


def report_from_file(fn: str) -> list[Reading]:
    return list(report_from_lines(open(fn)))


def report_from_lines(lines: Iterable[str]) -> Iterable[Reading]:
    beacons_buffer: list[Vector3] = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith('---'):
            if beacons_buffer:
                yield Reading(beacons_buffer)
                beacons_buffer.clear()
        else:
            x, y, z = line.split(',')
            beacons_buffer.append(Vector3(int(x), int(y), int(z)))

    if beacons_buffer:
        yield Reading(beacons_buffer)


if __name__ == '__main__':
    report_ = report_from_file('data/19-input.txt')
    world_ = part_1(report_)
    part_2(world_)
