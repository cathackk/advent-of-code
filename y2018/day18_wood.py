from collections import Counter
from itertools import count
from typing import Iterable
from typing import Optional

from rect import Rect
from utils import single_value


Pos = tuple[int, int]
Board = dict[Pos, str]

SPACE = '.'
TREES = '|'
LUMBER = '#'


class State:

    def __init__(self, board: Board, bounds: Rect):
        self.board = board
        self.bounds = bounds

        self.minute = 0

        self.hash_to_board: dict[int, Board] = dict()
        self.next_hash: dict[int, int] = dict()
        self.current_hash = None
        self._capture_history()

    @classmethod
    def load(cls, fn: str):
        lines = list(line.rstrip() for line in open(fn))

        height = len(lines)
        assert height > 0
        width = single_value(set(len(line) for line in lines))

        board = {
            (x, y): c
            for y, line in enumerate(lines)
            for x, c in enumerate(line)
        }

        return cls(board, Rect.at_origin(width, height))

    def _capture_history(self):
        previous_hash = self.current_hash
        self.current_hash = hash(''.join(
            self.board[(x, y)]
            for x in self.bounds.range_x()
            for y in self.bounds.range_y()
        ))
        if previous_hash is not None:
            self.next_hash[previous_hash] = self.current_hash
        self.hash_to_board[self.current_hash] = self.board

    def _detect_cycle(self) -> Optional[int]:
        h = self.current_hash
        for step in count(1):
            h = self.next_hash.get(h)
            if h is None:
                return None
            elif h == self.current_hash:
                return step

    def current_score(self) -> int:
        """
        Multiplying the number of wooded acres by the number of lumberyards
        gives the total resource value.
        """
        c = Counter(self.board.values())
        return c[TREES] * c[LUMBER]

    def current_description(self) -> str:
        if self.minute == 0:
            return "Initial state"
        elif self.minute == 1:
            return "After 1 minute"
        else:
            return f"After {self.minute} minutes"

    def step(self):
        self.minute += 1

        if self.current_hash in self.next_hash:
            self.current_hash = self.next_hash[self.current_hash]
            self.board = self.hash_to_board[self.current_hash]
            return True

        def new_acre(current_acre: str, neighbors: Iterable[str]) -> str:
            nc = Counter(neighbors)

            # An open acre will become filled with trees if  three or more adjacent acres
            # contained trees. Otherwise, nothing happens.
            if current_acre == SPACE:
                return TREES if nc[TREES] >= 3 else SPACE

            # An acre filled with trees will become a lumberyard if three or more adjacent acres
            # were lumberyards. Otherwise, nothing happens.
            elif current_acre == TREES:
                return LUMBER if nc[LUMBER] >= 3 else TREES

            # An acre containing a lumberyard will remain a lumberyard if it was adjacent to at
            # least one other lumberyard and at least one acre containing trees. Otherwise, it
            # becomes open.
            elif current_acre == LUMBER:
                return LUMBER if nc[LUMBER] >= 1 and nc[TREES] >= 1 else SPACE

        self.board = {
            (x, y): new_acre(
                current_acre=self.board[(x, y)],
                neighbors=(
                    self.board[(x+dx, y+dy)]
                    for dx in (-1, 0, +1)
                    for dy in (-1, 0, +1)
                    if not (dx == dy == 0)
                    if (x+dx, y+dy) in self.board
                )
            )
            for x in self.bounds.range_x()
            for y in self.bounds.range_y()
        }

        self._capture_history()
        return False

    def run(self, minutes: int, draw_each: int = 0, detect_cycles: bool = True):
        while self.minute < minutes:
            cycling = self.step()
            if draw_each > 0 and self.minute % draw_each == 0:
                self.draw()

            if detect_cycles and cycling:
                cycle_length = self._detect_cycle()
                assert cycle_length is not None
                for _ in range((minutes - self.minute) % cycle_length):
                    self.current_hash = self.next_hash[self.current_hash]

                self.board = self.hash_to_board[self.current_hash]
                self.minute = minutes
                break

        return self

    def draw(self):
        print(f"{self.current_description()}:")
        for y in self.bounds.range_y():
            print(''.join(self.board[(x, y)] for x in self.bounds.range_x()))
        print()
        return self


def part(part_n: int, minutes: int, fn: str) -> int:
    state = State.load(fn).run(minutes)
    score = state.current_score()
    print(f"part {part_n}: score after {minutes} minutes is {score}")
    return score


if __name__ == '__main__':
    filename = "data/18-input.txt"
    part(1, 10, filename)
    part(2, 1_000_000_000, filename)
