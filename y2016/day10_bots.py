from collections import defaultdict
from typing import Dict

from utils import product

Target = tuple[str, int]
Values = Dict[Target, list[int]]
Instructions = Dict[int, tuple[Target, Target]]


def load(fn: str) -> tuple[Values, Instructions]:
    initials: Values = defaultdict(list)
    instructions: Instructions = dict()

    for line in open(fn):
        line = line.strip()

        # value 3 goes to bot 1
        if line.startswith("value "):
            _, value, _, _, tt, tn = line.split(' ')
            initials[(tt, int(tn))].append(int(value))

        # bot 1 gives low to output 1 and high to bot 0
        elif line.startswith("bot "):
            _, botn, _, low, _, ltt, ltn, _, high, _, htt, htn = line.split(' ')
            assert low == "low"
            assert high == "high"
            target_low = (ltt, int(ltn))
            target_high = (htt, int(htn))
            instructions[int(botn)] = (target_low, target_high)

        else:
            raise ValueError(line)

    return dict(initials), instructions


class Factory:
    def __init__(self, values: Values):
        self.values = dict(values)
        for t, tvs in self.values.items():
            assert len(tvs) <= 2

    def __str__(self):
        return "\n".join(
            f"{tt} {tn}: {' '.join(str(v) for v in sorted(tvs))}"
            for (tt, tn), tvs in sorted(self.values.items())
        )

    def values_in_output(self, n: int) -> list[int]:
        return self.values[('output', n)]

    def single_value_in_output(self, n: int) -> int:
        values = self.values_in_output(n)
        assert len(values) == 1
        return values[0]

    def step(self, instructions: Instructions) -> int:
        new_values: Values = defaultdict(list)
        moved_count = 0

        for (tt, tn), tvs in self.values.items():
            assert len(tvs) <= 2
            if tt == 'bot' and len(tvs) == 2:
                low_value, high_value = sorted(tvs)
                assert low_value < high_value
                if low_value == 17 and high_value == 61:
                    print(f"part 1: bot {tn} is comparing {low_value} and {high_value}")
                low_target, high_target = instructions[tn]
                new_values[low_target].append(low_value)
                new_values[high_target].append(high_value)
                if low_target != (tt, tn):
                    moved_count += 1
                if high_target != (tt, tn):
                    moved_count += 1
            else:
                new_values[(tt, tn)].extend(tvs)

        old_values_count = sum(len(vs) for vs in self.values.values())
        new_values_count = sum(len(tvs) for tvs in new_values.values())
        assert old_values_count == new_values_count

        self.values = dict(new_values)
        return moved_count


if __name__ == '__main__':
    initials_, instructions_ = load("data/10-input.txt")
    f = Factory(initials_)
    while f.step(instructions_) > 0:
        pass
    result = product(f.single_value_in_output(n) for n in range(3))
    print(f"part 2: result is {result}")
