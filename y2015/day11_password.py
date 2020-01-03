import string
from typing import Iterable

VALID_CHARS = set(string.ascii_lowercase)

def pairs(s: str) -> Iterable[str]:
    """
    >>> list(pairs("abcddabbc"))
    ['dd', 'bb']
    >>> list(pairs("aaaaabbbaa"))
    ['aa', 'aa', 'bb', 'aa']
    """
    last_pair_k = None
    for k in range(len(s)-1):
        if s[k] == s[k+1]:
            if last_pair_k is None or last_pair_k < k-1:
                yield s[k:k+2]
                last_pair_k = k


def is_valid(pwd: str) -> bool:
    """
    >>> is_valid('hijklmmn')
    False
    >>> is_valid('abbceffg')
    False
    >>> is_valid('abbcegjk')
    False
    >>> is_valid('abcdffaa')
    True
    >>> is_valid('ghjaabcc')
    True
    """
    assert len(pwd) == 8
    assert all(c in VALID_CHARS for c in pwd)

    def c(k):
        return ord(pwd[k])

    return (
        any(c(k)+2 == c(k+1)+1 == c(k+2) for k in range(len(pwd) - 2))
        and not any(c in 'iol' for c in pwd)
        and len(set(pairs(pwd))) >= 2
    )


def nexts(s: str) -> str:
    """
    >>> nexts('abc')
    'abd'
    >>> nexts('xxxx')
    'xxxy'
    >>> nexts('xyz')
    'xza'
    >>> nexts('z')
    'a'
    """
    if not s:
        return s
    elif s[-1] == 'z':
        return nexts(s[:-1]) + 'a'
    else:
        return s[:-1] + chr(ord(s[-1])+1)


def valid_passwords(start: str) -> Iterable[str]:
    pwd = start
    while True:
        pwd = nexts(pwd)
        if is_valid(pwd):
            yield pwd


def next_valid(pwd: str) -> str:
    """
    >>> next_valid('abcdefgh')
    'abcdffaa'
    >>> next_valid('ghijklmn')
    'ghjaabcc'
    """
    return next(valid_passwords(pwd))


if __name__ == '__main__':
    last_password = 'vzbxkghb'
    next_password = next_valid(last_password)
    print(f"part 1: next password after {last_password!r} is {next_password!r}")

    next_password_2 = next_valid(next_password)
    print(f"part 2: next password after {next_password!r} is {next_password_2!r}")
