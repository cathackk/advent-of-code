"""
Advent of Code 2020
Day 14: Docking Data
https://adventofcode.com/2020/day/14
"""

from typing import Iterable
from typing import Optional

from common.utils import parse_line


def part_1(program: 'Program') -> int:
    """
    The initialization program (your puzzle input) can either update the bitmask or write a value
    to memory. Values and memory addresses are both 36-bit unsigned integers. For example, ignoring
    bitmasks for a moment, a line like `mem[8] = 11` would write the value 11 to memory address 8.

    The bitmask is always given as a string of 36 bits, written with the most significant bit
    (representing 2^35) on the left and the least significant bit (2^0, that is, the 1s bit) on the
    right. The current bitmask is applied to values immediately before they are written to memory:
    a 0 or 1 overwrites the corresponding bit in the value, while an X leaves the bit in the value
    unchanged.

    For example, consider the following program:

        >>> prog = Program.from_text('''
        ...
        ...     mask = XXXXXXXXXXXXXXXXXXXXXXXXXXXXX1XXXX0X
        ...     mem[8] = 11
        ...     mem[7] = 101
        ...     mem[8] = 0
        ...
        ... ''')
        >>> len(prog)
        4

    This program starts by specifying a bitmask. The mask it specifies will overwrite two bits in
    every written value: the 2s bit is overwritten with 0, and the 64s bit is overwritten with 1.

        >>> prog[0]
        ('mask', BitMask('XXXXXXXXXXXXXXXXXXXXXXXXXXXXX1XXXX0X'))
        >>> mask = prog[0][1]

    The program then attempts to write the value `11` to memory address 8.

        >>> prog[1]
        ('mem', 8, 11)
        >>> mask.apply(11)
        73

    So, because of the mask, the value `73` is written to memory address 8 instead.

    Then, the program tries to write `101` to address 7:

        >>> prog[2]
        ('mem', 7, 101)
        >>> mask.apply(101)
        101

    This time, the mask has no effect, as the bits it overwrote were already the values the mask
    tried to set.

    Finally, the program tries to write 0 to address 8:

        >>> prog[3]
        ('mem', 8, 0)
        >>> mask.apply(0)
        64

    `64` is written to address 8 instead, overwriting the value that was there previously.

    To initialize your ferry's docking program, you need the sum of all values left in memory after
    the initialization program completes. (The entire 36-bit address space begins initialized to
    the value 0 at every address.) In the above example, only two values in memory are not zero:

        >>> prog.run()
        {8: 64, 7: 101}
        >>> sum(_.values())
        165

    Execute the initialization program. *What is the sum of all values left in memory after it
    completes?*

        >>> part_1(prog)
        part 1: after running the program, memory sum is 165
        165
    """

    memory = program.run()
    result = sum(memory.values())

    print(f"part 1: after running the program, memory sum is {result}")
    return result


def part_2(program: 'Program') -> int:
    """
    A version 2 decoder chip doesn't modify the values being written at all. Instead, it acts as a
    memory address decoder. Immediately before a val is written to memory, each bit in the bitmask
    modifies the corresponding bit of the destination *memory address* in the following way:

        - If the bitmask bit is `0`, the corresponding memory address bit is *unchanged*.
        - If the bitmask bit is `1`, the corresponding memory address bit is *overwritten with `1`*
        - If the bitmask bit is `X`, the corresponding memory address bit is *floating*.

    A *floating* bit is not connected to anything and instead fluctuates unpredictably. In
    practice, this means the floating bits will take on *all possible values*, potentially causing
    many memory addresses to be written all at once!

    For example, consider the following program:

        >>> prog = Program.from_text('''
        ...
        ...     mask = 000000000000000000000000000000X1001X
        ...     mem[42] = 100
        ...     mask = 00000000000000000000000000000000X0XX
        ...     mem[26] = 1
        ...
        ... ''')
        >>> len(prog)
        4

    When this program goes to write to memory address 42, it first applies the bitmask:

        >>> prog[0]
        ('mask', BitMask('000000000000000000000000000000X1001X'))
        >>> mask_1 = prog[0][1]
        >>> prog[1]
        ('mem', 42, 100)

        ```
        address: 000000000000000000000000000000101010  (decimal 42)
        mask:    000000000000000000000000000000X1001X
        result:  000000000000000000000000000000X1101X
        ```

    After applying the mask, four bits are overwritten, three of which are different, and two of
    which are *floating*. Floating bits take on every possible combination of values; with two
    floating bits, four actual memory addresses are written:

        ```
        000000000000000000000000000000011010  (decimal 26)
        000000000000000000000000000000011011  (decimal 27)
        000000000000000000000000000000111010  (decimal 58)
        000000000000000000000000000000111011  (decimal 59)
        ```

        >>> list(mask_1.apply_floating(42))
        [26, 27, 58, 59]

    Next, the program is about to write to memory address 26 with a different bitmask. This results
    in an address with three floating bits, causing writes to eight memory addresses:

        >>> prog[2]
        ('mask', BitMask('00000000000000000000000000000000X0XX'))
        >>> mask_2 = prog[2][1]
        >>> prog[3]
        ('mem', 26, 1)
        >>> list(mask_2.apply_floating(26))
        [16, 17, 18, 19, 24, 25, 26, 27]

    The entire 36-bit address space still begins initialized to the value 0 at every address, and
    you still need the sum of all values left in memory at the end of the program. In this example,
    the sum is *`208`*.

        >>> prog.run(chip_version=2)
        {26: 1, 27: 1, 58: 100, 59: 100, 16: 1, 17: 1, 18: 1, 19: 1, 24: 1, 25: 1}
        >>> sum(_.values())
        208

    Execute the initialization program using an emulator for a version 2 decoder chip.
    *What is the sum of all values left in memory after it completes?*

        >>> part_2(prog)
        part 2: after running the program on chip v2, memory sum is 208
        208
    """

    memory = program.run(chip_version=2)
    result = sum(memory.values())

    print(f"part 2: after running the program on chip v2, memory sum is {result}")
    return result


