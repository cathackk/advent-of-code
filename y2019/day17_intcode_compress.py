"""
Advent of Code 2019
Day 17: Set and Forget
https://adventofcode.com/2019/day/17
"""

from itertools import count
from textwrap import dedent
from typing import Iterable

from common.heading import Heading
from common.iteration import last
from common.iteration import slidingw
from common.rect import Rect
from meta.aoc_tools import data_path
from y2019.intcode import load_tape
from y2019.intcode import Machine
from y2019.intcode import Tape


def part_1(tape: Tape) -> int:
    r"""
    An early warning system detects an incoming solar flare and automatically activates the ship's
    electromagnetic shield. Unfortunately, this has cut off the Wi-Fi for many small robots that,
    unaware of the impending danger, are now trapped on exterior scaffolding on the unsafe side of
    the shield. To rescue them, you'll have to act quickly!

    The only tools at your disposal are some wired cameras and a small vacuum robot currently asleep
    at its charging station. The video quality is poor, but the vacuum robot has a needlessly bright
    LED that makes it easy to spot no matter where it is.

    An Intcode program, the **Aft Scaffolding Control and Information Interface** (ASCII, your
    puzzle input), provides access to the cameras and the vacuum robot. Currently, because the
    vacuum robot is asleep, you can only access the cameras.

    Running the ASCII program on your Intcode computer will provide the current view of the
    scaffolds. This is output, purely coincidentally, as ASCII code: `35` means `#`, `46` means `.`,
    `10` starts a new line of output below the current one, and so on. (Within a line, characters
    are drawn left-to-right.)

        >>> chr(35), chr(46), chr(10)
        ('#', '.', '\n')

    In the camera output, `#` represents a scaffold and `.` represents open space. The vacuum robot
    is visible as `^`, `v`, `<`, or `>` depending on whether it is facing up, down, left, or right
    respectively. When drawn like this, the vacuum robot is **always on a scaffold**; if the vacuum
    robot ever walks off of a scaffold and **begins tumbling through space uncontrollably**, it will
    instead be visible as `X`.

    In general, the scaffold forms a path, but it sometimes loops back onto itself. For example,
    suppose you can see the following view from the cameras:

        >>> example_map = Map.from_text('''
        ...     ..#..........
        ...     ..#..........
        ...     #######...###
        ...     #.#...#...#.#
        ...     #############
        ...     ..#...#...#..
        ...     ..#####...^..
        ... ''')

    Here, the vacuum robot, `^` is facing up and sitting at one end of the scaffold near the bottom-
    -right of the image. The scaffold continues up, loops across itself several times, and ends at
    the top-left of the image.

    The first step is to calibrate the cameras by getting the **alignment parameters** of some well-
    -defined points. Locate all **scaffold intersections**; for each, its alignment parameter is the
    distance between its left edge and the left edge of the view multiplied by the distance between
    its top edge and the top edge of the view. Here, the intersections from the above image are
    marked `O`:

        >>> xs = list(find_intersections(example_map))
        >>> example_map.draw(intersections=xs)
        ..#..........
        ..#..........
        ##O####...###
        #.#...#...#.#
        ##O###O###O##
        ..#...#...#..
        ..#####...^..

    For these intersections:

        >>> xs
        [(2, 2), (2, 4), (6, 4), (10, 4)]
        >>> [alignment_parameter(x) for x in xs]
        [4, 8, 24, 40]

    To calibrate the cameras, you need the **sum of the alignment parameters**. In the above
    example, this is **`76`**.

        >>> sum(alignment_parameter(x) for x in xs)
        76

    Run your ASCII program. **What is the sum of the alignment parameters** for the scaffold
    intersections?

        >>> part_1(example_map.to_tape())
        part 1: sum of alignment parameters is 76
        76
    """

    map_ = Map.from_tape(tape)
    intersections = list(find_intersections(map_))
    # map_.draw(intersections)
    result = sum(alignment_parameter(xsect) for xsect in intersections)

    print(f"part 1: sum of alignment parameters is {result}")
    return result


