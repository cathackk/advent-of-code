from itertools import permutations
from typing import Iterable

from common.utils import zip1

Rule = tuple[str, str, int]


def load_rules(fn: str) -> Iterable[Rule]:
    for line in open(fn):
        parts = line.strip(' \n.').split(' ')
        name1, would, lg, value, happiness, units, by, sitting, next_, to, name2 = parts

        assert would == "would"
        assert lg in ("lose", "gain")
        assert happiness == "happiness"
        assert units == "units"
        assert by == "by"
        assert sitting == "sitting"
        assert next_ == "next"
        assert to == "to"

        value = int(value)
        if lg == "lose":
            value = -value

        yield name1, name2, value


def find_best_seating(rules: list[Rule]) -> tuple[list[str], int]:
    people = sorted(set(person for rule in rules for person in rule[:2]))
    table = {(p1, p2): h for p1, p2, h in rules}

    def happiness(seating: list[str]) -> int:
        return sum(
            table.get((p1,p2), 0) + table.get((p2,p1), 0)
            for p1, p2 in zip1(seating, wrap=True)
        )

    seatings = (
        [people[0]] + list(rest)
        for rest in permutations(people[1:])
    )

    best_seating = max(seatings, key=happiness)
    best_happiness = happiness(best_seating)
    return best_seating, best_happiness


def part_1(rules: list[Rule]) -> int:
    seating, happiness = find_best_seating(rules)
    print(f"part 1: best happiness: {happiness} ({'-'.join(seating)})")
    return happiness


def part_2(rules: list[Rule]) -> int:
    rules = rules + [('myself', 'myself', 0)]
    seating, happiness = find_best_seating(rules)
    print(f"part 2: best happiness: {happiness} ({'-'.join(seating)})")
    return happiness


if __name__ == '__main__':
    rules = list(load_rules("data/13-input.txt"))
    part_1(rules)
    part_2(rules)
