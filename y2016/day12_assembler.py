from y2016.assembunny import load_tape
from y2016.assembunny import Machine
from y2016.assembunny import Tape


def part_1(tape: Tape) -> int:
    m = Machine()
    m.run(tape)
    print(f"part 1: a = {m.a}")
    return m.a


def part_2(tape: Tape) -> int:
    m = Machine(c=1)
    m.run(tape)
    print(f"part 2: a = {m.a}")
    return m.a


if __name__ == '__main__':
    tape_ = load_tape("data/11-program.txt")
    part_1(tape_)
    part_2(tape_)
