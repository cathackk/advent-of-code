REV = {'0': '1', '1': '0'}


def dragon(s: str, target_length: int):
    """
    >>> dragon('0', 3)
    '001'
    >>> dragon('1', 3)
    '100'
    >>> dragon('10', 3)
    '10010'
    >>> dragon('10', 6)
    '10010010110'
    >>> dragon('111', 4)
    '1110000'
    >>> dragon('111', 14)
    '111000001111000'
    """
    while len(s) < target_length:
        s = s + '0' + ''.join(REV[c] for c in s[::-1])
    return s


def checksum(s: str) -> str:
    """
    >>> checksum('00011011')
    '1'
    >>> checksum('110010110100')
    '100'
    """
    while len(s) % 2 == 0:
        s = ''.join('1' if s[k] == s[k+1] else '0' for k in range(0, len(s), 2))
    return s


def dragon_checksum(start: str, length: int) -> str:
    """
    >>> dragon_checksum('10000', 20)
    '01100'
    """
    return checksum(dragon(start, length)[:length])


if __name__ == '__main__':
    s_ = '11100010111110100'
    chks_1 = dragon_checksum(s_, 272)
    print(f"part 1: checksum is {chks_1}")
    chks_2 = dragon_checksum(s_, 35651584)
    print(f"part 2: checksum is {chks_2}")
