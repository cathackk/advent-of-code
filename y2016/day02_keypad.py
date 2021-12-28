from typing import Iterable

from common.heading import Heading


Pos = tuple[int, int]
Instructions = Iterable[list[Heading]]
Keypad = dict[Pos, str]


def heading_from_code(code: str) -> Heading:
    return {
        'U': Heading.NORTH,
        'D': Heading.SOUTH,
        'L': Heading.WEST,
        'R': Heading.EAST
    }[code]


def load_instructions(fn: str) -> Instructions:
    for line in open(fn):
        yield [heading_from_code(c) for c in line.strip()]


def create_keypad(lines: str) -> Keypad:
    return {
        (x, y): c
        for y, line in enumerate(lines.split('\n'))
        for x, c in enumerate(line)
        if c != ' '
    }


keypad_1 = create_keypad('123\n456\n789')
keypad_2 = create_keypad('  1  \n 234\n56789\n ABC\n  D')


def walk_keypad(keypad: Keypad, start: str, instrs: Instructions) -> Iterable[str]:
    pos = next(pos for pos, c in keypad.items() if c == start)
    for line in instrs:
        for h in line:
            new_pos = h.move(pos)
            if new_pos in keypad:
                pos = new_pos
        yield keypad[pos]


def test_1():
    assert ''.join(walk_keypad(
        keypad=keypad_1,
        start='5',
        instrs=load_instructions("data/02-example.txt")
    )) == '1985'


def test_2():
    assert ''.join(walk_keypad(
        keypad=keypad_2,
        start='5',
        instrs=load_instructions("data/02-example.txt")
    )) == '5DB3'


def part_1(instrs: Instructions) -> str:
    code = ''.join(walk_keypad(keypad_1, '5', instrs))
    print(f"part 1: code is {code}")
    return code


def part_2(instrs: Instructions) -> str:
    code = ''.join(walk_keypad(keypad_2, '5', instrs))
    print(f"part 2: code is {code}")
    return code


if __name__ == '__main__':
    walk = list(load_instructions("data/02-input.txt"))
    part_1(walk)
    part_2(walk)