def part_2(tape: Tape) -> int:
    """
    Now for the tricky part: notifying all the other robots about the solar flare. The vacuum robot
    can do this automatically if it gets into range of a robot. However, you can't see the other
    robots on the camera, so you need to be thorough instead: you need to make the vacuum robot
    **visit every part of the scaffold at least once**.

    The vacuum robot normally wanders randomly, but there isn't time for that today. Instead, you
    can **override its movement logic** with new rules.

    Force the vacuum robot to wake up by changing the value in your ASCII program at address `0`
    from `1` to **`2`**. When you do this, you will be automatically prompted for the new movement
    rules that the vacuum robot should use. The ASCII program will use input instructions to receive
    them, but they need to be provided as ASCII code; end each line of logic with a single newline,
    ASCII code `10`.

    First, you will be prompted for the **main movement routine**. The main routine may only call
    the movement functions: `A`, `B`, or `C`. Supply the movement functions to use as ASCII text,
    separating them with commas (`,`, ASCII code `44`), and ending the list with a newline (ASCII
    code `10`). For example, to call `A` twice, then alternate between `B` and `C` three times,
    provide the string `A,A,B,C,B,C,B,C` and then a newline.

    Then, you will be prompted for each **movement function**. Movement functions may use `L` to
    **turn left**, `R` to **turn right**, or a number to **move forward** that many units. Movement
    functions may not call other movement functions. Again, separate the actions with commas and end
    the list with a newline. For example, to move forward `10` units, turn left, move forward `8`
    units, turn right, and finally move forward `6` units, provide the string `10,L,8,R,6` and then
    a newline.

    Finally, you will be asked whether you want to see a **continuous video feed**; provide either
    `y` or `n` and a newline. Enabling the continuous video feed can help you see what's going on,
    but it also requires a significant amount of processing power, and may even cause your Intcode
    computer to overheat.

    Due to the limited amount of memory in the vacuum robot, the ASCII definitions of the main
    routine and the movement functions may each contain **at most 20 characters**, not counting the
    newline.

    For example, consider the following camera feed:

        >>> example = Map.from_text('''
        ...     #######...#####
        ...     #.....#...#...#
        ...     #.....#...#...#
        ...     ......#...#...#
        ...     ......#...###.#
        ...     ......#.....#.#
        ...     ^########...#.#
        ...     ......#.#...#.#
        ...     ......#########
        ...     ........#...#..
        ...     ....#########..
        ...     ....#...#......
        ...     ....#...#......
        ...     ....#...#......
        ...     ....#####......
        ... ''')

    In order for the vacuum robot to **visit every part of the scaffold at least once**, one path it
    could take is:

        >>> (example_path := list(trace_path(example)))  # doctest: +NORMALIZE_WHITESPACE
        [('R', 8), ('R', 8), ('R', 4), ('R', 4), ('R', 8), ('L', 6), ('L', 2),
         ('R', 4), ('R', 4), ('R', 8), ('R', 8), ('R', 8), ('L', 6), ('L', 2)]

    Without the memory limit, you could just supply this whole string to function `A` and have the
    main routine call `A` once. However, you'll need to split it into smaller parts.

        >>> path_to_str(example_path)
        'R,8,R,8,R,4,R,4,R,8,L,6,L,2,R,4,R,4,R,8,R,8,R,8,L,6,L,2'
        >>> len(path_to_str(example_path))
        55

    One approach is:

        >>> (example_movement := compress(example_path))
        ('A,B,C,B,A,C', 'R,8,R,8', 'R,4,R,4', 'R,8,L,6,L,2')

    Visually, this would break the desired path into the following parts:

        A,        B,        C,            B,        A,        C
        R,8,R,8,  R,4,R,4,  R,8,L,6,L,2,  R,4,R,4,  R,8,R,8,  R,8,L,6,L,2
        <BLANKLINE>
        CCCCCCC...BBBBB
        C.....C...B...A
        C.....C...B...A
        ......C...B...A
        ......C...CCC.A
        ......C.....C.A
        ^AAAAA#AA...C.A
        ......C.A...C.A
        ......AAAAAA#AA
        ........A...C..
        ....BCCC#CCCC..
        ....B...A......
        ....B...A......
        ....B...A......
        ....BBBBA......

    Of course, the scaffolding outside your ship is much more complex.

    As the vacuum robot finds other robots and notifies them of the impending solar flare, it also
    can't help but leave them squeaky clean, collecting any space dust it finds. Once it finishes
    the programmed set of movements, assuming it hasn't drifted off into space, the cleaning robot
    will return to its docking station and report the amount of space dust it collected as a large,
    non-ASCII value in a single output instruction.

    After visiting every part of the scaffold at least once, **how much dust does the vacuum robot
    report it has collected?**
    """

    movement = compress(trace_path(Map.from_tape(tape)))
    result = enter_movement(Machine(adjusted_tape(tape)), movement)

    print(f"part 2: robot collected {result} dust")
    return result


Pos = tuple[int, int]
MovementInstr = tuple[str, int]
Path = Iterable[MovementInstr]
PathCompressed = tuple[str, str, str, str]


