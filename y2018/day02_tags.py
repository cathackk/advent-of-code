from collections import Counter
from itertools import combinations


def part_1(tags: list[str]) -> int:
    tags2 = [tag for tag in tags if 2 in Counter(tag).values()]
    tags3 = [tag for tag in tags if 3 in Counter(tag).values()]
    checksum = len(tags2) * len(tags3)
    print(f"part 1: checksum is {checksum}")
    return checksum


def part_2(tags: list[str]) -> str:
    pairs = [
        (tag1, tag2)
        for tag1, tag2 in combinations(tags, 2)
        if sum(1 for c1, c2 in zip(tag1, tag2) if c1 != c2) == 1
    ]
    assert len(pairs) == 1
    tag1, tag2 = pairs[0]
    common = ''.join(c1 for c1, c2 in zip(tag1, tag2) if c1 == c2)
    print(f"part 2: {common}")
    return common


if __name__ == '__main__':
    tags_ = [line.strip() for line in open("data/02-input.txt")]
    part_1(tags_)
    part_2(tags_)
