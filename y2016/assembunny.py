from dataclasses import dataclass
from typing import Final
from typing import Generator
from typing import Iterable
from typing import Iterator

from common.file import relative_path
from common.iteration import exhaust


class Command:
    __match_args__: Final[tuple] = ('instr', 'args')

    def __init__(self, instr: str, *args: str | int):
        self.instr = instr
        self.args = args

    def __repr__(self) -> str:
        args_repr = ''.join(f', {arg!r}' for arg in self.args)
        return f'{type(self).__name__}({self.instr!r}{args_repr})'

    def __str__(self) -> str:
        return " ".join(str(p) for p in (self.instr,) + self.args)

    @classmethod
    def from_str(cls, line: str) -> 'Command':
        instr, *args = line.split()
        return cls(instr, *(try_int(arg) for arg in args))

    def toggled(self) -> 'Command':
        cls = type(self)
        match self:
            case Command('inc', (arg_1,)):
                return cls('dec', arg_1)
            case Command(_, (arg_1,)):
                return cls('inc', arg_1)
            case Command('jnz', (arg_1, arg_2)):
                return cls('cpy', arg_1, arg_2)
            case Command(_, (arg_1, arg_2)):
                return cls('jnz', arg_1, arg_2)
            case _:
                raise ValueError(self)

        # TODO: remove when mypy realizes this is unreachable
        assert False


def try_int(arg: str) -> str | int:
    try:
        return int(arg)
    except ValueError:
        return arg


class Tape:
    def __init__(self, commands: Iterable[Command]):
        self.commands = list(commands)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.commands!r})'

    def __str__(self) -> str:
        return format(self, "; ")

    def __format__(self, sep: str) -> str:
        return sep.join(str(cmd) for cmd in self)

    @classmethod
    def from_text(cls, text: str) -> 'Tape':
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_file(cls, fn: str) -> 'Tape':
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Tape':
        return cls(Command.from_str(cmd.strip()) for line in lines for cmd in line.split(';'))

    def __iter__(self) -> Iterator[Command]:
        return iter(self.commands)

    def __getitem__(self, key):
        return self.commands[key]

    def __setitem__(self, key, new) -> None:
        if isinstance(key, slice):
            assert key.step in (None, 1)

            old_region = self.commands[key]
            delta = len(old_region) - len(new)
            assert delta >= 0, "replacing with longer not supported"

            # replace with new + some optional nops as padding
            self.commands[key] = list(new) + [Command('nop')] * delta

        else:
            self.commands[key] = new

    def __len__(self) -> int:
        return len(self.commands)


Registers = dict[str, int]


@dataclass(frozen=True)
class RunState:
    head: int
    head_next: int
    command: Command
    registers: Registers
    tape: Tape
    out_value: int | None

    def __repr__(self) -> str:
        head_next_repr = (
            f', head_next={self.head_next!r}' if self.head_next != self.head + 1 else ''
        )
        out_value_repr = f', out_value={self.out_value!r}' if self.out_value is not None else ''

        return (
            f'{type(self).__name__}('
            f'head={self.head!r}'
            f'{head_next_repr}, '
            f'command={self.command!r}, '
            f'registers={self.registers!r}, '
            f'tape={str(self.tape)!r}'
            f'{out_value_repr})'
        )


def run(tape: Tape, optimized: bool = False, **kwargs: int) -> Registers:
    # pylint: disable=unpacking-non-sequence
    _, final_registers = exhaust(run_generator(tape, optimized=optimized, **kwargs))
    return final_registers


def run_out(tape: Tape, optimized: bool = False, **kwargs: int) -> Iterator[int]:
    return (
        state.out_value
        for state in run_generator(tape, optimized=optimized, **kwargs)
        if state.out_value is not None
    )


def run_generator(
    tape: Tape,
    optimized: bool = False,
    **kwargs: int
) -> Generator[RunState, None, tuple[int, Registers]]:

    regs = {r: 0 for r in 'abcd'}

    for reg, init_val in kwargs.items():
        regs[reg] = int(init_val)

    if optimized:
        tape = optimized_tape(tape)
    else:
        tape = type(tape)(tape)

    def val(src: str | int) -> int:
        return src if isinstance(src, int) else regs[src]

    head = 0

    while True:

        try:
            command = tape[head]
        except IndexError:
            break

        jump = 1
        out_value = None

        match command:
            case Command('cpy', (source, target)):
                regs[target] = val(source)
            case Command('inc', (target,)):
                regs[target] += 1
            case Command('dec', (target,)):
                regs[target] -= 1
            case Command('jnz', (source, offset)):
                if val(source):
                    jump = val(offset)

            case Command('tgl', (offset,)):
                pos = head + val(offset)
                if pos in range(len(tape)):
                    tape[pos] = tape[pos].toggled()
            case Command('out', (value,)):
                out_value = val(value)

            case Command('add', (source, target)):
                regs[target] += val(source)
            case Command('mul', (source, target)):
                regs[target] *= val(source)
            case Command('nop', ()):
                pass

            case _:
                raise ValueError(command)

        yield RunState(
            head=head,
            head_next=head + jump,
            command=command,
            registers=dict(regs),
            tape=tape,
            out_value=out_value
        )

        head += jump

    return head, regs


