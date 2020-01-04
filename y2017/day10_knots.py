import operator
from functools import reduce
from typing import Iterable
from typing import List


def pinched(rope_length: int, lengths: Iterable[int], rounds: int = 1) -> List[int]:
    """
    >>> pinched(5, [3])
    [2, 1, 0, 3, 4]
    >>> pinched(5, [3, 4])
    [4, 3, 0, 1, 2]
    >>> pinched(5, [3, 4, 1])
    [4, 3, 0, 1, 2]
    >>> pinched(5, [3, 4, 1, 5])
    [3, 4, 2, 1, 0]
    >>> pinched(5, [3, 4, 1, 5, 0])
    [3, 4, 2, 1, 0]
    """
    rope = list(range(rope_length))
    head = 0
    skip_size = 0

    lengths = list(lengths)

    for _ in range(rounds):
        for length in lengths:
            assert 0 <= length <= rope_length
            if length > 0:
                rope[:length] = rope[length-1::-1]
            shift = (length + skip_size) % rope_length
            rope = rope[shift:] + rope[:shift]
            head = (head + shift) % rope_length
            skip_size += 1

    return list(rope[-head:] + rope[:-head])


def xor(ns: Iterable[int]) -> int:
    """
    >>> xor([1, 2])
    3
    >>> xor([65, 27, 9, 1, 4, 3, 40, 50, 91, 7, 6, 0, 2, 5, 68, 22])
    64
    """
    return reduce(operator.xor, ns, 0)


def knot_hash(bs: bytes) -> bytes:
    """
    >>> knot_hash(b'').hex()
    'a2582a3a0e66e6e86e3812dcb672a272'
    >>> knot_hash(b'AoC 2017').hex()
    '33efeb34ea91902bb2f59c9920caa6cd'
    >>> knot_hash(b'1,2,3').hex()
    '3efbe78a8d82f29979031a4aa0b16a9d'
    >>> knot_hash(b'1,2,4').hex()
    '63960835bcdc130f0b66d7ff4f6a5a8e'
    """
    sparse = pinched(256, list(bs) + [17, 31, 73, 47, 23], 64)
    assert len(sparse) == 256
    dense = [xor(sparse[k:k+16]) for k in range(0, 256, 16)]
    assert len(dense) == 16
    return bytes(dense)


def part_1(fn: str) -> int:
    lengths = [int(v) for v in open(fn).readline().split(',')]
    a, b = pinched(256, lengths)[:2]
    print(f"part 1: {a} * {b} = {a * b}")
    return a * b


def part_2(fn: str) -> str:
    line = open(fn).readline().strip().encode()
    hashed = knot_hash(line).hex()
    print(f"part 2: knot hash is {hashed!r}")
    return hashed


if __name__ == '__main__':
    fn_ = "data/10-input.txt"
    part_1(fn_)
    part_2(fn_)
