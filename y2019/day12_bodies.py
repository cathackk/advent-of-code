"""
Advent of Code 2019
Day 12: The N-Body Problem
https://adventofcode.com/2019/day/12
"""

from typing import Iterable

from tqdm import tqdm

from common.math import lcm
from common.math import sgn
from common.text import parse_line
from common.xyz import Point3
from common.xyz import Vector3
from common.xyz import XYZ
from meta.aoc_tools import data_path


def part_1(positions: Iterable[Point3], steps: int = 1000) -> int:
    """
    The space near Jupiter is not a very safe place; you need to be careful of a big distracting red
    spot, extreme radiation, and a whole lot of moons swirling around. You decide to start by
    tracking the four largest moons: **Io**, **Europa**, **Ganymede**, and **Callisto**.

    After a brief scan, you calculate the **position of each moon** (your puzzle input). You just
    need to **simulate their motion** so you can avoid them.

    Each moon has a 3-dimensional position (`x`, `y`, and `z`) and a 3-dimensional velocity.
    The position of each moon is given in your scan; the `x`, `y`, and `z` velocity of each moon
    starts at `0`.

    Simulate the motion of the moons in **time steps**. Within each time step, first update the
    velocity of every moon by applying **gravity**. Then, once all moons' velocities have been
    updated, update the position of every moon by applying **velocity**. Time progresses by one step
    once all of the positions are updated.

    To apply **gravity**, consider every **pair** of moons. On each axis (`x`, `y`, and `z`), the
    velocity of each moon changes by **exactly `+1` or `-1`** to pull the moons together. For
    example, if Ganymede has an `x` position of `3`, and Callisto has a `x` position of `5`, then
    Ganymede's `x` velocity **changes by +1** (because `5 > 3`) and Callisto's `x` velocity
    **changes by -1** (because `3 < 5`). However, if the positions on a given axis are the same, the
    velocity on that axis **does not change** for that pair of moons.

    Once all gravity has been applied, apply **velocity**: simply add the velocity of each moon to
    its own position. For example, if Europa has a position of `x=1, y=2, z=3` and a velocity of
    `x=-2, y=0,z=3`, then its new position would be `x=-1, y=2, z=6`. This process does not modify
    the velocity of any moon.

        >>> Point3(1, 2, 3) + Vector3(-2, 0, 3)
        Point3(-1, 2, 6)

    For example, suppose your scan reveals the following positions:

        >>> example_1 = positions_from_text('''
        ...     <x=-1, y=0, z=2>
        ...     <x=2, y=-10, z=-7>
        ...     <x=4, y=-8, z=8>
        ...     <x=3, y=5, z=-1>
        ... ''')
        >>> example_1
        [Point3(-1, 0, 2), Point3(2, -10, -7), Point3(4, -8, 8), Point3(3, 5, -1)]

    Simulating the motion of these moons would produce the following:

        >>> final_state_1 = simulate(example_1, steps_count=10, log=True)
        After 0 steps:
        pos=<x= -1, y=  0, z=  2>, vel=<x=  0, y=  0, z=  0>
        pos=<x=  2, y=-10, z= -7>, vel=<x=  0, y=  0, z=  0>
        pos=<x=  4, y= -8, z=  8>, vel=<x=  0, y=  0, z=  0>
        pos=<x=  3, y=  5, z= -1>, vel=<x=  0, y=  0, z=  0>
        After 1 step:
        pos=<x=  2, y= -1, z=  1>, vel=<x=  3, y= -1, z= -1>
        pos=<x=  3, y= -7, z= -4>, vel=<x=  1, y=  3, z=  3>
        pos=<x=  1, y= -7, z=  5>, vel=<x= -3, y=  1, z= -3>
        pos=<x=  2, y=  2, z=  0>, vel=<x= -1, y= -3, z=  1>
        After 2 steps:
        pos=<x=  5, y= -3, z= -1>, vel=<x=  3, y= -2, z= -2>
        pos=<x=  1, y= -2, z=  2>, vel=<x= -2, y=  5, z=  6>
        pos=<x=  1, y= -4, z= -1>, vel=<x=  0, y=  3, z= -6>
        pos=<x=  1, y= -4, z=  2>, vel=<x= -1, y= -6, z=  2>
        After 3 steps:
        pos=<x=  5, y= -6, z= -1>, vel=<x=  0, y= -3, z=  0>
        pos=<x=  0, y=  0, z=  6>, vel=<x= -1, y=  2, z=  4>
        pos=<x=  2, y=  1, z= -5>, vel=<x=  1, y=  5, z= -4>
        pos=<x=  1, y= -8, z=  2>, vel=<x=  0, y= -4, z=  0>
        After 4 steps:
        pos=<x=  2, y= -8, z=  0>, vel=<x= -3, y= -2, z=  1>
        pos=<x=  2, y=  1, z=  7>, vel=<x=  2, y=  1, z=  1>
        pos=<x=  2, y=  3, z= -6>, vel=<x=  0, y=  2, z= -1>
        pos=<x=  2, y= -9, z=  1>, vel=<x=  1, y= -1, z= -1>
        After 5 steps:
        pos=<x= -1, y= -9, z=  2>, vel=<x= -3, y= -1, z=  2>
        pos=<x=  4, y=  1, z=  5>, vel=<x=  2, y=  0, z= -2>
        pos=<x=  2, y=  2, z= -4>, vel=<x=  0, y= -1, z=  2>
        pos=<x=  3, y= -7, z= -1>, vel=<x=  1, y=  2, z= -2>
        After 6 steps:
        pos=<x= -1, y= -7, z=  3>, vel=<x=  0, y=  2, z=  1>
        pos=<x=  3, y=  0, z=  0>, vel=<x= -1, y= -1, z= -5>
        pos=<x=  3, y= -2, z=  1>, vel=<x=  1, y= -4, z=  5>
        pos=<x=  3, y= -4, z= -2>, vel=<x=  0, y=  3, z= -1>
        After 7 steps:
        pos=<x=  2, y= -2, z=  1>, vel=<x=  3, y=  5, z= -2>
        pos=<x=  1, y= -4, z= -4>, vel=<x= -2, y= -4, z= -4>
        pos=<x=  3, y= -7, z=  5>, vel=<x=  0, y= -5, z=  4>
        pos=<x=  2, y=  0, z=  0>, vel=<x= -1, y=  4, z=  2>
        After 8 steps:
        pos=<x=  5, y=  2, z= -2>, vel=<x=  3, y=  4, z= -3>
        pos=<x=  2, y= -7, z= -5>, vel=<x=  1, y= -3, z= -1>
        pos=<x=  0, y= -9, z=  6>, vel=<x= -3, y= -2, z=  1>
        pos=<x=  1, y=  1, z=  3>, vel=<x= -1, y=  1, z=  3>
        After 9 steps:
        pos=<x=  5, y=  3, z= -4>, vel=<x=  0, y=  1, z= -2>
        pos=<x=  2, y= -9, z= -3>, vel=<x=  0, y= -2, z=  2>
        pos=<x=  0, y= -8, z=  4>, vel=<x=  0, y=  1, z= -2>
        pos=<x=  1, y=  1, z=  5>, vel=<x=  0, y=  0, z=  2>
        After 10 steps:
        pos=<x=  2, y=  1, z= -3>, vel=<x= -3, y= -2, z=  1>
        pos=<x=  1, y= -8, z=  0>, vel=<x= -1, y=  1, z=  3>
        pos=<x=  3, y= -6, z=  1>, vel=<x=  3, y=  2, z= -3>
        pos=<x=  2, y=  0, z=  4>, vel=<x=  1, y= -1, z= -1>
        >>> final_state_1.step
        10

    Then, it might help to calculate the **total energy in the system**. The total energy for
    a single moon is its **potential energy** multiplied by its **kinetic energy**. A moon's
    **potential energy** is the sum of the absolute values of its `x`, `y`, and `z` position
    coordinates. A moon's **kinetic energy** is the sum of the absolute values of its velocity
    coordinates. Below, each line shows the calculations for a moon's potential energy (pot),
    kinetic energy (kin), and total energy:

        >>> print(final_state_1.energy_description())  # doctest: +NORMALIZE_WHITESPACE
        Energy after 10 steps:
        pot: 2 + 1 + 3 =  6;   kin: 3 + 2 + 1 = 6;   total:  6 * 6 = 36
        pot: 1 + 8 + 0 =  9;   kin: 1 + 1 + 3 = 5;   total:  9 * 5 = 45
        pot: 3 + 6 + 1 = 10;   kin: 3 + 2 + 3 = 8;   total: 10 * 8 = 80
        pot: 2 + 0 + 4 =  6;   kin: 1 + 1 + 1 = 3;   total:  6 * 3 = 18
        Sum of total energy: 36 + 45 + 80 + 18 = 179

    In the above example, adding together the total energy for all moons after 10 steps produces
    the total energy in the system, **179**.

        >>> final_state_1.total_energy()
        179

    Here's a second example:

        >>> example_2 = positions_from_text('''
        ...     <x=-8, y=-10, z=0>
        ...     <x=5, y=5, z=10>
        ...     <x=2, y=-7, z=3>
        ...     <x=9, y=-8, z=-3>
        ... ''')

    Every ten steps of simulation for 100 steps produces:

        >>> final_state_2 = simulate(example_2, steps_count=100, log=range(0, 101, 10))
        After 0 steps:
        pos=<x= -8, y=-10, z=  0>, vel=<x=  0, y=  0, z=  0>
        pos=<x=  5, y=  5, z= 10>, vel=<x=  0, y=  0, z=  0>
        pos=<x=  2, y= -7, z=  3>, vel=<x=  0, y=  0, z=  0>
        pos=<x=  9, y= -8, z= -3>, vel=<x=  0, y=  0, z=  0>
        After 10 steps:
        pos=<x= -9, y=-10, z=  1>, vel=<x= -2, y= -2, z= -1>
        pos=<x=  4, y= 10, z=  9>, vel=<x= -3, y=  7, z= -2>
        pos=<x=  8, y=-10, z= -3>, vel=<x=  5, y= -1, z= -2>
        pos=<x=  5, y=-10, z=  3>, vel=<x=  0, y= -4, z=  5>
        After 20 steps:
        pos=<x=-10, y=  3, z= -4>, vel=<x= -5, y=  2, z=  0>
        pos=<x=  5, y=-25, z=  6>, vel=<x=  1, y=  1, z= -4>
        pos=<x= 13, y=  1, z=  1>, vel=<x=  5, y= -2, z=  2>
        pos=<x=  0, y=  1, z=  7>, vel=<x= -1, y= -1, z=  2>
        After 30 steps:
        pos=<x= 15, y= -6, z= -9>, vel=<x= -5, y=  4, z=  0>
        pos=<x= -4, y=-11, z=  3>, vel=<x= -3, y=-10, z=  0>
        pos=<x=  0, y= -1, z= 11>, vel=<x=  7, y=  4, z=  3>
        pos=<x= -3, y= -2, z=  5>, vel=<x=  1, y=  2, z= -3>
        After 40 steps:
        pos=<x= 14, y=-12, z= -4>, vel=<x= 11, y=  3, z=  0>
        pos=<x= -1, y= 18, z=  8>, vel=<x= -5, y=  2, z=  3>
        pos=<x= -5, y=-14, z=  8>, vel=<x=  1, y= -2, z=  0>
        pos=<x=  0, y=-12, z= -2>, vel=<x= -7, y= -3, z= -3>
        After 50 steps:
        pos=<x=-23, y=  4, z=  1>, vel=<x= -7, y= -1, z=  2>
        pos=<x= 20, y=-31, z= 13>, vel=<x=  5, y=  3, z=  4>
        pos=<x= -4, y=  6, z=  1>, vel=<x= -1, y=  1, z= -3>
        pos=<x= 15, y=  1, z= -5>, vel=<x=  3, y= -3, z= -3>
        After 60 steps:
        pos=<x= 36, y=-10, z=  6>, vel=<x=  5, y=  0, z=  3>
        pos=<x=-18, y= 10, z=  9>, vel=<x= -3, y= -7, z=  5>
        pos=<x=  8, y=-12, z= -3>, vel=<x= -2, y=  1, z= -7>
        pos=<x=-18, y= -8, z= -2>, vel=<x=  0, y=  6, z= -1>
        After 70 steps:
        pos=<x=-33, y= -6, z=  5>, vel=<x= -5, y= -4, z=  7>
        pos=<x= 13, y= -9, z=  2>, vel=<x= -2, y= 11, z=  3>
        pos=<x= 11, y= -8, z=  2>, vel=<x=  8, y= -6, z= -7>
        pos=<x= 17, y=  3, z=  1>, vel=<x= -1, y= -1, z= -3>
        After 80 steps:
        pos=<x= 30, y= -8, z=  3>, vel=<x=  3, y=  3, z=  0>
        pos=<x= -2, y= -4, z=  0>, vel=<x=  4, y=-13, z=  2>
        pos=<x=-18, y= -7, z= 15>, vel=<x= -8, y=  2, z= -2>
        pos=<x= -2, y= -1, z= -8>, vel=<x=  1, y=  8, z=  0>
        After 90 steps:
        pos=<x=-25, y= -1, z=  4>, vel=<x=  1, y= -3, z=  4>
        pos=<x=  2, y= -9, z=  0>, vel=<x= -3, y= 13, z= -1>
        pos=<x= 32, y= -8, z= 14>, vel=<x=  5, y= -4, z=  6>
        pos=<x= -1, y= -2, z= -8>, vel=<x= -3, y= -6, z= -9>
        After 100 steps:
        pos=<x=  8, y=-12, z= -9>, vel=<x= -7, y=  3, z=  0>
        pos=<x= 13, y= 16, z= -3>, vel=<x=  3, y=-11, z= -5>
        pos=<x=-29, y=-11, z= -1>, vel=<x= -3, y=  7, z=  4>
        pos=<x= 16, y=-13, z= 23>, vel=<x=  7, y=  1, z=  1>
        >>> print(final_state_2.energy_description())  # doctest: +NORMALIZE_WHITESPACE
        Energy after 100 steps:
        pot:  8 + 12 +  9 = 29;   kin: 7 +  3 + 0 = 10;   total: 29 * 10 = 290
        pot: 13 + 16 +  3 = 32;   kin: 3 + 11 + 5 = 19;   total: 32 * 19 = 608
        pot: 29 + 11 +  1 = 41;   kin: 3 +  7 + 4 = 14;   total: 41 * 14 = 574
        pot: 16 + 13 + 23 = 52;   kin: 7 +  1 + 1 =  9;   total: 52 *  9 = 468
        Sum of total energy: 290 + 608 + 574 + 468 = 1940

    **What is the total energy in the system** after simulating the moons given in your scan for
    1000 steps?

        >>> part_1(example_2, steps=100)
        part 1: after 100 steps, total energy is 1940
        1940
    """

    result = simulate(positions, steps_count=steps).total_energy()

    print(f"part 1: after {steps} steps, total energy is {result}")
    return result


