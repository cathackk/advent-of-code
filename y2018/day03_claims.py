"""
Advent of Code 2018
Day 3: No Matter How You Slice It
https://adventofcode.com/2018/day/3
"""

from collections import Counter
from typing import Iterable, Self

from common.canvas import Canvas
from common.iteration import dgroupby_pairs, single_value
from common.rect import Rect
from common.text import parse_line
from meta.aoc_tools import data_path


def part_1(claims: Iterable['Claim']) -> int:
    """
    The Elves managed to locate the chimney-squeeze prototype fabric for Santa's suit (thanks to
    someone who helpfully wrote its box IDs on the wall of the warehouse in the middle of the
    night). Unfortunately, anomalies are still affecting them - nobody can even agree on how to cut
    the fabric.

    The whole piece of fabric they're working on is a very large square - at least `1000` inches on
    each side.

    Each Elf has made a **claim** about which area of fabric would be ideal for Santa's suit. All
    claims have an ID and consist of a single rectangle with edges parallel to the edges of the
    fabric. Each claim's rectangle is defined as follows:

      - The number of inches between the left edge of the fabric and the left edge of the rectangle.
      - The number of inches between the top edge of the fabric and the top edge of the rectangle.
      - The width of the rectangle in inches.
      - The height of the rectangle in inches.

    A claim like `#123 @ 3,2: 5x4` means that claim ID `123` specifies a rectangle `3` inches from
    the left edge, `2` inches from the top edge, `5` inches wide, and `4` inches tall.

        >>> (example_claim := Claim.from_str('#123 @ 3,2: 5x4'))
        Claim(id_=123, left=3, top=2, width=5, height=4)

    Visually, it claims the square inches of fabric represented by `#` (and ignores the square
    inches of fabric represented by `·`) in the diagram below:

        >>> print_claims(example_claim, bounds=Rect.at_origin(11, 9))
        ···········
        ···········
        ···#####···
        ···#####···
        ···#####···
        ···#####···
        ···········
        ···········
        ···········

    The problem is that many of the claims **overlap**, causing two or more claims to cover part of
    the same areas. For example, consider the following claims:

        >>> example_claims = claims_from_text('''
        ...     #1 @ 1,3: 4x4
        ...     #2 @ 3,1: 4x4
        ...     #3 @ 5,5: 2x2
        ... ''')
        >>> example_claims  # doctest: +NORMALIZE_WHITESPACE
        [Claim(id_=1, left=1, top=3, width=4, height=4),
         Claim(id_=2, left=3, top=1, width=4, height=4),
         Claim(id_=3, left=5, top=5, width=2, height=2)]

    Visually, these claim the following areas:

        >>> print_claims(*example_claims, bounds=Rect.at_origin(8, 8))
        ········
        ···2222·
        ···2222·
        ·11XX22·
        ·11XX22·
        ·111133·
        ·111133·
        ········

    The four square inches marked with `X` are claimed by **both `1` and `2`**. (Claim `3`, while
    adjacent to the others, does not overlap either of them.)

    If the Elves all proceed with their own plans, none of them will have enough fabric.
    **How many square inches of fabric are within two or more claims?**

        >>> part_1(example_claims)
        part 1: 4 square inches of overlapping claims
        4
    """

    overlaps = count_overlaps(claims)
    print(f"part 1: {overlaps} square inches of overlapping claims")
    return overlaps


def part_2(claims: Iterable['Claim']) -> int:
    """
    Amidst the chaos, you notice that exactly one claim doesn't overlap by even a single square inch
    of fabric with any other claim. If you can somehow draw attention to it, maybe the Elves will be
    able to make Santa's suit after all!

    For example, in the claims above, only claim `3` is intact after all claims are made:

        >>> example_claims = claims_from_file(data_path(__file__, 'example.txt'))
        >>> list(without_overlaps(example_claims))
        [Claim(id_=3, left=5, top=5, width=2, height=2)]

    **What is the ID of the only claim that doesn't overlap?**

        >>> part_2(example_claims)
        part 2: claim ID 3 overlaps no other claims
        3
    """

    claim_id = single_value(without_overlaps(claims)).id_
    print(f"part 2: claim ID {claim_id} overlaps no other claims")
    return claim_id


Pos = tuple[int, int]


class Claim:
    def __init__(self, id_, left, top, width, height):
        self.id_ = int(id_)
        right_int = (left_int := int(left)) + int(width) - 1
        bottom_int = (top_int := int(top)) + int(height) - 1
        self.rect = Rect((left_int, top_int), (right_int, bottom_int))

    def __repr__(self) -> str:
        tn = type(self).__name__
        return (
            f'{tn}(id_={self.id_!r}, '
            f'left={self.left!r}, '
            f'top={self.top!r}, '
            f'width={self.width!r}, '
            f'height={self.height!r})'
        )

    @property
    def left(self) -> int:
        return self.rect.left_x

    @property
    def top(self) -> int:
        return self.rect.top_y

    @property
    def width(self) -> int:
        return self.rect.width

    @property
    def height(self) -> int:
        return self.rect.height

    @classmethod
    def from_str(cls, line: str) -> Self:
        id_, left, top, width, height = parse_line(line, "#$ @ $,$: $x$")
        return cls(id_=int(id_), top=int(top), left=int(left), width=int(width), height=int(height))


def count_overlaps(claims: Iterable[Claim]) -> int:
    counter = Counter(pos for claim in claims for pos in claim.rect)
    return sum(1 for count in counter.values() if count > 1)


def without_overlaps(claims: Iterable[Claim]) -> Iterable[Claim]:
    claims_list = list(claims)
    pos_to_claim_ids = dgroupby_pairs((pos, claim.id_) for claim in claims for pos in claim.rect)
    claim_ids_with_overlaps = {
        claim_id
        for claims_group in pos_to_claim_ids.values()
        if len(claims_group) > 1
        for claim_id in claims_group
    }
    return (claim for claim in claims_list if claim.id_ not in claim_ids_with_overlaps)


def print_claims(
    *claims: Claim,
    empty_color: str = '·',
    overlapping_color: str = 'X',
    long_id_color: str = '#',
    bounds: Rect | None = None
):
    def color(claim: Claim) -> str:
        id_str = str(claim.id_)
        return id_str if len(id_str) == 1 else long_id_color

    canvas = Canvas(
        chars=((pos, color(claim)) for claim in claims for pos in claim.rect),
        blending=lambda a, b: overlapping_color if a != b else None
    )

    canvas.print(empty_char=empty_color, bounds=bounds)


def claims_from_text(text: str) -> list[Claim]:
    return list(claims_from_lines(text.strip().splitlines()))


def claims_from_file(fn: str) -> list[Claim]:
    return list(claims_from_lines(open(fn)))


def claims_from_lines(lines: Iterable[str]) -> Iterable[Claim]:
    return (Claim.from_str(line.strip()) for line in lines)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    claims = claims_from_file(input_path)
    result_1 = part_1(claims)
    result_2 = part_2(claims)
    return result_1, result_2


if __name__ == '__main__':
    main()
