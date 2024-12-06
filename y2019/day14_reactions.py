"""
Advent of Code 2019
Day 14: Space Stoichiometry
https://adventofcode.com/2019/day/14
"""

from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Self

from common.bsrange import BSRange
from common.maths import ceildiv
from meta.aoc_tools import data_path


def part_1(recipes: Iterable['Recipe'], goal: 'Amount' = (1, 'FUEL')) -> int:
    """
    As you approach the rings of Saturn, your ship's **low fuel** indicator turns on. There isn't
    any fuel here, but the rings have plenty of raw material. Perhaps your ship's Inter-Stellar
    Refinery Union brand **nanofactory** can turn these raw materials into fuel.

    You ask the nanofactory to produce a list of the **reactions** it can perform that are relevant
    to this process (your puzzle input). Every reaction turns some quantities of specific **input
    chemicals** into some quantity of an **output chemical**. Almost every **chemical** is produced
    by exactly one reaction; the only exception, `ORE`, is the raw material input to the entire
    process and is not produced by a reaction.

    You just need to know how much **`ORE`** you'll need to collect before you can produce one unit
    of **`FUEL`**.

    Each reaction gives specific quantities for its inputs and output; reactions cannot be partially
    run, so only whole integer multiples of these quantities can be used. (It's okay to have
    leftover chemicals when you're done, though.) For example, the reaction `1 A, 2 B, 3 C => 2 D`
    means that exactly 2 units of chemical `D` can be produced by consuming exactly `1 A`, `2 B`
    and `3 C`.

        >>> Recipe.from_line('1 A, 2 B, 3 C => 2 D')
        Recipe(ins=[(1, 'A'), (2, 'B'), (3, 'C')], out=(2, 'D'))

    You can run the full reaction as many times as necessary; for example, you could produce `10 D`
    by consuming `5 A`, `10 B`, and `15 C`.

    Suppose your nanofactory produces the following list of reactions:

        >>> example_1 = recipes_from_text('''
        ...     10 ORE => 10 A
        ...     1 ORE => 1 B
        ...     7 A, 1 B => 1 C
        ...     7 A, 1 C => 1 D
        ...     7 A, 1 D => 1 E
        ...     7 A, 1 E => 1 FUEL
        ... ''')
        >>> example_1  # doctest: +NORMALIZE_WHITESPACE
        [Recipe(ins=[(10, 'ORE')], out=(10, 'A')),
         Recipe(ins=[(1, 'ORE')], out=(1, 'B')),
         Recipe(ins=[(7, 'A'), (1, 'B')], out=(1, 'C')),
         Recipe(ins=[(7, 'A'), (1, 'C')], out=(1, 'D')),
         Recipe(ins=[(7, 'A'), (1, 'D')], out=(1, 'E')),
         Recipe(ins=[(7, 'A'), (1, 'E')], out=(1, 'FUEL'))]

    The first two reactions use only `ORE` as inputs; they indicate that you can produce as much of
    chemical `A` as you want (in increments of 10 units, each 10 costing 10 `ORE`) and as much
    of chemical `B` as you want (each costing 1 `ORE`).

        >>> production_cost(example_1, (10, 'A'))
        (10, 'ORE')
        >>> production_cost(example_1, (15, 'A'))
        (20, 'ORE')
        >>> production_cost(example_1, (15, 'B'))
        (15, 'ORE')

    To produce 1 `FUEL`, a total of **31** `ORE` is required: 1 `ORE` to produce 1 `B`, then 30 more
    `ORE` to produce the `7 + 7 + 7 + 7 = 28 A` (with 2 extra `A` wasted) required in the reactions
    to convert the `B` into `C`, `C` into `D`, `D` into `E`, and finally `E` into `FUEL`.
    (30 `A` is produced because its reaction requires that it is created in increments of 10.)

        >>> production_cost(example_1, (1, 'FUEL'))
        (31, 'ORE')

    Or, suppose you have the following list of reactions:

        >>> example_2 = recipes_from_text('''
        ...     9 ORE => 2 A
        ...     8 ORE => 3 B
        ...     7 ORE => 5 C
        ...     3 A, 4 B => 1 AB
        ...     5 B, 7 C => 1 BC
        ...     4 C, 1 A => 1 CA
        ...     2 AB, 3 BC, 4 CA => 1 FUEL
        ... ''')

    The above list of reactions requires 165 `ORE` to produce 1 `FUEL`:

      - Consume 45 `ORE` to produce 10 `A`:

        >>> production_cost(example_2, (10, 'A'))
        (45, 'ORE')

      - Consume 64 `ORE` to produce 24 `B`:

        >>> production_cost(example_2, (24, 'B'))
        (64, 'ORE')

      - Consume 56 `ORE` to produce 40 `C`:

        >>> production_cost(example_2, (40, 'C'))
        (56, 'ORE')

      - Consume 6 `A`, 8 `B` to produce 2 `AB`.
      - Consume 15 `B`, 21 `C` to produce 3 `BC`.
      - Consume 16 `C`, 4 `A` to produce 4 `CA`.
      - Consume 2 `AB`, 3 `BC`, 4 `CA` to produce 1 `FUEL`:

        >>> production_cost(example_2, (1, 'FUEL'))
        (165, 'ORE')

    Here are some larger examples:

        >>> production_cost(recipes_from_file(data_path(__file__, 'example-3.txt')))
        (13312, 'ORE')
        >>> production_cost(recipes_from_file(data_path(__file__, 'example-4.txt')))
        (180697, 'ORE')
        >>> production_cost(recipes_from_file(data_path(__file__, 'example-5.txt')))
        (2210736, 'ORE')

    Given the list of reactions in your puzzle input, what is the **minimum amount of `ORE` required
    to produce exactly 1 `FUEL`?**

        >>> part_1(example_1)
        part 1: you need 31 ORE to produce 1 FUEL
        31
    """

    result, ore = production_cost(recipes, goal)
    assert ore == 'ORE'

    goal_volume, goal_code = goal
    print(f"part 1: you need {result} {ore} to produce {goal_volume} {goal_code}")
    return result


