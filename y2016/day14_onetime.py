from itertools import count
from itertools import islice
from typing import Generator
from typing import Optional

from common.md5 import rmd5
from common.utils import ilog
from common.utils import last


def find_repeating(s: str, length: int) -> Optional[tuple[int, str]]:
    """
    >>> find_repeating('ahoooj', 3)
    (2, 'ooo')
    >>> find_repeating('oooohoooohoohooooo', 5)
    (13, 'ooooo')
    >>> find_repeating('ahooj', 3) is None
    True
    >>> find_repeating('x', 2) is None
    True
    """
    return next((
        (i, s[i:i+length])
        for i in range(len(s) - length + 1)
        if all(s[i] == s[j] for j in range(i+1, i+length))
    ), None)


def generate_keys(salt: str, repeats: int = 1) -> Generator[tuple[int, str], None, None]:
    """
    >>> g = generate_keys('abc')
    >>> next(g)
    (39, '347dac6ee8eeea4652c7476d0f97bee5')
    >>> next(g)
    (92, 'ae2e85dd75d63e916a525df95e999ea0')
    """
    for index in count(0):
        key = rmd5(salt + str(index), repeats)
        triple = find_repeating(key, 3)
        if triple is None:
            continue
        quintuple = triple[1][0]*5
        if any(quintuple in rmd5(salt + str(index+n), repeats) for n in range(1, 1001)):
            yield index, key


def part_1(salt: str) -> int:
    index, _ = last(ilog(islice(generate_keys(salt), 64)))
    print(f"part 1: 64th key is generated at index {index}")
    return index


def part_2(salt: str) -> int:
    index, _ = last(ilog(islice(generate_keys(salt, repeats=2017), 64)))
    print(f"part 2: 64th key is generated at index {index}")
    return index


if __name__ == '__main__':
    salt_ = 'qzyelonm'
    part_1(salt_)
    part_2(salt_)
