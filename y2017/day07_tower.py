"""
Advent of Code 2017
Day 7: Recursive Circus
https://adventofcode.com/2017/day/7
"""

from collections import Counter
from typing import Iterable
from typing import Optional

from common.text import parse_line
from common.utils import some
from meta.aoc_tools import data_path


def part_1(tower: 'Tower') -> str:
    """
    Wandering further through the circuits of the computer, you come upon a tower of programs that
    have gotten themselves into a bit of trouble. A recursive algorithm has gotten out of hand, and
    now they're balanced precariously in a large tower.

    One program at the bottom supports the entire tower. It's holding a large disc, and on the disc
    are balanced several more sub-towers. At the bottom of these sub-towers, standing on the bottom
    disc, are other programs, each holding **their** own disc, and so on. At the very tops of these
    sub-sub-sub-...-towers, many programs stand simply keeping the disc below them balanced but with
    no disc of their own.

    You offer to help, but first you need to understand the structure of these towers. You ask each
    program to yell out their **name**, their **weight**, and (if they're holding a disc) the
    **names of the programs immediately above them** balancing on that disc. You write this
    information down (your puzzle input). Unfortunately, in their panic, they don't do this in an
    orderly fashion; by the time you're done, you're not sure which program gave which information.

    For example, if your list is the following:

        >>> example = Tower.from_text('''
        ...     pbga (66)
        ...     xhth (57)
        ...     ebii (61)
        ...     havc (66)
        ...     ktlj (57)
        ...     fwft (72) -> ktlj, cntj, xhth
        ...     qoyq (66)
        ...     padx (45) -> pbga, havc, qoyq
        ...     tknk (41) -> ugml, padx, fwft
        ...     jptl (61)
        ...     ugml (68) -> gyxo, ebii, jptl
        ...     gyxo (61)
        ...     cntj (57)
        ... ''')
        >>> example  # doctest: +NORMALIZE_WHITESPACE
        Tower('tknk', 41, [Tower('ugml', 68, [Tower('gyxo', 61),
                                              Tower('ebii', 61),
                                              Tower('jptl', 61)]),
                           Tower('padx', 45, [Tower('pbga', 66),
                                              Tower('havc', 66),
                                              Tower('qoyq', 66)]),
                           Tower('fwft', 72, [Tower('ktlj', 57),
                                              Tower('cntj', 57),
                                              Tower('xhth', 57)])])

    ...then you would be able to recreate the structure of the towers that looks like this:

        >>> print(example)
        tknk
        ├── ugml
        │   ├── gyxo
        │   ├── ebii
        │   └── jptl
        ├── padx
        │   ├── pbga
        │   ├── havc
        │   └── qoyq
        └── fwft
            ├── ktlj
            ├── cntj
            └── xhth

    In this example, `tknk` is at the bottom of the tower (the **bottom program**), and is holding
    up `ugml`, `padx`, and `fwft`. Those programs are, in turn, holding up other programs; in this
    example, none of those programs are holding up any other programs, and are all the tops of their
    own towers. (The actual tower balancing in front of you is much larger.)

    Before you're ready to help them, you need to make sure your information is correct.
    **What is the name of the bottom program?**

        >>> part_1(example)
        part 1: bottom program is named 'tknk'
        'tknk'
    """

    print(f"part 1: bottom program is named {tower.name!r}")
    return tower.name


def part_2(tower: 'Tower') -> int:
    """
    The programs explain the situation: they can't get down. Rather, they **could** get down, if
    they weren't expending all of their energy trying to keep the tower balanced. Apparently, one
    program has the **wrong weight**, and until it's fixed, they're stuck here.

    For any program holding a disc, each program standing on that disc forms a sub-tower. Each of
    those sub-towers are supposed to be the same weight, or the disc itself isn't balanced.
    The weight of a tower is the sum of the weights of the programs in that tower.

    In the example above, this means that for `ugml`'s disc to be balanced, `gyxo`, `ebii`, and
    `jptl` must all have the same weight, and they do: `61`.

        >>> example = Tower.from_file('data/07-example.txt')
        >>> print(format(example, 'weights'))
        tknk (41 + 737 = 778)
        ├── ugml (68 + 183 = 251)
        │   ├── gyxo (61)
        │   ├── ebii (61)
        │   └── jptl (61)
        ├── padx (45 + 198 = 243)
        │   ├── pbga (66)
        │   ├── havc (66)
        │   └── qoyq (66)
        └── fwft (72 + 171 = 243)
            ├── ktlj (57)
            ├── cntj (57)
            └── xhth (57)


    However, for `tknk` to be balanced, each of the programs standing on its disc and all programs
    above it must each match. This means that their sums be all the same.

    But as you can see, `tknk`'s disc is unbalanced: `ugml`'s stack is heavier than the other two.
    Even though the nodes above `ugml` are balanced, `ugml` itself is too heavy: it needs to be `8`
    units lighter for its stack to weigh `243` and keep the towers balanced:

        >>> unb, correct_weight = example.find_unbalanced()
        >>> unb  # doctest: +ELLIPSIS
        Tower('ugml', 68, [...])
        >>> unb.total_weight
        251
        >>> correct_weight
        243

    If this change were made, its weight would be `60`:

        >>> correct_weight - unb.sub_towers_weight
        60

    Given that exactly one program is the wrong weight, **what would its weight need to be** to
    balance the entire tower?

        >>> part_2(example)
        part 2: to weigh total 243 and balance the tower, 'ugml' itself needs to weigh 60
        60
    """

    unbalanced, target_total_weight = some(tower.find_unbalanced())
    target_weight = target_total_weight - unbalanced.sub_towers_weight
    print(
        f"part 2: to weigh total {target_total_weight} and balance the tower, "
        f"{unbalanced.name!r} itself needs to weigh {target_weight}"
    )
    return target_weight


