import math
from collections import Counter
from typing import Dict
from typing import Iterable
from typing import List
from typing import NamedTuple
from typing import Tuple

from bsrange import BSRange
from utils import dgroupby


class IngrAmount(NamedTuple):
    code: str
    amount: int

    def __str__(self):
        return f"{self.amount} {self.code}"

    @classmethod
    def from_str(cls, s: str) -> 'IngrAmount':
        amount, code = s.strip().split(' ', maxsplit=1)
        return IngrAmount(code, int(amount))

    def __mul__(self, k: int) -> 'IngrAmount':
        return IngrAmount(code=self.code, amount=self.amount * k)

    def __gt__(self, other):
        if not isinstance(other, IngrAmount):
            return False
        assert self.code == other.code
        return self.amount > other.amount


class Recipe:
    def __init__(self, ins: Iterable[IngrAmount], outs: Iterable[IngrAmount]):
        self.ins = list(ins)
        outs = list(outs)
        self.out = outs[0]
        self.byproducts = outs[1:]

    def __str__(self):
        ins_str = ", ".join(str(i) for i in self.ins)
        if self.byproducts:
            bp_str = ", ".join(str(p) for p in self.byproducts)
            return f"{ins_str} => {self.out} ({bp_str})"
        else:
            return f"{ins_str} => {self.out}"

    @classmethod
    def load(cls, fn: str) -> Iterable['Recipe']:
        with open(fn) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                if '=>' in line:
                    ins, outs = line.split('=>')
                elif '<=' in line:
                    outs, ins = line.split('<=')
                else:
                    raise ValueError(f"cannot split line {line!r}")

                delimiter = ',' if ',' in line else '+'

                yield Recipe(
                    ins=(IngrAmount.from_str(i) for i in ins.split(delimiter)),
                    outs=(IngrAmount.from_str(o) for o in outs.split(delimiter))
                )


def create_costs(
        recipes: Iterable[Recipe]
) -> Dict[str, Tuple[int, List[IngrAmount], List[IngrAmount]]]:
    return dgroupby(
        recipes,
        key=lambda r: r.out.code,
        value=lambda r: (r.out.amount, r.ins, r.byproducts)
    )


class Factory:
    def __init__(self, recipes: Iterable[Recipe]):
        self.costs = create_costs(recipes)
        self.stored = Counter()
        self.imported = Counter()

    def produce(self, ia: IngrAmount):
        remaining, code = ia.amount, ia.code

        while remaining > 0:

            if self.stored[code] >= remaining:
                # fully cover by store
                self.stored[code] -= remaining
                remaining = 0

            elif self.stored[code] > 0:
                # partly cover by store
                remaining -= self.stored[code]
                self.stored[code] = 0

            elif code in self.costs:
                # we have to produce some
                cycle_produces, cycle_costs, cycle_byproducts = self.costs[code]
                cycles_count = math.ceil(remaining / cycle_produces)

                for cycle_cost in cycle_costs:
                    self.produce(cycle_cost * cycles_count)
                produced_total = cycles_count * cycle_produces
                self.stored[code] += produced_total
                for cycle_byproduct in cycle_byproducts:
                    bp_produced_total = cycles_count * cycle_byproduct.amount
                    self.stored[cycle_byproduct.code] += bp_produced_total

            else:
                # we have to import some
                self.imported[code] += remaining
                self.stored[code] += remaining


def cost_of(
        *,
        required: IngrAmount = IngrAmount('FUEL', 1),
        resource_code: str = 'ORE',
        recipes: Iterable[Recipe]
) -> IngrAmount:
    factory = Factory(recipes)
    factory.produce(required)
    assert len(factory.imported) == 1
    assert resource_code in factory.imported
    return IngrAmount(code=resource_code, amount=factory.imported[resource_code])


def max_produced_from(
        *,
        required_code: str = 'FUEL',
        resource_stored: IngrAmount = IngrAmount('ORE', 1_000_000_000_000),
        recipes: Iterable[Recipe]
) -> IngrAmount:
    recipes = list(recipes)

    required = BSRange(1, None)
    while not required.has_single_value():
        required_tip = IngrAmount(
            code=required_code,
            amount=required.mid if required.is_bounded() else required.lower * 2
        )
        resource_cost = cost_of(
            required=required_tip,
            resource_code=resource_stored.code,
            recipes=recipes
        )
        if resource_cost > resource_stored:
            required.upper = required_tip.amount
        elif resource_cost < resource_stored:
            required.lower = required_tip.amount
        else:
            return required_tip
    else:
        return IngrAmount(code=required_code, amount=required.single_value)


def test_examples_part_1():
    for fn, ore_amount in [
        ('data/14-example-1.txt', 31),
        ('data/14-example-2.txt', 165),
        ('data/14-example-3.txt', 13312),
        ('data/14-example-4.txt', 180697),
        ('data/14-example-5.txt', 2210736),
    ]:
        assert cost_of(
            required=IngrAmount('FUEL', 1),
            resource_code='ORE',
            recipes=Recipe.load(fn)
        ) == IngrAmount('ORE', ore_amount)
        print(f">> passed test_example_part_1/{fn}")


def test_examples_part_2():
    for fn, fuel_amount in [
        ('data/14-example-3.txt', 82892753),
        ('data/14-example-4.txt', 5586022),
        ('data/14-example-5.txt', 460664),
    ]:
        assert max_produced_from(
            required_code='FUEL',
            resource_stored=IngrAmount('ORE', 1_000_000_000_000),
            recipes=Recipe.load(fn)
        ) == IngrAmount('FUEL', fuel_amount)
        print(f">> passed test_example_part_2/{fn}")


def part_1(fuel_amount: int = 1):
    fuel = IngrAmount('FUEL', fuel_amount)
    ore = cost_of(
        required=fuel,
        resource_code='ORE',
        recipes=Recipe.load('data/14-input.txt')
    )
    print(f"part 1: to create {fuel} you have to spend {ore}")


def part_2(ore_stored: int = 1_000_000_000_000):
    ore = IngrAmount('ORE', ore_stored)
    fuel = max_produced_from(
        required_code='FUEL',
        resource_stored=ore,
        recipes=Recipe.load('data/14-input.txt')
    )
    print(f"part 2: from {ore} you can create {fuel}")


def factorio(target):
    factory = Factory(Recipe.load('data/14-factorio.txt'))
    factory.produce(target)
    raw_text = " + ".join(
        str(IngrAmount(code, amount))
        for code, amount
        in factory.imported.most_common()
    )
    print(f"to produce {target}: {raw_text}")


if __name__ == '__main__':
    # part_1()
    # part_2()
    factorio(IngrAmount('space science pack', 1))
