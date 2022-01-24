from common.utils import some


def spin(count: int, steps: int) -> tuple[int, list[int]]:
    """
    >>> spin(0, 3)
    (0, [0])
    >>> spin(1, 3)
    (1, [0, 1])
    >>> spin(2, 3)
    (1, [0, 2, 1])
    >>> spin(3, 3)
    (2, [0, 2, 3, 1])
    >>> spin(4, 3)
    (2, [0, 2, 4, 3, 1])
    >>> spin(5, 3)
    (1, [0, 5, 2, 4, 3, 1])
    >>> spin(6, 3)
    (5, [0, 5, 2, 4, 3, 6, 1])
    >>> spin(7, 3)
    (2, [0, 5, 7, 2, 4, 3, 6, 1])
    >>> spin(8, 3)
    (6, [0, 5, 7, 2, 4, 3, 8, 6, 1])
    >>> spin(9, 3)
    (1, [0, 9, 5, 7, 2, 4, 3, 8, 6, 1])
    >>> h, b = spin(2017, 3)
    >>> b[h-3:h+4]
    [1512, 1134, 151, 2017, 638, 1513, 851]
    """
    buffer = [0]
    head = 0

    for k in range(1, count + 1):
        head = (head + steps) % len(buffer)
        buffer.insert(head + 1, k)
        head = head + 1
    return head, buffer


def spin1(count: int, steps: int) -> int:
    head = 0
    last_k1: int | None = None

    for k in range(1, count + 1):
        head = ((head + steps) % k) + 1
        if head == 1:
            last_k1 = k

    return some(last_k1)


def part_1(steps: int) -> int:
    hhh, bbb = spin(2017, steps)
    assert bbb[hhh] == 2017
    result = bbb[hhh + 1]
    print(f"part 1: value after 2017 is {result}")
    return result


def part_2(steps: int):
    result = spin1(50_000_000, steps)
    print(f"part 2: value after 0 is {result}")
    return result


if __name__ == '__main__':
    STEPS = 301
    part_1(STEPS)
    part_2(STEPS)
