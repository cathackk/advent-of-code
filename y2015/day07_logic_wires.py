from enum import Enum
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional


class Command(Enum):
    VALUE = (0, 1)
    NOT = (1, 1)
    AND = (2, 2)
    OR = (3, 2)
    LSHIFT = (4, 2)
    RSHIFT = (5, 2)

    def __init__(self, code: int, argcount: int):
        self.code = code
        self.argcount = argcount


class Instruction:
    def __init__(self, command: Command, arg1: str, arg2: Optional[str], target: str):
        assert arg1 is not None
        if command.argcount >= 2:
            assert arg2 is not None

        self.command = command
        self.arg1 = arg1
        self.arg2 = arg2
        self.target = target

    def __repr__(self):
        return (
            f'{type(self).__name__}('
            f'{self.command.name}, '
            f'{self.arg1!r}, '
            f'{self.arg2!r}, '
            f'{self.target!r})'
        )

    def __str__(self):
        if self.command == Command.VALUE:
            return f"{self.arg1} -> {self.target}"
        elif self.command == Command.NOT:
            return f"NOT {self.arg1} -> {self.target}"
        else:
            return f"{self.arg1} {self.command.name} {self.arg2} -> {self.target}"

    def required_variables(self) -> Iterable[str]:
        if not self.arg1.isnumeric():
            yield self.arg1
        if self.arg2 is not None and not self.arg2.isnumeric():
            yield self.arg2

    def evaluate(self, values: Dict[str, int]) -> tuple[str, int]:
        return self.target, self._eval_value(values)

    def _eval_value(self, values: Dict[str, int]) -> int:
        v1 = int(self.arg1) if self.arg1.isnumeric() else values[self.arg1]

        if self.command == Command.VALUE:
            return v1
        elif self.command == Command.NOT:
            return v1 ^ 0xffff

        v2 = int(self.arg2) if self.arg2.isnumeric() else values[self.arg2]
        if self.command == Command.AND:
            return v1 & v2
        elif self.command == Command.OR:
            return v1 | v2
        elif self.command == Command.LSHIFT:
            return v1 << v2
        elif self.command == Command.RSHIFT:
            return v1 >> v2
        else:
            raise ValueError(f"unsupported command {self.command.name}")

    @classmethod
    def from_line(cls, line: str):
        """
        456 -> y
        x AND y -> d
        x OR y -> e
        x LSHIFT 2 -> f
        y RSHIFT 2 -> g
        NOT x -> h
        """
        parts = line.strip().split(' ')
        assert parts[-2] == "->"
        target = parts[-1]
        del parts[-2:]

        if len(parts) == 1:
            return cls(Command.VALUE, parts[0], None, target)
        elif len(parts) == 2:
            assert parts[0] == "NOT"
            return cls(Command.NOT, parts[1], None, target)
        elif len(parts) == 3:
            return cls(Command[parts[1]], parts[0], parts[2], target)


def evaluate(instructions: Iterable[Instruction]) -> Dict[str, int]:
    unprocessed_instructions = list(instructions)

    values: Dict[str, int] = dict()

    while unprocessed_instructions:
        known_variables = set(values.keys())
        instr = next(
            i for i in unprocessed_instructions
            if all(
                rv in known_variables
                for rv in i.required_variables()
            )
        )
        unprocessed_instructions.remove(instr)
        # print(f"left={len(unprocessed_instructions)}, instruction: {instr}")
        key, value = instr.evaluate(values)
        # print(f"  {value} -> {key}")
        values[key] = value

    return values


def test_example():
    instructions = [
        Instruction(Command.VALUE, '123', None, 'x'),
        Instruction(Command.VALUE, '456', None, 'y'),
        Instruction(Command.AND, 'x', 'y', 'd'),
        Instruction(Command.OR, 'x', 'y', 'e'),
        Instruction(Command.LSHIFT, 'x', '2', 'f'),
        Instruction(Command.RSHIFT, 'y', '2', 'g'),
        Instruction(Command.NOT, 'x', None, 'h'),
        Instruction(Command.NOT, 'y', None, 'i')
    ]
    for instr in instructions:
        print(instr)
    print()
    result = evaluate(instructions)
    print("result:", result)
    assert result == {
        'x': 123, 'y': 456,
        'd': 72, 'e': 507,
        'f': 492, 'g': 114,
        'h': 65412, 'i': 65079
    }


def part_1(instructions: List[Instruction]) -> int:
    result = evaluate(instructions)
    a = result['a']
    print(f"part 1: a={a}")
    return a


def part_2(instructions: List[Instruction], b_override: int) -> int:
    # first override the ?? -> b instruction
    b_instr = next(
        instr for instr in instructions
        if instr.command == Command.VALUE and instr.target == 'b'
    )
    b_instr.arg1 = str(b_override)
    # then evaluate
    result = evaluate(instructions)
    a = result['a']
    print(f"part 2: a={a}")
    return a


if __name__ == '__main__':
    instructions = [Instruction.from_line(line) for line in open("data/07-input.txt") if line]
    a = part_1(instructions)
    part_2(instructions, b_override=a)
