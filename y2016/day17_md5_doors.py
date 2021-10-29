from typing import Generator
from typing import Iterable
from typing import List
from typing import Optional

from md5 import md5
from rect import Pos
from rect import Rect
from utils import last

Path = tuple[Pos, str]


def neighbors(path: Path, bounds: Rect, password: str) -> Iterable[Path]:
    (x, y), ps = path
    h = md5(password + ps)
    open_up, open_down, open_left, open_right = tuple(c in 'bcdef' for c in h[:4])
    if open_up and y-1 in bounds.range_y():
        yield (x, y-1), ps+'U'
    if open_down and y+1 in bounds.range_y():
        yield (x, y+1), ps+'D'
    if open_left and x-1 in bounds.range_x():
        yield (x-1, y), ps+'L'
    if open_right and x+1 in bounds.range_x():
        yield (x+1, y), ps+'R'


def find_paths(
        password: str,
        bounds: Rect = Rect.at_origin(4, 4),
        start: Pos = None,
        end: Pos = None
) -> Generator[str, None, None]:
    if start is None:
        start = bounds.top_left
    if end is None:
        end = bounds.bottom_right

    assert start in bounds
    assert end in bounds

    to_visit: List[Path] = [(start, '')]

    while to_visit:
        visiting = to_visit
        to_visit = []
        for path in visiting:
            for npath in neighbors(path, bounds, password):
                pos, ps = npath
                if pos == end:
                    yield ps
                else:
                    to_visit.append(npath)


def find_shortest_path(
        password: str,
        bounds: Rect = Rect.at_origin(4, 4),
        start: Pos = None,
        end: Pos = None,
) -> Optional[str]:
    return next(find_paths(password, bounds, start, end), None)


def find_longest_path(
        password: str,
        bounds: Rect = Rect.at_origin(4, 4),
        start: Pos = None,
        end: Pos = None,
) -> Optional[str]:
    return last(find_paths(password, bounds, start, end), None)


def test_find_shortest_path():
    assert find_shortest_path('ihgpwlah') == 'DDRRRD'
    assert find_shortest_path('kglvqrro') == 'DDUDRLRRUDRD'
    assert find_shortest_path('ulqzkmiv') == 'DRURDRUDDLLDLUURRDULRLDUUDDDRR'


def test_find_longest_path():
    assert len(find_longest_path('ihgpwlah')) == 370
    assert len(find_longest_path('kglvqrro')) == 492
    assert len(find_longest_path('ulqzkmiv')) == 830


def part_1(password: str) -> str:
    path = find_shortest_path(password)
    print(f"part 1: shortest path is {path}")
    return path


def part_2(password: str) -> int:
    path = find_longest_path(password)
    steps = len(path)
    print(f"part 2: longest path is {steps} steps long")
    return steps


if __name__ == '__main__':
    password_ = 'qljzarfv'
    part_1(password_)
    part_2(password_)
