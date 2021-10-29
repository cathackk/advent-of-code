"""
Advent of Code 2020
Day 4: Passport Processing
https://adventofcode.com/2020/day/4
"""

import re
from functools import partial
from typing import Dict
from typing import Iterable

from utils import line_groups


def part_1(passports: list['Passport']) -> int:
    """
    The automatic passport scanners are detecting which passports have all required fields.
    The expected fields are as follows:

        - `byr` (Birth Year)
        - `iyr` (Issue Year)
        - `eyr` (Expiration Year)
        - `hgt` (Height)
        - `hcl` (Hair Color)
        - `ecl` (Eye Color)
        - `pid` (Passport ID)
        - `cid` (Country ID)

    Passport data is validated in batch files (your puzzle input). Each passport is represented
    as a sequence of `key:value` pairs separated by spaces or newlines. Passports are separated by
    blank lines.

    Here is an example batch file containing four passports:

        >>> pps = passports_from_text('''
        ...
        ...     ecl:gry pid:860033327 eyr:2020 hcl:#fffffd
        ...     byr:1937 iyr:2017 cid:147 hgt:183cm
        ...
        ...     iyr:2013 ecl:amb cid:350 eyr:2023 pid:028048884
        ...     hcl:#cfa07d byr:1929
        ...
        ...     hcl:#ae17e1 iyr:2013
        ...     eyr:2024
        ...     ecl:brn pid:760753108 byr:1931
        ...     hgt:179cm
        ...
        ...     hcl:#cfa07d eyr:2025 pid:166559648
        ...     iyr:2011 ecl:brn hgt:59in
        ...
        ... ''')
        >>> len(pps)
        4

    The first passport is *valid* - all eight fields are present:

        >>> has_required_fields(pps[0])
        True
        >>> len(pps[0])
        8

    The second passport is *invalid* - it is missing `hgt` (the Height field):

        >>> has_required_fields(pps[1])
        False
        >>> 'hgt' in pps[1]
        False

    The third passport is interesting; the only missing field is `cid`. ... Surely, nobody would
    mind if you made the system temporarily ignore missing `cid` fields. Treat this "passport" as
    valid:

        >>> 'cid' in pps[2]
        False
        >>> has_required_fields(pps[2])
        True

    The fourth passport is missing two fields, `cid` and `byr`. Missing `cid` is fine, but missing
    any other field is not, so this passport is invalid:

        >>> 'cid' in pps[3]
        False
        >>> 'byr' in pps[3]
        False
        >>> has_required_fields(pps[3])
        False

    Count the number of *valid* passports - those that have all required fields. Treat `cid` as
    optional. *In your batch file, how many passports are valid?*

        >>> part_1(pps)
        part 1: 2 passports out of 4 have all required fields
        2
    """

    result = sum(1 for p in passports if has_required_fields(p))
    print(f"part 1: {result} passports out of {len(passports)} have all required fields")
    return result


