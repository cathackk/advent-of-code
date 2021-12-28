from common.utils import slidingw


def captcha(digits: str) -> int:
    """
    >>> captcha('1122')
    3
    >>> captcha('1111')
    4
    >>> captcha('1234')
    0
    >>> captcha('91212129')
    9
    """
    return sum(
        int(a)
        for a, b in slidingw(digits, 2, wrap=True)
        if a == b
    )


def captcha2(digits: str) -> int:
    """
    >>> captcha2('1212')
    6
    >>> captcha2('1221')
    0
    >>> captcha2('123425')
    4
    >>> captcha2('123123')
    12
    >>> captcha2('12131415')
    4
    """
    d = len(digits)
    return sum(
        int(digits[k])
        for k in range(d)
        if digits[k] == digits[(k+d//2)%d]
    )


def part_1(s: str) -> int:
    result = captcha(s)
    print(f"part 1: {result}")
    return result


def part_2(s: str) -> int:
    result = captcha2(s)
    print(f"part 2: {result}")
    return result


if __name__ == '__main__':
    s = open("data/01-input.txt").readline().strip()
    part_1(s)
    part_2(s)
