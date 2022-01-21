"""
Advent of Code 2016
Day 9: Explosives in Cyberspace
https://adventofcode.com/2016/day/9
"""

from typing import Iterable

from common.file import relative_path


def part_1(compressed: str) -> int:
    """
    Wandering around a secure area, you come across a datalink port to a new part of the network.
    After briefly scanning it for interesting files, you find one file in particular that catches
    your attention. It's compressed with an experimental format, but fortunately, the documentation
    for the format is nearby.

    The format compresses a sequence of characters. Whitespace is ignored. To indicate that some
    sequence should be repeated, a marker is added to the file, like `(10x2)`. To decompress this
    marker, take the subsequent `10` characters and repeat them `2` times. Then, continue reading
    the file **after** the repeated data. The marker itself is not included in the decompressed
    output.

    If parentheses or other characters appear within the data referenced by a marker, that's okay -
    treat it like normal data, not a marker, and then resume looking for markers after
    the decompressed section.

    For example:

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

    What is the **decompressed length** of the file (your puzzle input)? Don't count whitespace.

        >>> part_1('X(8x2)(3x3)ABCY')
        part 1: decompressed length is 18
        18
    """

    length = decompressed_length(compressed)
    print(f"part 1: decompressed length is {length}")
    return length


def part_2(compressed: str) -> int:
    """
    Apparently, the file actually uses **version two** of the format.

    In version two, the only difference is that markers within decompressed data **are** decompres-
    sed. This, the documentation explains, provides much more substantial compression capabilities,
    allowing many-gigabyte files to be stored in only a few kilobytes.

    For example:

      - `(3x3)XYZ` still becomes `XYZXYZXYZ`, as the decompressed section contains no markers:

        >>> decompress('(3x3)XYZ', recursive=True)
        'XYZXYZXYZ'

      - `X(8x2)(3x3)ABCY` becomes `XABCABCABCABCABCABCY`, because the decompressed data from
        the `(8x2)` marker is then further decompressed, thus triggering the `(3x3)` marker twice
        for a total of six ABC sequences:

        >>> decompress('X(8x2)(3x3)ABCY', recursive=True)
        'XABCABCABCABCABCABCY'

      - The following strings decompresses into a string of `A` repeated 241920 times:

        >>> decompress('(27x12)(20x12)(13x14)(7x10)(1x12)A', recursive=True) == 'A' * 12*12*14*10*12
        True

    Unfortunately, the computer you brought probably doesn't have enough memory to actually
    decompress the file; you'll have to **come up with another way** to get its decompressed length.

    What is the **decompressed length** of the file using this improved format?

        >>> part_2('(25x3)(3x3)ABC(2x3)XY(5x2)PQRSTX(18x9)(3x2)TWO(5x7)SEVEN')
        part 2: decompressed length is 445
        445
    """

    length = decompressed_length(compressed, recursive=True)
    print(f"part 2: decompressed length is {length}")
    return length


def decompress(string: str, recursive: bool = False) -> str:
    string = ''.join(_decompress_parts(string))
    while recursive and '(' in string:
        string = ''.join(_decompress_parts(string))
    return string


def _decompress_parts(string: str) -> Iterable[str]:
    pos = 0
    while True:
        group = _find_group(string, pos)
        if group is not None:
            start, end, length, repeats = group
            yield string[pos:start]
            pos = end + length
            yield string[end:pos] * repeats
        else:
            yield string[pos:]
            return


def _find_group(string: str, pos: int = 0) -> tuple[int, int, int, int] | None:
    """
    Finds the first marker in `string` starting at `pos` and returns tuple of four numbers:

      - start of the group (and of the marker)
      - end of the compressed group
      - length of the group
      - number of repeats for the group

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
    start = string.find('(', pos)
    if start < 0:
        return None
    end = string.find(')', start)
    assert end >= 0
    length, repeats = string[start + 1:end].split('x')
    return start, end + 1, int(length), int(repeats)


def decompressed_length(string: str, recursive: bool = False) -> int:
    return sum(_decompressed_length_parts(string, recursive=recursive))


def _decompressed_length_parts(string: str, recursive: bool) -> Iterable[int]:
    pos = 0
    while True:
        group = _find_group(string, pos)
        if group is not None:
            start, end, length, repeats = group
            yield start - pos
            pos = end + length
            group_target = string[end:pos]
            if recursive:
                yield decompressed_length(group_target, recursive=True) * repeats
            else:
                yield length * repeats
        else:
            yield len(string) - pos
            return


def string_from_file(fn: str) -> str:
    return open(relative_path(__file__, fn)).readline().strip()


if __name__ == '__main__':
    compressed_ = string_from_file('data/09-input.txt')
    part_1(compressed_)
    part_2(compressed_)
