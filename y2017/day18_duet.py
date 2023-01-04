"""
Advent of Code 2017
Day 18: Duet
https://adventofcode.com/2017/day/18
"""

from collections import defaultdict
from typing import Final
from typing import Generator
from typing import Iterable
from typing import Optional

from common.utils import some
from meta.aoc_tools import data_path


def part_1(tape: 'Tape'):
    """
    You discover a tablet containing some strange assembly code labeled simply "Duet". Rather than
    bother the sound card with it, you decide to run the code yourself. Unfortunately, you don't see
    any documentation, so you're left to figure out what the instructions mean on your own.

    It seems like the assembly is meant to operate on a set of **registers** that are each named
    with a single letter and that can each hold a single integer. You suppose each register should
    start with a value of `0`.

    There aren't that many instructions, so it shouldn't be hard to figure out what they do. Here's
    what you determine:

      - `snd X` **plays a sound** with a frequency equal to the value of `X`.
      - `set X Y` **sets** register `X` to the value of `Y`.
      - `add X Y` **increases** register `X` by the value of `Y`.
      - `mul X Y` sets register `X` to the result of **multiplying** the value contained in register
        `X` by the value of `Y`.
      - `mod X Y` sets register `X` to the **remainder** of dividing the value contained in register
        `X` by the value of `Y` (that is, it sets `X` to the result of `X` modulo `Y`).
      - `rcv X` **recovers** the frequency of the last sound played, but only when the value of `X`
        is not zero. (If it is zero, the command does nothing.)
      - `jgz X Y` **jumps** with an offset of the value of `Y`, but only if the value of `X` is
        **greater than zero**. (An offset of `2` skips the next instruction, an offset of `-1` jumps
        to the previous instruction, and so on.)

    Many of the instructions can take either a register (a single letter) or a number. The value of
    a register is the integer it contains; the value of a number is that number.

    After each **jump** instruction, the program continues with the instruction to which the
    **jump** jumped. After any other instruction, the program continues with the next instruction.
    Continuing (or jumping) off either end of the program terminates it.

    For example:

        >>> example = tape_from_text('''
        ...     set a 1
        ...     add a 2
        ...     mul a a
        ...     mod a 5
        ...     snd a
        ...     set a 0
        ...     rcv a
        ...     jgz a -1
        ...     set a 1
        ...     jgz a -2
        ... ''')

      - The first four instructions set `a` to `1`, add `2` to it, square it, and then set it to
        itself modulo `5`, resulting in a value of `4`.

        >>> example[:4]
        [Instr('set', 'a', 1), Instr('add', 'a', 2), Instr('mul', 'a', 'a'), Instr('mod', 'a', 5)]

      - Then, a sound with frequency `4` (the value of `a`) is played.

        >>> example[4]
        Instr('snd', 'a')

      - After that, `a` is set to `0`, causing the subsequent `rcv` and `jgz` instructions to both
        be skipped (`rcv` because `a` is `0`, and `jgz` because `a` is not greater than `0`).

        >>> example[5:8]
        [Instr('set', 'a', 0), Instr('rcv', 'a'), Instr('jgz', 'a', -1)]

      - Finally, `a` is set to `1`, causing the next `jgz` instruction to activate, jumping back two
        instructions to another jump, which jumps again to the `rcv`, which ultimately triggers the
        **recover** operation.

        >>> example[8:]
        [Instr('set', 'a', 1), Instr('jgz', 'a', -2)]
        >>> example[6]
        Instr('rcv', 'a')

    At the time the **recover** operation is executed, the freq. of the last sound played is `4`.

        >>> run_single_program(example)
        4

    **What is the value of the recovered frequency** (the value of the most recently played sound)
    the **first** time a `rcv` instruction is executed with a non-zero value?

        >>> part_1(example)
        part 1: the recovered value is 4
        4
    """

    result = run_single_program(tape)
    print(f"part 1: the recovered value is {result}")
    return result


def part_2(tape: 'Tape'):
    """
    As you congratulate yourself for a job well done, you notice that the documentation has been on
    the back of the tablet this entire time. While you actually got most of the instructions
    correct, there are a few key differences. This assembly code isn't about sound at all - it's
    meant to be run **twice at the same time**.

    Each running copy of the program has its own set of registers and follows the code independently
    - in fact, the programs don't even necessarily run at the same speed. To coordinate, they use
    the **send** (`snd`) and **receive** (`rcv`) instructions:

      - `snd X` **sends** the value of `X` to the other program. These values wait in a queue until
        that program is ready to receive them. Each program has its own message queue, so a program
        can never receive a message it sent.
      - `rcv X` **receives** the next value and stores it in register `X`. If no values are in the
        queue, the program **waits for a value to be sent to it**. Programs do not continue to the
        next instruction until they have received a value. Values are received in the order they are
        sent.

    Each program also has its own **program ID** (one `0` and the other `1`); the register `p`
    should begin with this value.

    For example:

        >>> example = tape_from_text('''
        ...     snd 1
        ...     snd 2
        ...     snd p
        ...     rcv a
        ...     rcv b
        ...     rcv c
        ...     rcv d
        ... ''')

    Both programs begin by sending three values to the other. Program `0` sends `1, 2, 0`;
    program `1` sends `1, 2, 1`. Then, each program receives a value (both `1`) and stores it in
    `a`, receives another value (both `2`) and stores it in `b`, and then each receives the program
    ID of the other program (program `0` receives `1`; program `1` receives `0`) and stores it in
    `c`. Each program now sees a different value in its own copy of register `c`.

    Finally, both programs try to `rcv` a **fourth** time, but no data is waiting for either of
    them, and they reach a **deadlock**. When this happens, both programs terminate.

    It should be noted that it would be equally valid for the programs to run at different speeds;
    for example, program `0` might have sent all three values and then stopped at the first `rcv`
    before program `1` executed even its first instruction.

    Once both of your programs have terminated (regardless of what caused them to do so), **how many
    times did program `1` send a value**?

        >>> part_2(example)
        part 2: before deadlock, program 1 sent a value 3 times
        3
    """
    _, sent_1 = run_dual_program(tape)
    print(f"part 2: before deadlock, program 1 sent a value {sent_1} times")
    return sent_1


