from collections import defaultdict
from typing import Dict
from typing import Generator
from typing import Iterable
from typing import List
from typing import Tuple

from multibuffer import MultiBuffer
from utils import last

Rules = Dict[str, List[str]]


def load(fn: str) -> Tuple[str, Rules]:
    rules = defaultdict(list)
    f = open(fn)
    for line in f:
        line = line.strip()
        if not line:
            break
        rfrom, rto = line.split(' => ')
        rules[rfrom].append(rto)

    molecule = f.readline().strip()
    return molecule, dict(rules)


def replaces(molecule: str, rules: Rules) -> Iterable[str]:
    for rfrom, rtos in rules.items():
        ln = len(rfrom)
        yield from (
            molecule[:k] + rto + molecule[k+ln:]
            for k in range(len(molecule)-ln+1)
            if molecule[k:k+ln] == rfrom
            for rto in rtos
        )


def creates(start: str, rules: Rules, target: str) -> Generator[Tuple[str, int], None, int]:
    buffer = MultiBuffer(scoring=lambda ms: len(ms[0]), items=[(start, 0)])
    known: Dict[str, int] = {start: 0}

    while buffer:
        molecule, steps = buffer.pop_min()

        for rfrom, rtos in rules.items():
            ln = len(rfrom)
            for k in range(len(molecule) - ln + 1):
                if molecule[k:k+ln] == rfrom:
                    for rto in rtos:
                        molecule_after = molecule[:k]+rto+molecule[k+ln:]
                        if molecule_after not in known:
                            known[molecule_after] = steps + 1
                            buffer.append((molecule_after, steps+1))
                            yield (molecule_after, steps + 1)
                        if molecule_after == target:
                            return steps + 1


def reversed_rules(rules: Rules) -> Rules:
    rules_rev = defaultdict(list)
    for rfrom, rtos in rules.items():
        for rto in rtos:
            rules_rev[rto].append(rfrom)
    return dict(rules_rev)


def test_replaces():
    rules = {
        'H': ['HO', 'OH'],
        'O': ['HH']
    }
    assert sum(1 for _ in replaces('HOH', rules)) == 5
    assert len(set(replaces('HOH', rules))) == 4
    assert len(set(replaces('HOHOHO', rules))) == 7


def test_creates():
    rules = {
        'e': ['H', 'O'],
        'H': ['HO', 'OH'],
        'O': ['HH']
    }
    assert list(creates('e', rules, 'HOH'))[-1] == ('HOH', 3)
    assert list(creates('e', rules, 'HOHOHO'))[-1] == ('HOHOHO', 6)


def part_1(molecule: str, rules: Rules) -> int:
    result = len(set(replaces(molecule, rules)))
    print(f"part 1: {result} distinct molecules can be created with one replacement")
    return result


def part_2(molecule: str, rules: Rules) -> int:
    target, steps = last(creates(molecule, reversed_rules(rules), 'e'))
    assert target == 'e'
    print(f"part 2: takes {steps} steps to create the molecule from 'e'")
    return steps


if __name__ == '__main__':
    m, rs = load("data/19-input.txt")
    part_1(m, rs)
    part_2(m, rs)
