"""
Advent of Code 2019
Day 19: Tractor Beam
https://adventofcode.com/2019/day/19
"""

from itertools import count, islice
from typing import Callable, Iterator

from tqdm import tqdm

from common.iteration import slidingw
from common.rect import Rect
from meta.aoc_tools import data_path
from y2019.intcode import load_tape, Machine, Tape


def part_1(beam_func: 'BeamFunc', area_size: int = 50) -> int:
    """
    Unsure of the state of Santa's ship, you borrowed the tractor beam technology from Triton.
    Time to test it out.

    When you're safely away from anything else, you activate the tractor beam, but nothing happens.
    It's hard to tell whether it's working if there's nothing to use it on. Fortunately, your
    ship's drone system can be configured to deploy a drone to specific coordinates and then check
    whether it's being pulled. There's even an Intcode program (your puzzle input) that gives you
    access to the drone system.

    The program uses two input instructions to request the **X and Y position** to which the drone
    should be deployed. Negative numbers are invalid and will confuse the drone; all numbers should
    be **zero or positive**.

    Then, the program will output whether the drone is **stationary (`0`) or **being pulled by
    something** (`1`). For example, the coordinate X=`0`, Y=`0` is directly in front of the tractor
    beam emitter, so the drone control program will always report `1` at that location.

    To better understand the tractor beam, it is important to **get a good picture** of the beam
    itself. For example, suppose you scan the 10x10 grid of points closest to the emitter:

        >>> example_beam_func = testing_beam_func(1.18, 1.7)
        >>> draw_area(example_beam_func, area=Rect.at_origin(10, 10))
        #·········
        ·#········
        ··##······
        ···###····
        ····###···
        ·····####·
        ······####
        ······####
        ·······###
        ········##

    In this example, the **number of points affected by the tractor beam** in the 10x10 area closest
    to the emitter is **`27`**.

        >>> count_active(example_beam_func, area_size=10)
        27

    However, you'll need to scan a larger area to **understand the shape** of the beam. **How many
    points are affected by the tractor beam in the 50x50 area closest to the emitter?** (For each of
    X and Y, this will be `0` through `49`.)

        >>> part_1(example_beam_func)
        part 1: tractor beam affects 694 points (out of 2500)
        694
    """

    result = count_active(beam_func, area_size)

    print(f"part 1: tractor beam affects {result} points (out of {area_size**2})")
    return result


def part_2(beam_func: 'BeamFunc', ship_size: int = 100) -> int:
    """
    You aren't sure how large Santa's ship is. You aren't even sure if you'll need to use this thing
    on Santa's ship, but it doesn't hurt to be prepared. You figure Santa's ship might fit in
    a **100x100** square.

    The beam gets wider as it travels away from the emitter; you'll need to be a minimum distance
    away to fit a square of that size into the beam fully. (Don't rotate the square; it should be
    aligned to the same axes as the drone grid.)

    For example, suppose you have the following tractor beam readings:

        >>> example_beam_func = testing_beam_func(31/26, 36/21)
        >>> draw_area(example_beam_func, area=Rect.at_origin(40, 35), ship=Rect((25, 20), (34, 29)))
        #·······································
        ·#······································
        ··##····································
        ···###··································
        ····###·································
        ·····####·······························
        ······#####·····························
        ······#######···························
        ·······#######··························
        ········########························
        ·········#########······················
        ··········#########·····················
        ···········##########···················
        ···········############·················
        ············#############···············
        ·············#############··············
        ··············##############············
        ···············###############··········
        ················###############·········
        ················#################·······
        ·················########OOOOOOOOOO·····
        ··················#######OOOOOOOOOO##···
        ···················######OOOOOOOOOO###··
        ····················#####OOOOOOOOOO#####
        ·····················####OOOOOOOOOO#####
        ·····················####OOOOOOOOOO#####
        ······················###OOOOOOOOOO#####
        ·······················##OOOOOOOOOO#####
        ························#OOOOOOOOOO#####
        ·························OOOOOOOOOO#####
        ··························##############
        ··························##############
        ···························#############
        ····························############
        ·····························###########

    In this example, the **10x10** square closest to the emitter that fits entirely within the
    tractor beam has been marked `O`. Within it, the point closest to the emitter is at X=25, Y=20.

        >>> place_ship(example_beam_func, ship_size=10)
        (25, 20)

    Find the **100x100** square closest to the emitter that fits entirely within the tractor beam;
    within that square, find the point closest to the emitter. **What value do you get if you take
    that point's X coordinate, multiply it by `10_000`, then add the point's Y coordinate?**

        >>> part_2(example_beam_func, ship_size=10)
        part 2: ship is at (25, 20) -> 250020
        250020
    """
    ship_x, ship_y = place_ship(beam_func, ship_size)
    result = ship_x * 10_000 + ship_y

    print(f"part 2: ship is at {(ship_x, ship_y)} -> {result}")
    return result


BeamFunc = Callable[[int, int], bool]


def beam_x_ranges(beam_func: BeamFunc) -> Iterator[range]:
    x_min, x_max = 0, 1
    for y in count(0):
        new_x_min = next((x for x in range(x_min, x_min + 16) if beam_func(x, y)), None)
        if new_x_min is None:
            # no active point at this y
            yield range(x_min, x_min)
            continue

        x_min = new_x_min
        x_max = next(x for x in count(max(x_min, x_max)) if not beam_func(x, y))
        yield range(x_min, x_max)


def count_active(beam_func: BeamFunc, area_size: int) -> int:
    return sum(
        min(x_range.stop, area_size) - x_range.start
        for x_range in islice(beam_x_ranges(beam_func), area_size)
    )


def place_ship(beam_func: BeamFunc, ship_size: int) -> tuple[int, int]:
    assert ship_size > 1

    for ship_top, ranges in tqdm(enumerate(slidingw(beam_x_ranges(beam_func), ship_size))):
        top, *_, bottom = ranges
        if len(bottom) >= ship_size:
            ship_left, ship_right = bottom.start, bottom.start + ship_size - 1
            if ship_left in top and ship_right in top:
                return ship_left, ship_top


def draw_area(beam_func: BeamFunc, area: Rect, ship: Rect = None) -> None:
    def char(x: int, y: int, beam_range: range) -> str:
        in_beam = x in beam_range
        in_ship = ship and (x, y) in ship

        if in_beam and in_ship:
            return 'O'
        elif in_beam:
            return '#'
        elif in_ship:
            return 'X'
        else:
            return '·'

    for y, x_range in enumerate(islice(beam_x_ranges(beam_func), area.top_y, area.bottom_y + 1)):
        print(''.join(char(x, y, x_range) for x in area.range_x()))


def tape_to_beam_func(tape: Tape) -> BeamFunc:
    raw_func = Machine(tape).as_function_scalar(restarting=True)

    def beam_func(x: int, y: int) -> bool:
        return bool(raw_func(x, y))

    return beam_func


def testing_beam_func(xr: float, yr: float) -> BeamFunc:
    def beam_func(x: int, y: int) -> bool:
        return x <= yr * y and y <= xr * x

    return beam_func


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    beam_func = tape_to_beam_func(load_tape(input_path))
    result_1 = part_1(beam_func)
    result_2 = part_2(beam_func)
    return result_1, result_2


if __name__ == '__main__':
    main()
