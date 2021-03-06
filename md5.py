import hashlib
from functools import lru_cache


def md5(v: str) -> str:
    """
    >>> md5('abc0')
    '577571be4de9dcce85a041ba0410f29f'
    """
    return hashlib.md5(v.encode()).hexdigest()


@lru_cache(maxsize=1200)
def rmd5(v: str, repeats: int) -> str:
    """
    >>> rmd5('abc0', 0)
    'abc0'
    >>> rmd5('abc0', 1)
    '577571be4de9dcce85a041ba0410f29f'
    >>> rmd5('abc0', 2)
    'eec80a0c92dc8a0777c619d9bb51e910'
    >>> rmd5('abc0', 3)
    '16062ce768787384c81fe17a7a60c7e3'
    >>> rmd5('abc0', 2017)
    'a107ff634856bb300138cac6568c0f24'
    """
    for r in range(repeats):
        v = md5(v)
    return v
