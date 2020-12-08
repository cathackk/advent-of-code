"""
Advent of Code 2020
Day 8: Handheld Halting
https://adventofcode.com/2020/day/8
"""

from dataclasses import dataclass
from typing import Generator
from typing import Iterable
from typing import List
from typing import Tuple


def part_1(program: List['Instruction']) -> int:
    """
    There is a strange infinite loop in the boot code (your puzzle input) of the device. You should
    be able to fix it, but first you need to be able to run the code in isolation.

    The boot code is represented as a text file with one instruction per line of text. Each
    *instruction* consists of an *operation* (`acc`, `jmp`, or `nop`) and an *argument* (a signed
    number like `+4` or `-20`).

        - `acc` increases or decreases a single global value called the *accumulator* by the value
          given in the argument. For example, `acc +7` would increase the accumulator by 7.
          The accumulator starts at `0`. After an `acc` instruction, the instruction immediately
          below it is executed next.
        - `jmp` jumps to a new instruction relative to itself. The next instruction to execute is
          found using the argument as an offset from the `jmp` instruction; for example, `jmp +2`
          would skip the next instruction, `jmp +1` would continue to the instruction immediately
          below it, and `jmp -20` would cause the instruction 20 lines above to be executed next.
        - `nop` stands for *No OPeration* - it does nothing. The instruction immediately below it
          is executed next.

    For example, consider the following program:

        >>> prog = program_from_text('''
        ...
        ...     nop +0
        ...     acc +1
        ...     jmp +4
        ...     acc +3
        ...     jmp -3
        ...     acc -99
        ...     acc +1
        ...     jmp -4
        ...     acc +6
        ...
        ... ''')
        >>> len(prog)
        9
        >>> prog[0]
        ('nop', 0)
        >>> prog[-1]
        ('acc', 6)

    These instructions are visited in this order:

        >>> final_acc, terminated = run_program_safe(prog, debug=True)
        1. nop +0 | ip=0
        2. acc +1 | ip=1 -> acc=1
        3. jmp +4 | ip=2 -> ip=6
        4. acc +1 | ip=6 -> acc=2
        5. jmp -4 | ip=7 -> ip=3
        6. acc +3 | ip=3 -> acc=5
        7. jmp -3 | ip=4 -> ip=1
        8. acc +1 | ip=1 (loop!)

    First, the `1. nop +0` does nothing. Then, the accumulator is increased from 0 to 1
    (`2. acc +1`) and `3. jmp +4` sets the next instruction to `4. acc +1`. After it increases
    the accumulator from 1 to 2, `5. jmp -4` executes, setting the next instruction to `6. acc +3`.
    It sets the accumulator to 5, and `7. jmp -3` causes the program to continue back at
    `8. acc +1 | ip=1`.

    This is an *infinite loop*: with this sequence of jumps, the program will run forever.
    The moment the program tries to run any instruction a second time, you know it will never
    terminate.

        >>> terminated
        False

    Immediately *before* the program would run an instruction a second time, the value in the
    accumulator is *5*.

        >>> final_acc
        5

    Run your copy of the boot code. Immediately before any instruction is executed a second time,
    *what value is in the accumulator?*

        >>> part_1(prog)
        part 1: when program loop was detected, accumulator value was 5
        5
    """

    final_acc, terminated = run_program_safe(program)
    assert terminated is False

    print(f"part 1: when program loop was detected, accumulator value was {final_acc}")
    return final_acc


def part_2(program: List['Instruction']) -> int:
    """
    After some careful analysis, you believe that *exactly one instruction is corrupted*.

    Somewhere in the program, either a `jmp` is supposed to be a `nop`, or a `nop` is supposed to
    be a `jmp`. (No `acc` instructions were harmed in the corruption of this boot code.)

    The program is supposed to terminate by *attempting to execute an instruction immediately after
    the last instruction in the file*. By changing exactly one `jmp` or `nop`, you can repair the
    boot code and make it terminate correctly.

    For example, consider the same program from above:

        >>> prog = program_from_text('''
        ...
        ...     nop +0
        ...     acc +1
        ...     jmp +4
        ...     acc +3
        ...     jmp -3
        ...     acc -99
        ...     acc +1
        ...     jmp -4
        ...     acc +6
        ...
        ... ''')

    If you change the first instruction from `nop +0` to `jmp +0`, it would create
    a single-instruction infinite loop, never leaving that instruction.

        >>> prog1 = adjusted_program(prog, flip_ip=0)
        >>> prog1[0]
        ('jmp', 0)
        >>> run_program_safe(prog1, debug=True)
        1. jmp +0 | ip=0 -> ip=0
        2. jmp +0 | ip=0 (loop!)
        (0, False)

    If you change almost any of the `jmp` instructions, the program will still eventually find
    another `jmp` instruction and loop forever.

    However, if you change the second-to-last instruction from `jmp -4` to `nop -4`, ...

        >>> prog2 = adjusted_program(prog, flip_ip=7)
        >>> prog2[7]
        ('nop', -4)

    ... the program terminates! The instructions are visited in this order:

        >>> run_program_safe(prog2, debug=True)
        1. nop +0 | ip=0
        2. acc +1 | ip=1 -> acc=1
        3. jmp +4 | ip=2 -> ip=6
        4. acc +1 | ip=6 -> acc=2
        5. nop -4 | ip=7
        6. acc +6 | ip=8 -> acc=8
        (8, True)

    After the last instruction (`6. acc +6`), the program terminates by attempting to run the
    instruction below the last instruction in the file. With this change, after the program
    terminates, the accumulator contains the value 8.

    Fix the program so that it terminates normally by changing exactly one `jmp` (to `nop`)
    or `nop` (to `jmp`). *What is the value of the accumulator after the program terminates?*

        >>> part_2(prog)
        part 2: after modifying instruction at ip=7, program terminates with accumulator value 8
        8
    """

    final_acc, flipped_ip = repair_program(program)

    print(
        f"part 2: after modifying instruction at ip={flipped_ip}, "
        f"program terminates with accumulator value {final_acc}"
    )
    return final_acc


