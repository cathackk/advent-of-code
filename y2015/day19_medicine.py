"""
Advent of Code 2015
Day 19: Medicine for Rudolph
https://adventofcode.com/2015/day/19
"""

from collections import defaultdict
from typing import Generator
from typing import Iterable

from common.file import relative_path
from common.iteration import exhaust
from common.multibuffer import MultiBuffer

Rules = dict[str, list[str]]


def part_1(molecule: str, rules: Rules) -> int:
    """
    Rudolph the Red-Nosed Reindeer is sick! His nose isn't shining very brightly, and he needs
    medicine.

    Red-Nosed Reindeer biology isn't similar to regular reindeer biology; Rudolph is going to need
    custom-made medicine. Unfortunately, Red-Nosed Reindeer chemistry isn't similar to regular
    reindeer chemistry, either.

    The North Pole is equipped with a Red-Nosed Reindeer nuclear fusion/fission plant, capable of
    constructing any Red-Nosed Reindeer molecule you need. It works by starting with some input
    molecule and then doing a series of **replacements**, one per step, until it has the right
    molecule.

    However, the machine has to be calibrated before it can be used. Calibration involves deter-
    mining the number of molecules that can be generated in one step from a given starting point.

    For example, imagine a simpler machine that supports only the following replacements:

        >>> example_rules = rules_from_text('''
        ...     H => HO
        ...     H => OH
        ...     O => HH
        ... ''')
        >>> example_rules
        {'H': ['HO', 'OH'], 'O': ['HH']}

    Given the replacements above and starting with `HOH`, the following molecules could be
    generated:

        >>> (hoh_replacements := list(replacements('HOH', example_rules)))
        ['HOOH', 'OHOH', 'HOHO', 'HOOH', 'HHHH']

    So, in the example above, there are 4 **distinct** molecules (not five, because `HOOH` appears
    twice) after one replacement from `HOH`.

        >>> len(set(hoh_replacements))
        4

    Santa's favorite molecule, `HOHOHO`, can become 7 **distinct** molecules (over nine
    replacements: six from `H`, and three from `O`).

        >>> len(set(replacements('HOHOHO', example_rules)))
        7

    The machine replaces without regard for the surrounding characters. For example, given
    the string `H2O`, the transition `H => OO` would result in `OO2O`.

    Your puzzle input describes all of the possible replacements and, at the bottom, the medicine
    molecule for which you need to calibrate the machine. **How many distinct molecules can be
    created** after all the different ways you can do one replacement on the medicine molecule?

        >>> part_1('HOHOHO', example_rules)
        part 1: 7 distinct molecules can be created with one replacement
        7
    """

    result = len(set(replacements(molecule, rules)))
    print(f"part 1: {result} distinct molecules can be created with one replacement")
    return result


def part_2(target_molecule: str, rules: Rules, start: str = 'e') -> int:
    """
    Now that the machine is calibrated, you're ready to begin molecule fabrication.

    Molecule fabrication always begins with just a single electron, `e`, and applying replacements
    one at a time, just like the ones during calibration.

    For example, suppose you have the following replacements:

        >>> example_rules = rules_from_text('''
        ...     e => H
        ...     e => O
        ...     H => HO
        ...     H => OH
        ...     O => HH
        ... ''')
        >>> example_rules
        {'e': ['H', 'O'], 'H': ['HO', 'OH'], 'O': ['HH']}

    If you'd like to make `HOH`, you start with `e`, and then make the following replacements:

      - `e => O` to get `O`
      - `O => HH` to get `HH`
      - `H => OH` (on the second `H`) to get `HOH`

    So, you could make HOH after 3 steps.

        >>> steps_to_create('e', example_rules, 'HOH')
        3

    Santa's favorite molecule, HOHOHO, can be made in 6 steps.

        >>> steps_to_create('e', example_rules, 'HOHOHO')
        6

    How long will it take to make the medicine? Given the available **replacements** and
    the **medicine molecule** in your puzzle input, what is the **fewest number of steps** to go
    from `e` to the medicine molecule?

        >>> part_2('HOHOHO', example_rules)
        part 2: it takes 6 steps to create the molecule from 'e'
        6
    """

    result = steps_to_create(start, rules, target_molecule)
    print(f"part 2: it takes {result} steps to create the molecule from {start!r}")
    return result


def replacements(molecule: str, rules: Rules) -> Iterable[str]:
    for rfrom, rtos in rules.items():
        length = len(rfrom)
        yield from (
            molecule[:k] + rto + molecule[k + length:]
            for k in range(len(molecule) - length + 1)
            if molecule[k:k + length] == rfrom
            for rto in rtos
        )


def steps_to_create(start: str, rules: Rules, target: str) -> int:
    return exhaust(traceback(start, rules, target))


def traceback(start: str, rules: Rules, target: str) -> Generator[tuple[str, int], None, int]:
    """
    Instead of making the molecule larger and larger by going start->target,
    we'll try to go backwards target->start.
    """

    rrules = reversed_rules(rules)

    def scoring(molecule_steps: tuple[str, int]) -> int:
        molecule, _ = molecule_steps
        return len(molecule)

    buffer = MultiBuffer(scoring, items=[(target, 0)])
    known: dict[str, int] = {target: 0}

    while buffer:
        molecule_steps: tuple[str, int] = buffer.pop_min()
        molecule, steps = molecule_steps

        for rfrom, rtos in rrules.items():
            length = len(rfrom)
            for k in range(len(molecule) - length + 1):
                if molecule[k:k + length] != rfrom:
                    continue
                for rto in rtos:
                    molecule_after = molecule[:k] + rto + molecule[k + length:]
                    if molecule_after not in known:
                        known[molecule_after] = steps + 1
                        buffer.append((molecule_after, steps + 1))
                        yield molecule_after, steps + 1
                    if molecule_after == start:
                        return steps + 1

    raise ValueError(f"molecule unsynthesizable: {start!r} -> {target!r}")


def reversed_rules(rules: Rules) -> Rules:
    """
        >>> reversed_rules({'H': ['O']})
        {'O': ['H']}
        >>> reversed_rules({'H': ['HO', 'OH'], 'O': ['HH', 'XX'], 'X': ['OH']})
        {'HO': ['H'], 'OH': ['H', 'X'], 'HH': ['O'], 'XX': ['O']}
    """
    rules_rev = defaultdict(list)
    for rfrom, rtos in rules.items():
        for rto in rtos:
            rules_rev[rto].append(rfrom)
    return dict(rules_rev)


def input_from_file(fn: str) -> tuple[str, Rules]:
    return input_from_lines(open(relative_path(__file__, fn)))


def input_from_lines(lines: Iterable[str]) -> tuple[str, Rules]:
    lines = iter(lines)

    rules_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            break
        rules_lines.append(line)

    molecule = next(lines).strip()
    return molecule, rules_from_lines(rules_lines)


def rules_from_text(text: str) -> Rules:
    return rules_from_lines(text.strip().splitlines())


def rules_from_lines(lines: Iterable[str]) -> Rules:
    rules = defaultdict(list)
    for line in lines:
        rfrom, rto = line.strip().split(' => ')
        rules[rfrom].append(rto)
    return dict(rules)


if __name__ == '__main__':
    molecule_, rules_ = input_from_file('data/19-input.txt')
    part_1(molecule_, rules_)
    part_2(molecule_, rules_)
