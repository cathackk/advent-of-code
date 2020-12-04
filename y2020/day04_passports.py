"""
Advent of Code 2020
Day 4: Passport Processing
https://adventofcode.com/2020/day/4
"""

from typing import Dict
from typing import Iterable
from typing import List
from typing import Tuple


def part_1(passports: List['Passport']) -> int:
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
        ... ecl:gry pid:860033327 eyr:2020 hcl:#fffffd
        ... byr:1937 iyr:2017 cid:147 hgt:183cm
        ...
        ... iyr:2013 ecl:amb cid:350 eyr:2023 pid:028048884
        ... hcl:#cfa07d byr:1929
        ...
        ... hcl:#ae17e1 iyr:2013
        ... eyr:2024
        ... ecl:brn pid:760753108 byr:1931
        ... hgt:179cm
        ...
        ... hcl:#cfa07d eyr:2025 pid:166559648
        ... iyr:2011 ecl:brn hgt:59in
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


def part_2(passports: List['Passport']) -> int:
    """
    Better add some data validation! You can continue to ignore the `cid` field, but each other
    field has strict rules about what values are valid for automatic validation.

    (Rules are listed with examples in `is_valid_entry` function.)

    Your job is to count the passports where *all required fields are both present and valid*
    according to the above rules.

    Here are some invalid passports:

        >>> invalid_passports = passports_from_text('''
        ... eyr:1972 cid:100
        ... hcl:#18171d ecl:amb hgt:170 pid:186cm iyr:2018 byr:1926
        ...
        ... iyr:2019
        ... hcl:#602927 eyr:1967 hgt:170cm
        ... ecl:grn pid:012533040 byr:1946
        ...
        ... hcl:dab227 iyr:2012
        ... ecl:brn hgt:182cm pid:021572410 eyr:2020 byr:1992 cid:277
        ...
        ... hgt:59cm ecl:zzz
        ... eyr:2038 hcl:74454a iyr:2023
        ... pid:3556412378 byr:2007
        ... ''')
        >>> len(invalid_passports)
        4
        >>> any(is_valid_passport(p) for p in invalid_passports)
        False

    Here are some valid passports:

        >>> valid_passports = passports_from_text('''
        ... pid:087499704 hgt:74in ecl:grn iyr:2012 eyr:2030 byr:1980
        ... hcl:#623a2f
        ...
        ... eyr:2029 ecl:blu cid:129 byr:1989
        ... iyr:2014 pid:896056539 hcl:#a97842 hgt:165cm
        ...
        ... hcl:#888785
        ... hgt:164cm byr:2001 iyr:2015 cid:88
        ... pid:545766238 ecl:hzl
        ... eyr:2022
        ...
        ... iyr:2010 hgt:158cm hcl:#b6652a ecl:blu byr:1944 eyr:2021 pid:093154719
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


def passports_from_file(fn: str) -> List[Passport]:
    with open(fn) as f:
        return list(passports_from_lines(f))


def passports_from_text(text: str) -> List[Passport]:
    return list(passports_from_lines(text.strip().split('\n')))


def passports_from_lines(lines: Iterable[str]) -> Iterable[Passport]:
    """
    Each passport is represented as a sequence of `key:value` pairs separated by spaces or
    newlines. Passports are separated by blank lines.
    """

    passport = dict()

    def entry_from_text(text: str) -> Tuple[str, str]:
        k, v = text.split(':')
        return k, v

    for line in lines:
        line = line.strip()

        if line:
            passport.update(
                entry_from_text(part)
                for part in line.split(' ')
            )

        elif passport:
            # flush on empty line
            yield passport
            passport = dict()

    # flush the rest at the end of input
    if passport:
        yield passport


def has_required_fields(passport: Passport) -> bool:
    required_fields = {'byr', 'iyr', 'eyr', 'hgt', 'hcl', 'ecl', 'pid'}
    return set(passport.keys()).issuperset(required_fields)


def is_valid_entry(key: str, value: str) -> bool:
    """
    - `byr` (Birth Year) - four digits; at least `1920` and at most `2002`.

        >>> is_valid_entry('byr', '2002')
        True
        >>> is_valid_entry('byr', '2003')
        False
        >>> is_valid_entry('byr', '20XY')
        False

    - `iyr` (Issue Year) - four digits; at least `2010` and at most `2020`.

        >>> is_valid_entry('iyr', '2010')
        True
        >>> is_valid_entry('iyr', '2000')
        False
        >>> is_valid_entry('iyr', ':)')
        False

    - `eyr` (Expiration Year) - four digits; at least `2020` and at most `2030`.

        >>> is_valid_entry('eyr', '2030')
        True
        >>> is_valid_entry('eyr', '2031')
        False
        >>> is_valid_entry('eyr', '????')
        False

    - `hgt` (Height) - a number followed by either `cm` or `in`:
        - If `cm`, the number must be at least `150` and at most `193`.
        - If `in`, the number must be at least `59` and at most `76`.

        >>> is_valid_entry('hgt', '60in')
        True
        >>> is_valid_entry('hgt', '190cm')
        True
        >>> is_valid_entry('hgt', '190in')
        False
        >>> is_valid_entry('hgt', '190')
        False
        >>> is_valid_entry('hgt', 'xxcm')
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
        >>> is_valid_entry('pid', '01234567x')
        False

    - `cid` (Country ID) - ignored, missing or not.
    """

    try:
        if key == 'byr':
            return 1920 <= int(value) <= 2002

        elif key == 'iyr':
            return 2010 <= int(value) <= 2020

        elif key == 'eyr':
            return 2020 <= int(value) <= 2030

        elif key == 'hgt':
            if value.endswith('cm'):
                return 150 <= int(value[:-2]) <= 193
            elif value.endswith('in'):
                return 59 <= int(value[:-2]) <= 76
            else:
                return False

        elif key == 'hcl':
            return len(value) == 7 \
                   and value[0] == '#' \
                   and all(c in '0123456789abcdef' for c in value[1:])

        elif key == 'ecl':
            return value in {'amb', 'blu', 'brn', 'gry', 'grn', 'hzl', 'oth'}

        elif key == 'pid':
            return len(value) == 9 \
                   and all(c in '0123456789' for c in value)

        elif key == 'cid':
            return True

        else:
            # unsupported key
            return False

    except ValueError:
        # failed to parse an int
        return False


def is_valid_passport(passport: Passport) -> bool:
    return has_required_fields(passport) \
           and all(is_valid_entry(*entry) for entry in passport.items())


if __name__ == '__main__':
    passports_ = passports_from_file('data/04-input.txt')
    part_1(passports_)
    part_2(passports_)
