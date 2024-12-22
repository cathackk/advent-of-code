"""
Advent of Code 2024
Day 21: Keypad Conundrum
https://adventofcode.com/2024/day/21
"""

from functools import lru_cache
from typing import Iterable, Self

from common.canvas import Canvas
from common.file import relative_path
from common.heading import Heading
from common.iteration import zip1


def part_1(codes: Iterable[str]) -> int:
    """
    As you teleport onto Santa's Reindeer-class starship (y2024/day25_adventure.py), The Historians
    begin to panic: someone from their search party is **missing**. A quick life-form scan by the
    ship's computer reveals that when the missing Historian teleported, he arrived in another part
    of the ship.

    The door to that area is locked, but the computer can't open it; it can only be opened by
    **physically typing** the door codes (your puzzle input) on the numeric keypad on the door.

    The numeric keypad has four rows of buttons: `789`, `456`, `123`, and finally an empty gap
    followed by `0A`. Visually, they are arranged like this:

        >>> print(KEYPAD_NUMERIC)
        +---+---+---+
        | 7 | 8 | 9 |
        +---+---+---+
        | 4 | 5 | 6 |
        +---+---+---+
        | 1 | 2 | 3 |
        +---+---+---+
            | 0 | A |
            +---+---+
        >>> len(KEYPAD_NUMERIC)
        11
        >>> KEYPAD_NUMERIC.button_at((1, 2))
        '2'
        >>> KEYPAD_NUMERIC.button_pos('A')
        (2, 3)

    Unfortunately, the area outside the door is currently **depressurized** and nobody can go near
    the door. A robot needs to be sent instead.

    The robot has no problem navigating the ship and finding the numeric keypad, but it's not
    designed for button pushing: it can't be told to push a specific button directly. Instead,
    it has a robotic arm that can be controlled remotely via a **directional keypad**.

    The directional keypad has two rows of buttons: a gap / `^` (up) / `A` (activate) on the first
    row and `<` (left) / `v` (down) / `>` (right) on the second row. Visually, they are arranged
    like this:

        >>> print(KEYPAD_DIRECTIONAL)
            +---+---+
            | ^ | A |
        +---+---+---+
        | < | v | > |
        +---+---+---+
        >>> len(KEYPAD_DIRECTIONAL)
        5
        >>> KEYPAD_DIRECTIONAL.button_at((0, 1))
        '<'
        >>> KEYPAD_DIRECTIONAL.button_pos('A')
        (2, 0)

    When the robot arrives at the numeric keypad, its robotic arm is pointed at the `A` button in
    the bottom right corner. After that, this directional keypad remote control must be used to
    maneuver the robotic arm: the up / down / left / right buttons cause it to move its arm one
    button in that direction, and the `A` button causes the robot to briefly move forward, pressing
    the button being aimed at by the robotic arm.

    For example, to make the robot type `029A` on the numeric keypad, one sequence of inputs on
    the directional keypad you could use is:

      - `<` to move the arm from `A` (its initial position) to `0`.
      - `A` to push the `0` button.
      - `^`A to move the arm to the `2` button and push it.
      - `>^^`A to move the arm to the `9` button and push it.
      - `vvvA` to move the arm to the `A` button and push it.

    In total, there are three shortest possible sequences of button presses on this directional
    keypad that would cause the robot to type `029A`:

        >>> evaluate('<A^A>^^AvvvA', level=1)
        '029A'
        >>> evaluate('<A^A^>^AvvvA', level=1)
        '029A'
        >>> evaluate('<A^A^^>AvvvA', level=1)
        '029A'

    Unfortunately, the area containing this directional keypad remote control is currently
    experiencing **high levels of radiation** and nobody can go near it. A robot needs to be sent
    instead.

    When the robot arrives at the directional keypad, its robot arm is pointed at the `A` button in
    the upper right corner. After that, a **second, different** directional keypad remote control is
    used to control this robot (in the same way as the first robot, except that this one is typing
    on a directional keypad instead of a numeric keypad).

    There are multiple shortest possible sequences of directional keypad button presses that would
    cause this robot to tell the first robot to type `029A` on the door. One such sequence is:

        >>> evaluate('v<<A>>^A<A>AvA<^AA>A<vAAA>^A', level=2)
        '029A'

    Unfortunately, the area containing this second directional keypad remote control is currently
    **-40 degrees**! Another robot will need to be sent to type on that directional keypad, too.

    There are many shortest possible sequences of directional keypad button presses that would cause
    this robot to tell the second robot to tell the first robot to eventually type `029A` on
    the door. One such sequence is

        >>> seq_3 = '<vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A'
        >>> evaluate(seq_3, level=3)
        '029A'

    Unfortunately, the area containing this third directional keypad remote control is currently
    **full of Historians**, so no robots can find a clear path there. Instead, **you** will have to
    type this sequence yourself.

    Were you to choose this sequence of button presses, here are all of the buttons that would be
    pressed on your directional keypad, the two robots' directional keypads, and the numeric keypad:

        >>> evaluate(seq_3, level=3, print_intermediate=True)
        <vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A
        v<<A>>^A<A>AvA<^AA>A<vAAA>^A
        <A^A>^^AvvvA
        029A
        '029A'

    In summary, there are the following keypads:

      - One directional keypad that **you** are using.
      - Two directional keypads that **robots** are using.
      - One numeric keypad (on a door) that a **robot** is using.

    It is important to remember that these robots are not designed for button pushing.
    In particular, if a robot arm is ever aimed at a **gap** where no button is present on
    the keypad, even for an instant, the robot will panic unrecoverably. So, don't do that.
    All robots will initially aim at the keypad's `A` key, wherever it is.

    To unlock the door, **five** codes will need to be typed on its numeric keypad. For example:

        >>> example_codes = codes_from_text('''
        ...     029A
        ...     980A
        ...     179A
        ...     456A
        ...     379A
        ... ''')
        >>> example_codes
        ['029A', '980A', '179A', '456A', '379A']

    For each of these, here is a shortest sequence of button presses you could type to cause
    the desired code to be typed on the numeric keypad:

        >>> evaluate('<vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A', 3)
        '029A'
        >>> evaluate('<v<A>>^AAAvA^A<vA<AA>>^AvAA<^A>A<v<A>A>^AAAvA<^A>A<vA>^A<A>A', level=3)
        '980A'
        >>> evaluate('<v<A>>^A<vA<A>>^AAvAA<^A>A<v<A>>^AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A', 3)
        '179A'
        >>> evaluate('<v<A>>^AA<vA<A>>^AAvAA<^A>A<vA>^A<A>A<vA>^A<A>A<v<A>A>^AAvA<^A>A', level=3)
        '456A'
        >>> evaluate('<v<A>>^AvA^A<vA<AA>>^AAvA<^A>AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A', level=3)
        '379A'

    The Historians are getting nervous; the ship computer doesn't remember whether the missing
    Historian is trapped in the area containing a **giant electromagnet** or **molten lava**. You'll
    need to make sure that for each of the five codes, you find the **shortest sequence** of button
    presses necessary.

    The **complexity** of a single code (like `029A`) is equal to the result of multiplying these
    two values:

      - The **length of the shortest sequence** of button presses you need to type on your
        directional keypad in order to cause the code to be typed on the numeric keypad;
        for 029A, this would be `68`:

            >>> shortest_sequence_length('029A', level=3)
            68

      - The **numeric part of the code** (ignoring leading zeroes);
        for `029A`, this would be `29`:

            >>> numeric_part('029A')
            29

    In the above example, complexity of the five codes can be found by calculating:

        >>> [(shortest_sequence_length(code, 3), numeric_part(code)) for code in example_codes]
        [(68, 29), (60, 980), (68, 179), (64, 456), (64, 379)]
        >>> [complexity(code, level=3) for code in example_codes]
        [1972, 58800, 12172, 29184, 24256]
        >>> sum(_)
        126384

    Find the fewest number of button presses you'll need to perform in order to cause the robot in
    front of the door to type each code.
    **What is the sum of the complexities of the five codes on your list?**

        >>> part_1(example_codes)
        part 1: sum of code complexities is 126384
        126384
    """

    result = sum(complexity(code, level=3) for code in codes)

    print(f"part 1: sum of code complexities is {result}")
    return result


