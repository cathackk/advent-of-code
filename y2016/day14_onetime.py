"""
Advent of Code 2016
Day 14: One-Time Pad
https://adventofcode.com/2016/day/14
"""

from functools import lru_cache
from itertools import count
from itertools import islice
from typing import Callable
from typing import Iterable

from tqdm import tqdm

from common.md5 import md5 as plain_md5
from common.utils import last
from common.utils import relative_path


def part_1(salt: str, nth: int = 64) -> int:
    """
    In order to communicate securely with Santa while you're on this mission, you've been using
    a one-time pad that you generate using a pre-agreed algorithm. Unfortunately, you've run out of
    keys in your one-time pad, and so you need to generate some more.

    To generate keys, you first get a stream of random data by taking the MD5 of a pre-arranged salt
    (your puzzle input) and an increasing integer index (starting with `0`, and represented in
    decimal); the resulting MD5 hash should be represented as a string of **lowercase** hexadecimal
    digits.

    However, not all of these MD5 hashes are **keys**, and you need `64` new keys for your one-time
    pad. A hash is a key **only if**:

      - It contains **three** of the same character in a row, like `777`. Only consider the first
        such triplet in a hash.
      - One of the next `1000` hashes in the stream contains that same character **five** times in
        a row, like `77777`.

    Considering future hashes for five-of-a-kind sequences does not cause those hashes to be
    skipped; instead, regardless of whether the current hash is a key, always resume testing for
    keys starting with the very next hash.

    For example, if the pre-arranged salt is `abc`:

      - The first index which produces a triple is `18`:

        >>> md5('abc', 18)  # doctest: +ELLIPSIS
        '...888...'

        However, index `18` does not count as a key for your one-time pad, because none of the next
        thousand hashes (index `19` through index `1018`) contain `88888`:

        >>> any('88888' in md5('abc', ix) for ix in range(19, 1019))
        False

      - The next index which produces a triple is `39`:

        >>> md5('abc', 39)  # doctest: +ELLIPSIS
        '...eee...'

        It is also the first key: one of the next thousand hashes contains `eeeee`:

        >>> md5('abc', 816)  # doctest: +ELLIPSIS
        '...eeeee...'
        >>> next_key('abc')  # doctest: +ELLIPSIS
        (39, '...eee...', 816, '...eeeee...')

      - None of the next six triples are keys, but the one after that, at index `92`, is:

        >>> next_key('abc', start=40)  # doctest: +ELLIPSIS
        (92, '...999...', 200, '...99999...')

      - Eventually, index `22728` meets all of the criteria to generate the 64th key:

        >>> next_key('abc', start=22728)  # doctest: +ELLIPSIS
        (22728, '...ccc...', 22804, '...ccccc...')

    So, using our example salt of `abc`, index `22728` produces the `64`th key.

    Given the actual salt in your puzzle input, **what index** produces your `64`th one-time pad
    key?

        >>> part_1('abc')
        part 1: 64th key is generated at index 22728
        22728
    """
    result, _ = generate_nth_key(salt, md5, nth)
    print(f"part 1: {nth}th key is generated at index {result}")
    return result


