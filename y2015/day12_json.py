"""
Advent of Code 2015
Day 12: JSAbacusFramework.io
https://adventofcode.com/2015/day/12
"""

import json

from common.utils import relative_path


def part_1(document) -> int:
    """
    Santa's Accounting-Elves need help balancing the books after a recent order. Unfortunately,
    their accounting software uses a peculiar storage format. That's where you come in.

    They have a JSON document which contains a variety of things: arrays (`[1,2,3]`), objects
    (`{"a":1, "b":2}`), numbers, and strings. Your first job is to simply find all of
    the **numbers** throughout the document and add them together.

    For example:

        >>> sumj([1, 2, 3])
        6
        >>> sumj({"a": 2, "b": 4})
        6
        >>> sumj([[[3]]])
        3
        >>> sumj({"a": {"b": 4}, "c": -1})
        3
        >>> sumj({"a": [-1,1]})
        0
        >>> sumj([-1, {"a": 1}])
        0
        >>> sumj([])
        0
        >>> sumj({})
        0

    You will not encounter any strings containing numbers.

    What is the **sum of all numbers** in the document?

        >>> part_1(load_document('data/12-example.json'))
        part 1: sum of all numbers in document is 6
        6
    """

    result = sumj(document)
    print(f"part 1: sum of all numbers in document is {result}")
    return result


def part_2(document) -> int:
    """
    Uh oh - the Accounting-Elves have realized that they double-counted everything **red**.

    Ignore any object (and all of its children) which has any property with the value `"red"`.
    Do this only for objects (`{...}`), not arrays (`[...]`).

        >>> sumj([1, 2, 3], fv='red')
        6
        >>> sumj([1, {"c": "red", "b": 2}, 3], fv='red')
        4
        >>> sumj({"d": "red", "e": [1, 2, 3, 4], "f": 5}, fv='red')
        0
        >>> sumj([1, "red", 5])
        6

        >>> part_2(load_document('data/12-example.json'))
        part 2: sum of all numbers in document (ignoring "red") is 4
        4
    """

    result = sumj(document, fobidden_value='red')
    print(f'part 2: sum of all numbers in document (ignoring "red") is {result}')
    return result


def sumj(d, fobidden_value=None) -> int:
    if isinstance(d, int):
        return d

    elif isinstance(d, list):
        return sum(sumj(v, fobidden_value) for v in d)

    elif isinstance(d, dict):
        return (
            sum(sumj(value, fobidden_value) for value in d.values())
            if fobidden_value is None or all(value != fobidden_value for value in d.values())
            else 0
        )

    elif isinstance(d, str):
        return 0

    else:
        raise ValueError(f"unsupported type {type(d).__name__}")


def load_document(fn: str):
    return json.load(open(relative_path(__file__, fn)))


if __name__ == '__main__':
    document_ = load_document('data/12-input.json')
    part_1(document_)
    part_2(document_)