def part_2(codes: Iterable[str]) -> int:
    """
    Just as the missing Historian is released, The Historians realize that a **second** member of
    their search party has also been missing this entire time!

    A quick life-form scan reveals the Historian is also trapped in a locked area of the ship. Due
    to a variety of hazards, robots are once again dispatched, forming another chain of remote
    control keypads managing robotic-arm-wielding robots.

    This time, many more robots are involved. In summary, there are the following keypads:

      - One directional keypad that **you** are using.
      - **25** directional keypads that **robots** are using.
      - One numeric keypad (on a door) that a **robot** is using.

    The keypads form a chain, just like before: your directional keypad controls a robot which is
    typing on a directional keypad which controls a robot which is typing on a directional keypad...
    and so on, ending with the robot which is typing on the numeric keypad.

    The door codes are the same this time around; only the number of robots and directional keypads
    has changed.

        >>> example_codes = codes_from_file('data/21-example.txt')
        >>> example_codes
        ['029A', '980A', '179A', '456A', '379A']
        >>> [shortest_sequence_length(code, level=26) for code in example_codes]
        [82050061710, 72242026390, 81251039228, 80786362258, 77985628636]
        >>> [complexity(code, level=26) for code in example_codes]
        [2379451789590, 70797185862200, 14543936021812, 36838581189648, 29556553253044]

    Find the fewest number of button presses you'll need to perform in order to cause the robot in
    front of the door to type each code.
    **What is the sum of the complexities of the five codes on your list?**

        >>> part_2(example_codes)
        part 2: sum of code complexities is 154115708116294
        154115708116294
    """

    result = sum(complexity(code, level=26) for code in codes)

    print(f"part 2: sum of code complexities is {result}")
    return result


Pos = tuple[int, int]


