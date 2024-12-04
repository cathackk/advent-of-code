"""
Advent of Code 2016
Day 20: Firewall Rules
https://adventofcode.com/2016/day/20
"""

from typing import Iterable, Self

from meta.aoc_tools import data_path


def part_1(ranges: 'RangeSet') -> int:
    """
    You'd like to set up a small hidden computer here so you can use it to get back into the network
    later. However, the corporate firewall only allows communication with certain external IP
    addresses.

    You've retrieved the list of blocked IPs from the firewall, but the list seems to be messy and
    poorly maintained, and it's not clear which IPs are allowed. Also, rather than being written in
    dot-decimal notation, they are written as plain 32-bit integers, which can have any value from
    `0` through `4294967295`, inclusive.

        >>> range(0, 1 << 32)
        range(0, 4294967296)

    For example, suppose only the values `0` through `9` were valid, and that you retrieved
    the following blacklist:


        >>> example_blacklist = RangeSet.from_text('''
        ...     5-8
        ...     0-2
        ...     4-7
        ... ''')
        >>> print(example_blacklist)
        0-2, 4-8

    The blacklist specifies ranges of IPs (inclusive of both the start and end value) that are
    **not** allowed. Then, the only IPs that this firewall allows are `3` and `9`, since those are
    the only numbers not in any range.

        >>> [ip for ip in range(10) if ip not in example_blacklist]
        [3, 9]

    Given the list of blocked IPs you retrieved from the firewall (your puzzle input), **what is
    the lowest-valued IP** that is not blocked?

        >>> part_1(example_blacklist)
        part 1: first allowed IP address is 3
        3
    """

    first_allowed = ranges.ranges[0].vmax + 1
    print(f"part 1: first allowed IP address is {first_allowed}")
    return first_allowed


def part_2(ranges: 'RangeSet', total_ips_count: int = 1 << 32) -> int:
    """
    **How many IPs** are allowed by the blacklist?

        >>> example_blacklist = RangeSet.from_file(data_path(__file__, 'example.txt'))
        >>> print(example_blacklist)
        0-2, 4-8
        >>> part_2(example_blacklist, total_ips_count=10)
        part 2: there are total 2 allowed IPs
        2
    """

    allowed_count = total_ips_count - len(ranges)
    print(f"part 2: there are total {allowed_count} allowed IPs")
    return allowed_count


class Range:
    def __init__(self, vmin, vmax):
        vmin, vmax = int(vmin), int(vmax)
        if vmin > vmax:
            vmin, vmax = vmax, vmin
        self.vmin = vmin
        self.vmax = vmax

    def __repr__(self):
        return f'{type(self).__name__}({self.vmin}, {self.vmax})'

    def __str__(self):
        return f'{self.vmin}-{self.vmax}'

    def __len__(self):
        return self.vmax - self.vmin + 1

    def __iter__(self):
        yield from range(self.vmin, self.vmax+1)

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
        Logical conjuction of two ranges. Result contains only items present in both.

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
        Logical disjunction of two ranges. Contains items present in either.
        However if the two ranges are disjunct (no common items), `None` is returned.

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
    def _simplify(ranges: Iterable[Range]) -> list[Range]:
        simplified_ranges: list[Range] = []
        for range_ in ranges:
            # combine with as many other ranges as possible
            while True:
                merged_range = next((xr for xr in simplified_ranges if range_ | xr), None)
                if merged_range:
                    # found one to merge with
                    simplified_ranges.remove(merged_range)
                    range_ = range_ | merged_range
                else:
                    # nothing to merge with -> we are done for this particular range
                    simplified_ranges.append(range_)
                    break

        return sorted(simplified_ranges, key=lambda r: r.vmin)

    def __repr__(self):
        return f'{type(self).__name__}({self.ranges!r})'

    def __str__(self):
        return ", ".join(str(r) for r in self.ranges)

    def __contains__(self, item):
        return any(item in r for r in self.ranges)

    def __len__(self):
        return sum(len(r) for r in self.ranges)

    def __iter__(self):
        for r in self.ranges:
            yield from r

    @classmethod
    def from_file(cls, fn: str) -> Self:
        return cls.from_lines(open(fn))

    @classmethod
    def from_text(cls, text: str) -> Self:
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        return cls(Range(*line.strip().split('-')) for line in lines)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    ranges = RangeSet.from_file(input_path)
    result_1 = part_1(ranges)
    result_2 = part_2(ranges)
    return result_1, result_2


if __name__ == '__main__':
    main()