def part_2(positions: Iterable[Point3]) -> int:
    """
    All this drifting around in space makes you wonder about the nature of the universe. Does
    history really repeat itself? You're curious whether the moons will ever return to a previous
    state.

    Determine **the number of steps** that must occur before all of the moons' positions and
    velocities exactly match a previous point in time.

    For example, the first example above takes `2772` steps before they exactly match a previous
    point in time; it eventually returns to the initial state:

        >>> example_1 = positions_from_file(data_path(__file__, 'example-1.txt'))
        >>> steps_until_repeat(example_1)
        2772
        >>> final_state_1 = simulate(example_1, log=[0, 2770, 2771, 2772])
        After 0 steps:
        pos=<x= -1, y=  0, z=  2>, vel=<x=  0, y=  0, z=  0>
        pos=<x=  2, y=-10, z= -7>, vel=<x=  0, y=  0, z=  0>
        pos=<x=  4, y= -8, z=  8>, vel=<x=  0, y=  0, z=  0>
        pos=<x=  3, y=  5, z= -1>, vel=<x=  0, y=  0, z=  0>
        After 2770 steps:
        pos=<x=  2, y= -1, z=  1>, vel=<x= -3, y=  2, z=  2>
        pos=<x=  3, y= -7, z= -4>, vel=<x=  2, y= -5, z= -6>
        pos=<x=  1, y= -7, z=  5>, vel=<x=  0, y= -3, z=  6>
        pos=<x=  2, y=  2, z=  0>, vel=<x=  1, y=  6, z= -2>
        After 2771 steps:
        pos=<x= -1, y=  0, z=  2>, vel=<x= -3, y=  1, z=  1>
        pos=<x=  2, y=-10, z= -7>, vel=<x= -1, y= -3, z= -3>
        pos=<x=  4, y= -8, z=  8>, vel=<x=  3, y= -1, z=  3>
        pos=<x=  3, y=  5, z= -1>, vel=<x=  1, y=  3, z= -1>
        After 2772 steps:
        pos=<x= -1, y=  0, z=  2>, vel=<x=  0, y=  0, z=  0>
        pos=<x=  2, y=-10, z= -7>, vel=<x=  0, y=  0, z=  0>
        pos=<x=  4, y= -8, z=  8>, vel=<x=  0, y=  0, z=  0>
        pos=<x=  3, y=  5, z= -1>, vel=<x=  0, y=  0, z=  0>
        >>> final_state_1.step
        2772

    Of course, the universe might last for a very long time before repeating. The second example
    from above takes `4686774924` steps before it repeats a previous state!

        >>> example_2 = positions_from_file(data_path(__file__, 'example-2.txt'))
        >>> steps_until_repeat(example_2)
        4686774924

    Clearly, you might need to **find a more efficient way to simulate the universe**.

    **How many steps does it take** to reach the first state that exactly matches a previous state?

        >>> part_2(example_2)
        part 2: it takes 4686774924 steps to match a previous state
        4686774924
    """

    result = steps_until_repeat(positions)

    print(f"part 2: it takes {result} steps to match a previous state")
    return result


