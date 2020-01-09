from typing import Iterable


def load_data(fn: str) -> Iterable[int]:
    return (int(line) for line in open(fn))


def fuel1(mass):
    return mass // 3 - 2


def fuel2(mass):
    r = fuel1(mass)
    return r + fuel2(r) if r > 0 else 0


if __name__ == '__main__':
    data_ = list(load_data("data/01-input.txt"))
    result_1 = sum(fuel1(mass) for mass in data_)
    print(f"part 1: {result_1} fuel needed")
    result_2 = sum(fuel2(mass) for mass in data_)
    print(f"part 2: {result_2} fuel needed")
