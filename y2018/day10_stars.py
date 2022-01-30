from itertools import count
from typing import Iterable

from common.rect import Rect
from common.text import parse_line
from common.xy import Point
from common.xy import Vector

Star = tuple[Point, Vector]


def load_stars(fn: str) -> Iterable[Star]:
    # position=< 54660, -43357> velocity=< 5,  4>
    with open(fn) as file:
        for line in file:
            p_x, p_y, v_x, v_y = parse_line(line, "position=<$, $> velocity=<$, $>\n")
            yield Point(int(p_x), int(p_y)), Vector(int(v_x), int(v_y))


def draw(stars: Iterable[Star]):
    positions = set(tuple(pos) for pos, _ in stars)
    bounds = Rect.with_all((x, y) for x, y in positions)
    for y in bounds.range_y():
        print(''.join('*' if (x, y) in positions else ' ' for x in bounds.range_x()))


def watch(stars: Iterable[Star]):
    stars = list(stars)

    for tick in count(0):
        bounds = Rect.with_all((x, y) for (x, y), _ in stars)
        if bounds.width <= 80 and bounds.height <= 10:
            print(f"After {tick} seconds:")
            draw(stars)
            return
        elif tick % 1000 == 0:
            print(f"{tick} ...")
        stars = [(pos + vel, vel) for pos, vel in stars]


if __name__ == '__main__':
    stars_ = list(load_stars("data/10-input.txt"))
    watch(stars_)
