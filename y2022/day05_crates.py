"""
Advent of Code 2022
Day 5: Supply Stacks
https://adventofcode.com/2022/day/5
"""

from dataclasses import dataclass
from typing import Iterable, Self

from common.text import parse_line
from meta.aoc_tools import data_path


def part_1(stacks: list['Stack'], moves: Iterable['Move']) -> str:
    """
    The expedition can depart as soon as the final supplies have been unloaded from the ships.
    Supplies are stored in stacks of marked **crates**, but because the needed supplies are buried
    under many other crates, the crates need to be rearranged.

    The ship has a **giant cargo crane** capable of moving crates between stacks. To ensure none of
    the crates get crushed or fall over, the crane operator will rearrange them in a series of
    carefully-planned steps. After the crates are rearranged, the desired crates will be at the top
    of each stack.

    The Elves don't want to interrupt the crane operator during this delicate procedure, but they
    forgot to ask her **which** crate will end up where, and they want to be ready to unload them
    as soon as possible so they can embark.

    They do, however, have a drawing of the starting stacks of crates **and** the rearrangement
    procedure (your puzzle input). For example:


        >>> state_0, movez = input_from_text('''
        ...         [D]
        ...     [N] [C]
        ...     [Z] [M] [P]
        ...      1   2   3
        ...
        ...     move 1 from 2 to 1
        ...     move 3 from 1 to 3
        ...     move 2 from 2 to 1
        ...     move 1 from 1 to 2
        ... ''')

    In this example, there are three stacks of crates.

        >>> len(state_0)
        3

    Stack 1 contains two crates: crate `Z` is on the bottom, and crate `N` is on top.

        >>> state_0[0]
        ['Z', 'N']

    Stack 2 contains three crates; from bottom to top, they are crates `M`, `C`, and `D`.

        >>> state_0[1]
        ['M', 'C', 'D']

    Finally, stack 3 contains a single crate, `P`.

        >>> state_0[2]
        ['P']

    Then, the rearrangement procedure is given.

        >>> len(movez)
        4

    In each step of the procedure, a quantity of crates is moved from one stack to a different
    stack. In the first step of the above rearrangement procedure, one crate is moved from stack 2
    to stack 1:

        >>> movez[0]
        Move(count=1, stack_from=2, stack_to=1)

    ... resulting in this configuration:

        >>> state_1 = rearrange(state_0, movez[0])
        >>> state_1
        [['Z', 'N', 'D'], ['M', 'C'], ['P']]
        >>> draw_stacks(state_1)
        [D]
        [N] [C]
        [Z] [M] [P]
         1   2   3

    In the second step, three crates are moved from stack 1 to stack 3. Crates are moved **one at
    a time**, so the first crate to be moved (`D`) ends up below the second and third crates:

        >>> draw_stacks(state_2 := rearrange(state_1, movez[1]))
                [Z]
                [N]
            [C] [D]
            [M] [P]
         1   2   3

    Then, both crates are moved from stack 2 to stack 1. Again, because crates are moved **one at
    a time**, crate `C` ends up below crate M:

        >>> draw_stacks(state_3 := rearrange(state_2, movez[2]))
                [Z]
                [N]
        [M]     [D]
        [C]     [P]
         1   2   3

    Finally, one crate is moved from stack 1 to stack 2:


        >>> draw_stacks(state_4 := rearrange(state_3, movez[3]))
                [Z]
                [N]
                [D]
        [C] [M] [P]
         1   2   3

    The Elves just need to know **which crate will end up on top of each stack**; in this example,
    the top crates are `C` in stack 1, `M` in stack 2, and `Z` in stack 3, so you should combine
    these together and give the Elves the message **`CMZ`**.

        >>> top_crates(state_4)
        'CMZ'

    **After the rearrangement procedure completes, what crate ends up on top of each stack?**

        >>> part_1(state_0, movez)
        part 1: after rearrangement, the top crates are 'CMZ'
        'CMZ'
    """

    result = top_crates(rearrange(stacks, *moves))

    print(f"part 1: after rearrangement, the top crates are {result!r}")
    return result


