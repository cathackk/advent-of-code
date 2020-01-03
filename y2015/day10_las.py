from typing import Iterable
from typing import Tuple


def group(seq: Iterable[int]) -> Iterable[Tuple[int, int]]:
    value, count = None, 0
    for n in seq:
        if value is None:
            value, count = n, 1
        elif n == value:
            count += 1
        else:
            yield count, value
            value, count = n, 1
    yield count, value


def lass(seq: Iterable[int]) -> Iterable[int]:
    for digit, count in group(seq):
        yield digit
        yield count


def lass_num(num: int) -> int:
    ls = lass(int(c) for c in str(num))
    return int(''.join(str(c) for c in ls))


def lass_str(num: str) -> str:
    return ''.join(str(c) for c in lass(num))


def tests():
    assert lass_num(1) == 11
    assert lass_num(11) == 21
    assert lass_num(21) == 1211
    assert lass_num(1211) == 111221
    assert lass_num(111221) == 312211

    assert lass_str('111221') == '312211'


if __name__ == '__main__':
    tests()

    n = '3113322113'
    for _ in range(40):
        n = lass_str(n)
    print(f"part 1: length of the number is {len(n)}")

    for _ in range(10):
        n = lass_str(n)
    print(f"part 2: length of the number is {len(n)}")
