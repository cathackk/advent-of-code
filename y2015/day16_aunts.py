"""
Advent of Code 2015
Day 16: Aunt Sue
https://adventofcode.com/2015/day/16
"""

from typing import Iterable

from common.iteration import single_value
from meta.aoc_tools import data_path


def part_1(aunts: list['Aunt'], criteria: list['Criterium']) -> int:
    """
    Your Aunt Sue has given you a wonderful gift, and you'd like to send her a thank you card.
    However, there's a small problem: she signed it "From, Aunt Sue".

    You have 500 Aunts named "Sue".

    So, to avoid sending the card to the wrong person, you need to figure out which Aunt Sue (which
    you conveniently number 1 to 500, for sanity) gave you the gift. You open the present and, as
    luck would have it, good ol' Aunt Sue got you a My First Crime Scene Analysis Machine! Just what
    you wanted. Or needed, as the case may be.

    The My First Crime Scene Analysis Machine (MFCSAM for short) can detect a few specific compounds
    in a given sample, as well as how many distinct kinds of those compounds there are. According to
    the instructions, these are what the MFCSAM can detect:

      - `children`, by human DNA age analysis.
      - `cats`. It doesn't differentiate individual breeds.
      - Several seemingly random breeds of dog: `samoyeds`, `pomeranians`, `akitas`, and `vizslas`.
      - `goldfish`. No other kinds of fish.
      - `trees`, all in one group.
      - `cars`, presumably by exhaust or gasoline or something.
      - `perfumes`, which is handy, since many of your Aunts Sue wear a few kinds.

    In fact, many of your Aunts Sue have many of these. You put the wrapping from the gift into the
    MFCSAM. It beeps inquisitively at you a few times and then prints out a message on ticker tape:

        >>> example_crits = criteria_from_text('''
        ...     children: 3
        ...     samoyeds: 1
        ...     akitas: 3
        ...     goldfish: 1
        ...     cars: 3
        ...     perfumes: 2
        ... ''')
        >>> example_crits[0]
        Criterium('children', '=', 3)

    You make a list of the things you can remember about each Aunt Sue. Things missing from your
    list aren't zero - you simply don't remember the value.

        >>> example_aunts = aunts_from_text('''
        ...     Sue 1: cars: 3, akitas: 3, goldfish: 0
        ...     Sue 2: akitas: 3, children: 1, samoyeds: 0
        ...     Sue 3: perfumes: 2, cars: 3, goldfish: 1
        ... ''')
        >>> example_aunts[0]
        Aunt(1, cars=3, akitas=3, goldfish=0)

    What is the number of the Sue that got you the gift?

        >>> part_1(example_aunts, example_crits)
        part 1: the gift is from aunt Sue 3
        3
    """

    result = single_value(filter_aunts(aunts, criteria)).number
    print(f"part 1: the gift is from aunt Sue {result}")
    return result


def part_2(aunts: list['Aunt'], criteria: list['Criterium']) -> int:
    r"""
    As you're about to send the thank you note, something in the MFCSAM's instructions catches your
    eye. Apparently, it has an outdated retroencabulator, and so the output from the machine isn't
    exact values - some of them indicate ranges.

    In particular, the `cats` and `trees` readings indicates that there are **greater than** that
    many (due to the unpredictable nuclear decay of cat dander and tree pollen), while the
    `pomeranians` and `goldfish` readings indicate that there are **fewer than** that many (due to
    the modial interaction of magnetoreluctance).

    What is the number of the real Aunt Sue?

        >>> example_criteria = criteria_from_file(data_path(__file__, 'criteria.txt'))
        >>> example_criteria_adjusted = list(adjust_criteria(example_criteria))
        >>> example_criteria_adjusted[1]
        Criterium('cats', '>', 7)
        >>> example_criteria_adjusted[3]
        Criterium('pomeranians', '<', 3)
        >>> example_criteria_adjusted[6]
        Criterium('goldfish', '<', 5)
        >>> example_criteria_adjusted[7]
        Criterium('trees', '>', 3)
        >>> example_aunts = aunts_from_file(data_path(__file__, 'example.txt'))
        >>> print("\n".join(str(aunt) for aunt in example_aunts))
        Sue 1: cats: 10, pomeranians: 2, trees: 4
        Sue 2: goldfish: 3, trees: 3, children: 0
        Sue 3: pomeranians: 1, cats: 5, perfumes: 6

        >>> part_2(example_aunts, example_criteria)
        part 2: the gift is from aunt Sue 1
        1
    """

    result = single_value(filter_aunts(aunts, adjust_criteria(criteria))).number
    print(f"part 2: the gift is from aunt Sue {result}")
    return result


