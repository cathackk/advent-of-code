"""
Advent of Code 2020
Day 8: Handheld Halting
https://adventofcode.com/2020/day/8
"""

from dataclasses import dataclass
from typing import Generator
from typing import Iterable

from common.utils import relative_path


def part_1(program: 'Program') -> int:
    """
    There is a strange infinite loop in the boot code (your puzzle input) of the device. You should
    be able to fix it, but first you need to be able to run the code in isolation.

    The boot code is represented as a text file with one instruction per line of text. Each
    *instruction* consists of an *operation* (`acc`, `jmp`, or `nop`) and an *argument* (a signed
    number like `+4` or `-20`).

        - `acc` increases or decreases a single global value called the *accumulator* by the value
          given in the argument. For example, `acc +7` would increase the accumulator by 7.
          The accumulator starts at 0. After an `acc` instruction, the instruction immediately
          below it is executed next.
        - `jmp` jumps to a new instruction relative to itself. The next instruction to execute is
          found using the argument as an offset from the `jmp` instruction; for example, `jmp +2`
          would skip the next instruction, `jmp +1` would continue to the instruction immediately
          below it, and `jmp -20` would cause the instruction 20 lines above to be executed next.
        - `nop` stands for *No OPeration* - it does nothing. The instruction immediately below it
          is executed next.

    For example, consider the following program:

        >>> prog = Program.from_text('''
        ...     nop +0
        ...     acc +1
        ...     jmp +4
        ...     acc +3
        ...     jmp -3
        ...     acc -99
        ...     acc +1
        ...     jmp -4
        ...     acc +6
        ... ''')
        >>> len(prog)
        9
        >>> prog[0]
        ('nop', 0)
        >>> prog[-1]
        ('acc', 6)

    These instructions are visited in this order:

        >>> final_acc, terminated = prog.run_safe(debug=True)
        1. nop +0 | ip=0
        2. acc +1 | ip=1 -> acc=1
        3. jmp +4 | ip=2 -> ip=6
        4. acc +1 | ip=6 -> acc=2
        5. jmp -4 | ip=7 -> ip=3
        6. acc +3 | ip=3 -> acc=5
        7. jmp -3 | ip=4 -> ip=1
        8. acc +1 | ip=1 (loop!)

    Explanation:

        1. `nop +0` does nothing. Then
        2. `acc +1` increases the accumulator from 0 to 1 and
        3. `jmp +4` sets the next instruction to
        4. `acc +1` at instruction pointer `ip=6`. After it increases the accumulator from 1 to 2,
        5. `jmp -4` executes, setting the next instruction to
        6. `acc +3` at `ip=3`. It sets the accumulator to 5, and
        7. `jmp -3` causes the program to continue back at
        8. `acc +1` at `ip=1`, ie. the second program instruction from the top.

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

    final_acc, terminated = program.run_safe()
    assert terminated is False

    print(f"part 1: when program loop was detected, accumulator value was {final_acc}")
    return final_acc


def part_2(program: 'Program') -> int:
    """
    After some careful analysis, you believe that *exactly one instruction is corrupted*.

    Somewhere in the program, either a `jmp` is supposed to be a `nop`, or a `nop` is supposed to
    be a `jmp`. (No `acc` instructions were harmed in the corruption of this boot code.)

    The program is supposed to terminate by *attempting to execute an instruction immediately after
    the last instruction in the file*. By changing exactly one `jmp` or `nop`, you can repair the
    boot code and make it terminate correctly.

    For example, consider the same program from above:

        >>> prog = Program.from_text('''
        ...     nop +0
        ...     acc +1
        ...     jmp +4
        ...     acc +3
        ...     jmp -3
        ...     acc -99
        ...     acc +1
        ...     jmp -4
        ...     acc +6
        ... ''')

    If you change the first instruction from `nop +0` to `jmp +0`, it would create
    a single-instruction infinite loop, never leaving that instruction.

        >>> prog1 = Program(prog)
        >>> prog1.flip_instruction(0)
        True
        >>> prog1[0]
        ('jmp', 0)
        >>> prog1.run_safe(debug=True)
        1. jmp +0 | ip=0 -> ip=0
        2. jmp +0 | ip=0 (loop!)
        (0, False)

    If you change almost any of the `jmp` instructions, the program will still eventually find
    another `jmp` instruction and loop forever.

    However, if you change the second-to-last instruction from `jmp -4` to `nop -4`, ...

        >>> prog2 = Program(prog)
        >>> prog2.flip_instruction(7)
        True
        >>> prog2[7]
        ('nop', -4)

    ... the program terminates! The instructions are visited in this order:

        >>> prog2.run_safe(debug=True)
        1. nop +0 | ip=0
        2. acc +1 | ip=1 -> acc=1
        3. jmp +4 | ip=2 -> ip=6
        4. acc +1 | ip=6 -> acc=2
        5. nop -4 | ip=7
        6. acc +6 | ip=8 -> acc=8
        (8, True)

    After the last instruction (`acc +6`), the program terminates by attempting to run the
    instruction below the last instruction in the file. With this change, after the program
    terminates, the accumulator contains the value *8* (`acc +1`, `acc +1`, `acc +6`).

    Fix the program so that it terminates normally by changing exactly one `jmp` (to `nop`)
    or `nop` (to `jmp`). *What is the value of the accumulator after the program terminates?*

        >>> part_2(prog)
        part 2: after modifying instruction at ip=7, program terminates with accumulator value 8
        8
    """

    final_acc, flipped_ip = program.repair()

    print(
        f"part 2: after modifying instruction at ip={flipped_ip}, "
        f"program terminates with accumulator value {final_acc}"
    )
    return final_acc


Instruction = tuple[str, int]


class Program:
    def __init__(self, instructions: Iterable[Instruction]):
        self.instructions = list(instructions)

    @classmethod
    def from_text(cls, text: str):
        return cls.from_lines(text.strip().split("\n"))

    @classmethod
    def from_file(cls, fn: str):
        return cls.from_lines(relative_path(__file__, fn))

    @classmethod
    def from_lines(cls, lines: Iterable[str]):

        def instruction_from_line(line: str) -> Instruction:
            op, arg = line.strip().split(" ")
            return op, int(arg)

        return cls(instruction_from_line(line) for line in lines)

    def __len__(self):
        return len(self.instructions)

    def __iter__(self):
        return iter(self.instructions)

    def __getitem__(self, index):
        return self.instructions[index]

    def __str__(self):
        return "".join(f"{op} {arg:+}\n" for op, arg in self)

    @dataclass()
    class State:
        """
        Helper class for reporting and logging the running program states.
        """

        ip_before: int
        ip_after: int
        acc_before: int
        acc_after: int
        instruction: Instruction

        @property
        def instr_op(self) -> str:
            return self.instruction[0]

        @property
        def instr_arg(self) -> int:
            return self.instruction[1]

        def effects_text(self, loop_detected: bool) -> str:
            changes = []
            # collect all changes that happened during evaluation of the current instruction;
            # if loop was just detected, do not report the changes as they are irrelevant
            if not loop_detected:
                if self.ip_before + 1 != self.ip_after:
                    changes.append(f"ip={self.ip_after}")
                if self.acc_before != self.acc_after:
                    changes.append(f"acc={self.acc_after}")

            changes_text = (" -> " + ", ".join(changes)) if changes else ""
            result_text = " (loop!)" if loop_detected else ""
            return changes_text + result_text

        def log(self, debug: bool, tick: int, loop_detected: bool = False):
            if debug:
                print(
                    f"{tick}. {self.instr_op} {self.instr_arg:+} "
                    f"| ip={self.ip_before}{self.effects_text(loop_detected)}"
                )

    def run(self) -> Generator[State, None, int]:
        """
        Runs the program until instruction points points after the last instruction.
        Reports (yields) current state after each instruction is evaluated.
        Returns the final accumulator value upon termination.
        """

        ip, acc = 0, 0
        while True:

            if not 0 <= ip <= len(self):
                # make sure instruction pointer is within bounds of the program
                raise IndexError(f"ip={ip} out of program range (0..{len(self)})")

            if ip == len(self):
                # instruction pointer points right after the last instruction -> program terminates
                return acc

            # evaluate current instruction
            op, arg = self[ip]
            match op:
                case 'acc':
                    acc_new = acc + arg
                    ip_new = ip + 1
                case 'jmp':
                    acc_new = acc
                    ip_new = ip + arg
                case 'nop':
                    acc_new = acc
                    ip_new = ip + 1
                case _:
                    raise ValueError(f"unsupported operaetion {op!r}")

            # report state
            yield self.State(
                ip_before=ip,
                ip_after=ip_new,
                acc_before=acc,
                acc_after=acc_new,
                instruction=(op, arg)
            )

            ip, acc = ip_new, acc_new

    def run_safe(self, *, debug: bool = False) -> tuple[int, bool]:
        """
        Runs the program until loop is detected or program terminates.

        Returns the final accumulator value and a bool value indicating whether the program
        terminated (`True`) or if loop was detected (`False`).

        Optionally prints the evaluated instructions if `debug` is set to `True`.
        """

        visited_ips = set()
        states = self.run()
        tick = 0

        try:
            while True:
                state = next(states)
                tick += 1

                if state.ip_before not in visited_ips:
                    # remember visited instruction pointers
                    state.log(debug, tick)
                    visited_ips.add(state.ip_before)

                else:
                    # if visited for the second time, we detected a loop -> terminate
                    state.log(debug, tick, loop_detected=True)
                    return state.acc_before, False

        except StopIteration as stop:

            # program terminated without encountering a loop
            return stop.value, True

    def flip_instruction(self, instruction_index: int) -> bool:
        """
        Flip instruction (`jmp`->`nop`, `nop`->`jmp`) at given index and returns `True`.

        If the instruction cannot be flipped, no change is made and `False` is returned.
        """
        assert 0 <= instruction_index < len(self)

        flips = {
            'jmp': 'nop',
            'nop': 'jmp'
        }

        # flipping instruction at given index
        op_before, arg = self[instruction_index]
        if op_before in flips:
            op_after = flips[op_before]
            self.instructions[instruction_index] = (op_after, arg)
            return True

        else:
            return False

    def repair(self) -> tuple[int, int]:
        """
        Tries to "repair" to program by finding a single instruction which when flipped
        (`jmp`->`nop` and vice versa) causes the program to terminate.

        Returns final accumulator value of the repaired program and index of the flipped
        instruction.

        This also assumes the program is "broken" in the first place (has endless loop).
        """

        for flip_ip in range(len(self)):
            # duplicate self
            program_adjusted = type(self)(self)
            # adjust one instruction
            flipped = program_adjusted.flip_instruction(flip_ip)
            # and let's see if it had the intended effect
            if flipped:
                final_acc, terminates = program_adjusted.run_safe()
                if terminates:
                    return final_acc, flip_ip

        else:
            raise ValueError("program cannot be repaired")


if __name__ == '__main__':
    program_ = Program.from_file('data/08-input.txt')
    assert len(program_) == 605

    part_1(program_)
    part_2(program_)
