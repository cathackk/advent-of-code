"""
Advent of Code 2018
Day 18: Settlers of The North Pole
https://adventofcode.com/2018/day/18
"""

from collections import Counter
from itertools import count
from typing import Iterable
from typing import Optional

from common.iteration import single_value
from common.rect import Rect
from common.utils import some

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

        self.hash_to_board: dict[int, Board] = {}
        self.next_hash: dict[int, int] = {}
        self.current_hash: int | None = None
        self._capture_history()

    @classmethod
    def load(cls, fn: str):
        with open(fn) as file:
            lines = [line.rstrip() for line in file]

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
        hash_ = self.current_hash
        for step in count(1):
            hash_ = self.next_hash.get(some(hash_))
            if hash_ is None:
                return None
            elif hash_ == self.current_hash:
                return step

        # unreachable
        assert False

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
            neighbors_count = Counter(neighbors)

            # An open acre will become filled with trees if  three or more adjacent acres
            # contained trees. Otherwise, nothing happens.
            if current_acre == SPACE:
                return TREES if neighbors_count[TREES] >= 3 else SPACE

            # An acre filled with trees will become a lumberyard if three or more adjacent acres
            # were lumberyards. Otherwise, nothing happens.
            elif current_acre == TREES:
                return LUMBER if neighbors_count[LUMBER] >= 3 else TREES

            # An acre containing a lumberyard will remain a lumberyard if it was adjacent to at
            # least one other lumberyard and at least one acre containing trees. Otherwise, it
            # becomes open.
            elif current_acre == LUMBER:
                if neighbors_count[LUMBER] >= 1 and neighbors_count[TREES] >= 1:
                    return LUMBER
                else:
                    return SPACE

            else:
                raise ValueError(current_acre)

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
                    self.current_hash = self.next_hash[some(self.current_hash)]

                self.board = self.hash_to_board[some(self.current_hash)]
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
    FILENAME = "data/18-input.txt"
    part(1, 10, FILENAME)
    part(2, 1_000_000_000, FILENAME)
