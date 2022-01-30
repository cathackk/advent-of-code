"""
Advent of Code 2018
Day 5: Alchemical Reduction
https://adventofcode.com/2018/day/5
"""

from common.file import relative_path
from common.iteration import mink


def part_1(polymer: str) -> int:
    """
    You've managed to sneak in to the prototype suit manufacturing lab. The Elves are making decent
    progress, but are still struggling with the suit's size reduction capabilities.

    While the very latest in 1518 alchemical technology might have solved their problem eventually,
    you can do better. You scan the chemical composition of the suit's material and discover that it
    is formed by extremely long polymers (one of which is available as your puzzle input).

    The polymer is formed by smaller **units** which, when triggered, react with each other such
    that two adjacent units of the same type and opposite polarity are destroyed. Units' types are
    represented by letters; units' polarity is represented by capitalization. For instance, `r` and
    `R` are units with the same type but opposite polarity, whereas `r` and `s` are entirely
    different types and do not react.

    For example:

      - In `aA`, `a` and `A` react, leaving nothing behind:

        >>> react('aA')
        ''

      - In `abBA`, `bB` destroys itself, leaving `aA`. As above, this then destroys itself, leaving
        nothing:

        >>> react('abBA')
        ''

      - In `abAB`, no two adjacent units are of the same type, and so nothing happens:

        >>> react('aBBA')
        'aBBA'

      - In `aabAAB`, even though aa and `AA` are of the same type, their polarities match, and so
        nothing happens:

        >>> react('aabAAB')
        'aabAAB'

    Now, consider a larger example, `dabAcCaCBAcCcaDA`:

      - The first 'cC' is removed:                                `dabAcCaCBAcCcaDA`
      - This creates 'Aa', which is removed:                      `dabAaCBAcCcaDA`
      - Either 'cC' or 'Cc' are removed (the result is the same): `dabCBAcCcaDA`
      - No further actions can be taken:                          `dabCBAcaDA`

        >>> react('dabAcCaCBAcCcaDA')
        'dabCBAcaDA'

    After all possible reactions, the resulting polymer contains **`10` units**.

    **How many units remain after fully reacting the polymer you scanned?**

        >>> part_1('dabAcCaCBAcCcaDA')
        part 1: polymer length after reactions is 10 units
        10
    """

    result = len(react(polymer))
    print(f"part 1: polymer length after reactions is {result} units")
    return result


def part_2(polymer: str) -> int:
    """
    Time to improve the polymer.

    One of the unit types is causing problems; it's preventing the polymer from collapsing as much
    as it should. Your goal is to figure out which unit type is causing the most problems, remove
    all instances of it (regardless of polarity), fully react the remaining polymer, and measure its
    length.

    For example, again using the polymer `dabAcCaCBAcCcaDA` from above:

        >>> example = 'dabAcCaCBAcCcaDA'

      - Removing all `A`/`a` units produces `dbcCCBcCcD`.
        Fully reacting this polymer produces `dbCBcD`, which has length `6`.

        >>> react(without_units(example, 'A'))
        'dbCBcD'

      - Removing all `B`/`b` units produces `daAcCaCAcCcaDA`.
        Fully reacting this polymer produces `daCAcaDA`, which has length `8`.

        >>> react(without_units(example, 'B'))
        'daCAcaDA'

      - Removing all `C`/`c` units produces `dabAaBAaDA`.
        Fully reacting this polymer produces daDA, which has length `4`.

        >>> react(without_units(example, 'C'))
        'daDA'

      - Removing all `D`/`d` units produces `abAcCaCBAcCcaA`.
        Fully reacting this polymer produces abCBAc, which has length `6`.

        >>> react(without_units(example, 'D'))
        'abCBAc'

    In this example, removing all `C`/`c` units was best, producing the answer `4`.

    **What is the length of the shortest polymer you can produce** by removing all units of exactly
    one type and fully reacting the result?

        >>> part_2(example)
        part 2: best to remove 'C'/'c' -> polymer length after reactions is then 4
        4
    """

    units = sorted(set(polymer.lower()))
    removed, polymer_length = mink(units, key=lambda rc: len(react(without_units(polymer, rc))))

    print(
        f"part 2: best to remove {removed.upper()!r}/{removed!r} "
        f"-> polymer length after reactions is then {polymer_length}"
    )
    return polymer_length


def react(polymer: str) -> str:
    def is_reactive(p_1: str, p_2: str) -> bool:
        return p_1.isupper() != p_2.isupper() and p_1.upper() == p_2.upper()

    p_out: list[str] = []

    for c in polymer:
        if p_out and is_reactive(p_out[-1], c):
            p_out.pop()
        else:
            p_out.append(c)

    return ''.join(p_out)


def without_units(polymer: str, removed: str) -> str:
    assert len(removed) == 1
    removed = removed.casefold()
    return ''.join(unit for unit in polymer if unit.casefold() != removed)


def polymer_from_file(fn: str) -> str:
    return open(relative_path(__file__, fn)).readline().strip()


if __name__ == '__main__':
    polymer_ = polymer_from_file('data/05-input.txt')
    assert len(polymer_) == 50_000
    part_1(polymer_)
    part_2(polymer_)
