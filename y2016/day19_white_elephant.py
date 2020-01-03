def elimination_naive(count: int) -> int:
    """
    >>> elimination_naive(5)
    3
    >>> elimination_naive(7)
    7
    >>> elimination_naive(12)
    9
    >>> [elimination_naive(n) for n in range(1, 21)]
    [1, 1, 3, 1, 3, 5, 7, 1, 3, 5, 7, 9, 11, 13, 15, 1, 3, 5, 7, 9]
    """
    assert count > 0
    nums = list(range(1, count+1))
    while len(nums) > 1:
        if len(nums) % 2 == 0:
            nums = nums[::2]
        else:
            nums = nums[-1:] + nums[:-1:2]
    return nums[0]


def elimination_fast(count: int) -> int:
    """
    >>> elimination_fast(5)
    3
    >>> elimination_fast(7)
    7
    >>> elimination_fast(12)
    9
    >>> [elimination_fast(n) for n in range(1, 21)]
    [1, 1, 3, 1, 3, 5, 7, 1, 3, 5, 7, 9, 11, 13, 15, 1, 3, 5, 7, 9]
    """
    assert count > 0
    # take binary form and move first digit to the end
    # 18 = '0b10010' -> '0b00101' = 5
    return int(bin(count)[3:]+'1', 2)


def across_elimination_naive(count: int, debug: bool = False) -> int:
    """
    >>> [across_elimination_naive(n) for n in range(1, 21)]
    [1, 1, 3, 1, 2, 3, 5, 7, 9, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 13]
    >>> across_elimination_naive(1000)
    271
    >>> across_elimination_naive(1237)
    508
    """
    assert count > 0
    nums = list(range(1, count+1))

    active_index = 0
    while len(nums) > 1:
        if debug and len(nums) % 1000 == 0:
            progress = 1 - len(nums)/count
            print(f"{len(nums)//1000}k ({progress:.2%}) ai={active_index}")
        across_index = (active_index + len(nums)//2) % len(nums)
        nums.pop(across_index)
        if active_index < across_index:
            active_index += 1
        if active_index >= len(nums):
            active_index -= len(nums)

    return nums[0]


def terc(n) -> str:
    assert n >= 0
    if n == 0:
        return '0'
    digits = []
    while n > 0:
        digits.append(str(n % 3))
        n //= 3
    return ''.join(reversed(digits))


def across_elimination_fast(count: int) -> int:
    """
    >>> [across_elimination_fast(n) for n in range(1, 21)]
    [1, 1, 3, 1, 2, 3, 5, 7, 9, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 13]
    >>> across_elimination_fast(1000)
    271
    >>> across_elimination_fast(1237)
    508
    """
    assert count > 0

    # take tertiary form of n:
    #
    # (1) if it consists of a digit followed by z zeroes,
    #     return 1 followed by z zeroes (aka magnitude)
    #       • 27 = 0t1000 -> 0t1000 = 27;
    #       • 54 = 0t2000 -> 0t1000 = 27
    #
    # (2) if first digit is 1 (n < 2 * magnitude),
    #     return the rest of digits (n - magnitude)
    #       • 48 = 0t1210 -> 0t210 = 21
    #       • 111 = 0t11010 ->0t1010 = 30
    #
    # (3) if first digit is 2 (n > 2 * magnitude),
    #     return twice the rest of digits plus magnitude (2*n - 3*magnitude)
    #       • 19 = 0t201 -> 0t100 + 2 * 0t01 = 0t102 = 11
    #       • 176 = 0t20112 -> 0t10000 + 2 * 0t112 = 0t11001 = 109
    t = terc(count)
    mag = int('1' + '0'*(len(t)-1), 3)
    if count == mag:
        return mag
    elif count <= 2 * mag:
        return count - mag
    else:
        return 2 * count - 3 * mag


def part_1(count: int) -> int:
    winner = elimination_fast(count)
    print(f"part 1: winner is elf number {winner}")
    return winner


def part_2(count: int) -> int:
    winner = across_elimination_fast(count)
    print(f"part 2: winner is elf number {winner}")
    return winner


if __name__ == '__main__':
    count_ = 3005290
    part_1(count_)
    part_2(count_)