Instruction = Tuple[str, int]


def program_from_text(text: str) -> List[Instruction]:
    return list(program_from_lines(text.strip().split('\n')))


def program_from_file(fn: str) -> List[Instruction]:
    return list(program_from_lines(open(fn)))


def program_from_lines(lines: Iterable[str]) -> Iterable[Instruction]:
    for line in lines:
        op, arg = line.strip().split(" ")
        yield op, int(arg)


@dataclass
class ProgramState:
    ip_before: int
    ip_after: int
    acc_before: int
    acc_after: int
    instruction: Instruction


def run_program(program: List[Instruction]) -> Generator[ProgramState, None, int]:
    ip, acc = 0, 0
    while True:

        if not 0 <= ip <= len(program):
            # make sure instructino pointer is within bounds of the program
            raise IndexError(f"ip={ip} out of program range (0..{len(program)})")

        if ip == len(program):
            # instruction pointer points right after the last instruction -> program terminates
            return acc

        # evaluate current instruction
        op, arg = program[ip]
        if op == 'acc':
            acc_new = acc + arg
            ip_new = ip + 1
        elif op == 'jmp':
            acc_new = acc
            ip_new = ip + arg
        elif op == 'nop':
            acc_new = acc
            ip_new = ip + 1
        else:
            raise ValueError(f"unsupported operation {op!r}")

        # report state
        yield ProgramState(
            ip_before=ip,
            ip_after=ip_new,
            acc_before=acc,
            acc_after=acc_new,
            instruction=(op, arg)
        )

        ip, acc = ip_new, acc_new


def run_program_safe(program: List[Instruction], debug: bool = False) -> Tuple[int, bool]:
    """
    Runs the program until loop is detected or program terminates.

    Returns the final accumulator value and flag indicating whether a loop was detected (`False`)
    or if program terminated (`True`).

    Optionally prints the instructions it evaluates if `debug` is set to `True`.
    """

    visited_ips = set()
    tick = 0
    run = run_program(program)

    def effects_text(ps: ProgramState, loop_detected: bool) -> Iterable[str]:
        changes = []
        # collect all changes that happened during evaluation of the current instruction;
        # if loop was just detected, do not report the changes as they are irrelevant
        if not loop_detected:
            if ps.ip_before + 1 != ps.ip_after:
                changes.append(f"ip={ps.ip_after}")
            if ps.acc_before != ps.acc_after:
                changes.append(f"acc={ps.acc_after}")

        changes_text = (" -> " + ", ".join(changes)) if changes else ""
        result_text = f" (loop!)" if loop_detected else ""
        return changes_text + result_text

    def log(t: int, ps: ProgramState, loop_detected: bool = False):
        if debug:
            op, arg = ps.instruction
            print(f"{t}. {op} {arg:+} | ip={ps.ip_before}{effects_text(ps, loop_detected)}")

    try:
        while True:
            state = next(run)
            tick += 1

            if state.ip_before not in visited_ips:
                # remember visited instruction pointers
                visited_ips.add(state.ip_before)
                log(tick, state)

            else:
                # if visited for the second time, we detected a loop -> terminate
                log(tick, state, loop_detected=True)
                return state.acc_before, False

    except StopIteration as stop:

        # program terminated without encountering a loop
        return stop.value, True


def adjusted_program(program: List[Instruction], flip_ip: int) -> List[Instruction]:
    assert 0 <= flip_ip < len(program)

    # flipping instruction at given ip
    op_before, arg = program[flip_ip]
    if op_before == 'jmp':
        op_after = 'nop'
    elif op_before == 'nop':
        op_after = 'jmp'
    else:
        # no change
        op_after = op_before

    # duplicate program
    program1 = list(program)
    # ... and adjust the single instruction
    program1[flip_ip] = (op_after, arg)
    return program1


def repair_program(program: List[Instruction]) -> Tuple[int, int]:
    """
    Tries to "repair" to program by finding a single instruction which when flipped
    (`jmp`->`nop` and vice versa) causes the program to terminate.

    Returns final accumulator value of the repaired program and index of the flipped instruction.

    This also assumes the program is "broken" in the first place (has endless loop).
    """

    for ip in range(len(program)):
        program_adjusted = adjusted_program(program, flip_ip=ip)
        final_acc, terminates = run_program_safe(program_adjusted)
        if terminates:
            return final_acc, ip

    else:
        raise ValueError("program cannot be repaired")


if __name__ == '__main__':
    program_ = program_from_file('data/08-input.txt')
    part_1(program_)
    part_2(program_)
