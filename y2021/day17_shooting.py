"""
Advent of Code 2021
Day 17: Trick Shot
https://adventofcode.com/2021/day/17
"""

from math import sqrt
from typing import Iterable

from rect import Rect
from utils import last
from utils import parse_line
from utils import sgn
from utils import single_value


def part_1(target: Rect) -> int:
    """
    Ahead of you is what appears to be a large ocean trench. Could the keys have fallen into it?
    You'd better send a probe to investigate.

    The probe launcher on your submarine can fire the probe with any integer velocity in the `x`
    (forward) and `y` (upward, or downward if negative) directions. For example, an initial `x,y`
    velocity like `0,10` would fire the probe straight up, while an initial velocity like `10,-1`
    would fire the probe forward at a slight downward angle.

    The probe's `x,y` position starts at `0,0`. Then, it will follow some trajectory by moving in
    **steps**. On each step, these changes occur in the following order:

      - The probe's `x` position increases by its `x` velocity.
      - The probe's `y` position increases by its `y` velocity.
      - Due to drag, the probe's `x` velocity changes by `1` toward the value `0`; that is, it
        decreases by `1` if it is greater than `0`, increases by `1` if it is less than `0`, or does
        not change if it is already `0`.
      - Due to gravity, the probe's `y` velocity decreases by `1`.

    For the probe to successfully make it into the trench, the probe must be on some trajectory that
    causes it to be within a **target area** after any step. The submarine computer has already cal-
    culated this target area (your puzzle input). For example:

        >>> (target_area := target_area_from_text('target area: x=20..30, y=-10..-5'))
        Rect((20, -10), (30, -5))

    This target area means that you need to find initial `x,y` velocity values such that after any
    step, the probe's `x` position is at least `20` and at most `30`, and the probe's `y` position
    is at least `-10` and at most `-5`.

    Given this target area, one initial velocity that causes the probe to be within the target area
    after any step is `7,2`:

        >>> draw_trajectory(initial_velocity=(7, 2), target=target_area)
        ·············#····#············
        ·······#··············#········
        ·······························
        S························#·····
        ·······························
        ·······························
        ···························#···
        ·······························
        ····················TTTTTTTTTTT
        ····················TTTTTTTTTTT
        ····················TTTTTTTT#TT
        ····················TTTTTTTTTTT
        ····················TTTTTTTTTTT
        ····················TTTTTTTTTTT

    In this diagram, `S` is the probe's initial position, `0,0`. The `x` coordinate increases to
    the right, and the `y` coordinate increases upward. In the bottom right, positions that are
    within the target area are shown as `T`. After each step (until the target area is reached),
    the position of the probe is marked with `#`. (The bottom-right `#` is both a position the probe
    reaches and a position in the target area.)

    Another initial velocity that causes the probe to be within the target area after any step is:

        >>> draw_trajectory((6, 3), target_area)
        ···············#··#············
        ···········#········#··········
        ·······························
        ······#··············#·········
        ·······························
        ·······························
        S····················#·········
        ·······························
        ·······························
        ·······························
        ·····················#·········
        ····················TTTTTTTTTTT
        ····················TTTTTTTTTTT
        ····················TTTTTTTTTTT
        ····················TTTTTTTTTTT
        ····················T#TTTTTTTTT
        ····················TTTTTTTTTTT

    Another one is:

        >>> draw_trajectory((9, 0), target_area)
        S········#·····················
        ·················#·············
        ·······························
        ························#······
        ·······························
        ····················TTTTTTTTTTT
        ····················TTTTTTTTTT#
        ····················TTTTTTTTTTT
        ····················TTTTTTTTTTT
        ····················TTTTTTTTTTT
        ····················TTTTTTTTTTT

    One initial velocity that doesn't cause the probe to be within the target area after any step:

        >>> draw_trajectory((17, -4), target_area)
        S·································
        ··································
        ··································
        ··································
        ·················#················
        ····················TTTTTTTTTTT···
        ····················TTTTTTTTTTT···
        ····················TTTTTTTTTTT···
        ····················TTTTTTTTTTT···
        ····················TTTTTTTTTTT··#
        ····················TTTTTTTTTTT···

    The probe appears to pass through the target area, but is never within it after any step.
    Instead, it continues down and to the right - only the first few steps are shown.

    If you're going to fire a highly scientific probe out of a super cool probe launcher, you might
    as well do it with **style**. How high can you make the probe go while still reaching the target
    area?

    In the above example, using an initial velocity of `6,9` is the best you can do, causing the
    probe to reach a maximum `y` position of **`45`**. (Any higher initial y velocity causes the
    probe to overshoot the target area entirely.)

    Find the initial velocity that causes the probe to reach the highest `y` position and still
    eventually be within the target area after any step. **What is the highest `y` position it
    reaches on this trajectory?**

        >>> part_1(target_area)
        part 1: the probe reaches y=45 using initial velocity (6, 9)
        45
    """

    max_y, v0 = highest_y(target)
    assert does_hit(v0, target)

    print(f"part 1: the probe reaches y={max_y} using initial velocity {v0}")
    return max_y


