from itertools import count
from typing import Any
from typing import Generator

from y2016.assembunny import load_tape
from y2016.assembunny import Machine
from y2016.assembunny import Tape


def clock_length(signal: Generator[int, Any, Any], test_length: int = 1000) -> int:
    expected = 0
    for tick in range(test_length):
        if next(signal) != expected:
            return tick
        expected = 1 if expected == 0 else 0
    else:
        return test_length


def part_1(tape: Tape):
    tl = 100
    for a in count(1):
        g = Machine(a=a).run_gen(tape)
        length = clock_length(g, test_length=tl)
        if length == tl:
            print(f"part 1: a={a}")
            return length
        else:
            print(f"{a:3} -> {length:2}")


if __name__ == '__main__':
    tape_ = load_tape("data/25-program.txt")
    part_1(tape_)
