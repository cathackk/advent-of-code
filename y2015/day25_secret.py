def code_by_index(index: int) -> int:
    start = 20151125
    q = 252533
    m = 33554393
    return (start * pow(q, index, m)) % m


def code_by_pos(row: int, column: int) -> int:
    index = pos_to_index(row, column)
    return code_by_index(index)


def pos_to_index(row: int, column: int) -> int:
    """
    >>> pos_to_index(0, 0)
    0
    >>> pos_to_index(1, 0)
    1
    >>> pos_to_index(0, 1)
    2
    >>> pos_to_index(0, 3)
    9
    >>> pos_to_index(2, 3)
    18
    >>> pos_to_index(4, 1)
    16
    """
    s = row + column
    offset = (s * (s + 1)) // 2
    return offset + column


def test():
    assert code_by_pos(row=3, column=0) == 24592653
    assert code_by_pos(row=5, column=5) == 27995004
    assert code_by_pos(row=2, column=4) == 11661866
    assert code_by_pos(row=2, column=5) == 16474243


if __name__ == '__main__':
    print("part 1:", code_by_pos(row=2980, column=3074))