def part_2(target: Rect) -> int:
    """
    Maybe a fancy trick shot isn't the best idea; after all, you only have one probe, so you had
    better not miss.

    To get the best idea of what your options are for launching the probe, you need to find **every
    initial velocity** that causes the probe to eventually be within the target area after any step.

    In the above example, there are **112** different initial velocity values that meet these
    criteria:

        >>> target_area = Rect((20, -10), (30, -5))
        >>> vs = list(hitting_velocities(target_area))
        >>> len(vs)
        112
        >>> vs  # doctest: +NORMALIZE_WHITESPACE
        [(20, -10), (21, -10), (22, -10), (23, -10), (24, -10), (25, -10), (26, -10), (27, -10),
         (28, -10), (29, -10), (30, -10), (20, -9), (21, -9), (22, -9), (23, -9), (24, -9),
         (25, -9), (26, -9), (27, -9), (28, -9), (29, -9), (30, -9), (20, -8), (21, -8), (22, -8),
         (23, -8), (24, -8), (25, -8), (26, -8), (27, -8), (28, -8), (29, -8), (30, -8), (20, -7),
         (21, -7), (22, -7), (23, -7), (24, -7), (25, -7), (26, -7), (27, -7), (28, -7), (29, -7),
         (30, -7), (20, -6), (21, -6), (22, -6), (23, -6), (24, -6), (25, -6), (26, -6), (27, -6),
         (28, -6), (29, -6), (30, -6), (20, -5), (21, -5), (22, -5), (23, -5), (24, -5), (25, -5),
         (26, -5), (27, -5), (28, -5), (29, -5), (30, -5), (11, -4), (12, -4), (13, -4), (14, -4),
         (15, -4), (11, -3), (12, -3), (13, -3), (14, -3), (15, -3), (8, -2), (9, -2), (10, -2),
         (11, -2), (12, -2), (13, -2), (14, -2), (15, -2), (7, -1), (8, -1), (9, -1), (10, -1),
         (11, -1), (6, 0), (7, 0), (8, 0), (9, 0), (6, 1), (7, 1), (8, 1), (6, 2), (7, 2), (6, 3),
         (7, 3), (6, 4), (7, 4), (6, 5), (7, 5), (6, 6), (7, 6), (6, 7), (7, 7), (6, 8), (7, 8),
         (6, 9), (7, 9)]

    **How many distinct initial velocity values cause the probe to be within the target area after
    any step?**

        >>> part_2(target_area)
        part 2: there are 112 distinct initial velocities to hit target
        112
    """

    result = sum(1 for _ in hitting_velocities(target))

    print(f"part 2: there are {result} distinct initial velocities to hit target")
    return result


Vector = tuple[int, int]
Pos = tuple[int, int]


def shoot(initial_velocity: Vector, target: Rect) -> Iterable[Pos]:
    assert target.top_y < 0
    assert target.left_x > 0

    x, y = 0, 0
    vx, vy = initial_velocity

    while True:
        x += vx
        y += vy
        vx -= sgn(vx)
        vy -= 1
        yield x, y

        # hit!
        if (x, y) in target:
            break

        # overshoot :(
        if x > target.right_x:
            break
        if y < target.top_y:
            break


def draw_trajectory(initial_velocity: Vector, target: Rect) -> None:
    steps = list(shoot(initial_velocity, target))

    origin = (0, 0)
    bounds = Rect.with_all([origin, target.top_left, target.bottom_right] + steps)

    def ch(pos: Pos) -> str:
        if pos == origin:
            return 'S'
        elif pos in steps:
            return '#'
        elif pos in target:
            return 'T'
        else:
            return '·'

    for y in reversed(bounds.range_y()):
        print(''.join(ch((x, y)) for x in bounds.range_x()))


def does_hit(initial_velocity: Vector, target: Rect) -> bool:
    return last(shoot(initial_velocity, target)) in target