class Map:
    def __init__(self, chars: Iterable[tuple[Pos, str]]):
        self.chars = dict(chars)
        self.floors = set(pos for pos, char in self.chars.items() if char != '.')
        self.bounds = Rect.with_all(self.chars)
        self.robot = next(
            (pos, Heading.from_caret(ch))
            for pos, ch in self.chars.items()
            if ch in {h.caret for h in Heading}
        )

    def draw(self, intersections: Iterable[Pos] = ()) -> None:
        intersections_set = set(intersections)

        def char(pos: Pos) -> str:
            if pos in intersections_set:
                return 'O'
            else:
                return self.chars[pos]

        for y in self.bounds.range_y():
            print(''.join(char((x, y)) for x in self.bounds.range_x()))

    @classmethod
    def from_tape(cls, tape: Tape) -> 'Map':
        text = ''.join(chr(val) for val in Machine(tape).run_output_only())
        return cls.from_text(text)

    @classmethod
    def from_text(cls, text: str) -> 'Map':
        return cls.from_lines(dedent(text.strip('\n')).splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Map':
        return cls(
            ((x, y), char)
            for y, line in enumerate(lines)
            for x, char in enumerate(line.strip())
        )

    def to_tape(self) -> list[int]:
        lines = (
            [ord(self.chars[x, y]) for x in self.bounds.range_x()] + [ord('\n')]
            for y in self.bounds.range_y()
        )
        return [val for line in lines for code in line for val in (104, code)] + [99]


def find_intersections(map_: Map) -> Iterable[Pos]:
    cross_pattern = {
        (x, y): char
        for y, line in enumerate(['.#.', '###', '.#.'], start=-1)
        for x, char in enumerate(line, start=-1)
    }

    def has_cross(center: Pos) -> bool:
        x, y = center
        return all(
            map_.chars.get((x + dx, y + dy)) == char
            for (dx, dy), char in cross_pattern.items()
        )

    return (pos for pos in map_.chars if has_cross(pos))


def alignment_parameter(pos: Pos) -> int:
    x, y = pos
    return x * y


def trace_path(map_: Map) -> Path:
    pos, heading = map_.robot
    floors_unvisited = set(map_.floors) - {pos}

    while floors_unvisited:
        # next step is not on floor
        assert heading.move(pos) not in map_.floors

        # so where can I turn?
        if (heading_left := heading.left()).move(pos) in map_.floors:
            turn, heading = 'L', heading_left
        elif (heading_right := heading.right()).move(pos) in map_.floors:
            turn, heading = 'R', heading_right
        else:
            raise ValueError(pos, heading)

        # now that I'm turned the right way, how far can I go?
        for dist in count(1):
            new_pos = heading.move(pos, dist)
            if new_pos in map_.floors:
                # go on ...
                floors_unvisited.discard(new_pos)
            else:
                # end of the line!
                final_distance = dist - 1
                pos = heading.move(pos, final_distance)
                yield turn, final_distance
                break


def path_to_str(path: Path) -> str:
    return ','.join(f'{turn},{dist}' for turn, dist in path)


def compress(path: Path, length_limit: int = 20) -> PathCompressed:
    def replace(
        seq: list[MovementInstr | str],
        to_find: Iterable[MovementInstr],
        replacement: str
    ) -> list[MovementInstr | str]:

        to_find = tuple(to_find)
        seq_replaced = list(seq)
        while True:
            try:
                index = next(
                    k
                    for k, part in enumerate(slidingw(seq_replaced, len(to_find)))
                    if part == to_find
                )
                seq_replaced[index:index+len(to_find)] = replacement
            except StopIteration:
                # nothing more to replace
                return seq_replaced

    path = list(path)

    # assumption: each movement part is between 2 and 5 items long
    # assumption: each movement part is used at least twice in the main sequence

    # determine A
    for a_length in range(2, 6):
        a_part = path[:a_length]
        if len(a_part_str := path_to_str(a_part)) > length_limit:
            break  # A too long!
        path_a = replace(path, a_part, 'A')
        if path_a.count('A') < 2:
            break  # only a single subst of A -> not worth it

        # determine C
        for c_length in range(2, 6):
            c_part = path_a[-c_length:]
            if 'A' in c_part or len(c_part_str := path_to_str(c_part)) > length_limit:
                break  # C too long
            path_ac = replace(path_a, c_part, 'C')
            if path_ac.count('C') < 2:
                break  # only a single subst of C -> not worth it

            # determine B
            rem_start = next(
                ix for ix, item in enumerate(path_ac) if isinstance(item, tuple)
            )
            rem_stop = next(
                ix for ix, item in enumerate(path_ac) if ix > rem_start if isinstance(item, str)
            )
            first_rem = path_ac[rem_start:rem_stop]
            if len(first_rem) < 2:
                continue  # B would be too short
            for b_length in range(2, len(first_rem) + 1):
                b_part = first_rem[:b_length]
                if len(b_part_str := path_to_str(b_part)) > length_limit:
                    break  # B too long
                path_abc = replace(path_ac, b_part, 'B')
                if all(isinstance(item, str) for item in path_abc):
                    path_abc_str = ','.join(path_abc)
                    assert len(path_abc_str) < length_limit
                    return path_abc_str, a_part_str, b_part_str, c_part_str

    raise ValueError(f"failed to compress {path_to_str(path)}")


def adjusted_tape(tape: Tape) -> Tape:
    return [2] + tape[1:]


def enter_movement(machine: Machine, movement: PathCompressed) -> int:
    io = machine.run_io()
    main_seq, part_a, part_b, part_c = movement

    assert io.read_str().endswith("Main:\n")
    io.write(main_seq + "\n")
    assert io.read_str() == "Function A:\n"
    io.write(part_a + "\n")
    assert io.read_str() == "Function B:\n"
    io.write(part_b + "\n")
    assert io.read_str() == "Function C:\n"
    io.write(part_c + "\n")
    assert io.read_str() == "Continuous video feed?\n"
    io.write("n\n")

    return last(io.read())


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    tape = load_tape(input_path)
    result_1 = part_1(tape)
    result_2 = part_2(tape)
    return result_1, result_2


if __name__ == '__main__':
    main()