class Tower:
    def __init__(self, name: str, weight: int, sub_towers: Iterable['Tower'] = ()):
        self.name = name
        self.weight = weight
        self.sub_towers = list(sub_towers)
        self.sub_towers_weight = sum(st.total_weight for st in self.sub_towers)

    def __repr__(self):
        sub_repr = f', {self.sub_towers}' if self.sub_towers else ''
        return f'{type(self).__name__}({self.name!r}, {self.weight}{sub_repr})'

    @property
    def total_weight(self) -> int:
        return self.weight + self.sub_towers_weight

    def total_count(self) -> int:
        return 1 + sum(m.total_count() for m in self.sub_towers)

    def is_balanced(self) -> bool:
        if len(self.sub_towers) >= 2:
            first_sub_weight = self.sub_towers[0].total_weight
            return all(sub.total_weight == first_sub_weight for sub in self.sub_towers[1:])
        else:
            return True

    def find_unbalanced(self) -> Optional[tuple['Tower', int]]:
        """
        Returns tuple of:

          - the sub-tower that is causing unbalance,
          - weight it should have to bring balance.
        """

        if len(self.sub_towers) < 2:
            # 0 or 1 subtowers -> nothing to be unbalanced
            return None

        weights = [sub.total_weight for sub in self.sub_towers]
        weights_counter = Counter(weights)

        if len(weights_counter) == 1:
            # all weigh the same -> balanced
            return None

        elif len(weights_counter) == 2:
            (weight_ok, cnt_ok), (weight_wrong, cnt_wrong) = weights_counter.most_common(2)
            if cnt_ok > 1 and cnt_wrong == 1:
                disbalanced_sub = self.sub_towers[weights.index(weight_wrong)]
                return disbalanced_sub.find_unbalanced() or (disbalanced_sub, weight_ok)

        # otherwise
        raise ValueError(f"cannot determine disbalanced with weights {weights}")

    @classmethod
    def from_file(cls, fn: str) -> 'Tower':
        return cls.from_lines(open(fn))

    @classmethod
    def from_text(cls, text: str) -> 'Tower':
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Tower':
        # name -> weight, names of subtowers
        protos: dict[str, tuple[int, list[str]]] = {}
        # name -> parent (tower it stands on)
        depends_on: dict[str, str] = {}

        for line in lines:
            line = line.strip()
            # enurd (528) -> gpaljor, ncuksjv, ozdrm, qkmsfo
            name, weight, children_part = parse_line(line, "$ ($)$")
            children = children_part.removeprefix(' -> ').split(', ') if children_part else []
            protos[name] = (int(weight), children)
            for child in children:
                depends_on[child] = name

        def find_root_tower_name(dependences: dict[str, str]) -> str:
            # take any name ...
            key = next(iter(dependences.keys()))
            # ... and traverse to parents until you reach the root (bottom) tower,
            while key in dependences:
                key = dependences[key]
            # ... which is not dependent on any other tower
            return key

        return cls._from_protos(find_root_tower_name(depends_on), protos)

    @classmethod
    def _from_protos(cls, name: str, protos: dict[str, tuple[int, list[str]]]) -> 'Tower':
        weight, children_names = protos[name]
        return Tower(
            name=name,
            weight=weight,
            sub_towers=(cls._from_protos(cname, protos) for cname in children_names)
        )

    def __str__(self) -> str:
        return format(self)

    def __format__(self, format_spec: str) -> str:
        return "\n".join(
            self.str_lines(
                include_weights='weights' in format_spec
            )
        )

    def str_lines(self, include_weights: bool) -> Iterable[str]:
        if not include_weights:
            yield self.name
        elif self.sub_towers:
            yield f"{self.name} ({self.weight} + {self.sub_towers_weight} = {self.total_weight})"
        else:
            yield f"{self.name} ({self.weight})"

        for sub_ix, sub in enumerate(self.sub_towers):
            is_last = (sub_ix == len(self.sub_towers) - 1)
            branch, trunk = ("└── ", "    ") if is_last else ("├── ", "│   ")
            for line_ix, sub_line in enumerate(sub.str_lines(include_weights)):
                prefix = branch if line_ix == 0 else trunk
                yield prefix + sub_line


def main(input_path: str = data_path(__file__)) -> tuple[str, int]:
    tower = Tower.from_file(input_path)
    # print(format(tower_, 'weights'))
    result_1 = part_1(tower)
    result_2 = part_2(tower)
    return result_1, result_2


if __name__ == '__main__':
    main()
