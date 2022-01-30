from typing import Iterable
from typing import NamedTuple

from common.iteration import ilen
from common.iteration import single_value
from common.text import strip_line

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


def four_ints(values) -> FourInts:
    a, b, c, d = values
    return int(a), int(b), int(c), int(d)


class Sample(NamedTuple):
    instructions: FourInts
    regs_before: FourInts
    regs_after: FourInts

    @classmethod
    def load(cls, fn: str) -> Iterable['Sample']:
        with open(fn) as file:
            while True:
                before = four_ints(
                    v for v in strip_line(file.readline().rstrip(), 'Before: [', ']').split(', ')
                )
                instructions = four_ints(int(v) for v in file.readline().rstrip().split(' '))
                after = four_ints(
                    v for v in strip_line(file.readline().rstrip(), 'After:  [', ']').split(', ')
                )

                yield Sample(
                    instructions=instructions,
                    regs_before=before,
                    regs_after=after
                )

                empty_line = file.readline()
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
    possible_n2c: dict[int, set[str]] = {
        opnum: set(all_ops.keys())
        for opnum in range(len(all_ops))
    }

    for sample in samples:
        possible_n2c[sample.opnum].intersection_update(sample.possible_opcodes())

    while possible_n2c:
        try:
            opnum, opcode = next(
                (n, single_value(cs))
                for n, cs in possible_n2c.items()
                if len(cs) == 1
            )
        except StopIteration as stop:
            raise ValueError("no more matches") from stop

        yield opnum, opcode
        del possible_n2c[opnum]
        for opcodes in possible_n2c.values():
            opcodes.discard(opcode)


def load_program(fn: str) -> Iterable[FourInts]:
    with open(fn) as file:
        for line in file:
            yield four_ints(line.split(' '))


def part_1(fn_samples: str) -> int:
    three_or_more = ilen(
        s for s in Sample.load(fn_samples)
        if ilen(s.possible_opcodes()) >= 3
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
    part_1("data/16-input-samples.txt")
    part_2("data/16-input-samples.txt", "data/16-input-program.txt")
