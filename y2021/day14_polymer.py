"""
Advent of Code 2021
Day 14: Extended Polymerization
https://adventofcode.com/2021/day/14
"""

from collections import Counter
from itertools import chain
from typing import Iterable
from typing import TypeVar

from common.utils import parse_line
from common.utils import relative_path
from common.utils import slidingw


def part_1(template: str, rules: 'Rules', steps: int = 10) -> int:
    """
    The submarine manual contains instructions for finding the optimal polymer formula;
    specifically, it offers a **polymer template** and a list of **pair insertion** rules (your
    puzzle input). You just need to work out what polymer would result after repeating the pair
    insertion process a few times.

    For example:

        >>> p0, insertion_rules = input_from_text('''
        ...
        ...     NNCB
        ...
        ...     CH -> B
        ...     HH -> N
        ...     CB -> H
        ...     NH -> C
        ...     HB -> C
        ...     HC -> B
        ...     HN -> C
        ...     NN -> C
        ...     BH -> H
        ...     NC -> B
        ...     NB -> B
        ...     BN -> B
        ...     BB -> N
        ...     BC -> B
        ...     CC -> N
        ...     CN -> C
        ...
        ... ''')

    The first line is the **polymer template** - this is the starting point of the process.

        >>> p0
        'NNCB'

    The following section defines the **pair insertion** rules. A rule like `AB -> C` means that
    when elements `A` and `B` are immediately adjacent, element `C` should be inserted between them.
    These insertions all happen simultaneously.

        >>> len(insertion_rules), insertion_rules[('C', 'H')]
        (16, 'B')

    So, starting with the polymer template `NNCB`, the first step simultaneously considers all three
    pairs:

    - The first pair (`NN`) matches the rule `NN -> C`,
      so element `C` is inserted between the first `N` and the second `N`.
    - The second pair (`NC`) matches the rule `NC -> B`,
      so element `B` is inserted between the `N` and the `C`.
    - The third pair (`CB`) matches the rule `CB -> H`,
      so element `H` is inserted between the `C` and the `B`.

        >>> insertion_rules[('N', 'N')], insertion_rules[('N', 'C')], insertion_rules[('C', 'B')]
        ('C', 'B', 'H')

    Note that these pairs overlap: the second element of one pair is the first element of the next
    pair. Also, because all pairs are considered simultaneously, inserted elements are not conside-
    red to be part of a pair until the next step.

    After the first step of this process, the polymer becomes NCNBCHB.

    Here are the results of a few steps using the above rules:


        >>> p4 = grow(p0, insertion_rules, steps=4, log=True)
        Template:     NNCB
        After step 1: NCNBCHB
        After step 2: NBCCNBBBCBHCB
        After step 3: NBBBCNCCNBBNBNBBCHBHHBCHB
        After step 4: NBBNBNBBCCNBCNCCNBBNBBNBBBNBBNBBCBHCBHHNHCBBCBHCB
        >>> p4
        'NBBNBNBBCCNBCNCCNBBNBBNBBBNBBNBBCBHCBHHNHCBBCBHCB'

    This polymer grows quickly. After step 5, it has length 97; After step 10, it has length 3073.

        >>> len(p5 := grow(p4, insertion_rules, steps=1))
        97
        >>> len(p10 := grow(p5, insertion_rules, steps=5))
        3073


    After step 10, `B` occurs 1749 times, `C` occurs 298 times, `H` occurs 161 times, and `N` occurs
    865 times.

        >>> Counter(p10)
        Counter({'B': 1749, 'N': 865, 'C': 298, 'H': 161})

    taking the quantity of the most common element (`B`, 1749) and subtracting the quantity of
    the least common element (`H`, 161) produces `1749 - 161 = 1588`.

    Apply 10 steps of pair insertion to the polymer template and find the most and least common
    elements in the result. **What do you get if you take the quantity of the most common element
    and subtract the quantity of the least common element?**

        >>> part_1(p0, insertion_rules)
        part 1: after 10 steps, result is 1749 (B) - 161 (H) = 1588
        1588
    """

    counts = Counter(grow(template, rules, steps))
    (most_element, most_count), *_, (least_element, least_count) = counts.most_common()
    result = most_count - least_count

    print(
        f"part 1: after {steps} steps, "
        f"result is {most_count} ({most_element}) - {least_count} ({least_element}) = {result}"
    )
    return result