def part_2(salt: str, nth: int = 64) -> int:
    """
    Of course, in order to make this process even more secure, you've also implemented key
    stretching.

    Key stretching forces attackers to spend more time generating hashes. Unfortunately, it forces
    everyone else to spend more time, too.

    To implement key stretching, whenever you generate a hash, before you use it, you first find the
    MD5 hash of that hash, then the MD5 hash of that hash, and so on, a total of **`2016` additional
    hashings**. Always use lowercase hexadecimal representations of hashes.

    For example, to find the stretched hash for index `0` and salt `abc`:

      - Find the MD5 hash of `abc0`:

        >>> md5('abc', 0)
        '577571be4de9dcce85a041ba0410f29f'

      - Then, find the MD5 hash of that hash:

        >>> plain_md5(_)
        'eec80a0c92dc8a0777c619d9bb51e910'

      - Then, find the MD5 hash of that hash:

        >>> plain_md5(_)
        '16062ce768787384c81fe17a7a60c7e3'

      - ... repeat many times ...
      - Then, find the MD5 hash of that hash:

        >>> md5x2017('abc', 0)
        'a107ff634856bb300138cac6568c0f24'

    So, the stretched hash for index `0` in this situation is `a107ff...`. In the end, you find
    the original hash (one use of MD5), then find the hash-of-the-previous-hash `2016` times, for
    a total of `2017` uses of MD5.

    The rest of the process remains the same, but now the keys are entirely different. Again for
    salt `abc`:

      - The first triple (`222`, at index `5`) has no matching `22222` in the next thousand hashes:

        >>> md5x2017('abc', 5)  # doctest: +ELLIPSIS
        '...222...'
        >>> any('22222' in md5x2017('abc', ix) for ix in range(6, 1006))
        False

      - The second triple (`eee`, at index `10`) has a matching `eeeee` at index `89`, and so it is
        the first key:

        >>> next_key('abc', md5x2017)  # doctest: +ELLIPSIS
        (10, '...eee...', 89, '...eeeee...')

      - Eventually, index `22551` produces the 64th key:

        >>> next_key('abc', md5x2017, start=22551)  # doctest: +ELLIPSIS
        (22551, '...fff', 22859, '...fffff...')

    Given the actual salt in your puzzle input and using `2016` extra MD5 calls of key stretching,
    **what index** now produces your `64`th one-time pad key?

        >>> part_2('abc')
        part 2: 64th key is generated at index 22551
        22551
    """

    result, _ = generate_nth_key(salt, md5x2017, nth)
    print(f"part 2: {nth}th key is generated at index {result}")
    return result


def find_repeating(string: str, length: int) -> tuple[int, str] | None:
    """
        >>> find_repeating('xxxyyy', 3)
        (0, 'xxx')
        >>> find_repeating('ahoooj', 3)
        (2, 'ooo')
        >>> find_repeating('oooohoooohoohooooo', 5)
        (13, 'ooooo')
        >>> find_repeating('ahooj', 3) is None
        True
        >>> find_repeating('x', 2) is None
        True
    """
    if not string:
        return None

    group_pos, group_char = -1, ''

    for pos, char in enumerate(string):
        if char == group_char:
            if pos - group_pos + 1 >= length:
                return group_pos, string[group_pos:pos + 1]
        else:
            group_pos, group_char = pos, char

    else:
        return None


@lru_cache(maxsize=2048)
def md5(salt: str, index: int) -> str:
    return plain_md5(salt + str(index))


@lru_cache(maxsize=2048)
def md5x2017(salt: str, index: int) -> str:
    val = salt + str(index)
    for _ in range(2017):
        val = plain_md5(val)
    return val


Hasher = Callable[[str, int], str]


# pylint: disable=inconsistent-return-statements
def next_key(salt: str, hasher: Hasher = md5, start: int = 0) -> tuple[int, str, int, str]:
    for index in count(start):
        digest = hasher(salt, index)

        triple = find_repeating(digest, 3)
        if triple is None:
            continue

        expected_substring = triple[1][0] * 5
        matching_quintuples = (
            (qix, qdig)
            for n in range(1, 1001)
            if expected_substring in (qdig := hasher(salt, qix := index + n))
        )
        quintuple = next(matching_quintuples, None)
        if quintuple:
            return (index, digest) + quintuple


def generate_keys(salt: str, hasher: Hasher) -> Iterable[tuple[int, str]]:
    index = -1
    while True:
        index, key, _, _ = next_key(salt, hasher, index + 1)
        yield index, key


def generate_nth_key(salt: str, hasher: Hasher, nth: int) -> tuple[int, str]:
    keys = islice(generate_keys(salt, hasher), nth)
    desc = f"generating keys with {hasher.__name__}"
    return last(tqdm(keys, desc=desc, total=nth, unit=" keys", delay=1.0))


def salt_from_file(fn: str) -> str:
    return open(relative_path(__file__, fn)).readline().strip()


if __name__ == '__main__':
    salt_ = salt_from_file('data/14-input.txt')
    part_1(salt_)
    part_2(salt_)