def part_2(recipes: Iterable['Recipe'], stored: 'Amount' = (1_000_000_000_000, 'ORE')) -> int:
    """
    After collecting `ORE` for a while, you check your cargo hold: **1 trillion**
    (**1_000_000_000_000**) units of `ORE`.

    With that much ore, given the examples above:

        >>> ore = (1_000_000_000_000, 'ORE')
        >>> example_3 = recipes_from_file(data_path(__file__, 'example-3.txt'))
        >>> production_yield(example_3, ore)
        (82892753, 'FUEL')
        >>> production_yield(recipes_from_file(data_path(__file__, 'example-4.txt')), ore)
        (5586022, 'FUEL')
        >>> production_yield(recipes_from_file(data_path(__file__, 'example-5.txt')), ore)
        (460664, 'FUEL')

    Given 1 trillion `ORE`, **what is the maximum amount of `FUEL` you can produce?**

        >>> part_2(example_3)
        part 2: from 1000000000000 ORE you can create 82892753 FUEL
        82892753
    """

    result, fuel = production_yield(recipes, stored)
    assert fuel == 'FUEL'

    stored_volume, stored_code = stored
    print(f"part 2: from {stored_volume} {stored_code} you can create {result} {fuel}")
    return result


Amount = tuple[int, str]


@dataclass(frozen=True)
class Recipe:
    ins: list[Amount]
    out: Amount

    @property
    def out_volume(self) -> int:
        return self.out[0]

    @property
    def out_material(self) -> str:
        return self.out[1]

    @classmethod
    def from_line(cls, line: str) -> Self:
        def parse_amount(text: str) -> Amount:
            volume, material = text.split(' ')
            return int(volume), material

        # 2 AB, 3 BC, 4 CA => 1 FUEL
        input_part, output_part = line.strip().split(' => ')
        return cls(
            ins=[parse_amount(input_text) for input_text in input_part.split(', ')],
            out=parse_amount(output_part)
        )


def production_cost(
    recipes: Iterable[Recipe],
    goal: Amount = (1, 'FUEL'),
    source_material: str = 'ORE'
) -> Amount:
    return Factory(recipes, source_material).produce(goal), source_material


class Factory:
    def __init__(self, recipes: Iterable[Recipe], source_material: str):
        self.costs = {recipe.out_material: (recipe.out_volume, recipe.ins) for recipe in recipes}
        self.source_material = source_material
        self.storage = Counter()

    def produce(self, goal: Amount) -> int:
        goal_remaining, goal_material = goal

        if goal_material == self.source_material:
            # source material is simply imported
            return goal_remaining

        # goal is fully or partially covered by storage
        spent = min(goal_remaining, self.storage[goal_material])
        self.storage[goal_material] -= spent
        goal_remaining -= spent

        if goal_remaining == 0:
            # production goal was fully covered by storage
            # -> no need to import or produce anything
            return 0

        # otherwise we need to produce some goal material
        produced_per_cycle, requirements_per_cycle = self.costs[goal_material]
        # we will run this production cycle several times
        cycles_count = ceildiv(goal_remaining, produced_per_cycle)
        imported_source_volume = sum(
            self.produce((req_volume * cycles_count, req_material))
            for req_volume, req_material in requirements_per_cycle
        )
        self.storage[goal_material] += cycles_count * produced_per_cycle

        # now we have enough in the storage
        assert self.storage[goal_material] >= goal_remaining
        self.storage[goal_material] -= goal_remaining

        return imported_source_volume


def production_yield(
    recipes: Iterable[Recipe],
    stored: Amount,
    goal_material: str = 'FUEL'
) -> Amount:
    stored_volume, stored_material = stored
    recipes = list(recipes)

    # use bisection to figure out how much goal material must be produced so that it costs
    # the stored amount of source material
    goal_amount = BSRange(lower=1, upper=None)

    while True:
        goal_guess = goal_amount.mid if goal_amount.is_bounded() else goal_amount.lower * 2
        cost, _ = production_cost(
            recipes=recipes,
            goal=(goal_guess, goal_material),
            source_material=stored_material
        )
        if cost >= stored_volume:
            goal_amount.upper = goal_guess
        if cost <= stored_volume:
            goal_amount.lower = goal_guess
        if goal_amount.has_single_value():
            return goal_amount.single_value, goal_material


def recipes_from_text(text: str) -> list[Recipe]:
    return list(recipes_from_lines(text.strip().splitlines()))


def recipes_from_file(fn: str) -> list[Recipe]:
    return list(recipes_from_lines(open(fn)))


def recipes_from_lines(lines: Iterable[str]) -> Iterable[Recipe]:
    return (Recipe.from_line(line) for line in lines)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    recipes = recipes_from_file(input_path)
    result_1 = part_1(recipes)
    result_2 = part_2(recipes)
    return result_1, result_2


if __name__ == '__main__':
    main()
