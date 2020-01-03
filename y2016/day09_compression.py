from typing import Iterable
from typing import Optional
from typing import Tuple


def decompress(s: str, recursive: bool = False) -> str:
    """
    >>> decompress('ADVENT')
    'ADVENT'
    >>> decompress('A(1x5)BC')
    'ABBBBBC'
    >>> decompress('(3x3)XYZ')
    'XYZXYZXYZ'
    >>> decompress('A(2x2)BCD(2x2)EFG')
    'ABCBCDEFEFG'
    >>> decompress('(6x1)(1x3)A')
    '(1x3)A'
    >>> decompress('X(8x2)(3x3)ABCY')
    'X(3x3)ABC(3x3)ABCY'

    >>> decompress('(3x3)XYZ', recursive=True)
    'XYZXYZXYZ'
    >>> decompress('X(8x2)(3x3)ABCY', recursive=True)
    'XABCABCABCABCABCABCY'
    >>> decompress('(27x12)(20x12)(13x14)(7x10)(1x12)A', recursive=True) == ('A' * 241920)
    True
    >>> len(decompress('(25x3)(3x3)ABC(2x3)XY(5x2)PQRSTX(18x9)(3x2)TWO(5x7)SEVEN', recursive=True))
    445
    """
    s = ''.join(_decompress_parts(s))
    while recursive and '(' in s:
        s = ''.join(_decompress_parts(s))
    return s


def _decompress_parts(s: str) -> Iterable[str]:
    pos = 0
    while True:
        group = _find_group(s, pos)
        if group is not None:
            start, end, length, repeats = group
            yield s[pos:start]
            pos = end + length
            yield s[end:pos] * repeats
        else:
            yield s[pos:]
            return


def _find_group(s: str, pos: int = 0) -> Optional[Tuple[int, int, int, int]]:
    """
    >>> _find_group('ADVENT') is None
    True
    >>> _find_group('XA(1x5)BC')
    (2, 7, 1, 5)
    >>> _find_group('XA(1x5)BC', 3) is None
    True
    >>> _find_group('A(2x2)BCD(2x2)EFG', 0)
    (1, 6, 2, 2)
    >>> _find_group('A(2x2)BCD(2x2)EFG', 7)
    (9, 14, 2, 2)
    """
    assert pos >= 0
    start = s.find('(', pos)
    if start < 0:
        return None
    end = s.find(')', start)
    assert end >= 0
    length, repeats = s[start+1:end].split('x')
    return start, end+1, int(length), int(repeats)


def decompressed_length(s: str, recursive: bool = False) -> int:
    """
    >>> decompressed_length('(25x3)(3x3)ABC(2x3)XY(5x2)PQRSTX(18x9)(3x2)TWO(5x7)SEVEN', False)
    238
    >>> decompressed_length('(25x3)(3x3)ABC(2x3)XY(5x2)PQRSTX(18x9)(3x2)TWO(5x7)SEVEN', True)
    445
    """
    return sum(_decompressed_length_parts(s, recursive=recursive))


def _decompressed_length_parts(s: str, recursive: bool) -> Iterable[int]:
    pos = 0
    while True:
        group = _find_group(s, pos)
        if group is not None:
            start, end, length, repeats = group
            yield start - pos
            pos = end + length
            group_target = s[end:pos]
            if recursive:
                yield decompressed_length(group_target, recursive=True) * repeats
            else:
                yield length * repeats
        else:
            yield len(s) - pos
            return


def part_1(fn: str) -> int:
    compressed = open(fn).readline().strip()
    length = decompressed_length(compressed)
    print(f"part 1: size went from {len(compressed)} to {length}")
    return length


def part_2(fn: str) -> int:
    compressed = open(fn).readline().strip()
    length = decompressed_length(compressed, recursive=True)
    print(f"part 2: size went from {len(compressed)} to {length}")
    return length


if __name__ == '__main__':
    fn_ = "data/09-input.txt"
    part_1(fn_)
    part_2(fn_)
