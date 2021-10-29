from typing import Dict
from typing import Iterable
from typing import NamedTuple
from typing import Set

from utils import count
from utils import single_value
from utils import strip_line

all_ops = {
    'addr': lambda a, b, regs: regs[a] + regs[b],
    'addi': lambda a, b, regs: regs[a] + b,
    'mulr': lambda a, b, regs: regs[a] * regs[b],
    'muli': lambda a, b, regs: regs[a] * b,
    'banr': lambda a, b, regs: regs[a] & regs[b],
    'bani': lambda a, b, regs: regs[a] & b,
    'borr': lambda a, b, regs: regs[a] | regs[b],
    'bori': lambda a, b, regs: regs[a] | b,
    'setr': lambda a, b, regs: regs[a],
    'seti': lambda a, b, regs: a,
    'gtir': lambda a, b, regs: int(a > regs[b]),
    'gtri': lambda a, b, regs: int(regs[a] > b),
    'gtrr': lambda a, b, regs: int(regs[a] > regs[b]),
    'eqir': lambda a, b, regs: int(a == regs[b]),
    'eqri': lambda a, b, regs: int(regs[a] == b),
    'eqrr': lambda a, b, regs: int(regs[a] == regs[b])
}


FourInts = tuple[int, int, int, int]


def four_ints(xs) -> FourInts:
    a, b, c, d = xs
    return int(a), int(b), int(c), int(d)


class Sample(NamedTuple):
    instructions: FourInts
    regs_before: FourInts
    regs_after: FourInts

    @classmethod
    def load(cls, fn: str) -> Iterable['Sample']:
        with open(fn) as f:
            while True:
                before = four_ints(
                    v for v in strip_line(f.readline().rstrip(), 'Before: [', ']').split(', ')
                )
                instructions = four_ints(int(v) for v in f.readline().rstrip().split(' '))
                after = four_ints(
                    v for v in strip_line(f.readline().rstrip(), 'After:  [', ']').split(', ')
                )

                yield Sample(
                    instructions=instructions,
                    regs_before=before,
                    regs_after=after
                )

                empty_line = f.readline()
                if empty_line == '':
                    return

    @property
    def opnum(self) -> int:
        return self.instructions[0]

    def possible_opcodes(self) -> Iterable[str]:
        _, a, b, c = self.instructions
        return (
            opcode
            for opcode, op in all_ops.items()
            if op(a, b, self.regs_before) == self.regs_after[c]
        )


def map_opnums_to_opcodes(samples: Iterable[Sample]) -> Iterable[tuple[int, str]]:
    possible_n2c: Dict[int, Set[str]] = {
        opnum: set(all_ops.keys())
        for opnum in range(len(all_ops))
    }

    for sample in samples:
        possible_n2c[sample.opnum].intersection_update(sample.possible_opcodes())

    while possible_n2c:
        opnum, opcode = next(
            (n, single_value(cs))
            for n, cs in possible_n2c.items()
            if len(cs) == 1
        )
        yield opnum, opcode
        del possible_n2c[opnum]
        for opcodes in possible_n2c.values():
            opcodes.discard(opcode)


def load_program(fn: str) -> Iterable[FourInts]:
    for line in open(fn):
        yield four_ints(line.split(' '))


def part_1(fn_samples: str) -> int:
    three_or_more = count(
        s for s in Sample.load(fn_samples)
        if count(s.possible_opcodes()) >= 3
    )
    print(f"part 1: there are {three_or_more} samples with at least three possible opcodes")
    return three_or_more


def part_2(fn_samples: str, fn_program: str):
    opnum_to_opcode = dict(map_opnums_to_opcodes(Sample.load(fn_samples)))
    print("opcode mapping:", ", ".join(f"{n}->{c}" for n, c in sorted(opnum_to_opcode.items())))

    registers = [0, 0, 0, 0]
    for instr in load_program(fn_program):
        opnum, a, b, c = instr
        opcode = opnum_to_opcode[opnum]
        registers[c] = all_ops[opcode](a, b, registers)

    print(f"part 2: after processing the instructions, register 0 contains value {registers[0]}")
    return registers[0]


if __name__ == '__main__':
    filename_samples = "data/16-input-samples.txt"
    filename_program = "data/16-input-program.txt"

    part_1(filename_samples)
    part_2(filename_samples, filename_program)
