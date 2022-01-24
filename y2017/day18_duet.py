from collections import defaultdict
from typing import Generator
from typing import Iterable
from typing import Optional

StrInt = str | int
Command = tuple[str, StrInt, StrInt | None]
Tape = list[Command]


def load_tape(fn: str) -> list[Command]:
    def parse(string: str) -> StrInt:
        return string if string.isalpha() else int(string)

    def commands() -> Iterable[Command]:
        with open(fn) as file:
            for line in file:
                instr, *args = line.strip().split(' ')
                if len(args) == 1:
                    yield instr, parse(args[0]), None
                elif len(args) == 2:
                    yield instr, parse(args[0]), parse(args[1])

    return list(commands())


def run_program(program_id: int, tape: Tape) -> Generator[Optional[int], Optional[int], None]:
    regs = defaultdict(int)
    regs['p'] = program_id

    head = 0

    def val(value) -> int:
        return value if isinstance(value, int) else regs[value]

    while True:
        instr, arg1, arg2 = tape[head]
        head += 1

        if instr == 'snd':
            assert arg2 is None
            yield val(arg1)

        elif instr == 'rcv':
            assert isinstance(arg1, str)
            assert arg2 is None
            received = yield None
            assert received is not None
            regs[arg1] = received

        elif instr == 'set':
            assert isinstance(arg1, str)
            regs[arg1] = val(arg2)

        elif instr == 'add':
            assert isinstance(arg1, str)
            regs[arg1] += val(arg2)

        elif instr == 'mul':
            assert isinstance(arg1, str)
            regs[arg1] *= val(arg2)

        elif instr == 'mod':
            assert isinstance(arg1, str)
            regs[arg1] %= val(arg2)

        elif instr == 'jgz':
            if val(arg1) > 0:
                jump = val(arg2)
                assert jump != 0  # endless loop
                assert jump != 1  # no effect
                head += jump - 1

        else:
            raise KeyError(instr)


def run_single_program(tape: Tape) -> Optional[int]:
    program = run_program(0, tape)
    last_sig = None
    while True:
        sig = next(program)
        if sig is not None:
            last_sig = sig
        else:
            return last_sig


def run_dual_program(tape: Tape) -> tuple[int, int]:
    program_0 = run_program(0, tape)
    program_1 = run_program(1, tape)

    sig0, sig1 = next(program_0), next(program_1)
    queue0 = []
    send_cnt0, send_cnt1 = 0, 0

    while True:
        if sig0 is not None:
            # p0 out -> buffer in queue0
            queue0.append(sig0)
            sig0 = next(program_0)

        elif sig1 is not None:
            # send p1 -> p0 directly
            sig0 = program_0.send(sig1)
            sig1 = next(program_1)
            send_cnt1 += 1

        elif len(queue0) > 0:
            # send p0 -> p1 via queue0
            val = queue0.pop(0)
            sig1 = program_1.send(val)
            send_cnt0 += 1

        else:
            # both need input, queue is empty -> deadlock
            return send_cnt0, send_cnt1


def test_machine():
    tape = load_tape("data/18-example.txt")
    assert run_single_program(tape) == 4


def test_dual():
    tape = load_tape("data/18-example-dual.txt")
    assert run_dual_program(tape) == (3, 3)


def part_1(tape: Tape):
    result = run_single_program(tape)
    print(f"part 1: recovered value is {result}")
    return result


def part_2(tape: Tape):
    _, sent1 = run_dual_program(tape)
    print(f"part 2: program 1 sent {sent1} times before deadlock")
    return sent1


if __name__ == '__main__':
    tape_ = load_tape("data/18-input.txt")
    part_1(tape_)
    part_2(tape_)