class Instr:

    __match_args__: Final[tuple] = ('command', 'arg_1', 'arg_2')

    def __init__(self, command: str, arg_1: str | int, arg_2: str | int | None = None):
        self.command = command
        self.arg_1 = arg_1
        self.arg_2 = arg_2

    def __repr__(self) -> str:
        arg_2_repr = f', {self.arg_2!r}' if self.arg_2 is not None else ''
        return f'{type(self).__name__}({self.command!r}, {self.arg_1!r}{arg_2_repr})'

    @classmethod
    def from_str(cls, line: str):

        def parse_arg(str_val: str) -> str | int:
            try:
                return int(str_val)
            except ValueError:
                return str_val

        command, *args = line.split()
        return Instr(command, *(parse_arg(arg) for arg in args))


Tape = list[Instr]


def run_program(program_id: int, tape: Tape) -> Generator[Optional[int], Optional[int], None]:
    regs = defaultdict(int)
    regs['p'] = program_id

    head = 0

    def val(value) -> int:
        return value if isinstance(value, int) else regs[value]

    def assert_is_register(value) -> None:
        assert isinstance(value, str), f"{value!r} is not a register value"

    while True:
        instr = tape[head]
        head += 1

        match instr:
            # sound (aka send) [reg/val]
            case Instr('snd', source, None):
                yield val(source)

            # recover (aka receive) to [reg]
            case Instr('rcv', reg, None):
                assert_is_register(reg)
                # signal receiving
                received = yield None
                # make sure something was actually received
                assert received is not None
                # store the received value
                regs[reg] = received

            # set [reg] to [reg/val]
            case Instr('set', target, source):
                assert_is_register(target)
                regs[target] = val(source)

            # increase [reg] with [reg/val]
            case Instr('add', target, source):
                assert_is_register(target)
                regs[target] += val(source)

            # multiply [reg] with [reg/val]
            case Instr('mul', target, source):
                assert_is_register(target)
                regs[target] *= val(source)

            # update [reg] with modulo of itself with [reg/val]
            case Instr('mod', target, source):
                assert_is_register(target)
                regs[target] %= val(source)

            # jump if [reg/val] > 0 by [reg/val]
            case Instr('jgz', control, offset):
                if val(control) > 0:
                    jump = val(offset)
                    assert jump != 0  # endless loop
                    assert jump != 1  # no effect
                    head += jump - 1

            case _:
                raise ValueError(instr)


def run_single_program(tape: Tape) -> int:
    # pylint: disable=assignment-from-no-return
    program = run_program(0, tape)

    sent_value = None
    while True:
        signal = next(program)
        if signal is not None:
            # program sent something using `snd` -> remember it
            sent_value = signal
        else:
            # program triggered `rcv` -> return the last sent value
            return some(sent_value, "no previously sent value")


def run_dual_program(tape: Tape) -> tuple[int, int]:
    # pylint: disable=assignment-from-no-return
    program_0 = run_program(0, tape)
    program_1 = run_program(1, tape)

    # next(program) = run program until it sends a value (`snd`)
    #                 or asks for one (`rcv`) by yielding signal:
    #
    #               - signal is integer = value sent
    #               - signal is None    = asking for a value to be received

    sig_0, sig_1 = next(program_0), next(program_1)
    # message queue for values sent by program 0
    # (program 1 doesn't need a message queue, see below)
    queue_0_to_1 = []
    # tally marks for number of of times a program sent something
    send_tally_0, send_tally_1 = 0, 0

    while True:
        if sig_0 is not None:
            # program 0 sending -> buffer in queue_0
            queue_0_to_1.append(sig_0)
            # => continue program 0
            sig_0 = next(program_0)
            # (tally the value sent by program 0)
            send_tally_0 += 1

        elif sig_1 is not None:
            # program 1 is sending and program 0 is receiving
            # => send p1 -> p0 directly and continue program 0
            sig_0 = program_0.send(sig_1)
            # => also continue program 1
            sig_1 = next(program_1)
            # (tally the value sent by program 1)
            send_tally_1 += 1

        elif queue_0_to_1:
            # both programs are receiving and there's something in the queue
            # => send p0 -> p1 using the queue and continue program 1
            sig_1 = program_1.send(queue_0_to_1.pop(0))

        else:
            # both programs are receiving and the queue is empty -> deadlock
            # => we are done, return the tallies
            return send_tally_0, send_tally_1


def tape_from_text(text: str) -> Tape:
    return list(instructions_from_lines(text.strip().splitlines()))


def tape_from_file(fn: str) -> Tape:
    return list(instructions_from_lines(open(fn)))


def instructions_from_lines(lines: Iterable[str]) -> Iterable[Instr]:
    return (Instr.from_str(line.strip()) for line in lines)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    tape = tape_from_file(input_path)
    result_1 = part_1(tape)
    result_2 = part_2(tape)
    return result_1, result_2


if __name__ == '__main__':
    main()
