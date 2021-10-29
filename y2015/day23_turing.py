from typing import List
from typing import Optional


Command = tuple[str, str, Optional[str]]
Tape = List[Command]


class Machine:
    def __init__(self):
        self.registers = {'a': 0, 'b': 0}
        self.head = 0

    @property
    def a(self) -> int:
        return self.registers['a']

    @a.setter
    def a(self, value: int):
        self.registers['a'] = value

    @property
    def b(self) -> int:
        return self.registers['b']

    @b.setter
    def b(self, value: int):
        self.registers['b'] = value

    def jump(self, offset: int):
        #  0: endless loop
        # +1: normal flow, no effect
        assert offset not in (0, +1)
        self.head += offset - 1

    def run(self, tape: Tape):
        while 0 <= self.head < len(tape):
            command = tape[self.head]
            self.eval(command)
            self.head += 1

    def eval(self, command: Command):
        instr, arg1, arg2 = command
        assert arg1 is not None

        if instr == 'hlf':
            assert arg2 is None
            self.registers[arg1] //= 2

        elif instr == 'tpl':
            assert arg2 is None
            self.registers[arg1] *= 3

        elif instr == 'inc':
            assert arg2 is None
            self.registers[arg1] += 1

        elif instr == 'jmp':
            assert arg2 is None
            self.jump(int(arg1))

        elif instr == 'jie':
            # jump if even
            assert arg2 is not None
            if self.registers[arg1] % 2 == 0:
                self.jump(int(arg2))

        elif instr == 'jio':
            # jump if one
            assert arg2 is not None
            if self.registers[arg1] == 1:
                self.jump(int(arg2))

        else:
            raise ValueError(instr)



def load_tape(fn: str) -> Tape:
    tape = []
    for line in open(fn):
        line = line.strip()
        if not line:
            continue
        instr, args = line.strip().split(' ', 1)
        if ', ' in args:
            arg1, arg2 = args.split(', ')
        else:
            arg1, arg2 = args, None
        tape.append((instr, arg1, arg2))
    return tape


def test_1():
    tape = load_tape("data/23-example-1.txt")
    m = Machine()
    m.run(tape)
    assert m.a == 2
    assert m.b == 0
    assert m.head == len(tape)


def part_1(tape: Tape):
    m = Machine()
    m.run(tape)
    print(f"part 1: register b = {m.b}")
    return m.b


def part_2(tape: Tape):
    m = Machine()
    m.a = 1
    m.run(tape)
    print(f"part 2: register b = {m.b}")
    return m.b


if __name__ == '__main__':
    t = load_tape("data/23-input.txt")
    part_1(t)
    part_2(t)