Body = tuple[Point3, Vector3]


class State:
    def __init__(
        self,
        positions: Iterable[Point3],
        velocities: Iterable[Vector3] = None,
        step: int = 0
    ):
        self.positions = list(positions)
        if velocities is None:
            self.velocities = [Vector3.null()] * len(self.positions)
        else:
            self.velocities = list(velocities)
        self.step = step

        assert len(self.positions) == len(self.velocities)

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, type(self)) and
            self.positions == other.positions and
            self.velocities == other.velocities
        )

    def bodies(self) -> Iterable[Body]:
        return zip(self.positions, self.velocities)

    def next_state(self) -> 'State':
        def sgn_v3(vector: Vector3) -> Vector3:
            return Vector3(*(sgn(v) for v in vector))

        new_velocities = [
            vel_1 + sum((
                sgn_v3(pos_1.to(pos_2))
                for index_2, pos_2 in enumerate(self.positions)
                if index_1 != index_2
            ), start=Vector3.null())
            for index_1, (pos_1, vel_1) in enumerate(self.bodies())
        ]

        new_positions = (pos + vel for pos, vel in zip(self.positions, new_velocities))

        return type(self)(new_positions, new_velocities, self.step + 1)

    def total_energy(self) -> int:
        return sum(
            sum(abs(v) for v in pos) * sum(abs(v) for v in vel)
            for pos, vel in self.bodies()
        )

    def __str__(self) -> str:
        def lines() -> Iterable[str]:
            if self.step == 1:
                yield f"After 1 step:"
            else:
                yield f"After {self.step} steps:"

            yield from (
                f"pos={pos:<3>=}, vel={vel:<3>=}"
                for pos, vel in self.bodies()
            )

        return "\n".join(lines())

    def energy_description(self) -> str:
        def format_sum(xyz: XYZ) -> tuple[str, int]:
            sum_str = " + ".join(str(abs(v)).rjust(2) for v in xyz)
            sum_int = sum(abs(v) for v in xyz)
            return f"{sum_str} = {sum_int:2}", sum_int

        def lines() -> Iterable[str]:
            yield f"Energy after {self.step} steps:"
            totals = []
            for pos, vel in self.bodies():
                pot_str, pot = format_sum(pos)
                kin_str, kin = format_sum(vel)
                total_str = f"{pot:2} * {kin}"
                total = pot * kin
                yield f"pot: {pot_str};   kin: {kin_str};   total: {total_str} = {total:2}"
                totals.append(total)

            totals_sum = " + ".join(str(v) for v in totals)
            result = sum(totals)
            yield f"Sum of total energy: {totals_sum} = {result}"

        return "\n".join(lines())


