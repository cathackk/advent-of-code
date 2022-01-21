"""
Advent of Code 2016
Day 16: Dragon Checksum
https://adventofcode.com/2016/day/16
"""

from tqdm import tqdm

from common.file import relative_path


def part_1(initial_state: str, disk_size: int = 272) -> str:
    """
    You're done scanning this part of the network, but you've left traces of your presence. You need
    to overwrite some disks with random-looking data to cover your tracks and update the local
    security system with a new checksum for those disks.

    For the data to not be suspicious, it needs to have certain properties; purely random data will
    be detected as tampering. To generate appropriate random data, you'll need to use a modified
    [dragon curve](https://en.wikipedia.org/wiki/Dragon_curve).

    Start with an appropriate initial state (your puzzle input). Then, so long as you don't have
    enough data yet to fill the disk, repeat the following steps:

      - Call the data you have at this point "a".
      - Make a copy of "a"; call this copy "b".
      - Reverse the order of the characters in "b".
      - In "b", replace all instances of `0` with `1` and all `1`s with `0`.
      - The resulting data is "a", then a single `0`, then "b".

    For example, after a single step of this process:

        >>> dragon('1')
        '100'
        >>> dragon('0')
        '001'
        >>> dragon('11111')
        '11111000000'
        >>> dragon('111100001010')
        '1111000010100101011110000'


    Repeat these steps until you have enough data to fill the desired disk.

    Once the data has been generated, you also need to create a checksum of that data. Calculate the
    checksum **only** for the data that fits on the disk, even if you generated more data than that
    in the previous step.

    The checksum for some given data is created by considering each non-overlapping **pair** of
    characters in the input data. If the two characters match (`00` or `11`), the next checksum
    character is a `1`. If the characters do not match (`01` or `10`), the next checksum character
    is a `0`. This should produce a new string which is exactly half as long as the original. If the
    length of the checksum is **even**, repeat the process until you end up with a checksum with an
    **odd** length.

    For example, suppose we want to fill a disk of length `12`, and when we finally generate a
    string of at least length `12`, the first `12` characters are `110010110100`. To generate its
    checksum:

      - Consider each pair: `11`, `00`, `10`, `11`, `01`, `00`.
      - These are same, same, different, same, different, same, producing `110101`.
      - The resulting string has length `6`, which is **even**, so we repeat the process.
      - The pairs are `11` (same), `01` (different), `01` (different).
      - This produces the checksum `100`, which has an **odd** length, so we stop.

        >>> checksum('110010110100')
        '100'

    Combining all of these steps together, suppose you want to fill a disk of length `20` using an
    initial state of `10000`:

      - Because `10000` is too short, we first use the modified dragon curve to make it longer.
      - After one round, it becomes `10000011110` (`11` characters), still too short.
      - After two rounds, it becomes `10000011110010000111110` (`23` characters), which is enough.
      - Since we only need `20`, but we have `23`, we get rid of all but the first `20` characters:
        `10000011110010000111`.

        >>> dragon_curve('10000', length=20)
        '10000011110010000111'

      - Next, we start calculating the checksum; after one round, we have `0111110101`, which `10`
        characters long (**even**), so we continue.
      - After two rounds, we have `01100`, which is `5` characters long (**odd**), so we are done.

        >>> checksum('10000011110010000111')
        '01100'

    In this example, the correct checksum would therefore be `01100`:

        >>> disk_checksum('10000', 20)
        '01100'

    The first disk you have to fill has length `272`. Using the initial state in your puzzle input,
    **what is the correct checksum**?

        >>> part_1('10000')
        part 1: disk of size 272 has checksum '11010011110011010'
        '11010011110011010'
    """

    result = disk_checksum(initial_state, disk_size)
    print(f"part 1: disk of size {disk_size} has checksum {result!r}")
    return result


def part_2(initial_state: str, disk_size: int = 35651584) -> str:
    """
    The second disk you have to fill has length `35651584`. Again using the initial state in your
    puzzle input, **what is the correct checksum** for this disk?

        >>> part_2('10000')
        part 2: disk of size 35651584 has checksum '10111110011110111'
        '10111110011110111'
    """

    result = disk_checksum(initial_state, disk_size)
    print(f"part 2: disk of size {disk_size} has checksum {result!r}")
    return result


REV = {'0': '1', '1': '0'}


def dragon(curve: str) -> str:
    return curve + '0' + ''.join(REV[c] for c in reversed(curve))


def dragon_curve(curve: str, length: int) -> str:
    while len(curve) < length:
        curve = dragon(curve)

    return curve[:length]


def checksum(bits: str) -> str:

    def total(length: int) -> int:
        ops = 0
        while length % 2 == 0:
            length //= 2
            ops += length
        return ops

    with tqdm(
        desc="checksumming",
        total=total(len(bits)),
        unit="bits",
        unit_scale=True,
        delay=1.0
    ) as progress:

        while len(bits) % 2 == 0:
            bits = ''.join(
                str(int(bits[k] == bits[k+1]))
                for k in range(0, len(bits), 2)
            )
            progress.update(len(bits))

        return bits


def disk_checksum(seed: str, size: int) -> str:
    # TODO: optimize?
    return checksum(dragon_curve(seed, size))


def state_from_file(fn: str) -> str:
    return open(relative_path(__file__, fn)).readline().strip()


if __name__ == '__main__':
    initial_ = state_from_file('data/16-input.txt')
    part_1(initial_)
    part_2(initial_)