def part_2(stacks: list['Stack'], moves: Iterable['Move']) -> str:
    """
    As you watch the crane operator expertly rearrange the crates, you notice the process isn't
    following your prediction.

    Some mud was covering the writing on the side of the crane, and you quickly wipe it away.
    The crane isn't a CrateMover 9000 - it's a **CrateMover 9001**.

    The CrateMover 9001 is notable for many new and exciting features: air conditioning, leather
    seats, an extra cup holder, and **the ability to pick up and move multiple crates at once**.

    Again considering the example above, the crates begin in the same configuration:

        >>> state_0, movez = input_from_file(data_path(__file__, 'example.txt'))
        >>> draw_stacks(state_0)
            [D]
        [N] [C]
        [Z] [M] [P]
         1   2   3

    Moving a single crate from stack 2 to stack 1 behaves the same as before:

        >>> draw_stacks(state_1 := rearrange(state_0, movez[0], reverse_order=False))
        [D]
        [N] [C]
        [Z] [M] [P]
         1   2   3

    However, the action of moving three crates from stack 1 to stack 3 means that those three moved
    crates **stay in the same order**, resulting in this new configuration:

        >>> draw_stacks(state_2 := rearrange(state_1, movez[1], reverse_order=False))
                [D]
                [N]
            [C] [Z]
            [M] [P]
         1   2   3

    Next, as both crates are moved from stack 2 to stack 1, they **retain their order** as well:

        >>> draw_stacks(state_3 := rearrange(state_2, movez[2], reverse_order=False))
                [D]
                [N]
        [C]     [Z]
        [M]     [P]
         1   2   3

    Finally, a single crate is still moved from stack 1 to stack 2, but now it's crate `C` that gets
    moved:

        >>> draw_stacks(state_4 := rearrange(state_3, movez[3], reverse_order=False))
                [D]
                [N]
                [Z]
        [M] [C] [P]
         1   2   3

    In this example, the CrateMover 9001 has put the crates in a totally different order: **`MCD`**.

        >>> top_crates(state_4)
        'MCD'

    Before the rearrangement process finishes, update your simulation so that the Elves know where
    they should stand to be ready to unload the final supplies. **After the rearrangement procedure
    completes, what crate ends up on top of each stack?**

        >>> part_2(state_0, movez)
        part 2: after rearrangement, the top crates are 'MCD'
        'MCD'
    """

    result = top_crates(rearrange(stacks, *moves, reverse_order=False))

    print(f"part 2: after rearrangement, the top crates are {result!r}")
    return result


Stack = list[str]


@dataclass(frozen=True)
class Move:
    count: int
    stack_from: int
    stack_to: int

    def __str__(self) -> str:
        return f'move {self.count} from {self.stack_from} to {self.stack_to}'

    @classmethod
    def from_line(cls, line: str) -> Self:
        count, stack_from, stack_to = parse_line(line.strip(), 'move $ from $ to $')
        return cls(int(count), int(stack_from), int(stack_to))


def rearrange(stacks: list[Stack], *moves: Move, reverse_order: bool = True) -> list[Stack]:
    # work with a copy
    stacks = [list(stack) for stack in stacks]

    for move in moves:
        stack_from = stacks[move.stack_from - 1]
        crates_moved = stack_from[-move.count:]
        del stack_from[-move.count:]

        if reverse_order:
            crates_moved.reverse()

        stack_to = stacks[move.stack_to - 1]
        stack_to.extend(crates_moved)

    return stacks


def top_crates(stacks: list[Stack]) -> str:
    return ''.join(stack[-1] for stack in stacks)


def draw_stacks(stacks: list[Stack]) -> None:
    height = max(len(stack) for stack in stacks)
    for level in range(height - 1, -1, -1):
        print(
            ' '.join(
                f'[{stack[level]}]' if level < len(stack) else '   '
                for stack in stacks
            ).rstrip()
        )
    print(' '.join(f' {n + 1} ' for n in range(len(stacks))).rstrip())


def input_from_file(fn: str) -> tuple[list[Stack], list[Move]]:
    return input_from_lines(open(fn))


def input_from_text(text: str) -> tuple[list[Stack], list[Move]]:
    return input_from_lines(text.strip('\n').splitlines())


def input_from_lines(lines: Iterable[str]) -> tuple[list[Stack], list[Move]]:
    lines = iter(lines)

    def create_stacks() -> list[Stack]:
        crate_lines = []
        for line in lines:
            line = line.rstrip()
            first_char = line.lstrip()[0]
            if first_char == '[':
                crate_lines.append(line)
            elif first_char == '1':
                # stack number -> line position
                positions = {int(ch) - 1: pos for pos, ch in enumerate(line) if ch.isdigit()}
                return [
                    [
                        crate
                        for line in reversed(crate_lines)
                        if (pos := positions[stack_index]) < len(line)
                        if (crate := line[pos]).isalpha()
                    ]
                    for stack_index in range(len(positions))
                ]

        assert False

    # (1) parse stacks
    stacks = create_stacks()
    # next line should be empty
    assert not next(lines).strip()
    # (2) parse moves
    moves = [Move.from_line(line) for line in lines]

    return stacks, moves


def main(input_path: str = data_path(__file__)) -> tuple[str, str]:
    initial_stacks, moves = input_from_file(input_path)
    result_1 = part_1(initial_stacks, moves)
    result_2 = part_2(initial_stacks, moves)
    return result_1, result_2


if __name__ == '__main__':
    main()
