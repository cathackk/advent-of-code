from typing import Iterable
from typing import List


class Range:
    def __init__(self, vmin: int, vmax: int):
        if vmin > vmax:
            vmin, vmax = vmax, vmin
        self.vmin = vmin
        self.vmax = vmax

    def __repr__(self):
        return f'{type(self).__name__}({self.vmin}, {self.vmax})'

    def __str__(self):
        return f'{self.vmin}..{self.vmax}'

    def __len__(self):
        return self.vmax - self.vmin + 1

    def __iter__(self):
        for n in range(self.vmin, self.vmax+1):
            yield n

    def __eq__(self, other):
        return (
            isinstance(other, type(self))
            and self.vmin == other.vmin
            and self.vmax == other.vmax
        )

    def __hash__(self):
        return hash((self.vmin, self.vmax))

    def __contains__(self, item):
        return self.vmin <= item <= self.vmax

    def __lt__(self, other):
        return self.vmax < other

    def __le__(self, other):
        return self.vmax <= other

    def __gt__(self, other):
        return self.vmin > other

    def __ge__(self, other):
        return self.vmin >= other

    def __and__(self, other):
        """
        >>> Range(10, 20) & Range(1, 3)
        >>> Range(10, 20) & Range(1, 10)
        Range(10, 10)
        >>> Range(10, 20) & Range(1, 13)
        Range(10, 13)
        >>> Range(10, 20) & Range(1, 20)
        Range(10, 20)
        >>> Range(10, 20) & Range(1, 24)
        Range(10, 20)
        >>> Range(10, 20) & Range(10, 10)
        Range(10, 10)
        >>> Range(10, 20) & Range(10, 12)
        Range(10, 12)
        >>> Range(10, 20) & Range(10, 20)
        Range(10, 20)
        >>> Range(10, 20) & Range(10, 23)
        Range(10, 20)
        >>> Range(10, 20) & Range(12, 12)
        Range(12, 12)
        >>> Range(10, 20) & Range(12, 14)
        Range(12, 14)
        >>> Range(10, 20) & Range(12, 20)
        Range(12, 20)
        >>> Range(10, 20) & Range(12, 24)
        Range(12, 20)
        >>> Range(10, 20) & Range(20, 20)
        Range(20, 20)
        >>> Range(10, 20) & Range(20, 22)
        Range(20, 20)
        >>> Range(10, 20) & Range(23, 23)
        >>> Range(10, 20) & Range(23, 25)
        """
        if not isinstance(other, Range):
            raise TypeError(
                f"unsupported operand types for &: "
                f"{type(self).__name__!r} and {type(other).__name__!r}"
            )

        if self == other:
            return Range(self.vmin, self.vmax)
        elif self < other or self > other:
            return None

        return Range(
            vmin=max(self.vmin, other.vmin),
            vmax=min(self.vmax, other.vmax)
        )

    def __or__(self, other):
        """
        >>> Range(10, 20) | Range(1, 3)
        >>> Range(10, 20) | Range(1, 9)
        Range(1, 20)
        >>> Range(10, 20) | Range(1, 10)
        Range(1, 20)
        >>> Range(10, 20) | Range(1, 14)
        Range(1, 20)
        >>> Range(10, 20) | Range(1, 20)
        Range(1, 20)
        >>> Range(10, 20) | Range(1, 25)
        Range(1, 25)
        >>> Range(10, 20) | Range(9, 9)
        Range(9, 20)
        >>> Range(10, 20) | Range(9, 15)
        Range(9, 20)
        >>> Range(10, 20) | Range(9, 22)
        Range(9, 22)
        >>> Range(10, 20) | Range(10, 10)
        Range(10, 20)
        >>> Range(10, 20) | Range(10, 20)
        Range(10, 20)
        >>> Range(10, 20) | Range(10, 22)
        Range(10, 22)
        >>> Range(10, 20) | Range(14, 17)
        Range(10, 20)
        >>> Range(10, 20) | Range(14, 20)
        Range(10, 20)
        >>> Range(10, 20) | Range(14, 23)
        Range(10, 23)
        >>> Range(10, 20) | Range(20, 21)
        Range(10, 21)
        >>> Range(10, 20) | Range(21, 21)
        Range(10, 21)
        >>> Range(10, 20) | Range(21, 24)
        Range(10, 24)
        >>> Range(10, 20) | Range(22, 22)
        >>> Range(10, 20) | Range(22, 24)
        """
        if not isinstance(other, Range):
            raise TypeError(
                f"unsupported operand types for |: "
                f"{type(self).__name__!r} and {type(other).__name__!r}"
            )

        if self == other:
            return Range(self.vmin, self.vmax)
        elif self.vmax < other.vmin - 1:
            return None
        elif self.vmin > other.vmax + 1:
            return None

        return Range(
            vmin=min(self.vmin, other.vmin),
            vmax=max(self.vmax, other.vmax)
        )


class RangeSet:
    def __init__(self, ranges: Iterable[Range]):
        self.ranges = RangeSet._simplify(ranges)

    @staticmethod
    def _simplify(ranges: Iterable[Range]) -> List[Range]:
        xrs = []
        for r in ranges:
            while True:
                xr = next((xr for xr in xrs if r | xr), None)
                if xr:
                    xrs.remove(xr)
                    r = r | xr
                else:
                    xrs.append(r)
                    break
        return sorted(xrs, key=lambda r_: r_.vmin)

    def __repr__(self):
        return f'{type(self).__name__}({self.ranges!r})'

    def __str__(self):
        return ', '.join(str(r) for r in self.ranges)

    def __contains__(self, item):
        return any(item in r for r in self.ranges)

    def __len__(self):
        return sum(len(r) for r in self.ranges)

    def __iter__(self):
        for r in self.ranges:
            yield from r


def load_ranges(fn: str) -> Iterable[Range]:
    for line in open(fn):
        vmin, vmax = line.strip().split('-')
        yield Range(int(vmin), int(vmax))


def part_1(ranges: RangeSet) -> int:
    first_allowed = ranges.ranges[0].vmax + 1
    print(f"part 1: first allowed IP address is {first_allowed}")
    return first_allowed


def part_2(ranges: RangeSet) -> int:
    blocked_count = len(ranges)
    total_count = 1 << 32
    allowed_count = total_count - blocked_count
    print(f"part 2: there are total {allowed_count} allowed IPs")
    return allowed_count


if __name__ == '__main__':
    ranges_ = RangeSet(load_ranges("data/20-input.txt"))
    part_1(ranges_)
    part_2(ranges_)
