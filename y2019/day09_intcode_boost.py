"""
Advent of Code 2019
Day 9: Sensor Boost
https://adventofcode.com/2019/day/9
"""

from meta.aoc_tools import data_path
from y2019.intcode import load_tape, Machine, Tape


def part_1(tape: Tape) -> int:
    """
    You've just said goodbye to the rebooted rover and left Mars when you receive a faint distress
    signal coming from the asteroid belt. It must be the Ceres monitoring station!

    In order to lock on to the signal, you'll need to boost your sensors. The Elves send up the
    latest **BOOST** program - Basic Operation Of System Test.

    While BOOST (your puzzle input) is capable of boosting your sensors, for tenuous safety reasons,
    it refuses to do so until the computer it runs on passes some checks to demonstrate it is
    a **complete Intcode computer**.

    Your existing Intcode computer is missing one key feature: it needs support for parameters in
    **relative mode**.

    Parameters in mode `2`, **relative mode**, behave very similarly to parameters in **position
    mode**: the parameter is interpreted as a position. Like position mode, parameters in relative
    mode can be read from or written to.

    The important difference is that relative mode parameters don't count from address `0`. Instead,
    they count from a value called the **relative base**. The **relative base** starts at `0`.

    The address a relative mode parameter refers to is itself **plus** the current **relative
    base**. When the relative base is `0`, relative mode parameters and position mode parameters
    with the same value refer to the same address.

    For example, given a relative base of `50`, a relative mode parameter of `-7` refers to memory
    address `50 + -7 = 43`.

    The relative base is modified with the **relative base offset** instruction:

      - Opcode `9` **adjusts the relative base** by the value of its only parameter. The relative
        base increases (or decreases, if the value is negative) by the value of the parameter.

    For example, if the relative base is `2000`, then after the instruction `109,19`, the relative
    base would be `2019`. If the next instruction were `204,-34`, then the value at address 1985
    would be output.

    Your Intcode computer will also need a few other capabilities:

      - The computer's available memory should be much larger than the initial program. Memory
        beyond the initial program starts with the value `0` and can be read or written like any
        other memory. (It is invalid to try to access memory at a negative address, though.)
      - The computer should have support for large numbers. Some instructions near the beginning of
        the BOOST program will verify this capability.

    Here are some example programs that use these features:

        >>> quine_tape = [109, 1, 204, -1, 1001, 100, 1, 100, 1008, 100, 16, 101, 1006, 101, 0, 99]
        >>> list(Machine(quine_tape).run_output_only()) == quine_tape
        True
        >>> Machine([1102, 34915192, 34915192, 7, 4, 7, 99, 0]).as_function_scalar()()
        1219070632396864
        >>> Machine([104, 1125899906842624, 99]).as_function_scalar()()
        1125899906842624

    The BOOST program will ask for a single input; run it in test mode by providing it the value
    `1`. It will perform a series of checks on each opcode, output any opcodes (and the associated
    parameter modes) that seem to be functioning incorrectly, and finally output a BOOST keycode.

    Once your Intcode computer is fully functional, the BOOST program should report no
    malfunctioning opcodes when run in test mode; it should only output a single value, the BOOST
    keycode. **What BOOST keycode does it produce?**

        >>> part_1([3, 1, 1002, 1, 123456789, 1, 4, 1, 99])
        part 1: BOOST keycode is 123456789
        123456789
    """

    result = Machine(tape, name="BOOST").as_function_scalar()(1)

    print(f"part 1: BOOST keycode is {result}")
    return result


def part_2(tape: Tape) -> int:
    """
    **You now have a complete Intcode computer.**

    Finally, you can lock on to the Ceres distress signal! You just need to boost your sensors using
    the BOOST program.

    The program runs in sensor boost mode by providing the input instruction the value `2`. Once
    run, it will boost the sensors automatically, but it might take a few seconds to complete the
    operation on slower hardware. In sensor boost mode, the program will output a single value:
    **the coordinates of the distress signal**.

    Run the BOOST program in sensor boost mode. **What are the coordinates of the distress signal?**

        >>> part_2([3, 1, 1002, 1, 123456789, 1, 4, 1, 99])
        part 2: distress signal coordinates are 246913578
        246913578
    """

    result = Machine(tape, name="BOOST", progress=True).as_function_scalar()(2)

    print(f"part 2: distress signal coordinates are {result}")
    return result


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    tape = load_tape(input_path)
    result_1 = part_1(tape)
    result_2 = part_2(tape)
    return result_1, result_2


if __name__ == '__main__':
    main()
