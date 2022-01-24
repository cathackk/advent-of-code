"""
Advent of Code 2017
Day 16: Permutation Promenade
https://adventofcode.com/2017/day/16
"""

from typing import Callable
from typing import Iterable

from common.file import relative_path
from common.text import parse_line


def part_1(moves: Iterable['Move'], dancers_count: int = 16) -> 'Dancers':
    """
    You come upon a very unusual sight; a group of programs here appear to be dancing.

    There are sixteen programs in total, named `a` through `p`. They start by standing in a line:
    `a` stands in position `0`, `b` stands in position `1`, and so on until `p`, which stands in
    position `15`.

    The programs' **dance** consists of a sequence of **dance moves**:

      - **Spin**, written `sX`, makes `X` programs move from the end to the front, but maintain
        their order otherwise:

        >>> Spin(3)('abcde')
        'cdeab'
        >>> Spin(1)('abcde')
        'eabcd'

      - **Exchange**, written `xA/B`, makes the programs at positions `A` and `B` swap places:

        >>> Exchange(0, 1)('abcde')
        'bacde'
        >>> Exchange(4, 2)('abcde')
        'abedc'

      - **Partner**, written `pA/B`, makes the programs named `A` and `B` swap places:

        >>> Partner('a', 'e')('abcde')
        'ebcda'
        >>> Partner('d', 'b')('abcde')
        'adcbe'

    For example, with only five programs standing in a line (`abcde`), they could do the following
    dance:

        >>> example_moves = moves_from_text('s1,x3/4,pe/b')
        >>> move_1, move_2, move_3 = example_moves
        >>> move_1, move_1('abcde')
        (Spin(1), 'eabcd')
        >>> move_2, move_2('eabcd')
        (Exchange(3, 4), 'eabdc')
        >>> move_3, move_3('eabdc')
        (Partner('e', 'b'), 'baedc')

    After finishing their dance, the programs end up in order `baedc`.

        >>> dance(example_moves, 'abcde')
        'baedc'

    You watch the dance for a while and record their dance moves (your puzzle input).
    **In what order are the programs standing** after their dance?

        >>> part_1(example_moves, dancers_count=5)
        part 1: after the dance -> 'baedc'
        'baedc'
    """

    dancers = dance(moves, create_dancers(dancers_count))
    print(f"part 1: after the dance -> {dancers!r}")
    return dancers


def part_2(
    moves: Iterable['Move'],
    dancers_count: int = 16,
    rounds: int = 1_000_000_000
) -> 'Dancers':
    """
    Now that you're starting to get a feel for the dance moves, you turn your attention to
    **the dance as a whole**.

    Keeping the positions they ended up in from their previous dance, the programs perform it again
    and again: including the first dance, a total of **one billion** (`1_000_000_000`) times.

    In the example above, their second dance would **begin** with the order `baedc`, and use
    the same dance moves:

        >>> example_moves = moves_from_text('s1,x3/4,pe/b')
        >>> dance_repeated(example_moves, dancers='abcde', rounds=2)
        'ceadb'

    **In what order are the programs standing** after their billion dances?

        >>> part_2(example_moves)
        part 2: after repeating the dance 1000000000x -> 'ghidjklmnopabcef'
        'ghidjklmnopabcef'
    """
    dancers = dance_repeated(moves, create_dancers(dancers_count), rounds)
    print(f"part 2: after repeating the dance {rounds}x -> {dancers!r}")
    return dancers


Dancers = str
Move = Callable[[Dancers], Dancers]
Permutation = list[int]


def dance(moves: Iterable[Move], dancers: Dancers) -> Dancers:
    for move in moves:
        dancers = move(dancers)
    return dancers


def dance_repeated(moves: Iterable[Move], dancers: Dancers, rounds: int) -> Dancers:
    moves_list = list(moves)
    history: list[Dancers] = [dancers]
    history_lookup: dict[Dancers, int] = {dancers: 0}

    for current_round in range(1, rounds + 1):
        dancers = dance(moves_list, dancers)

        if dancers in history_lookup:
            # already seen this permutation -> shortcut!
            loop_size = current_round - history_lookup[dancers]
            rounds_remaining = rounds - current_round
            return history[rounds_remaining % loop_size]

        history.append(dancers)
        history_lookup[dancers] = current_round

    return dancers


class Spin:
    def __init__(self, length: int):
        assert length > 0
        self.length = length

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.length!r})'

    def __call__(self, dancers: Dancers) -> Dancers:
        return dancers[-self.length:] + dancers[:-self.length]


class Exchange:
    def __init__(self, pos_1: int, pos_2: int):
        assert pos_1 >= 0
        assert pos_2 >= 0

        if pos_1 > pos_2:
            pos_1, pos_2 = pos_2, pos_1

        self.pos_1 = pos_1
        self.pos_2 = pos_2

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.pos_1!r}, {self.pos_2!r})'

    def __call__(self, dancers: Dancers) -> Dancers:
        return _exchange_impl(self.pos_1, self.pos_2, dancers)


class Partner:
    def __init__(self, dancer_1: str, dancer_2: str):
        assert len(dancer_1) == len(dancer_2) == 1
        self.dancer_1 = dancer_1
        self.dancer_2 = dancer_2

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.dancer_1!r}, {self.dancer_2!r})'

    def __call__(self, dancers: Dancers) -> Dancers:
        pos_1 = dancers.index(self.dancer_1)
        pos_2 = dancers.index(self.dancer_2)
        if pos_1 > pos_2:
            pos_1, pos_2 = pos_2, pos_1
        return _exchange_impl(pos_1, pos_2, dancers)


def _exchange_impl(pos_1: int, pos_2: int, dancers: Dancers) -> Dancers:
    assert 0 <= pos_1 <= pos_2 < len(dancers)

    if pos_1 == pos_2:
        return dancers

    prefix, dancer_1, infix, dancer_2, suffix = (
        dancers[:pos_1],
        dancers[pos_1:pos_1 + 1],
        dancers[pos_1 + 1:pos_2],
        dancers[pos_2:pos_2 + 1],
        dancers[pos_2 + 1:]
    )

    return prefix + dancer_2 + infix + dancer_1 + suffix


def create_dancers(count: int) -> Dancers:
    return ''.join(chr(ord('a') + k) for k in range(count))


def moves_from_file(fn: str) -> list[Move]:
    return moves_from_text(open(relative_path(__file__, fn)).readline().strip())


def moves_from_text(text: str) -> list[Move]:
    return [move_from_str(move_str) for move_str in text.split(",")]


def move_from_str(line: str) -> Move:
    match line[0]:
        case 's':
            # s1
            length, = parse_line(line, "s$")
            return Spin(int(length))
        case 'x':
            # x3/4
            pos_1, pos_2 = parse_line(line, "x$/$")
            return Exchange(int(pos_1), int(pos_2))
        case 'p':
            # pe/b
            dancer_1, dancer_2 = parse_line(line, "p$/$")
            return Partner(dancer_1, dancer_2)
        case _:
            raise ValueError(line)

    # TODO: remove when mypy realizes this is unreachable
    assert False


if __name__ == '__main__':
    moves_ = moves_from_file('data/16-input.txt')
    part_1(moves_)
    part_2(moves_)
