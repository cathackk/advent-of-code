"""
Advent of Code 2024
Day X: title
https://adventofcode.com/2024/day/X
"""

from typing import Iterable

from common.file import relative_path


def part_1() -> int:
    """
    Instructions for part 1.
    """

    result = 1

    print(f"part 1: {result}")
    return result


def part_2() -> int:
    """
    Instructions for part 2.
    """

    result = 2

    print(f"part 2: {result}")
    return result


def input_from_file(fn: str) -> list[int]:
    return list(input_from_lines(open(relative_path(__file__, fn))))


def input_from_text(text: str) -> list[int]:
    return list(input_from_lines(text.strip().splitlines()))


def input_from_lines(lines: Iterable[str]) -> Iterable[int]:
    return (len(line.strip()) for line in lines)


def main(input_fn: str = 'data/XX-input.txt') -> tuple[int, int]:
    _ = input_from_file(input_fn)
    result_1 = part_1()
    result_2 = part_2()
    return result_1, result_2


if __name__ == '__main__':
    main()