class Aunt:
    def __init__(self, number, **data):
        self.number = int(number)
        self.data = {key: int(value) for key, value in data.items()}

    def __repr__(self) -> str:
        data_repr = ', '.join(f'{key}={value!r}' for key, value in self.data.items())
        return f'{type(self).__name__}({self.number!r}, {data_repr})'

    def __str__(self) -> str:
        data_str = ", ".join(f"{key}: {value}" for key, value in self.data.items())
        return f"Sue {self.number}: {data_str}"

    @classmethod
    def from_str(cls, line: str) -> 'Aunt':
        name_part, data_part = line.strip().split(': ', 1)
        sue, number = name_part.split(' ')
        assert sue == "Sue"
        return cls(number, **dict((item.split(': ') for item in data_part.split(', '))))


class Criterium:
    def __init__(self, key, op, value):
        self.key = str(key)
        self.op = str(op)
        self.value = int(value)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.key!r}, {self.op!r}, {self.value!r})'

    def __str__(self) -> str:
        if self.op == '=':
            return f"{self.key}: {self.value}"
        else:
            return f"{self.key} {self.op} {self.value}"

    @classmethod
    def from_str(cls, line: str) -> 'Criterium':
        key, value = line.split(': ')
        return cls(key, '=', value)

    def matches(self, aunt: Aunt) -> bool:
        if self.key not in aunt.data:
            return True

        aunt_value = aunt.data[self.key]
        match self.op:
            case '=':
                return aunt_value == self.value
            case '>':
                return aunt_value > self.value
            case '<':
                return aunt_value < self.value
            case _:
                raise ValueError(self.op)

        # TODO: remove when mypy realizes this is unreachable
        assert False


def filter_aunts(aunts: Iterable[Aunt], criteria: Iterable[Criterium]) -> Iterable[Aunt]:
    criteria = list(criteria)
    return (aunt for aunt in aunts if all(crit.matches(aunt) for crit in criteria))


def adjust_criteria(criteria: Iterable[Criterium]) -> Iterable[Criterium]:
    new_ops = {'cats': '>', 'pomeranians': '<', 'goldfish': '<', 'trees': '>'}
    return (
        type(crit)(crit.key, new_ops.get(crit.key, '='), crit.value)
        for crit in criteria
    )


def aunts_from_text(text: str) -> list[Aunt]:
    return list(aunts_from_lines(text.strip().splitlines()))


def aunts_from_file(fn: str) -> list[Aunt]:
    return list(aunts_from_lines(open(fn)))


def aunts_from_lines(lines: Iterable[str]) -> Iterable[Aunt]:
    return (Aunt.from_str(line.strip()) for line in lines)


def criteria_from_text(text: str) -> list[Criterium]:
    return list(criteria_from_lines(text.strip().splitlines()))


def criteria_from_file(fn: str) -> list[Criterium]:
    return list(criteria_from_lines(open(fn)))


def criteria_from_lines(lines: Iterable[str]) -> Iterable[Criterium]:
    return (Criterium.from_str(line.strip()) for line in lines)


def main(
    input_path: str = data_path(__file__),
    criteria_path: str = data_path(__file__, 'criteria.txt')
) -> tuple[int, int]:
    aunts = aunts_from_file(input_path)
    criteria = criteria_from_file(criteria_path)
    result_1 = part_1(aunts, criteria)
    result_2 = part_2(aunts, criteria)
    return result_1, result_2


if __name__ == '__main__':
    main()
