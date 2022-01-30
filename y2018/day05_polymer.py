import string

from common.file import relative_path
from common.iteration import mink


def react(polymer: str) -> str:
    """
        >>> react('aA')
        ''
        >>> react('abBA')
        ''
        >>> react('abAB')
        'abAB'
        >>> react('aabAAB')
        'aabAAB'
        >>> react('dabAcCaCBAcCcaDA')
        'dabCBAcaDA'
    """
    def is_reactive(p_1: str, p_2: str) -> bool:
        return p_1.isupper() != p_2.isupper() and p_1.upper() == p_2.upper()

    p_out: list[str] = []

    for c in polymer:
        if p_out and is_reactive(p_out[-1], c):
            p_out.pop()
        else:
            p_out.append(c)
    return ''.join(p_out)


def part_1(polymer: str) -> int:
    polymer = react(polymer)
    print(f"part 1: polymer length after reactions is {len(polymer)}")
    return len(polymer)


def part_2(polymer: str) -> int:
    char, plen = mink(
        string.ascii_lowercase,
        key=lambda pc: len(react(''.join(c for c in polymer if c.lower() != pc)))
    )
    print(f"part 2: best to remove {char!r} -> polymer length after reactions is then {plen}")
    return plen


def polymer_from_file(fn: str) -> str:
    return open(relative_path(__file__, fn)).readline().strip()


if __name__ == '__main__':
    polymer_ = polymer_from_file('data/05-input.txt')
    assert len(polymer_) == 50_000
    part_1(polymer_)
    part_2(polymer_)
