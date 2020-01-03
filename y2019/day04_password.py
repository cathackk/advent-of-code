from collections import Counter


def is_valid1(n):
    sn = str(n)
    return (
        111_111 <= n <= 999_999
        and all(c1 <= c2 for c1, c2 in zip(sn, sn[1:]))
        and len(set(sn)) < len(sn)
    )


def is_valid2(n):
    return (
        is_valid1(n)
        and Counter(Counter(str(n)).values())[2] >= 1
    )


if __name__ == '__main__':
    r = range(146_810, 612_564 + 1)
    count1 = sum(1 for n in r if is_valid1(n))
    print(f"count 1: {count1}")
    count2 = sum(1 for n in r if is_valid2(n))
    print(f"count 2: {count2}")
