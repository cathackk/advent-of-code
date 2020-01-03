from y2016.assembunny import load_tape
from y2016.assembunny import Machine
from y2016.assembunny import Tape


def test_toggle():
    tape = load_tape("data/23-example.txt")
    m = Machine().run(tape, debug=True)
    assert m.a == 3


def part_1(tape: Tape):
    m = Machine(a=7).run(tape)
    print(f"part 1: result is {m.a}")
    return m.a


def part_2(tape: Tape):
    m = Machine(a=12).run(tape)
    print(f"part 2: result is {m.a}")
    return m.a
    # 6606 too low


if __name__ == '__main__':
    tape_ = load_tape("data/23-program3.txt")
    part_1(tape_)
    part_2(tape_)
