from typing import Iterable
from typing import List


class Condition:
    def __init__(self, reg: str, op: str, value: int):
        self.reg = reg
        self.op = op
        self.value = value

    def evaluate(self, reg_val: int) -> bool:
        if self.op == '==':
            return reg_val == self.value
        elif self.op == '!=':
            return reg_val != self.value
        elif self.op == '>':
            return reg_val > self.value
        elif self.op == '>=':
            return reg_val >= self.value
        elif self.op == '<':
            return reg_val < self.value
        elif self.op == '<=':
            return reg_val <= self.value
        else:
            raise KeyError(self.op)

    def __repr__(self):
        return f'{type(self).__name__}({self.reg!r}, {self.op!r}, {self.value!r})'

    def __str__(self):
        return f"{self.reg} {self.op} {self.value}"

    @classmethod
    def parse(cls, text: str) -> 'Condition':
        # a >= 1
        reg, op, value = text.strip().split(" ")
        return cls(reg, op, int(value))


class Command:
    def __init__(self, reg: str, instr: str, value: int, condition: Condition):
        self.reg = reg
        self.instr = instr
        self.value = value
        self.condition = condition

    @property
    def inc_value(self) -> int:
        if self.instr == 'inc':
            return self.value
        elif self.instr == 'dec':
            return -self.value
        else:
            raise KeyError(self.instr)

    def __repr__(self):
        return (
            f'{type(self).__name__}('
            f'{self.reg!r}, {self.instr!r}, {self.value!r}, {self.condition!r}'
            f')'
        )

    def __str__(self):
        return f"{self.reg} {self.instr} {self.value} if {self.condition}"

    @classmethod
    def parse(cls, text: str) -> 'Command':
        # c dec -10 if a >= 1
        exec_part, cond_part = text.strip().split(" if ")
        reg, instr, value = exec_part.split()
        return cls(reg, instr, int(value), Condition.parse(cond_part))


def load_commands(fn: str) -> Iterable[Command]:
    for line in open(fn):
        yield Command.parse(line)


class Machine:
    def __init__(self, **kwargs):
        self.registers = {k: int(v) for k, v in kwargs.items()}
        self.max_value = max(self.registers.values(), default=0)

    def __repr__(self):
        rvs = ', '.join(f'{r!r}={v!r}' for r, v in self.registers.items())
        return f'{type(self).__name__}({rvs})'

    def __str__(self):
        rvs = ", ".join(f"{r}={v}" for r, v in self.registers.items())
        return f"[{rvs}]"

    def __getitem__(self, r: str):
        return self.registers.get(r, 0)

    def __setitem__(self, r: str, value: int):
        self.registers[r] = value
        if value > self.max_value:
            self.max_value = value

    def values(self) -> Iterable[int]:
        return self.registers.values()

    def run(self, cmds: Iterable[Command]):
        for cmd in cmds:
            self.execute(cmd)

    def execute(self, cmd: Command) -> bool:
        if cmd.condition.evaluate(self[cmd.condition.reg]):
            self[cmd.reg] += cmd.inc_value
            return True
        else:
            return False


if __name__ == '__main__':
    cmds_ = list(load_commands("data/08-input.txt"))
    m = Machine()
    m.run(cmds_)
    print(f"part 1: current max register value is {max(m.values())}")
    print(f"part 2: all the time max register value is {m.max_value}")