def optimized_tape(tape: Tape) -> Tape:
    tape = type(tape)(tape)

    _incdec_to_mul(tape)
    _incdec_to_add(tape)
    # ...

    return tape


def _incdec_to_mul(tape: Tape) -> None:
    """
    cpy x w; cpy 0 x; cpy y z; inc x; dec z; jnz z -2; dec w; jnz w -5
    ->
    mul y x; cpy 0 z, cpy 0 w

        >>> t = Tape.from_file('data/23-example.txt')
        >>> print(t)  # doctest: +NORMALIZE_WHITESPACE
        cpy 60 b; cpy -1 c; cpy -1 d;
        cpy a d; cpy 0 a; cpy b c; inc a; dec c; jnz c -2; dec d; jnz d -5;
        inc c; inc d
        >>> run(t, a=40)
        {'a': 2400, 'b': 60, 'c': 1, 'd': 1}

        >>> _incdec_to_mul(t)
        >>> print(t)  # doctest: +NORMALIZE_WHITESPACE
        cpy 60 b; cpy -1 c; cpy -1 d;
        mul b a; cpy 0 c; cpy 0 d; nop; nop; nop; nop; nop;
        inc c; inc d
        >>> run(t, a=40)
        {'a': 2400, 'b': 60, 'c': 1, 'd': 1}
    """

    pattern = [
        ('cpy', 'x', 'w'), ('cpy', 0, 'x'), ('cpy', 'y', 'z'), ('inc', 'x'),
        ('dec', 'z'), ('jnz', 'z', -2), ('dec', 'w'), ('jnz', 'w', -5)
    ]

    while True:
        pos = _find_pattern(tape, *pattern)
        if pos < 0:
            break
        cpy_x_w, _, cpy_y_z = tape[pos:pos+3]
        x, w = cpy_x_w.args
        y, z = cpy_y_z.args
        repl = [Command('mul', y, x), Command('cpy', 0, z), Command('cpy', 0, w)]
        tape[pos:pos+len(pattern)] = repl


def _incdec_to_add(tape: Tape) -> None:
    """
    inc x; dec y; jnz y -2
    ->
    add y x; cpy 0 y

        >>> t = Tape.from_text('cpy 3 a; cpy 4 b; inc a; dec b; jnz b -2')
        >>> run(t)
        {'a': 7, 'b': 0, 'c': 0, 'd': 0}

        >>> _incdec_to_add(t)
        >>> print(t)
        cpy 3 a; cpy 4 b; add b a; cpy 0 b; nop
        >>> run(t)
        {'a': 7, 'b': 0, 'c': 0, 'd': 0}
    """

    while True:
        pos = _find_pattern(tape, ('inc', 'x'), ('dec', 'y'), ('jnz', 'y', -2))
        if pos < 0:
            break
        inc, dec, _ = tape[pos:pos+3]
        repl = [Command('add', dec.args[0], inc.args[0]), Command('cpy', 0, dec.args[0])]
        tape[pos:pos+3] = repl


def _find_pattern(tape: Tape, *pattern: tuple) -> int:
    for pos in range(len(tape) - len(pattern) + 1):
        if _matches_pattern(tape[pos:pos + len(pattern)], pattern):
            return pos
    else:
        return -1


def _matches_pattern(cmds: Iterable[Command], pattern: Iterable[tuple]) -> bool:
    bound: dict[str, str | int] = {}  # var to value

    cmds = list(cmds)
    pattern = list(pattern)

    for cmd, ppart in zip(cmds, pattern):
        if 1 + len(cmd.args) != len(ppart):
            return False

        if cmd.instr != ppart[0]:
            return False

        for arg, parg in zip(cmd.args, ppart[1:]):
            if isinstance(parg, str):
                if parg not in bound:
                    if arg in bound.values():
                        return False  # already bound to a different var
                    bound[parg] = arg
                elif bound[parg] != arg:
                    return False

            elif isinstance(parg, int):
                if parg != arg:
                    return False

            else:
                raise TypeError(type(parg))

    return True
