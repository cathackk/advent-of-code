from typing import Iterable


def load_data(fn: str) -> Iterable[int]:
    return (int(line) for line in open(fn))


def part_1(fqs: list[int]) -> int:
    result = sum(fqs)
    print(f"part 1: {result} total")
    return result


def part_2(fqs: list[int]) -> int:
    total = 0
    seen = {total}
    while True:
        for fq in fqs:
            total += fq
            if total in seen:
                print(f"part 2: {total} is the first frequence reached twice")
                return total
            seen.add(total)


if __name__ == '__main__':
    fqs_ = list(load_data("data/01-input.txt"))
    part_1(fqs_)
    part_2(fqs_)
