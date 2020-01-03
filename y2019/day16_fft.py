import random
import time
from typing import Iterable
from typing import List


def fft(number: str, phases: int = 100) -> str:
    ns = [int(d) for d in list(number)]
    for phase in range(phases):
        # print(f">> phase={phase}")
        ns = [fft_digit(index, ns) for index in range(len(ns))]
    return ''.join(str(n) for n in ns)


def fft_digit(p: int, ns: List[int]):
    """
                   1111111111222
         01234567890123456789012
    0 -> +0-0+0-0+0-0+0-0+0-0+0-
    1 -> 0++00--00++00--00++00--
    2 -> 00+++000---000+++000---
    3 -> 000++++0000----0000++++
    4 -> 0000+++++00000-----0000
    5 -> 00000++++++000000------
    6 -> 000000+++++++0000000---
    7 -> 0000000++++++++00000000
    """
    return abs(
        sum(ns[i] for i in plus_indexes(p, len(ns)))
        - sum(ns[i] for i in minus_indexes(p, len(ns)))
    ) % 10


def plus_indexes(p: int, l: int) -> Iterable[int]:
    """
    0 -> 0, 4, 8, 12, ...
    1 -> 1,2, 9,10, 17,18, ...
    2 -> 2,3,4, 14,15,16, 26,27,28, ...
    """
    return (
        r
        for s in range(p, l, 4 * (p + 1))
        for r in range(s, min(s + p + 1, l))
    )


def minus_indexes(p: int, l: int) -> Iterable[int]:
    """
    0 -> 2, 6, 10, 14, ...
    1 -> 5,6, 13,14, 21,22, ...
    2 -> 8,9,10, 20,21,22, 32,33,34, ...
    """
    return (
        r
        for s in range(3 * p + 2, l, 4 * (p + 1))
        for r in range(s, min(s + p + 1, l))
    )


def fft_offset(number: str, repeats: int = 10_000, phases: int = 100, message_length: int = 8) -> str:

    def ns_to_str(ns, l=message_length):
        return ''.join(str(d) for d in ns[:l])

    offset = int(number[:7])
    assert offset > len(number) // 2
    ns = [int(d) for _ in range(repeats) for d in number][offset:]
    print(f"ns={ns_to_str(ns, 20)}")


    for phase in range(100):
        psum = sum(ns)
        for j in range(len(ns)):
            psum, ns[j] = psum - ns[j], abs(psum) % 10
        print(f"{phase+1:3}: {ns_to_str(ns, 20)}...")

    return ns_to_str(ns)


def test_fft():
    assert fft('12345678', 1) == '48226158'
    assert fft('12345678', 2) == '34040438'
    assert fft('12345678', 3) == '03415518'
    assert fft('12345678', 4) == '01029498'

    assert fft('80871224585914546619083218645595')[:8] == '24176176'
    assert fft('19617804207202209144916044189917')[:8] == '73745418'
    assert fft('69317163492948606335995924319873')[:8] == '52432133'


def test_fft_offset():
    assert fft_offset('03036732577212944063491565474664') == '84462026'
    assert fft_offset('02935109699940807407585447034323') == '78725270'
    assert fft_offset('03081770884921959731165446850517') == '53553731'


def part_1():
    n = list(open("data/16-input.txt"))[0].strip()
    result = fft(n, 100)[:8]
    print("part 1")
    print(f"input={n[:8]}...{n[-8:]}")
    print(f"after 100 phases of fft the first 8 digits are: {result[:8]}...")


def part_2():
    number = list(open("data/16-input.txt"))[0].strip()
    print("part 2")
    print(fft_offset(number))


if __name__ == '__main__':
    part_1()
    part_2()


def benchmark():
    for l2 in range(1, 16):
        length = 2 ** l2
        n = ''.join(random.choice('0123456789') for _ in range(length))
        start = time.perf_counter()
        result1 = fft(n, 1)
        end = time.perf_counter()
        print(f"1 phase of fft with input of length {length} took {end-start} seconds")

    for l2 in range(1, 16):
        length = 2 ** l2
        n = ''.join(random.choice('0123456789') for _ in range(length))
        start = time.perf_counter()
        result100 = fft(n, 100)
        end = time.perf_counter()
        print(f"100 phases of fft with input of length {length} took {end - start} seconds")
