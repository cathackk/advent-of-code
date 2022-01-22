"""
Advent of Code 2021
Day 4: Giant Squid
https://adventofcode.com/2021/day/4
"""

from itertools import islice
from typing import Iterable
from typing import Iterator

from common.file import relative_path
from common.iteration import last
from common.utils import some


def part_1(numbers_drawn: Iterable[int], boards: 'Boards') -> int:
    """
    Bingo is played on a set of boards each consisting of a 5x5 grid of numbers. Numbers are chosen
    at random, and the chosen number is **marked** on all boards on which it appears. (Numbers may
    not appear on all boards.) If all numbers in any row or any column of a board are marked, that
    board **wins**. (Diagonals don't count.)

    The submarine has a bingo subsystem to help passengers pass the time. It automatically generates
    a random order in which to draw numbers and a random set of boards (your puzzle input).

    For example:

        >>> numbers, boards = game_from_text('''
        ...     7,4,9,5,11,17,23,2,0,14,21,24,10,16,13,6,15,25,12,22,18,20,8,19,3,26,1
        ...
        ...     22 13 17 11  0
        ...      8  2 23  4 24
        ...     21  9 14 16  7
        ...      6 10  3 18  5
        ...      1 12 20 15 19
        ...
        ...      3 15  0  2 22
        ...      9 18 13 17  5
        ...     19  8  7 25 23
        ...     20 11 10 24  4
        ...     14 21 16 12  6
        ...
        ...     14 21 17 24  4
        ...     10 16 15  9 19
        ...     18  8 23 26 20
        ...     22 11 13  6  5
        ...      2  0 12  3  7
        ... ''')
        >>> len(boards)
        3
        >>> boards[0].row(0)
        [22, 13, 17, 11, 0]
        >>> boards[1].column(2)
        [0, 13, 7, 10, 16]

    After the first five numbers are drawn, ...

        >>> drawn = iter(numbers)
        >>> list(islice(drawn, 5))
        [7, 4, 9, 5, 11]

    ... there are no winners, but the boards are marked as follows:

        >>> boards.mark(*_)
        >>> print(boards)
        22 13 17 1̶1̶  0     3 15  0  2 22    14 21 17 24  4̶
         8  2 23  4̶ 24     9̶ 18 13 17  5̶    10 16 15  9̶ 19
        21  9̶ 14 16  7̶    19  8  7̶ 25 23    18  8 23 26 20
         6 10  3 18  5̶    20 1̶1̶ 10 24  4̶    22 1̶1̶ 13  6  5̶
         1 12 20 15 19    14 21 16 12  6     2  0 12  3  7̶

    After the next six numbers are drawn, there are still no winners:

        >>> list(islice(drawn, 6))
        [17, 23, 2, 0, 14, 21]
        >>> boards.mark(*_)
        >>> print(boards)
        22 13 1̶7̶ 1̶1̶  0̶     3 15  0̶  2̶ 22    1̶4̶ 2̶1̶ 1̶7̶ 24  4̶
         8  2̶ 2̶3̶  4̶ 24     9̶ 18 13 1̶7̶  5̶    10 16 15  9̶ 19
        2̶1̶  9̶ 1̶4̶ 16  7̶    19  8  7̶ 25 2̶3̶    18  8 2̶3̶ 26 20
         6 10  3 18  5̶    20 1̶1̶ 10 24  4̶    22 1̶1̶ 13  6  5̶
         1 12 20 15 19    1̶4̶ 2̶1̶ 16 12  6     2̶  0̶ 12  3  7̶

    Finally, `24` is drawn:

        >>> next(drawn)
        24
        >>> winning_board = boards.mark(_)
        >>> print(boards)
        22 13 1̶7̶ 1̶1̶  0̶     3 15  0̶  2̶ 22    1̶4̶ 2̶1̶ 1̶7̶ 2̶4̶  4̶
         8  2̶ 2̶3̶  4̶ 2̶4̶     9̶ 18 13 1̶7̶  5̶    10 16 15  9̶ 19
        2̶1̶  9̶ 1̶4̶ 16  7̶    19  8  7̶ 25 2̶3̶    18  8 2̶3̶ 26 20
         6 10  3 18  5̶    20 1̶1̶ 10 2̶4̶  4̶    22 1̶1̶ 13  6  5̶
         1 12 20 15 19    1̶4̶ 2̶1̶ 16 12  6     2̶  0̶ 12  3  7̶

    At this point, the third board **wins** because it has at least one complete row or column of
    marked numbers (in this case, the entire top row is marked: `1̶4̶ 2̶1̶ 1̶7̶ 2̶4̶ 4̶`).

        >>> winning_board is boards[2]
        True
        >>> winning_board.is_winner()
        True

    The **score** of the winning board can now be calculated. Start by finding the **sum of all
    unmarked numbers** on that board; in this case, the sum is `188`.

        >>> sum(winning_board.unmarked_numbers())
        188

    Then, multiply that sum by **the number that was just called** when the board won, `24`, to get
    the final score, `188 * 24 = 4512`.

        >>> winning_board.winning_number
        24
        >>> winning_board.winning_score()
        4512

    Figure out which board will win first. **What will your final score be if you choose that
    board?**

        >>> boards.reset()
        >>> part_1(numbers, boards)
        part 1: first winning board has score 4512
        4512

    TODO move to part 2

        >>> boards.reset()
        >>> part_2(numbers, boards)
        part 2: last winning board has score 1924
        1924
    """

    first_winning_board = some(boards.mark(*numbers_drawn))
    result = first_winning_board.winning_score()

    print(f"part 1: first winning board has score {result}")
    return result


