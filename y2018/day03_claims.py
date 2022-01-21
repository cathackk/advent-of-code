from typing import Iterable

from common.iteration import dgroupby
from common.rect import Rect
from common.text import parse_line

Claim = tuple[int, Rect]


def load_claims(fn: str) -> Iterable[Claim]:
    for line in open(fn):
        cid, x, y, w, h = parse_line(line, '#$ @ $,$: $x$\n')
        x1, y1 = int(x), int(y)
        x2, y2 = x1 + int(w) - 1, y1 + int(h) - 1
        yield int(cid), Rect((x1, y1), (x2, y2))


if __name__ == '__main__':
    claims = list(load_claims("data/03-input.txt"))
    claimed_positions = dgroupby(
        ((cid, pos) for cid, rect in claims for pos in rect),
        key=lambda cp: cp[1],
        value=lambda cp: cp[0]
    )
    result_1 = sum(1 for cids in claimed_positions.values() if len(cids) > 1)
    print(f"part 1: {result_1} overlapping squares")

    overlapping_ids = {
        cid
        for cids in claimed_positions.values()
        if len(cids) > 1
        for cid in cids
    }
    non_overlapping_ids = [
        cid
        for cid in range(1, len(claims)+1)
        if cid not in overlapping_ids
    ]
    assert len(non_overlapping_ids) == 1
    result_2 = non_overlapping_ids[0]
    print(f"part 2: #{result_2} is not overlapping any other claim")