class BitMask:
    def __init__(self, mask_string: str):
        self.mask_string = mask_string

    def __len__(self):
        return len(self.mask_string)

    def __repr__(self):
        return f'{type(self).__name__}({self.mask_string!r})'

    def apply(self, value: int) -> int:
        mask_and = int(''.join('0' if bit == '0' else '1' for bit in self.mask_string), 2)
        mask_or = int(''.join('1' if bit == '1' else '0' for bit in self.mask_string), 2)
        return value & mask_and | mask_or

    def apply_floating(self, value: int) -> Iterable[int]:
        # "fbit" = floating bit = bit in mask marked `X` which can have both balues
        fbits_at = [index for index, bit in enumerate(self.mask_string) if bit == 'X']

        # This algorithm yields (2 ** F) values, where F is the number of floating bits:
        possible_values_count = 2 ** len(fbits_at)

        # For each such value, we'll first create a "submask", a helper bitmask, which will then be
        # applied to the `value` in "normal" way. The submask is created using this key:
        #     0 -> X
        #     1 -> 1
        #     X -> 0/1
        #
        # ... where `0/1` marks the floating bit and `X` means "no change" (as in `apply()`)
        #
        #     X01X -> 0X10, 0X11, 1X10, 1X11
        submask_template = [
            {
                '0': 'X',
                '1': '1',
                'X': None
            }[bit]
            for bit in self.mask_string
        ]

        # Let's generate each possible combination of values for floating bits:
        for value_index in range(possible_values_count):

            # Adjust the submask template by writing fixed values into floating bit positions:
            for fbit_index, fbit_at in enumerate(reversed(fbits_at)):
                submask_template[fbit_at] = '1' if value_index & (1 << fbit_index) else '0'

            # Create current submask out of the template and apply it to the bvalue:
            submask = BitMask(''.join(submask_template))
            yield submask.apply(value)


Instruction = tuple[str, BitMask] | tuple[str, int, int]


class Program:
    def __init__(self, instructions: Iterable[Instruction]):
        self.instructions = list(instructions)

    @classmethod
    def from_text(cls, text: str):
        return cls.from_lines(text.strip().split("\n"))

    @classmethod
    def from_file(cls, fn: str):
        return cls.from_lines(open(fn))

    @classmethod
    def from_lines(cls, lines: Iterable[str]):
        def instructions_from_lines():
            for line in lines:
                line = line.strip()
                if line.startswith('mask'):
                    (mask_string,) = parse_line(line, 'mask = $')
                    yield 'mask', BitMask(mask_string)
                elif line.startswith('mem'):
                    address, value = parse_line(line, 'mem[$] = $')
                    yield 'mem', int(address), int(value)
                else:
                    raise ValueError(line)

        return cls(instructions_from_lines())

    def __len__(self):
        return len(self.instructions)

    def __iter__(self):
        return iter(self.instructions)

    def __getitem__(self, index):
        return self.instructions[index]

    def run(self, chip_version: int = 1) -> dict[int, int]:
        assert chip_version in (1, 2)

        current_mask: Optional[BitMask] = None
        memory: dict[int, int] = dict()

        for instruction in self:
            match instruction:
                case 'mask', mask:
                    current_mask = mask
                case 'mem', base_address, value:
                    assert current_mask, "mask not initialized"
                    if chip_version == 1:
                        memory[base_address] = current_mask.apply(value)
                    else:
                        for address in current_mask.apply_floating(base_address):
                            memory[address] = value
                case _:
                    raise ValueError(f"unsupported instruction {instruction}")

        return memory


if __name__ == '__main__':
    program_ = Program.from_file('data/14-input.txt')
    assert len(program_) == 545

    part_1(program_)
    part_2(program_)