def part_2(passports: list['Passport']) -> int:
    """
    Better add some data validation! You can continue to ignore the `cid` field, but each other
    field has strict rules about what values are valid for automatic validation.

        - `byr` (Birth Year) - four digits; at least 1920 and at most 2002.
        - `iyr` (Issue Year) - four digits; at least 2010 and at most 2020.
        - `eyr` (Expiration Year) - four digits; at least 2020 and at most 2030.

            >>> is_valid_entry('byr', '2002')
            True
            >>> is_valid_entry('byr', '2003')
            False
            >>> is_valid_entry('iyr', '2009')
            False
            >>> is_valid_entry('eyr', 'unknown')
            False

        - `hgt` (Height) - a number followed by either `cm` or `in`:
            - If `cm`, the number must be at least 150 and at most 193.
            - If `in`, the number must be at least 59 and at most 76.

            >>> is_valid_entry('hgt', '60in')
            True
            >>> is_valid_entry('hgt', '190cm')
            True
            >>> is_valid_entry('hgt', '190in')
            False
            >>> is_valid_entry('hgt', '6ft')
            False
            >>> is_valid_entry('hgt', '190')
            False
            >>> is_valid_entry('hgt', 'big')
            False

        - `hcl` (Hair Color) - a `#` followed by exactly six characters `0-9` or `a-f`.

            >>> is_valid_entry('hcl', '#123abc')
            True
            >>> is_valid_entry('hcl', '#123abz')
            False
            >>> is_valid_entry('hcl', '123abc')
            False

        - `ecl` (Eye Color) - exactly one of: `amb` `blu` `brn` `gry` `grn` `hzl` `oth`.

            >>> is_valid_entry('ecl', 'brn')
            True
            >>> is_valid_entry('ecl', 'wat')
            False

        - `pid` (Passport ID) - a nine-digit number, including leading zeroes.

            >>> is_valid_entry('pid', '000000001')
            True
            >>> is_valid_entry('pid', '0123456789')
            False

        - `cid` (Country ID) - ignored, missing or not.

    Your job is to count the passports where *all required fields are both present and valid*
    according to the above rules.

    Here are some invalid passports:

        >>> invalid_passports = passports_from_text('''
        ...
        ...     eyr:1972 cid:100
        ...     hcl:#18171d ecl:amb hgt:170 pid:186cm iyr:2018 byr:1926
        ...
        ...     iyr:2019
        ...     hcl:#602927 eyr:1967 hgt:170cm
        ...     ecl:grn pid:012533040 byr:1946
        ...
        ...     hcl:dab227 iyr:2012
        ...     ecl:brn hgt:182cm pid:021572410 eyr:2020 byr:1992 cid:277
        ...
        ...     hgt:59cm ecl:zzz
        ...     eyr:2038 hcl:74454a iyr:2023
        ...     pid:3556412378 byr:2007
        ...
        ... ''')
        >>> len(invalid_passports)
        4
        >>> any(is_valid_passport(p) for p in invalid_passports)
        False

    Here are some valid passports:

        >>> valid_passports = passports_from_text('''
        ...
        ...     pid:087499704 hgt:74in ecl:grn iyr:2012 eyr:2030 byr:1980
        ...     hcl:#623a2f
        ...
        ...     eyr:2029 ecl:blu cid:129 byr:1989
        ...     iyr:2014 pid:896056539 hcl:#a97842 hgt:165cm
        ...
        ...     hcl:#888785
        ...     hgt:164cm byr:2001 iyr:2015 cid:88
        ...     pid:545766238 ecl:hzl
        ...     eyr:2022
        ...
        ...     iyr:2010 hgt:158cm hcl:#b6652a ecl:blu byr:1944 eyr:2021 pid:093154719
        ...
        ... ''')
        >>> len(valid_passports)
        4
        >>> all(is_valid_passport(p) for p in valid_passports)
        True

    Count the number of valid passports - those that have all required fields and valid values.
    Continue to treat `cid` as optional. In your batch file, how many passports are valid?

        >>> part_2(invalid_passports + valid_passports)
        part 2: 4 passports out of 8 are valid
        4
    """

    result = sum(1 for p in passports if is_valid_passport(p))
    print(f"part 2: {result} passports out of {len(passports)} are valid")
    return result


Passport = Dict[str, str]


def passports_from_file(fn: str) -> list[Passport]:
    with open(fn) as f:
        return list(passports_from_lines(f))


def passports_from_text(text: str) -> list[Passport]:
    return list(passports_from_lines(text.strip().split('\n')))


def passports_from_lines(lines: Iterable[str]) -> Iterable[Passport]:
    """
    Each passport is represented as a sequence of `key:value` pairs separated by spaces or
    newlines. Passports are separated by blank lines.
    """

    def entry_from_text(text: str) -> tuple[str, str]:
        k, v = text.split(':')
        return k, v

    for lines_group in line_groups(lines):
        yield dict(
            entry_from_text(part)
            for line in lines_group
            for part in line.split(' ')
        )


def validate_range(min_value: int, max_value: int, value: str) -> bool:
    try:
        return min_value <= int(value) <= max_value
    except ValueError:
        # failed to convert value to int
        return False


def validate_height(ranges: Dict[str, tuple[int, int]], value: str) -> bool:
    for unit, (min_value, max_value) in ranges.items():
        if value.endswith(unit):
            return validate_range(min_value, max_value, value.removesuffix(unit))
    else:
        # unit not found
        return False


def validate_re(pattern: re.Pattern, value: str) -> bool:
    return bool(pattern.fullmatch(value))


validators = {
    'byr': partial(validate_range, 1920, 2002),
    'iyr': partial(validate_range, 2010, 2020),
    'eyr': partial(validate_range, 2020, 2030),
    'hgt': partial(validate_height, {'cm': (150, 193), 'in': (59, 76)}),
    'hcl': partial(validate_re, re.compile(r'#[0-9a-f]{6}')),
    'ecl': partial(validate_re, re.compile(r'(amb|blu|brn|gry|grn|hzl|oth)')),
    'pid': partial(validate_re, re.compile(r'[0-9]{9}')),
    'cid': None  # ignored
}


def has_required_fields(passport: Passport) -> bool:
    # fields with a defined validator are required
    required_fields = set(
        field
        for field, validator in validators.items()
        if validator
    )
    return set(passport.keys()).issuperset(required_fields)


def is_valid_entry(field: str, value: str) -> bool:
    if field not in validators:
        # unsupported field
        return False

    if validators[field] is None:
        # ignored field: always valid
        return True

    return validators[field](value)


def is_valid_passport(passport: Passport) -> bool:
    return has_required_fields(passport) \
           and all(is_valid_entry(*entry) for entry in passport.items())


if __name__ == '__main__':
    passports_ = passports_from_file('data/04-input.txt')
    part_1(passports_)
    part_2(passports_)