def part_2(template: str, rules: 'Rules', steps: int = 40) -> int:
    """
    The resulting polymer isn't nearly strong enough to reinforce the submarine. You'll need to run
    more steps of the pair insertion process; a total of **40 steps** should do it.

    In the above example, the most common element is `B` (occurring `2192039569602` times)
    and the least common element is `H` (occurring `3849876073` times):

        >>> p0, insertion_rules = input_from_file('data/14-example.txt')
        >>> p40 = grow_optimized(p0, insertion_rules, steps=40)
        >>> p40['B']
        2192039569602
        >>> p40['H']
        3849876073

    Subtracting these produces **`2188189693529`**.

        >>> p40['B'] - p40['H']
        2188189693529

    Apply **40** steps of pair insertion to the polymer template and find the most and least common
    elements in the result. **What do you get if you take the quantity of the most common element
    and subtract the quantity of the least common element?**

        >>> part_2(p0, insertion_rules)
        part 2: after 40 steps, result is 2192039569602 (B) - 3849876073 (H) = 2188189693529
        2188189693529
    """

    counts = grow_optimized(template, rules, steps)
    (most_element, most_count), *_, (least_element, least_count) = counts.most_common()
    result = most_count - least_count

    print(
        f"part 2: after {steps} steps, "
        f"result is {most_count} ({most_element}) - {least_count} ({least_element}) = {result}"
    )
    return result


Rules = dict[[str, str], str]


def grow(polymer: str, rules: Rules, steps: int, log: bool = False) -> str:
    assert len(polymer) >= 2

    if log:
        print(f'Template:     {polymer}')

    for step in range(steps):
        polymer = ''.join(
            e
            for i0, i1 in slidingw(polymer, 2)
            for e in (i0, rules[(i0, i1)])
        ) + polymer[-1]

        if log:
            print(f'After step {step + 1}: {polymer}')

    return polymer


def grow_optimized(polymer: str, rules: Rules, steps: int) -> Counter[str, int]:
    assert len(polymer) >= 2

    # instead of keeping track of the polymer itself, we'll watch only counts of its pairs
    pairs = Counter(slidingw(polymer, 2))

    for step in range(steps):
        pairs = _total_counts(
            (new_pair, count)
            for (i0, i1), count in pairs.items()
            if (out := rules[(i0, i1)])
            for new_pair in [(i0, out), (out, i1)]
        )

    return _total_counts(
        chain(
            # sum of pair quantities -> only first element (otherwise result would be ~doubled)
            ((e0, count) for (e0, _), count in pairs.items()),
            # plus 1 for the last element (which remains unchanged throughout the process)
            [(polymer[-1], 1)]
        )
    )


T = TypeVar('T')


def _total_counts(items: Iterable[tuple[T, int]]) -> Counter[T, int]:
    # cannot use Counter(dict(items)) in case of reduplicated keys
    counter = Counter()
    for key, count in items:
        counter[key] += count
    return counter


Input = tuple[str, dict[[str, str], str]]


def input_from_text(text: str) -> Input:
    return input_from_lines(text.strip().split('\n'))


def input_from_file(fn: str) -> Input:
    return input_from_lines(open(relative_path(__file__, fn)))


def input_from_lines(lines: Iterable[str]) -> Input:
    def parse_rule(line: str) -> tuple[tuple[str, str], str]:
        (i1, i2), o = parse_line(line, '$ -> $')
        return (i1, i2), o

    lines_it = (sline for line in lines if (sline := line.strip()))
    template = next(lines_it).strip()
    rules = dict(parse_rule(line.strip()) for line in lines_it)
    return template, rules


if __name__ == '__main__':
    template_, rules_ = input_from_file('data/14-input.txt')
    part_1(template_, rules_)
    part_2(template_, rules_)
