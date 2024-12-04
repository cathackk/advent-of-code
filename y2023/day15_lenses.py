"""
Advent of Code 2023
Day 15: Lens Library
https://adventofcode.com/2023/day/15
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Iterable, Self

from common.file import relative_path
from common.iteration import maybe_next
from common.utils import some


def part_1(steps: Iterable['Step']) -> int:
    """
    The newly-focused parabolic reflector dish is sending all of the collected light to a point on
    the side of yet another mountain - the largest mountain on Lava Island. As you approach
    the mountain, you find that the light is being collected by the wall of a large facility
    embedded in the mountainside.

    You find a door under a large sign that says "Lava Production Facility" and next to a smaller
    sign that says "Danger - Personal Protective Equipment required beyond this point".

    As you step inside, you are immediately greeted by a somewhat panicked reindeer wearing goggles
    and a loose-fitting hard hat. The reindeer leads you to a shelf of goggles and hard hats
    (you quickly find some that fit) and then further into the facility. At one point, you pass
    a button with a faint snout mark and the label "PUSH FOR HELP". No wonder you were loaded into
    that trebuchet so quickly!

    You pass through a final set of doors surrounded with even more warning signs and into what must
    be the room that collects all of the light from outside. As you admire the large assortment of
    lenses available to further focus the light, the reindeer brings you a book titled
    "Initialization Manual".

    "Hello!", the book cheerfully begins, apparently unaware of the concerned reindeer reading over
    your shoulder. "This procedure will let you bring the Lava Production Facility online - all
    without burning or melting anything unintended!"

    "Before you begin, please be prepared to use the Holiday ASCII String Helper algorithm
    (appendix 1A)." You turn to appendix 1A. The reindeer leans closer with interest.

    The HASH algorithm is a way to turn any string of characters into a single **number** in
    the range 0 to 255. To run the HASH algorithm on a string, start with a **current value** of 0.
    Then, for each character in the string starting from the beginning:

      - Determine the ASCII code for the current character of the string.
      - Increase the **current value** by the ASCII code you just determined.
      - Set the **current value** to itself multiplied by `17`.
      - Set the **current value** to the remainder of dividing itself by `256`.

    After following these steps for each character in the string in order, the **current value** is
    the output of the HASH algorithm.

    So, to find the result of running the HASH algorithm on the string `HASH`:

      - The **current value** starts at `0`.
      - The first character is `H`; its ASCII code is:

        >>> ord('H')
        72

      - The **current value** increases to `72`.
      - The **current value** is multiplied by `17` to become `1224`.
      - The **current value** becomes:

        >>> (72 * 17) % 256
        200

      - The next character is `A`; its ASCII code is:

        >>> ord('A')
        65

      - The **current value** increases to `265`.
      - The **current value** is multiplied by `17` to become `4505`.
      - The **current value** becomes:

        >>> ((200 + 65) * 17) % 256
        153

      - The next character is `S`:

        >>> ord('S')
        83

      - The **current value** increases to `236`.
      - The **current value** is multiplied by `17` to become `4012`.
      - The **current value** becomes:

        >>> ((153 + 83) * 17) % 256
        172

      - The next character is `H`; its ASCII code is `72`.
      - The **current value** increases to `244`.
      - The **current value** is multiplied by `17` to become `4148`.
      - The **current value** becomes:

        >>> ((172 + 72) * 17) % 256
        52

    So, the result of running the HASH algorithm on the string `HASH` is **`52`**:

        >>> hash_alg('HASH')
        52

    The **initialization sequence** (your puzzle input) is a comma-separated list of steps to start
    the Lava Production Facility. Ignore newline characters when parsing the initialization
    sequence. To verify that your HASH algorithm is working, the book offers the sum of the result
    of running the HASH algorithm on each step in the initialization sequence.

    For example:

        >>> example = Step.from_text('rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7')
        >>> example  # doctest: +NORMALIZE_WHITESPACE
        [Step('rn', '=', 1), Step('cm', '-'), Step('qp', '=', 3), Step('cm', '=', 2),
         Step('qp', '-'), Step('pc', '=', 4), Step('ot', '=', 9), Step('ab', '=', 5),
         Step('pc', '-'), Step('pc', '=', 6), Step('ot', '=', 7)]
        >>> [str(step) for step in example]
        ['rn=1', 'cm-', 'qp=3', 'cm=2', 'qp-', 'pc=4', 'ot=9', 'ab=5', 'pc-', 'pc=6', 'ot=7']

    This initialization sequence specifies 11 individual steps; the result of running the HASH
    algorithm on each of the steps is as follows:

        >>> [hash(step) for step in example]
        [30, 253, 97, 47, 14, 180, 9, 197, 48, 214, 231]
        >>> sum(_)
        1320

    Unfortunately, the reindeer has stolen the page containing the expected verification number and
    is currently running around the facility with it excitedly.

    Run the HASH algorithm on each step in the initialization sequence.
    **What is the sum of the results?**

        >>> part_1(example)
        part 1: sum of HASH results is 1320
        1320
    """

    result = sum(hash(step) for step in steps)

    print(f"part 1: sum of HASH results is {result}")
    return result


def part_2(steps: Iterable['Step']) -> int:
    """
    You convince the reindeer to bring you the page; the page confirms that your HASH algorithm is
    working.

    The book goes on to describe a series of 256 **boxes** numbered `0` through `255`. The boxes are
    arranged in a line starting from the point where light enters the facility. The boxes have holes
    that allow light to pass from one box to the next all the way down the line:

                 +-----+  +-----+         +-----+
                 | box |  | box |   ...   | box |
        light -------------------------------------->
                 |  0  |  |  1  |   ...   | 255 |
                 +-----+  +-----+         +-----+

    Inside each box, there are several **lens slots** that will keep a lens correctly positioned to
    focus light passing through the box. The side of each box has a panel that opens to allow you to
    insert or remove lenses as necessary.

    Along the wall running parallel to the boxes is a large library containing lenses organized by
    **focal length** ranging from `1` through `9`. The reindeer also brings you a small handheld
    label printer.

    The book goes on to explain how to perform each step in the initialization sequence, a process
    it calls the Holiday ASCII String Helper Manual Arrangement Procedure, or **HASHMAP** for short.

    Each step begins with a sequence of letters that indicate the **label** of the lens on which
    the step operates. The result of running the HASH algorithm on the label indicates the correct
    box for that step.

    The label will be immediately followed by a character that indicates the **operation** to
    perform: either an equals sign (`=`) or a dash (`-`).

    If the operation character is a **dash** (`-`), go to the relevant box and remove the lens with
    the given label if it is present in the box. Then, move any remaining lenses as far forward in
    the box as they can go without changing their order, filling any space made by removing the
    indicated lens. (If no lens in that box has the given label, nothing happens.)

    If the operation character is an **equals sign** (`=`), it will be followed by a number
    indicating the **focal length** of the lens that needs to go into the relevant box; be sure to
    use the label maker to mark the lens with the label given in the beginning of the step so you
    can find it later. There are two possible situations:

      - If there is already a lens in the box with the same label, **replace the old lens** with
        the new lens: remove the old lens and put the new lens in its place, not moving any other
        lenses in the box.
      - If there is **not** already a lens in the box with the same label, add the lens to the box
        immediately behind any lenses already in the box. Don't move any of the other lenses when
        you do this. If there aren't any lenses in the box, the new lens goes all the way to the
        front of the box.

    Here is the contents of every box after each step in the example initialization sequence above:

        >>> example = Step.from_file('data/15-example.txt')
        >>> example_result = run(example, log=True)
        After "rn=1":
          Box 0: [rn 1]
        After "cm-":
          Box 0: [rn 1]
        After "qp=3":
          Box 0: [rn 1]
          Box 1: [qp 3]
        After "cm=2":
          Box 0: [rn 1] [cm 2]
          Box 1: [qp 3]
        After "qp-":
          Box 0: [rn 1] [cm 2]
        After "pc=4":
          Box 0: [rn 1] [cm 2]
          Box 3: [pc 4]
        After "ot=9":
          Box 0: [rn 1] [cm 2]
          Box 3: [pc 4] [ot 9]
        After "ab=5":
          Box 0: [rn 1] [cm 2]
          Box 3: [pc 4] [ot 9] [ab 5]
        After "pc-":
          Box 0: [rn 1] [cm 2]
          Box 3: [ot 9] [ab 5]
        After "pc=6":
          Box 0: [rn 1] [cm 2]
          Box 3: [ot 9] [ab 5] [pc 6]
        After "ot=7":
          Box 0: [rn 1] [cm 2]
          Box 3: [ot 7] [ab 5] [pc 6]
        >>> example_result
        {0: [('rn', 1), ('cm', 2)], 3: [('ot', 7), ('ab', 5), ('pc', 6)]}

    All 256 boxes are always present; only the boxes that contain any lenses are shown here.
    Within each box, lenses are listed from front to back; each lens is shown as its label and focal
    length in square brackets.

    To confirm that all of the lenses are installed correctly, add up the **focusing power** of all
    of the lenses. The focusing power of a single lens is the result of multiplying together:

      - One plus the box number of the lens in question.
      - The slot number of the lens within the box: `1` for the first lens, `2` for the second lens,
        and so on.
      - The focal length of the lens.

    At the end of the above example, the focusing power of each lens is as follows:

        >>> {
        ...     label: focusing_power(box_num, slot, fl)
        ...     for box_num, lenses in example_result.items()
        ...     for slot, (label, fl) in enumerate(lenses)
        ... }
        {'rn': 1, 'cm': 4, 'ot': 28, 'ab': 40, 'pc': 72}

    So, the above example ends up with a total focusing power of:

        >>> sum(_.values())
        145

    With the help of an over-enthusiastic reindeer in a hard hat, follow the initialization
    sequence. **What is the focusing power of the resulting lens configuration?**

        >>> part_2(example)
        part 2: total focusing power of resulting lens configuration is 145
        145
    """

    result = sum(
        focusing_power(box_num, slot, value)
        for box_num, box in run(steps).items()
        for slot, (label, value) in enumerate(box)
    )

    print(f"part 2: total focusing power of resulting lens configuration is {result}")
    return result


def hash_alg(obj: Any) -> int:
    val = 0
    for char in str(obj):
        val = ((val + ord(char)) * 17) % 256
    return val


Lens = tuple[str, int]


@dataclass(frozen=True)
class Step:
    label: str
    op: str
    value: int | None = None

    @property
    def box_number(self) -> int:
        return hash_alg(self.label)

    def lens(self) -> Lens:
        return self.label, some(self.value)

    def __str__(self) -> str:
        return f'{self.label}{self.op}{self.value or ""}'

    def __repr__(self) -> str:
        value_repr = f', {self.value!r}' if self.value is not None else ''
        return f'{type(self).__name__}({self.label!r}, {self.op!r}{value_repr})'

    def __hash__(self) -> int:
        return hash_alg(self)

    @classmethod
    def from_file(cls, fn: str) -> list[Self]:
        return list(cls.from_lines(open(relative_path(__file__, fn))))

    @classmethod
    def from_text(cls, text: str) -> list[Self]:
        return list(cls.from_lines(text.strip().splitlines()))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Iterable[Self]:
        return (
            cls.from_str(step)
            for line in lines
            for step in line.strip().split(',')
        )

    @classmethod
    def from_str(cls, string: str) -> Self:
        if string.endswith('-'):
            return cls(string[:-1], '-')
        elif '=' in string:
            label, value = string.split('=')
            return cls(label, '=', int(value))
        else:
            raise ValueError(string)


LensConfiguration = dict[int, list[Lens]]


def run(steps: Iterable[Step], log: bool = False) -> LensConfiguration:
    boxes: LensConfiguration = defaultdict(list)

    for step in steps:
        box = boxes[step.box_number]
        existing_index = maybe_next(
            index
            for index, (label, _) in enumerate(box)
            if label == step.label
        )

        match step.op:
            case '-':
                if existing_index is not None:
                    del box[existing_index]

            case '=':
                if existing_index is not None:
                    box[existing_index] = step.lens()
                else:
                    box.append(step.lens())

            case _ as not_supported:
                raise ValueError(not_supported)

        if log:
            print(f'After "{step}":')
            for box_num, box in sorted(boxes.items()):
                if not box:
                    continue
                print(f"  Box {box_num}:", " ".join(f"[{label} {val}]" for label, val in box))

    return {box_num: box for box_num, box in boxes.items() if box}


def focusing_power(box_num: int, slot: int, value: int) -> int:
    return (box_num + 1) * (slot + 1) * value


def main(input_fn: str = 'data/15-input.txt') -> tuple[int, int]:
    steps = Step.from_file(input_fn)
    result_1 = part_1(steps)
    result_2 = part_2(steps)
    return result_1, result_2


if __name__ == '__main__':
    main()