def highest_y(target: Rect) -> tuple[int, Vector]:
    """
    Finds the initial velocity to hit the target while reaching the highest possibly `y`.
    """

    # find any `vx_0` that will eventually stall to `vx=0` when `x` is in the target x range
    # e.g. target x=12..20
    #   - vx_0=4 (0:4, 4:3, 7:2, 9:1, 10:0) doesn't reach
    #   - vx_0=5 (0:5, 5:4, 9:3, 12:2, 14:1, 15:0) stalls at x=15 ok
    #   - vx_0=6 (0:6, 6:5, 11:4, 15:3, 18:2, 20:1, 21:0) overshoot

    vx_0 = triangular_root(target.left_x) + 1
    if not triangular(vx_0) in target.range_x():
        # not possible to "stall" x in target area -> still possible to shoot into target, but
        # this calculation is not supported
        raise ValueError(f"unable to stall x in {target.range_x()}")

    # one step after the projectile returns to `y=0`, it will hit the bottom of the target y range
    # e.g. target y=-20..-30
    # -> vy_0=28 (0:28, 28:27, 55:26, ..., 405:1, tr(28)=406:0, 406:-1, ..., 0:-29, -29:-30) hit
    # -> vy_0=29 (0:29, 29:28, 57:27, ..., 434:1, tr(29)=435:0, 435:-1, ..., 0:-30, -30:-31) hit
    # -> vy_0=30 (0:30, 30:29, 59:28, ..., 464:1, tr(30)=465:0, 465:-1, ..., 0:-31, -31:-32) miss
    # => max_y=435 using vy_0=29 (tr(29)=435)

    # target.top_y is actually the bottom part of the target because y-axis is inverted
    assert target.top_y < 0
    vy_0 = -target.top_y - 1
    max_y = triangular(vy_0)

    return max_y, (vx_0, vy_0)


def triangular(n: int) -> int:
    """
        >>> triangular(4)
        10
        >>> triangular(5)
        15
        >>> triangular(100)
        5050
    """
    assert n >= 0
    return (n * (n + 1)) // 2


def triangular_root(t: int) -> int:
    """
    Given a number `t`, find `n` such that `tr(n) <= t < tr(n+1)`.

    Perfect roots:

        >>> triangular_root(10)
        4
        >>> triangular_root(15)
        5
        >>> triangular_root(5050)
        100

    Close roots:

    tr(4) = 10 <= 12 < 15 = tr(4+1)

        >>> triangular_root(12)
        4

    tr(44) = 990 <= 1000 < 1035 = tr(44+1)

        >>> triangular_root(1000)
        44
        >>> triangular_root(990)
        44
        >>> triangular_root(1034)
        44
        >>> triangular_root(1035)
        45
    """

    # (n+1) * (n/2) = t
    # (n^2 + n) / 2 = t
    #     4n^2 + 4n = 8t
    # 4n^2 + 4n + 1 = 8t + 1
    #    (2n + 1)^2 = 8t + 1
    #        2n + 1 = sqrt(8t + 1)
    #            2n = sqrt(8t + 1) - 1
    #             n = (sqrt(8t + 1) - 1) / 2

    return int((sqrt(8 * t + 1) - 1) / 2)


def hitting_velocities(target: Rect) -> Iterable[Vector]:
    # brute force! we just need to establish some boundaries:

    # min x ... stall x from part 1
    min_vx0 = triangular_root(target.left_x)
    # max x .... shoot directly to target right edge
    max_vx0 = target.right_x
    # min y ... shoot directly to target bottom
    # (note that target.top_y is actually bottom because y-axis is inverted)
    min_vy0 = target.top_y
    # max y ... use know-how from part 1
    max_vy0 = -target.top_y - 1

    velocities = Rect((min_vx0, min_vy0), (max_vx0, max_vy0))

    return (v0 for v0 in velocities if does_hit(v0, target))


def target_area_from_text(text: str) -> Rect:
    # target area: x=20..30, y=-10..-5
    x1, x2, y1, y2 = parse_line(text.strip(), 'target area: x=$..$, y=$..$')
    return Rect((int(x1), int(y1)), (int(x2), int(y2)))


def target_area_from_file(fn: str) -> Rect:
    return target_area_from_text(single_value(open(fn)).strip())


if __name__ == '__main__':
    target_ = target_area_from_file('data/17-input.txt')
    part_1(target_)
    part_2(target_)