def part_2(numbers_drawn: list[int], boards: 'Boards') -> int:
    """
    Instructions for part 2.
    """

    last_winning_board = some(boards.mark(*numbers_drawn, stop_at_first_win=False))
    result = last_winning_board.winning_score()

    print(f"part 2: last winning board has score {result}")
    return result


BOARD_HEIGHT = 5
BOARD_WIDTH = 5
BOARD_SIZE = BOARD_HEIGHT * BOARD_WIDTH

class Board:
    def __init__(self, numbers: Iterable[int]):
        self.numbers = list(numbers)
        assert len(self.numbers) == BOARD_SIZE
        assert len(set(self.numbers)) == BOARD_SIZE  # numbers are unique
        self.marked_numbers: set[int] = set()
        self.winning_number: int | None = None

    def row(self, row_index: int) -> list[int]:
        assert 0 <= row_index < BOARD_HEIGHT
        start = row_index * BOARD_WIDTH
        end = start + BOARD_WIDTH
        return self.numbers[start:end]

    def row_with_number(self, number: int) -> list[int]:
        return self.row(self.numbers.index(number) // BOARD_WIDTH)

    def rows(self) -> Iterable[list[int]]:
        return (self.row(rown) for rown in range(BOARD_HEIGHT))

    def column(self, column_index: int) -> list[int]:
        assert 0 <= column_index < BOARD_WIDTH
        return self.numbers[column_index::BOARD_WIDTH]

    def column_with_number(self, number: int) -> list[int]:
        return self.column(self.numbers.index(number) % BOARD_WIDTH)

    def columns(self) -> Iterable[list[int]]:
        return (self.column(coln) for coln in range(BOARD_WIDTH))

    def mark(self, number: int) -> bool:
        if self.is_winner():
            # already winner, no need to mark further
            return False

        if number not in self.numbers:
            # number not on board
            return False

        self.marked_numbers.add(number)
        becomes_winner = (
            self.marked_numbers.issuperset(self.row_with_number(number)) or
            self.marked_numbers.issuperset(self.column_with_number(number))
        )
        if becomes_winner:
            self.winning_number = number
            return True
        else:
            return False

    def is_marked(self, number: int) -> bool:
        return number in self.marked_numbers

    def unmarked_numbers(self) -> Iterable[int]:
        return (num for num in self.numbers if not self.is_marked(num))

    def is_winner(self) -> bool:
        return self.winning_number is not None

    def winning_score(self) -> int:
        return sum(self.unmarked_numbers()) * some(self.winning_number)

    def reset(self) -> None:
        self.marked_numbers.clear()
        self.winning_number = None

    def __str__(self) -> str:
        def strike_through(val) -> str:
            return ''.join((c + chr(822) if not c.isspace() else c) for c in str(val))

        def format_num(num: int) -> str:
            num_str = str(num).rjust(2)
            return strike_through(num_str) if self.is_marked(num) else num_str

        return '\n'.join(' '.join(format_num(num) for num in row) for row in self.rows())


class Boards:
    def __init__(self, *boards: Board):
        self._boards = boards

    @classmethod
    def from_lines(cls, lines: Iterator[str]) -> 'Boards':
        def boards() -> Iterable[Board]:
            while True:
                rows = [[int(num) for num in line.split()] for line in islice(lines, BOARD_HEIGHT)]
                assert all(len(row) == BOARD_WIDTH for row in rows)
                yield Board(num for row in rows for num in row)

                separator_line = next(lines, None)
                if separator_line is None:
                    break

        return cls(*boards())

    def mark(self, *numbers: int, stop_at_first_win: bool = True) -> Board | None:
        winning_boards = (
            board
            for number in numbers
            for board in self
            if board.mark(number)
        )

        if stop_at_first_win:
            return next(winning_boards, None)
        else:
            return last(winning_boards, None)

    def reset(self) -> None:
        for board in self:
            board.reset()

    def winners(self) -> Iterable[Board]:
        return (board for board in self if board.is_winner())

    def __iter__(self) -> Iterator[Board]:
        return iter(self._boards)

    def __len__(self) -> int:
        return len(self._boards)

    def __getitem__(self, item: int) -> Board:
        return self._boards[item]

    def __str__(self) -> str:
        pad = 4 * ' '
        boards_lines = [str(board).splitlines() for board in self]
        return '\n'.join(pad.join(blines) for blines in zip(*boards_lines))


Game = tuple[list[int], 'Boards']


def game_from_file(fn: str) -> Game:
    return game_from_lines(open(relative_path(__file__, fn)))


def game_from_text(text: str) -> Game:
    return game_from_lines(text.strip().splitlines())


def game_from_lines(lines: Iterable[str]) -> Game:
    lines_gen = (line.strip() for line in lines)

    # numbers drawn
    line_drawn = next(lines_gen)
    numbers_drawn = [int(v) for v in line_drawn.split(',')]

    # empty line
    assert not next(lines_gen)

    # boards
    boards = Boards.from_lines(lines_gen)

    return numbers_drawn, boards


if __name__ == '__main__':
    drawn_nums_, boards_ = game_from_file('data/04-input.txt')
    part_1(drawn_nums_, boards_)
    boards_.reset()  # TODO: I don't like resetting - rework with immutable classes
    part_2(drawn_nums_, boards_)
