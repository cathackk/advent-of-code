from typing import Iterable
from typing import List


def find_abba(s: str) -> Iterable[str]:
    """
    >>> list(find_abba('abba'))
    ['abba']
    >>> list(find_abba('xoxoxo'))
    []
    >>> list(find_abba('xooxxoox'))
    ['xoox', 'oxxo', 'xoox']
    >>> list(find_abba('fffffff'))
    []
    >>> list(find_abba('aba'))
    []
    >>> list(find_abba(''))
    []
    >>> list(find_abba('xobohobooboxob'))
    ['boob']
    """
    for k in range(len(s) - 3):
        a1, b1, b2, a2 = s[k:k+4]
        if a1 == a2 and b1 == b2 and a1 != b1:
            yield s[k:k+4]


def has_abba(s: str) -> bool:
    """
    >>> has_abba('xabbaxxa')
    True
    >>> has_abba('xabax')
    False
    """
    return any(find_abba(s))


def find_aba(s: str) -> Iterable[str]:
    """
    >>> list(find_aba('xabax'))
    ['aba']
    >>> list(find_aba('xoxoxo'))
    ['xox', 'oxo', 'xox', 'oxo']
    >>> list(find_aba('xxxxo'))
    []
    >>> list(find_aba('hello'))
    []
    >>> list(find_aba('1'))
    []
    """
    for k in range(len(s)-2):
        a1, b, a2 = s[k:k+3]
        if a1 == a2 and a1 != b:
            yield s[k:k+3]


def split_ipv7(ip: str) -> tuple[str, ...]:
    """
    >>> split_ipv7('abc[def]ghi')
    ('abc', 'def', 'ghi')
    >>> split_ipv7('abc[def]ghi[jkl]mno[pqrstu]v[w]x[y]z')
    ('abc', 'def', 'ghi', 'jkl', 'mno', 'pqrstu', 'v', 'w', 'x', 'y', 'z')
    >>> split_ipv7('agog')
    ('agog',)
    """
    return tuple(ip.replace('[', '.').replace(']', '.').split('.'))


def supports_tls(ip: str) -> bool:
    """
    >>> supports_tls('abba[mnop]qrst')
    True
    >>> supports_tls('abcd[bddb]xyyx')
    False
    >>> supports_tls('aaaa[qwer]tyui')
    False
    >>> supports_tls('ioxxoj[asdfgh]zxcvbn')
    True
    >>> supports_tls('abc[def]ghi[jkl]mnoon')
    True
    >>> supports_tls('abc[def]ghi[jkl]mno')
    False
    >>> supports_tls('abc[def]ghi[jkllk]mnoon')
    False
    """
    sequences = split_ipv7(ip)
    supernet = sequences[0::2]
    hypernet = sequences[1::2]
    return (
        any(has_abba(s) for s in supernet)
        and all(not has_abba(s) for s in hypernet)
    )


def supports_ssl(ip: str) -> bool:
    """
    >>> supports_ssl('aba[bab]xyz')
    True
    >>> supports_ssl('xyx[xyx]xyx')
    False
    >>> supports_ssl('aaa[kek]eke')
    True
    >>> supports_ssl('zazbz[bzb]cdb')
    True
    """
    sequences = split_ipv7(ip)
    supernet = sequences[0::2]
    hypernet = sequences[1::2]
    super_abs = set(aba[:2] for s in supernet for aba in find_aba(s))
    hyper_abs = set(bab[1:] for h in hypernet for bab in find_aba(h))
    return bool(super_abs & hyper_abs)


def load_ips(fn: str) -> List[str]:
    return [line.strip() for line in open(fn)]


def part_1(ips: List[str]) -> int:
    count = sum(1 for ip in ips if supports_tls(ip))
    print(f"part 1: {count} IPs support TLS")
    return count


def part_2(ips: List[str]) -> int:
    count = sum(1 for ip in ips if supports_ssl(ip))
    print(f"part 2: {count} IPs support SSL")
    return count


if __name__ == '__main__':
    ips_ = load_ips("data/07-input.txt")
    part_1(ips_)
    part_2(ips_)
