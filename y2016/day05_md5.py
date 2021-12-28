from itertools import count
from typing import Iterable
from typing import Optional

from common.md5 import md5


def create_password(door_id: str, version: int, length: int = 8) -> str:
    if version == 1:
        return ''.join(generate_digits_v1(door_id, length))

    elif version == 2:
        digits: list[Optional[str]] = ['_'] * length
        remaining = length
        for pos, digit in generate_digits_v2(door_id, length):
            if digits[pos] == '_':
                digits[pos] = digit
                remaining -= 1
                print(f"> {''.join(digits)!r} ... remaining={remaining}")
                if remaining == 0:
                    return ''.join(digits)

    else:
        raise ValueError(f"unknown version {version}")


def generate_digits_v1(door_id: str, remaining: int) -> Iterable[str]:
    for index in count(0):
        h = md5(door_id + str(index))
        if h.startswith('00000'):
            print(f"md5('{door_id}{index}') = {h!r} -> {h[5]}")
            yield h[5]
            remaining -= 1
            if remaining <= 0:
                return


def generate_digits_v2(door_id: str, length: int) -> Iterable[str]:
    for index in count(0):
        h = md5(door_id + str(index))
        if h.startswith('00000'):
            pos, digit = int(h[5], 16), h[6]
            print(
                f"md5('{door_id}{index}') = {h!r} -> pos={pos}, digit={digit!r} "
                f"({'OK' if pos < length else 'XX'})"
            )
            if pos < length:
                yield pos, digit


def test_create_password_v1():
    assert create_password('abc', version=1) == '18f47a30'


def test_create_password_v2():
    assert create_password('abc', version=2) == '05ace8e3'


def part_1(door_id: str) -> str:
    pwd = create_password(door_id, version=1)
    print(f"part 1: password v1 for door_id {door_id!r} is {pwd!r}")
    return pwd


def part_2(door_id: str) -> str:
    pwd = create_password(door_id, version=2)
    print(f"part 2: password v2 for door_id {door_id!r} is {pwd!r}")
    return pwd


if __name__ == '__main__':
    did = 'abbhdwsy'
    part_1(did)
    part_2(did)
