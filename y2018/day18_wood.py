from collections import Counter
from typing import Dict
from typing import Iterable
from typing import Optional
from typing import Tuple

from rect import Rect
from utils import single


Pos = Tuple[int, int]


class State:

    def __init__(self, board: Dict[Pos, str], bounds: Rect):
        self.board = dict(board)
        self.bounds = bounds

        self.score_history = []
        self.hash_to_minute: Dict[int, int] = dict()
        self._capture_history()

    @classmethod
    def load(cls, fn: str):
        lines = list(line.rstrip() for line in open(fn))

        height = len(lines)
        assert height > 0
        width = single(set(len(line) for line in lines))

        board = {
            (x, y): c
            for y, line in enumerate(lines)
            for x, c in enumerate(line)
        }

        return cls(board, Rect.at_origin(width, height))

    @property
    def minute(self) -> int:
        return len(self.score_history) - 1

    def step(self) -> Optional[Tuple[int, int]]:
        def new_acre(current_acre: str, neighbors: Iterable[str]) -> str:
            nc = Counter(neighbors)

            # An open acre will become filled with trees if  three or more adjacent acres
            # contained trees. Otherwise, nothing happens.
            if current_acre == '.':
                return '|' if nc['|'] >= 3 else '.'

            # An acre filled with trees will become a lumberyard if three or more adjacent acres
            # were lumberyards. Otherwise, nothing happens.
            elif current_acre == '|':
                return '#' if nc['#'] >= 3 else '|'

            # An acre containing a lumberyard will remain a lumberyard if it was adjacent to at
            # least one other lumberyard and at least one acre containing trees. Otherwise, it
            # becomes open.
            elif current_acre == '#':
                return '#' if nc['#'] >= 1 and nc['|'] >= 1 else '.'

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

        return self._capture_history()

    def _capture_history(self) -> Optional[Tuple[int, int]]:
        score = self.current_score()
        self.score_history.append(score)

        h = self.current_acres_hash()
        if h in self.hash_to_minute:
            # found cycle!
            return self.hash_to_minute[h], self.minute
        else:
            self.hash_to_minute[h] = self.minute
            return None

    def current_acres_hash(self):
        return hash(''.join(
            self.board[(x, y)]
            for x in self.bounds.range_x()
            for y in self.bounds.range_y()
        ))

    def current_score(self) -> int:
        """
        Multiplying the number of wooded acres by the number of lumberyards
        gives the total resource value.
        """
        c = Counter(self.board.values())
        return c['|'] * c['#']

    def current_description(self) -> str:
        if self.minute == 0:
            return "Initial state"
        elif self.minute == 1:
            return "After 1 minute"
        else:
            return f"After {self.minute} minutes"

    def draw(self):
        print(f"{self.current_description()}:")
        for y in self.bounds.range_y():
            print(''.join(self.board[(x, y)] for x in self.bounds.range_x()))
        print()
        return self

    def run(self, minutes: int, draw_each: int = 1) -> int:
        for minute in range(minutes):
            cycle = self.step()
            if draw_each > 0 and minute % draw_each == 0:
                self.draw()
            if cycle:
                start, end = cycle
                cycle_length = end - start
                remaining_minutes = minutes - minute
                use_score_at = start + remaining_minutes % cycle_length
                result = self.score_history[use_score_at]
                print(
                    f"found cycle: "
                    f"start={start}, "
                    f"end={end}, "
                    f"cycle_length={cycle_length}, "
                    f"remaining_minutes={remaining_minutes}, "
                    f"use_score_at={use_score_at}, "
                    f"result={result}"
                )
                return result
        else:
            return self.current_score()


def part_1(fn: str) -> int:
    state = State.load(fn)
    score = state.run(10, draw_each=0)
    state.draw()
    print(f"part 1: score after 10 minutes is {score}")
    return score


def part_2(fn: str) -> int:
    ...


if __name__ == '__main__':
    filename = "data/18-input.txt"
    part_1(filename)
    part_2(filename)
