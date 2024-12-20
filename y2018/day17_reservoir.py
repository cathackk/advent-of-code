from itertools import count
from typing import Iterable, Optional

from common.rect import Rect
from common.text import parse_line

Pos = tuple[int, int]
Board = dict[Pos, str]

WALL = '#'
STILL = '='
FALLING = '|'
RUNNING = '~'
SOURCE = '+'
SPACE = ' '


def load_walls(fn: str) -> Iterable[Pos]:
    with open(fn) as file:
        for line in file:
            if line.startswith('x='):
                # x=651, y=334..355
                x, y1, y2 = (int(v) for v in parse_line(line, 'x=$, y=$..$\n'))
                assert y1 <= y2
                yield from ((x, y) for y in range(y1, y2 + 1))
            elif line.startswith('y='):
                # y=1708, x=505..523
                y, x1, x2 = (int(v) for v in parse_line(line, 'y=$, x=$..$\n'))
                assert x1 <= x2
                yield from ((x, y) for x in range(x1, x2 + 1))
            else:
                raise ValueError(line)


class State:
    @classmethod
    def load(cls, fn: str, sources=((500, 0),)):
        return cls(
            board={pos: WALL for pos in load_walls(fn)},
            sources=sources
        )

    def __init__(self, board: Board, sources: Iterable[Pos]):
        self.board = board
        self.sources = list(sources)
        self.scoring_bounds = Rect.with_all(self.board.keys())
        self.drawing_bounds = self.scoring_bounds.grow_to_fit(self.sources).grow_by(dx=2)
        self.ticks = 0

    def run(self):
        while self.sources:
            self.step()
        return self

    def step(self):
        assert bool(self.sources), "no more sources to flow!"
        self.ticks += 1

        current_source = self.sources.pop()
        # pour water (down or left/right)
        poured, new_sources = self._pour(current_source)
        # draw poured
        self.board.update(poured)
        # push new overflows
        self.sources.extend(new_sources)

        return self

    def _pour(self, pos: Pos) -> tuple[Board, Iterable[Pos]]:
        floor = self._scan_floor(pos)

        #   ...+...   ->   ...|...
        if floor is None:
            return {pos: FALLING}, []

        (tile_left, x_left), (tile_right, x_right) = floor
        p_x, p_y = pos

        #   ...+...        ...+...
        #   .......   ->   ...+...
        if x_left == x_right and tile_left == tile_right == '.':
            return {}, [(p_x, p_y), (p_x, p_y + 1)]

        #   ...+...        ...|...
        #   ...|...   ->   ...|...

        #   #  +           #  |
        #   #-----|   ->   #-----|
        if FALLING in (tile_left, tile_right):
            return {pos: FALLING}, []

        #   #  +  #        #~~~~~#
        #   #######   ->   #######

        #      +  #        +-----#
        #   .#~~~~#   ->   .#~~~~#

        #   #  +           #-----+
        #   ######.   ->   ######.

        #      +           +-----+
        #   .#~~~#.   ->   .#~~~#.

        overflows = []
        if tile_left == '.':
            overflows.append((x_left, p_y))
        if tile_right == '.':
            overflows.append((x_right, p_y))

        water_tile = RUNNING if overflows else STILL
        return {(x, p_y): water_tile for x in range(x_left + 1, x_right)}, overflows

    def _scan_floor(self, pos: Pos) -> Optional[tuple[tuple[str, int], tuple[str, int]]]:
        p_x, p_y = pos
        if p_y >= self.drawing_bounds.bottom_y:
            return None

        def walk(dx) -> tuple[str, int]:
            for x in count(p_x, dx):
                tile_current = self.board.get((x, p_y))
                if tile_current == WALL:
                    # wall on current level
                    return WALL, x
                tile_below = self.board.get((x, p_y + 1))
                if tile_below is None:
                    # empty space below
                    return '.', x
                elif tile_below in (FALLING, RUNNING):
                    # falling or running water below
                    return FALLING, x
                # otherwise continue ...

            # unreachable
            assert False

        return walk(-1), walk(+1)

    def water_score(self, include_running=True):
        scored_tiles = (STILL, FALLING, RUNNING) if include_running else (STILL,)
        return sum(
            1
            for (x, y), tile in self.board.items()
            if y in self.scoring_bounds.range_y() and tile in scored_tiles
        )

    def draw(self):
        print(f"======[{self.ticks}]======")

        def c(pos):
            if pos in self.sources:
                return SOURCE
            elif pos in self.board:
                return self.board[pos]
            else:
                return SPACE

        for y in self.drawing_bounds.range_y():
            print(''.join(c((x, y)) for x in self.drawing_bounds.range_x()))

        print()


def both_parts(fn: str) -> tuple[int, int]:
    state = State.load(fn).run()
    state.draw()

    score_1 = state.water_score(include_running=True)
    print(f"part 1: water reaches {score_1} tiles")

    score_2 = state.water_score(include_running=False)
    print(f"part 1: water remains at {score_2} tiles")

    return score_1, score_2


if __name__ == '__main__':
    both_parts("data/17-input.txt")