class Keypad:
    def __init__(self, buttons: Iterable[tuple[Pos, str]]):
        self._pos_to_button = dict(buttons)
        self._button_to_pos = {button: pos for pos, button in self._pos_to_button.items()}
        assert len(self._pos_to_button) == len(self._button_to_pos)
        assert all(len(char) == 1 for char in self._button_to_pos)

    def button_at(self, pos: Pos) -> str:
        return self._pos_to_button[pos]

    def button_pos(self, button: str) -> Pos:
        return self._button_to_pos[button]

    def items(self) -> Iterable[tuple[Pos, str]]:
        return self._pos_to_button.items()

    def __contains__(self, pos: Pos) -> bool:
        return pos in self._pos_to_button

    def __len__(self) -> int:
        return len(self._pos_to_button)

    @classmethod
    def from_text(cls, text: str) -> Self:
        return cls.from_lines(text.strip("\n").splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        return cls(
            ((x, y // 2), char.strip())
            for y, line in enumerate(lines)
            if y % 2 == 1
            for x, char in enumerate(line[2::4])
            if char.strip()
        )

    def __str__(self) -> str:
        canvas = Canvas()

        def draw_button(pos: Pos, char: str) -> None:
            px, py = pos
            bx, by = px * 4, py * 2
            canvas.draw((bx, by), '+---+')
            canvas.draw((bx, by+1), f'| {char} |')
            canvas.draw((bx, by+2), '+---+')

        for button in self.items():
            draw_button(*button)

        return str(canvas)


KEYPAD_NUMERIC = Keypad.from_text('''
+---+---+---+
| 7 | 8 | 9 |
+---+---+---+
| 4 | 5 | 6 |
+---+---+---+
| 1 | 2 | 3 |
+---+---+---+
    | 0 | A |
    +---+---+
''')

KEYPAD_DIRECTIONAL = Keypad.from_text('''
    +---+---+
    | ^ | A |
+---+---+---+
| < | v | > |
+---+---+---+
''')


def shortest_sequence_length(code: str, level: int) -> int:
    return sum(
        button_distance(b_from, b_to, level, KEYPAD_NUMERIC)
        for b_from, b_to in zip1('A' + code)
    )


@lru_cache(maxsize=None)
def button_distance(button_from: str, button_to: str, level: int, keypad: Keypad) -> int:
    """
    Return length of sequence of direction presses needed to move between the two given buttons and
    pressing the target button.
    """
    assert level > 0

    if button_from == button_to:
        return 1

    pos_from = keypad.button_pos(button_from)
    pos_to = keypad.button_pos(button_to)

    if level == 1:
        return manhattan_distance(pos_from, pos_to) + 1

    def paths_iter() -> Iterable[list[Heading]]:
        (x_from, y_from), (x_to, y_to) = pos_from, pos_to
        d_x, d_y = (x_to - x_from), (y_to - y_from)

        # if the target button is in the same row/column, there is just one path:
        if d_x == 0 or d_y == 0:
            yield list(Heading.from_vector((d_x, d_y)))
            return

        # otherwise there may be two paths, e.g.: ^^>>A or >>^^A
        path_x = list(Heading.from_vector((d_x, 0)))
        path_y = list(Heading.from_vector((0, d_y)))
        # ... if there is no gap along the way:
        if (x_from + d_x, y_from) in keypad:
            yield path_x + path_y
        if (x_from, y_from + d_y) in keypad:
            yield path_y + path_x

    return min(
        sum(
            button_distance(m_0, m_1, level-1, KEYPAD_DIRECTIONAL)
            for m_0, m_1 in zip1('A' + ''.join(h.caret for h in path) + 'A')  # ^< => A^, ^<, <A
        )
        for path in paths_iter()
    )


def manhattan_distance(pos_0: Pos, pos_1: Pos) -> int:
    return sum(abs(v_0 - v_1) for v_0, v_1 in zip(pos_0, pos_1))


def evaluate(presses: str, level: int, print_intermediate: bool = False) -> str:
    assert level >= 0

    if print_intermediate:
        print(presses)

    if level == 0:
        return presses

    keypad = KEYPAD_NUMERIC if level == 1 else KEYPAD_DIRECTIONAL

    def sub_presses_iter() -> Iterable[str]:
        pos = keypad.button_pos('A')
        for press in presses:
            if press == 'A':
                yield keypad.button_at(pos)
            else:
                pos += Heading.from_caret(press)

    return evaluate(''.join(sub_presses_iter()), level - 1, print_intermediate)


def numeric_part(code: str) -> int:
    return int(code.removesuffix('A'))


def complexity(code: str, level: int) -> int:
    return shortest_sequence_length(code, level) * numeric_part(code)


def codes_from_file(fn: str) -> list[str]:
    return list(codes_from_lines(open(relative_path(__file__, fn))))


def codes_from_text(text: str) -> list[str]:
    return list(codes_from_lines(text.strip().splitlines()))


def codes_from_lines(lines: Iterable[str]) -> Iterable[str]:
    return (line.strip() for line in lines)


def main(input_fn: str = 'data/21-input.txt') -> tuple[int, int]:
    codes = codes_from_file(input_fn)
    result_1 = part_1(codes)
    result_2 = part_2(codes)
    return result_1, result_2


if __name__ == '__main__':
    main()