def simulate(
    positions: Iterable[Point3],
    steps_count: int = 0,
    log: bool | Iterable[int] = False,
    desc: str = "simulating"
) -> State:
    init_state = State(positions)

    def log_state(state_: State) -> None:
        if log is False:
            return
        if log is True or state_.step in log:
            print(state_)

    progress = tqdm(unit_scale=True, unit=" steps", delay=1.0, desc=desc)
    if steps_count:
        progress.total = steps_count

    state = init_state
    while True:
        log_state(state)
        if steps_count and state.step >= steps_count:
            return state
        if state.step > 0 and state == init_state:
            return state
        state = state.next_state()
        progress.update()


def steps_until_repeat(positions: Iterable[Point3]) -> int:
    # idea: run simulations for each of the three dimensions apart
    #       and return LCM of the resulting periods

    positions = list(positions)

    def simulate_single_dimension(dim: int) -> int:
        single_dim_positions = (
            Point3(*(val if index == dim else 0 for index, val in enumerate(pos)))
            for pos in positions
        )
        dim_name = chr(ord('x') + dim)
        final_state = simulate(
            positions=single_dim_positions,
            desc=f"calculating {dim_name} period"
        )
        return final_state.step

    return lcm(*(simulate_single_dimension(d) for d in range(3)))


def positions_from_text(text: str) -> list[Point3]:
    return list(positions_from_lines(text.strip().splitlines()))


def positions_from_file(fn: str) -> list[Point3]:
    return list(positions_from_lines(open(fn)))


def positions_from_lines(lines: Iterable[str]) -> Iterable[Point3]:
    for line in lines:
        x, y, z = parse_line(line.strip(), '<x=$, y=$, z=$>')
        yield Point3(int(x), int(y), int(z))


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    positions = positions_from_file(input_path)
    result_1 = part_1(positions)
    result_2 = part_2(positions)
    return result_1, result_2


if __name__ == '__main__':
    main()
