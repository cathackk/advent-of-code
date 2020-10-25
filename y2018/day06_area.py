import string
from collections import Counter
from typing import Dict
from typing import Iterable
from typing import Set

from rect import Pos
from rect import Rect
from utils import dgroupby_set
from utils import single_value


def neighbors(pos: Pos) -> Iterable[Pos]:
    x, y = pos
    yield x+1, y
    yield x-1, y
    yield x, y+1
    yield x, y-1


def md(pos1: Pos, pos2: Pos):
    x1, y1 = pos1
    x2, y2 = pos2
    return abs(x1 - x2) + abs(y1 - y2)


def load_points(fn: str) -> Iterable[Pos]:
    for line in open(fn):
        x, y = line.strip().split(', ')
        yield int(x), int(y)


def claim(points: Set[Pos]) -> int:
    # name the original points for easier debugging
    names: Dict[Pos, str] = {
        pos: name
        for pos, name in zip(
            sorted(points),
            string.ascii_uppercase + string.ascii_lowercase
        )
    }
    # determine boundaries
    bounds = Rect.with_all(points).grow_by(+3, +3)
    # pos -> claimant
    claims: Dict[Pos, str] = dict(names)
    layer: Dict[Pos, str] = dict(claims)

    while layer:
        # (1) collect all new claims
        # pos -> claimants
        new_claims: Dict[Pos, Set[str]] = dgroupby_set(
            (
                (n, o)
                for p, o in layer.items()
                for n in neighbors(p)
                if n not in claims
                and n in bounds
            ),
            key=lambda no: no[0],
            value=lambda no: no[1]
        )
        # (2) mark new claims (with single claimant)
        layer = {
            p: single_value(claimants)
            for p, claimants in new_claims.items()
            if len(claimants) == 1
        }
        claims.update(layer)
        # (3) mark draws
        claims.update({
            p: '.'
            for p, claimants in new_claims.items()
            if len(claimants) > 1
        })
        # (4) draw (debug)
        # draw_claims(points, claims, bounds)

    # ignore all claims reaching bounds (infinite?)
    infinites = set(claims[pos] for pos in bounds.border_ps())
    # count claims = area
    areas = Counter(c for c in claims.values() if c not in infinites)
    # return largest area
    return areas.most_common(1)[0][1]


def draw_claims(points: Set[Pos], claims: Dict[Pos, str], bounds: Rect):
    def t(tx: int, ty: int) -> str:
        return '#' if (tx, ty) in points else claims.get((tx, ty), ' ')
    for y in bounds.range_y():
        print(''.join(t(x, y) for x in bounds.range_x()))
    print()


def closest(points: Set[Pos], limit: int) -> int:
    bounds = Rect.with_all(points)
    dists = {
        (x, y): sum(md((x, y), p) for p in points)
        for x in bounds.range_x()
        for y in bounds.range_y()
    }
    assert all(dists[b] > limit for b in bounds.border_ps())
    return sum(1 for d in dists.values() if d < limit)


def part_1(points: Set[Pos]) -> int:
    result = claim(points)
    print(f"part 1: largest finite area has size {result}")
    return result


def part_2(points: Set[Pos], limit: int = 10_000) -> int:
    result = closest(points, limit)
    print(f"part 2: area closer than {limit} to every point has size {result}")
    return result


if __name__ == '__main__':
    points_ = set(load_points("data/06-input.txt"))
    part_1(points_)
    part_2(points_)
