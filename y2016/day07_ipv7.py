"""
Advent of Code 2016
Day 7: Internet Protocol Version 7
https://adventofcode.com/2016/day/7
"""

from typing import Iterable

from common.utils import relative_path


def part_1(ips: list[str]) -> int:
    """
    While snooping around the local network of EBHQ, you compile a list of IP addresses
    (they're IPv7, of course; IPv6 is much too limited). You'd like to figure out which IPs support
    **TLS** (transport-layer snooping).

    An IP supports TLS if it has an Autonomous Bridge Bypass Annotation, or **ABBA**. An ABBA is any
    four-character sequence which consists of a pair of two different characters followed by the
    reverse of that pair, such as `xyyx` or `abba`. However, the IP also must not have an ABBA
    within any hypernet sequences, which are contained by **square brackets**.

    For example:

        >>> supports_tls('abba[mnop]qrst')
        True

    (`abba` outside square brackets)

        >>> supports_tls('abcd[bddb]xyyx')
        False

    (`bddb` is within square brackets, even though `xyyx` is outside square brackets)

        >>> supports_tls('aaaa[qwer]tyui')
        False

    (`aaaa` is invalid; the interior characters must be different)

        >>> supports_tls('ioxxoj[asdfgh]zxcvbn')
        True

    (`oxxo` is outside square brackets, even though it's within a larger string)

    **How many IPs** in your puzzle input support TLS?

        >>> example_ips = ips_from_text('''
        ...     abba[mnop]qrst
        ...     abcd[bddb]xyyx
        ...     aaaa[qwer]tyui
        ...     ioxxoj[asdfgh]zxcvbn
        ...     abc[def]ghi[jkl]mnoon
        ...     abc[def]ghi[jkl]mno
        ...     abc[def]ghi[jkllk]mnoon
        ... ''')
        >>> part_1(example_ips)
        part 1: 3 IPs out of 7 support TLS
        3
    """

    result = sum(1 for ip in ips if supports_tls(ip))
    print(f"part 1: {result} IPs out of {len(ips)} support TLS")
    return result


def part_2(ips: list[str]) -> int:
    """
    You would also like to know which IPs support **SSL** (super-secret listening).

    An IP supports SSL if it has an Area-Broadcast Accessor, or **ABA**, anywhere in the supernet
    sequences (outside any square bracketed sections), and a corresponding Byte Allocation Block,
    or **BAB**, anywhere in the hypernet sequences. An ABA is any three-character sequence which
    consists of the same character twice with a different character between them, such as `xyx`
    or `aba`. A corresponding BAB is the same characters but in reversed positions: `yxy` and `bab`,
    respectively.

    For example:

        >>> supports_ssl('aba[bab]xyz')
        True

    (`aba` outside square brackets with corresponding `bab` within square brackets)

        >>> supports_ssl('xyx[xyx]xyx')
        False

    (`xyx`, but no corresponding `yxy`)

        >>> supports_ssl('aaa[kek]eke')
        True

    (`eke` in supernet with corresponding `kek` in hypernet; the `aaa` sequence is not related,
    because the interior character must be different)

        >>> supports_ssl('zazbz[bzb]cdb')
        True

    (`zaz` has no corresponding `aza`, but `zbz` has a corresponding `bzb`, even though `zaz` and
    `zbz` overlap)

    **How many IPs** in your puzzle input support SSL?

        >>> example_ips = ips_from_text('''
        ...     aba[bab]xyz
        ...     xyx[xyx]xyx
        ...     aaa[kek]eke
        ...     zazbz[bzb]cdb
        ... ''')
        >>> part_2(example_ips)
        part 2: 3 IPs out of 4 support SSL
        3
    """

    result = sum(1 for ip in ips if supports_ssl(ip))
    print(f"part 2: {result} IPs out of {len(ips)} support SSL")
    return result


def find_abba(string: str) -> Iterable[str]:
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
    for k in range(len(string) - 3):
        a_1, b_1, b_2, a_2 = string[k:k + 4]
        if a_1 == a_2 and b_1 == b_2 and a_1 != b_1:
            yield string[k:k + 4]


def has_abba(string: str) -> bool:
    return any(find_abba(string))


def find_aba(string: str) -> Iterable[str]:
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
    for k in range(len(string) - 2):
        a_1, b, a_2 = string[k:k + 3]
        if a_1 == a_2 and a_1 != b:
            yield string[k:k + 3]


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
    sequences = split_ipv7(ip)
    supernet = sequences[0::2]
    hypernet = sequences[1::2]
    return (
        any(has_abba(s) for s in supernet)
        and all(not has_abba(s) for s in hypernet)
    )


def supports_ssl(ip: str) -> bool:
    sequences = split_ipv7(ip)
    supernet = sequences[0::2]
    hypernet = sequences[1::2]
    super_abs = set(aba[:2] for s in supernet for aba in find_aba(s))
    hyper_abs = set(bab[1:] for h in hypernet for bab in find_aba(h))
    return bool(super_abs & hyper_abs)


def ips_from_file(fn: str) -> list[str]:
    return [line.strip() for line in open(relative_path(__file__, fn))]


def ips_from_text(text: str) -> list[str]:
    return [line.strip() for line in text.strip().splitlines()]


if __name__ == '__main__':
    ips_ = ips_from_file('data/07-input.txt')
    part_1(ips_)
    part_2(ips_)
