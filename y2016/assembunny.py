from typing import Generator
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple

from utils import exhaust

Command = Tuple[str, str, Optional[str]]
Tape = List[Command]


def load_tape(fn: str) -> List[Command]:
    tape = []
    for line in open(fn):
        line = line.strip()
        if not line:
            continue
        parts = line.split(' ')
        if len(parts) == 3:
            tape.append(tuple(parts))
        elif len(parts) == 2:
            tape.append((parts[0], parts[1], None))
        else:
            raise ValueError(f"{line} -> {len(parts)}")
    return tape


class Machine:
    def __init__(self, a: int = 0, b: int = 0, c: int = 0, d: int = 0):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def __repr__(self):
        return f'{type(self).__name__}(a={self.a!r}, b={self.b!r}, c={self.c!r}, d={self.d!r})'

    def __str__(self):
        return f'[a={self.a}, b={self.b}, c={self.c}, d={self.d}]'

    def __getitem__(self, key: str) -> int:
        if key == 'a':
            return self.a
        elif key == 'b':
            return self.b
        elif key == 'c':
            return self.c
        elif key == 'd':
            return self.d
        else:
            raise KeyError(key)

    def __setitem__(self, key: str, value: int):
        if key == 'a':
            self.a = value
        elif key == 'b':
            self.b = value
        elif key == 'c':
            self.c = value
        elif key == 'd':
            self.d = value
        else:
            raise KeyError(key)

    def run(self, tape: Tape, debug: int = 0) -> 'Machine':
        return exhaust(self.run_gen(tape, debug))

    def run_gen(self, tape: Tape, debug: int = 0) -> Generator[int, None, 'Machine']:
        head = 0
        tick = 0
        tape = list(tape)

        while 0 <= head < len(tape):
            if debug > 0 and tick % debug == 0:
                print(f"t={tick}", self, f"h={head}", cs(tape[head]))
            (out, jump) = self.eval(tape, head)
            head += 1 if jump is None else jump
            tick += 1
            if out is not None:
                yield out

        return self

    def eval(self, tape: Tape, head: int) -> Tuple[Optional[int], Optional[int]]:
        instr, arg1, arg2 = tape[head]

        if instr == 'cpy':
            # cpy a b
            # cpy 1 b
            self[arg2] = self._val(arg1)

        elif instr == 'inc':
            # inc a
            assert arg2 is None
            self[arg1] += 1

        elif instr == 'dec':
            # dec a
            assert arg2 is None
            self[arg1] -= 1

        elif instr == 'add':
            # * add a b
            self[arg2] += self._val(arg1)

        elif instr == 'mul':
            # * mul a b
            self[arg2] *= self._val(arg1)

        elif instr == 'jnz':
            # jnz a 2
            if self._val(arg1) != 0:
                return None, self._val(arg2)

        elif instr == 'out':
            # out a
            assert arg2 is None
            return self._val(arg1), None

        elif instr == 'tgl':
            # tgl a
            assert arg2 is None

            toggle_pos = head + self._val(arg1)
            if 0 <= toggle_pos < len(tape):
                tcmd = tape[toggle_pos]
                tape[toggle_pos] = toggle(tcmd)

        elif instr == 'nop':
            pass

        else:
            raise KeyError(instr)

        return None, None

    def _val(self, arg: str) -> int:
        if arg.isalpha():
            return self[arg]
        else:
            return int(arg)


def cs(command: Command) -> str:
    return ' '.join(c for c in command if c)


def toggle(command: Command) -> Command:
    instr, arg1, arg2 = command
    toggled_instr = {
        'inc': 'dec',
        'dec': 'inc',
        'tgl': 'inc',
        'cpy': 'jnz',
        'jnz': 'cpy'
    }[instr]
    return toggled_instr, arg1, arg2


def test():
    m = Machine()
    m.run(load_tape("data/11-example.txt"))
    assert m.a == 42
    assert m.b == m.c == m.d == 0
    print(m)
