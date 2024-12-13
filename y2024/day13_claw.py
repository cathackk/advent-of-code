"""
Advent of Code 2024
Day 13: Claw Contraption
https://adventofcode.com/2024/day/13
"""
from dataclasses import dataclass, replace
from typing import Iterable, Self

from common.file import relative_path
from common.text import line_groups, parse_line
from common.xy import Point, Vector


def part_1(machines: Iterable['Machine']) -> int:
    """
    Next up: the lobby (y2020/day24_hex.py) of a resort on a tropical island. The Historians take
    a moment to admire the hexagonal floor tiles before spreading out.

    Fortunately, it looks like the resort has a new arcade! Maybe you can win some prizes from
    the claw machines?

    The claw machines here are a little unusual. Instead of a joystick or directional buttons to
    control the claw, these machines have two buttons labeled `A` and `B`. Worse, you can't just put
    in a token and play; it costs **3 tokens** to push the `A` button and **1 token** to push
    the `B` button.

    With a little experimentation, you figure out that each machine's buttons are configured to move
    the claw a specific amount to the **right** (along the `X` axis) and a specific amount
    **forward** (along the `Y` axis) each time that button is pressed.

    Each machine contains one prize; to win the **prize**, the claw must be positioned **exactly**
    above the prize on both the `X` and `Y` axes.

    You wonder: what is the smallest number of tokens you would have to spend to win as many prizes
    as possible? You assemble a list of every machine's button behavior and prize location (your
    puzzle input). For example:


        >>> example = Machine.many_from_text('''
        ...     Button A: X+94, Y+34
        ...     Button B: X+22, Y+67
        ...     Prize: X=8400, Y=5400
        ...
        ...     Button A: X+26, Y+66
        ...     Button B: X+67, Y+21
        ...     Prize: X=12748, Y=12176
        ...
        ...     Button A: X+17, Y+86
        ...     Button B: X+84, Y+37
        ...     Prize: X=7870, Y=6450
        ...
        ...     Button A: X+69, Y+23
        ...     Button B: X+27, Y+71
        ...     Prize: X=18641, Y=10279
        ... ''')
        >>> len(example)
        4

    This list describes the button configuration and prize location of four different claw machines.

    For now, consider just the first claw machine in the list:

        >>> machine_0 = example[0]

      - Pushing the machine's `A` button would move the claw
        `94` units along the `X` axis and `34` units along the `Y` axis:

        >>> machine_0.button_a
        Vector(94, 34)

      - Pushing the `B` button would move the claw
        `22` units along the `X` axis and `67` units along the `Y` axis:

        >>> machine_0.button_b
        Vector(22, 67)

      - The prize is located at `X=8400, Y=5400`; this means that from the claw's initial position,
        it would need to move exactly `8400` units along the `X` axis and exactly `5400` units along
        the `Y` axis to be perfectly aligned with the prize in this machine:

        >>> machine_0.prize_at
        Point(8400, 5400)

    The cheapest way to win the prize is by pushing the `A` button `80` times and the `B` button
    `40` times. This would line up the claw along the `X` axis (because `80*94 + 40*22 = 8400`) and
    along the Y axis (because `80*34 + 40*67 = 5400`).

        >>> machine_0.solve()
        Solution(a_pushes=80, b_pushes=40)

    Doing this would cost `80*3` tokens for the `A` presses and `40*1` for the `B` presses,
    a total of **`280`** tokens:

        >>> _.cost()
        280

    For the second and fourth claw machines, there is no combination of A and B presses that will
    ever win a prize:

        >>> example[1].solve() is None
        True
        >>> example[3].solve() is None
        True

    For the third claw machine, the cheapest way to win the prize is by pushing the `A` button
    `38` times and the `B` button `86` times. Doing this would cost a total of **`200`** tokens:

        >>> example[2].solve()
        Solution(a_pushes=38, b_pushes=86)
        >>> _.cost()
        200

    So, the most prizes you could possibly win is two; the minimum tokens you would have to spend
    to win all (two) prizes is **`480`**.

        >>> sum(sol.cost() for m in example if (sol := m.solve()))
        480

    You estimate that each button would need to be pressed **no more than `100` times** to win
    a prize. How else would someone be expected to play?

    Figure out how to win as many prizes as possible.
    **What is the fewest tokens you would have to spend to win all possible prizes?**

        >>> part_1(example)
        part 1: you can win 2 out of 4 prizes by spending 480 tokens
        480
    """

    machines_list = list(machines)
    solutions = [sol for m in machines_list if (sol := m.solve())]
    result = sum(sol.cost() for sol in solutions)

    print(
        f"part 1: "
        f"you can win {len(solutions)} out of {len(machines_list)} prizes "
        f"by spending {result} tokens"
    )
    return result


