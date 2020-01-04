from typing import Generator


Gen = Generator[int, None, None]
FACTOR_A = 16807
FACTOR_B = 48271
DIV_A = 4
DIV_B = 8


def gen(init_value: int, factor: int, divisible: int = None) -> Gen:
    """
    >>> a = gen(65, FACTOR_A)
    >>> next(a)
    1092455
    >>> next(a)
    1181022009
    >>> next(a)
    245556042

    >>> b = gen(8921, FACTOR_B)
    >>> next(b)
    430625591
    >>> next(b)
    1233683848
    >>> next(b)
    1431495498

    >>> ad = gen(65, FACTOR_A, DIV_A)
    >>> next(ad)
    1352636452
    >>> next(ad)
    1992081072
    >>> next(ad)
    530830436

    >>> bd = gen(8921, FACTOR_B, DIV_B)
    >>> next(bd)
    1233683848
    >>> next(bd)
    862516352
    >>> next(bd)
    1159784568
    """
    value = init_value
    while True:
        value = (value * factor) % 0x7fffffff
        if not divisible or value % divisible == 0:
            yield value


def count_matches(ga: Gen, gb: Gen, tests_count: int) -> int:
    matches = 0
    for test in range(tests_count):
        if test % 1_000_000 == 0:
            print(f"... {test//1_000_000}M / {tests_count//1_000_000}M -> {matches} matches")
        a, b = next(ga), next(gb)
        if a & 0xffff == b & 0xffff:
            matches += 1
    return matches


def test_count_matches():
    assert count_matches(
        gen(65, FACTOR_A),
        gen(8921, FACTOR_B),
        tests_count=40_000_000
    ) == 588


def test_count_matches_with_divisibility():
    assert count_matches(
        gen(65, FACTOR_A, DIV_A),
        gen(8921, FACTOR_B, DIV_B),
        tests_count=5_000_000
    ) == 309


def part_1(a: int, b: int) -> int:
    matches = count_matches(
        gen(a, FACTOR_A),
        gen(b, FACTOR_B),
        tests_count=40_000_000
    )
    print(f"part 1: {matches} matches")
    return matches


def part_2(a: int, b: int) -> int:
    matches = count_matches(
        gen(a, FACTOR_A, DIV_A),
        gen(b, FACTOR_B, DIV_B),
        tests_count=5_000_000
    )
    print(f"part 2: {matches} matches using divisibility")
    return matches


if __name__ == '__main__':
    a_, b_ = 873, 583
    part_1(a_, b_)
    part_2(a_, b_)
