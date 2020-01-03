from typing import Optional
from typing import Tuple

from machine import load_tape
from machine import Machine


def find_noun_verb(tape, target_value) -> Optional[Tuple[int, int]]:
    for noun in range(len(tape)):
        tape[1] = noun
        for verb in range(len(tape)):
            tape[2] = verb
            m = Machine(tape)
            assert list(m.run_output_only()) == []
            value = m.memory[0]
            if value == target_value:
                return noun, verb
    else:
        return None


def part_1():
    tape = load_tape("data/02-program.txt")
    tape[1], tape[2] = 12, 2
    m = Machine(tape)
    assert list(m.run_output_only()) == []
    print(f"part 1: value at memory address 1 is {m.memory[0]}")


def part_2():
    tape = load_tape("data/02-program.txt")
    answer = find_noun_verb(tape, target_value=19690720)
    if answer:
        noun, verb = answer
        print(f"part 2: noun={noun}, verb={verb}")
    else:
        print(f"part 2: answer not found")


if __name__ == '__main__':
    part_1()
    part_2()