def part_2(machines: Iterable['Machine'], adjustment: int = 10_000_000_000_000) -> int:
    r"""
    As you go to win the first prize, you discover that the claw is nowhere near where you expected
    it would be. Due to a unit conversion error in your measurements, the position of every prize is
    actually `10_000_000_000_000` higher on both the `X` and `Y` axis!

    Add `10_000_000_000_000` to the `X` and `Y` position of every prize. After making this change,
    the example above would now look like this:

        >>> example = Machine.many_from_file('data/13-example.txt')
        >>> example_adjusted = [m.prize_adjusted(10_000_000_000_000) for m in example]
        >>> print("\n\n".join(str(m) for m in example_adjusted))
        Button A: X+94, Y+34
        Button B: X+22, Y+67
        Prize: X=10000000008400, Y=10000000005400
        <BLANKLINE>
        Button A: X+26, Y+66
        Button B: X+67, Y+21
        Prize: X=10000000012748, Y=10000000012176
        <BLANKLINE>
        Button A: X+17, Y+86
        Button B: X+84, Y+37
        Prize: X=10000000007870, Y=10000000006450
        <BLANKLINE>
        Button A: X+69, Y+23
        Button B: X+27, Y+71
        Prize: X=10000000018641, Y=10000000010279

    Now, it is only possible to win a prize on the second and fourth claw machines. Unfortunately,
    it will take **many more than `100` presses** to do so.

        >>> [m.solve() is not None for m in example_adjusted]
        [False, True, False, True]

    Using the corrected prize coordinates, figure out how to win as many prizes as possible.
    **What is the fewest tokens you would have to spend to win all possible prizes?**

        >>> part_2(example)
        part 2: you can win 2 out of 4 prizes by spending 875318608908 tokens
        875318608908
    """

    machines_adjusted = [m.prize_adjusted(adjustment) for m in machines]
    solutions = [sol for m in machines_adjusted if (sol := m.solve())]
    result = sum(sol.cost() for sol in solutions)

    print(
        f"part 2: "
        f"you can win {len(solutions)} out of {len(machines_adjusted)} prizes "
        f"by spending {result} tokens"
    )
    return result


@dataclass(frozen=True)
class Solution:
    a_pushes: int
    b_pushes: int

    def cost(self) -> int:
        return 3 * self.a_pushes + self.b_pushes


@dataclass(frozen=True)
class Machine:
    button_a: Vector
    button_b: Vector
    prize_at: Point

    def solve(self) -> Solution | None:
        x_a, y_a = self.button_a
        x_b, y_b = self.button_b
        x_p, y_p = self.prize_at

        # two equations with two variables (`a_pushes`, `b_pushes`):
        #     (1)  x_p = a_pushes * x_a + b_pushes * x_b
        #     (2)  y_p = a_pushes * y_a + b_pushes * y_b
        #
        # multiply (1) with `y_a` and (2) with `x_a`:
        #     (1')  x_p * y_a = (a_pushes * x_a * y_a) + (b_pushes * x_b * y_a)
        #     (2')  x_a * y_p = (a_pushes * x_a * y_a) + (b_pushes * x_a * y_b)
        #
        # subtract (2') from (1'):
        #     (1'-2')  (x_p * y_a - x_a * y_p) = b_pushes * (x_b * y_a - x_a * y_b)
        #
        # and thus:
        #                x_p * y_a - x_a * y_p
        #     b_pushes = ---------------------
        #                x_b * y_a - x_a * y_b
        #
        b_num = (x_p * y_a - x_a * y_p)
        b_den = (x_b * y_a - x_a * y_b)
        if b_num % b_den != 0:
            return None
        b_pushes = b_num // b_den

        # now that we know `b_pushes`, we can simply deduct `a_pushes` from (1):
        #     (1) x_p = a_pushes * x_a + b_pushes * x_b
        #
        # which becomes:
        #                x_p - b_pushes * x_b
        #     a_pushes = --------------------
        #                        x_a
        #
        a_num = x_p - b_pushes * x_b
        if a_num % x_a != 0:
            return None
        a_pushes = a_num // x_a

        # make sure the solution works
        assert self.prize_at == Point(0, 0) + a_pushes * self.button_a + b_pushes * self.button_b

        return Solution(a_pushes, b_pushes)

    def prize_adjusted(self, delta: int) -> Self:
        return replace(self, prize_at=self.prize_at + Vector(delta, delta))

    def to_lines(self) -> Iterable[str]:
        yield f"Button A: X+{self.button_a.x}, Y+{self.button_a.y}"
        yield f"Button B: X+{self.button_b.x}, Y+{self.button_b.y}"
        yield f"Prize: X={self.prize_at.x}, Y={self.prize_at.y}"

    def __str__(self) -> str:
        return "\n".join(self.to_lines())

    @classmethod
    def many_from_file(cls, fn: str) -> list[Self]:
        return list(cls.many_from_lines(open(relative_path(__file__, fn))))

    @classmethod
    def many_from_text(cls, text: str) -> list[Self]:
        return list(cls.many_from_lines(text.strip().splitlines()))

    @classmethod
    def many_from_lines(cls, lines: Iterable[str]) -> Iterable[Self]:
        # Button A: X+94, Y+34
        # Button B: X+22, Y+67
        # Prize: X=8400, Y=5400

        for line_a, line_b, line_prize in line_groups(lines):
            button_a = parse_line(line_a, "Button A: X+$, Y+$")
            button_b = parse_line(line_b, "Button B: X+$, Y+$")
            prize_at = parse_line(line_prize, "Prize: X=$, Y=$")
            yield cls(
                button_a=Vector(*button_a),
                button_b=Vector(*button_b),
                prize_at=Point(*prize_at),
            )


def main(input_fn: str = 'data/13-input.txt') -> tuple[int, int]:
    machines = Machine.many_from_file(input_fn)
    result_1 = part_1(machines)
    result_2 = part_2(machines)
    return result_1, result_2


if __name__ == '__main__':
    main()
