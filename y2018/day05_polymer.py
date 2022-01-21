import string

from common.iteration import mink


def react(polymer: str):
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
    def is_reactive(p1: str, p2: str) -> bool:
        return p1.isupper() != p2.isupper() and p1.upper() == p2.upper()

    p_out = []

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
    ch, pl = mink(
        string.ascii_lowercase,
        key=lambda pc: len(react(''.join(c for c in polymer if c.lower() != pc)))
    )
    print(f"part 2: best to remove {ch!r} -> polymer length after reactions is then {pl}")
    return pl


if __name__ == '__main__':
    polymer_ = open("data/05-input.txt").readline().strip()
    assert len(polymer_) == 50_000
    part_1(polymer_)
    part_2(polymer_)
