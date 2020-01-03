from typing import Iterable
from typing import Tuple


Pos = Tuple[int, int]

DELTAS = {
    '^': (0, -1),
    '>': (+1, 0),
    'v': (0, +1),
    '<': (-1, 0)
}


def positions(moves: str, start: Pos = (0, 0)) -> Iterable[Pos]:
    yield start
    x, y = start
    for move in moves:
        xd, yd = DELTAS[move]
        x, y = x + xd, y + yd
        yield x, y


if __name__ == '__main__':
    moves = open("data/03-input.txt").readline().strip()

    visited = set(positions(moves))
    print(f"part 1: visited total {len(visited)} houses")

    visited_0 = set(positions(moves[0::2]))
    visited_1 = set(positions(moves[1::2]))
    print(f"part 2: visited total {len(visited_0 | visited_1)} houses")
