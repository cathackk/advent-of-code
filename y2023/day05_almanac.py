"""
Advent of Code 2023
Day 5: If You Give A Seed A Fertilizer
https://adventofcode.com/2023/day/5
"""
from typing import Iterable

from common.file import relative_path
from common.iteration import chunks, last
from common.text import line_groups, parse_line


def part_1(almanac: 'Almanac') -> int:
    """
    You take the boat and find the gardener right where you were told he would be: managing a giant
    "garden" that looks more to you like a farm.

    "A water source? Island Island **is** the water source!" You point out that Snow Island isn't
    receiving any water.

    "Oh, we had to stop the water because we **ran out of sand** to filter it with! Can't make snow
    with dirty water. Don't worry, I'm sure we'll get more sand soon; we only turned off the water
    a few days... weeks... oh no." His face sinks into a look of horrified realization.

    "I've been so busy making sure everyone here has food that I completely forgot to check why we
    stopped getting more sand! There's a ferry leaving soon that is headed over in that direction -
    it's much faster than your boat. Could you please go check it out?"

    You barely have time to agree to this request when he brings up another. "While you wait for
    the ferry, maybe you can help us with our **food production problem**. The latest Island Island
    Almanac just arrived and we're having trouble making sense of it."

    The almanac (your puzzle input) lists all of the seeds that need to be planted. It also lists
    what type of soil to use with each kind of seed, what type of fertilizer to use with each kind
    of soil, what type of water to use with each kind of fertilizer, and so on. Every type of seed,
    soil, fertilizer and so on is identified with a number, but numbers are reused by each category
    - that is, soil `123` and fertilizer `123` aren't necessarily related to each other.

    For example:

        >>> al = Almanac.from_text('''
        ...     seeds: 79 14 55 13
        ...
        ...     seed-to-soil map:
        ...     50 98 2
        ...     52 50 48
        ...
        ...     soil-to-fertilizer map:
        ...     0 15 37
        ...     37 52 2
        ...     39 0 15
        ...
        ...     fertilizer-to-water map:
        ...     49 53 8
        ...     0 11 42
        ...     42 0 7
        ...     57 7 4
        ...
        ...     water-to-light map:
        ...     88 18 7
        ...     18 25 70
        ...
        ...     light-to-temperature map:
        ...     45 77 23
        ...     81 45 19
        ...     68 64 13
        ...
        ...     temperature-to-humidity map:
        ...     0 69 1
        ...     1 0 69
        ...
        ...     humidity-to-location map:
        ...     60 56 37
        ...     56 93 4
        ... ''')


    The almanac starts by listing which seeds need to be planted:

        >>> al.seeds
        [79, 14, 55, 13]

    The rest of the almanac contains a list of **maps** which describe how to convert numbers from
    a **source category** into numbers in a **destination category**. That is, the section that
    starts with `seed-to-soil map:` describes how to convert a **seed number** (the source) to
    a **soil number** (the destination). This lets the gardener and his team know which soil to use
    with which seeds, which water to use with which fertilizer, and so on.

    Rather than list every source number and its corresponding destination number one by one,
    the maps describe entire **ranges** of numbers that can be converted. Each line within a map
    contains three numbers: the **destination range start**, the **source range start**,
    and the **range length**.

    Consider again the example seed-to-soil map:

        50 98 2
        52 50 48

    The first line means that the source range starts at `98` and contains two values:
    `98` and `99`. The destination range is the same length, but it starts at `50`, so its two
    values are `50` and `51`. With this information, you know that seed number `98` corresponds
    to soil number `50` and that seed number `99` corresponds to soil number `51`.

        >>> al.convert('seed', 98)
        ('soil', 50)
        >>> al.convert('seed', 99)
        ('soil', 51)

    The second line means that the source range starts at `50` and contains `48` values: `50`, `51`,
    ..., `96`, `97`. This corresponds to a destination range starting at `52` and also containing
    48 values: `52`, `53`, ..., `98`, `99`:

        >>> al.convert('seed', 50)
        ('soil', 52)
        >>> al.convert('seed', 53)
        ('soil', 55)
        >>> al.convert('seed', 97)
        ('soil', 99)

    Any source numbers that **aren't mapped** correspond to the **same** destination number:

        >>> al.convert('seed', 10)
        ('soil', 10)
        >>> al.convert('seed', 100)
        ('soil', 100)

    So, the entire list of seed numbers and their corresponding soil numbers looks like this:

        >>> al.print_map_table('seed', [range(0, 2), range(48, 52), range(96, 100)])
        seed  soil
        0     0
        1     1
        ...   ...
        48    48
        49    49
        50    52
        51    53
        ...   ...
        96    98
        97    99
        98    50
        99    51

    With this map, you can look up the soil number required for each initial seed number:

      - Seed number `79` corresponds to soil number `81`.
      - Seed number `14` corresponds to soil number `14`.
      - Seed number `55` corresponds to soil number `57`.
      - Seed number `13` corresponds to soil number `13`.

        >>> [al.convert('seed', seed)[1] for seed in al.seeds]
        [81, 14, 57, 13]

    The gardener and his team want to get started as soon as possible, so they'd like to know
    the closest location that needs a seed. Using these maps, find **the lowest location number that
    corresponds to any of the initial seeds**. To do this, you'll need to convert each seed number
    through other categories until you can find its corresponding **location number**.
    In this example, the corresponding types are:

        >>> al.category_chain
        ['seed', 'soil', 'fertilizer', 'water', 'light', 'temperature', 'humidity', 'location']

        >>> list(al.convert_chain('seed', 79))  # doctest: +NORMALIZE_WHITESPACE
        [('seed', 79), ('soil', 81), ('fertilizer', 81), ('water', 81), ('light', 74),
         ('temperature', 78), ('humidity', 78), ('location', 82)]
        >>> list(al.convert_chain('seed', 14))  # doctest: +NORMALIZE_WHITESPACE
        [('seed', 14), ('soil', 14), ('fertilizer', 53), ('water', 49), ('light', 42),
         ('temperature', 42), ('humidity', 43), ('location', 43)]
        >>> list(al.convert_chain('seed', 55))  # doctest: +NORMALIZE_WHITESPACE
        [('seed', 55), ('soil', 57), ('fertilizer', 57), ('water', 53), ('light', 46),
         ('temperature', 82), ('humidity', 82), ('location', 86)]
        >>> list(al.convert_chain('seed', 13))  # doctest: +NORMALIZE_WHITESPACE
        [('seed', 13), ('soil', 13), ('fertilizer', 52), ('water', 41), ('light', 34),
         ('temperature', 34), ('humidity', 35), ('location', 35)]

        >>> [al.convert_through('seed', seed) for seed in al.seeds]
        [('location', 82), ('location', 43), ('location', 86), ('location', 35)]

    So, the lowest location number in this example is **`35`**.

        >>> min(_)
        ('location', 35)

    **What is the lowest location number that corresponds to any of the initial seed numbers?**

        >>> part_1(al)
        part 1: the lowest location number is 35
        35
    """

    category, amount = min(almanac.convert_through('seed', seed) for seed in almanac.seeds)

    print(f"part 1: the lowest {category} number is {amount}")
    return amount


def part_2(almanac: 'Almanac') -> int:
    """
    Everyone will starve if you only plant such a small number of seeds. Re-reading the almanac,
    it looks like the seeds: line actually describes **ranges of seed numbers**.

    The values on the initial `seeds:` line come in pairs. Within each pair, the first value is
    the **start** of the range and the second value is the **length** of the range. So, in the first
    line of the example above:

        seeds: 79 14 55 13

    This line describes two ranges of seed numbers to be planted in the garden. The first range
    starts with seed number `79` and contains `14` values: `79`, `80`, ..., `92`.
    The second range starts with seed number `55` and contains `13` values: `55`, `56`, ..., `67`.

        >>> al = Almanac.from_file('data/05-example.txt')
        >>> al.seed_ranges
        [range(79, 93), range(55, 68)]

    Now, rather than considering four seed numbers, you need to consider a total of **27** seed
    numbers.

        >>> sum(len(rng) for rng in al.seed_ranges)
        27

    In the above example, the lowest location number can be obtained from seed number 82:

        >>> list(al.convert_chain('seed', 82))  # doctest: +NORMALIZE_WHITESPACE
        [('seed', 82), ('soil', 84), ('fertilizer', 84), ('water', 84), ('light', 77),
         ('temperature', 45), ('humidity', 46), ('location', 46)]
        >>> al.convert_through_range('seed', al.seed_ranges)  # doctest: +NORMALIZE_WHITESPACE
        ('location',
         [range(82, 85), range(46, 56), range(60, 61),
          range(86, 90), range(94, 97), range(56, 60), range(97, 99)])

    So, the lowest location number is **`46`**:

        >>> _[0], min(r.start for r in _[1])
        ('location', 46)

    Consider all of the initial seed numbers listed in the ranges on the first line of the almanac.
    **What is the lowest location number that corresponds to any of the initial seed numbers?**

        >>> part_2(al)
        part 2: the lowest location number is 46
        46
    """

    category, ranges = almanac.convert_through_range('seed', almanac.seed_ranges)
    amount = min(r.start for r in ranges)

    print(f"part 2: the lowest {category} number is {amount}")
    return amount


class RangeMap:
    def __init__(self, ranges: Iterable[tuple[range, int]]):
        self.ranges = sorted(ranges, key=lambda ro: ro[0].start)
        self.full_ranges = list(self._create_full_ranges(self.ranges))

    @staticmethod
    def _create_full_ranges(ranges: Iterable[tuple[range, int]]) -> Iterable[tuple[range, int]]:
        # fills empty gaps between ranges
        prev_stop = 0
        for rng, offset in ranges:
            if prev_stop < rng.start:
                yield range(prev_stop, rng.start), 0
            yield rng, offset
            prev_stop = rng.stop

    def __getitem__(self, value: int) -> int:
        # TODO: also allow ranges?
        return self.translate_value(value)

    def translate_value(self, value: int) -> int:
        _, offset = self._find_range(value)
        return value + offset

    def translate_range(self, input_range: range) -> Iterable[range]:
        remaining_range = input_range

        while remaining_range:
            matching_range, offset = self._find_range(remaining_range.start)
            if matching_range:
                result_range = range(
                    remaining_range.start + offset,
                    min(matching_range.stop, remaining_range.stop) + offset
                )
            else:
                result_range = remaining_range

            yield result_range
            remaining_range = range(
                remaining_range.start + len(result_range),
                remaining_range.stop
            )

    def _find_range(self, value: int) -> tuple[range | None, int]:
        return next(
            (
                (range_, offset)
                for range_, offset in self.full_ranges
                if value in range_
            ),
            (None, 0)
        )

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'RangeMap':
        def ranges() -> Iterable[tuple[range, int]]:
            for line in lines:
                dest, src, length = line.split(' ')
                yield range((start := int(src)), start + int(length)), int(dest) - start

        return cls(ranges())


class Almanac:
    def __init__(self, seeds: Iterable[int], maps: Iterable[tuple[tuple[str, str], RangeMap]]):
        self.seeds = list(seeds)
        self.seed_ranges = [range(start, start + length) for start, length in chunks(self.seeds, 2)]
        self.range_maps: dict[str, RangeMap] = {}
        self.category_map: dict[str, str] = {}
        self.category_chain = ['seed']

        for (src, dest), map_ in maps:
            self.range_maps[src] = map_
            self.category_map[src] = dest
            assert src == self.category_chain[-1]
            self.category_chain.append(dest)

    def convert(self, category: str, amount: int) -> tuple[str, int]:
        return self.category_map[category], self.range_maps[category][amount]

    def convert_chain(self, category: str, amount: int) -> Iterable[tuple[str, int]]:
        yield category, amount
        while category in self.category_map:
            category, amount = self.convert(category, amount)
            yield category, amount

    def convert_through(self, category: str, amount: int) -> tuple[str, int]:
        return last(self.convert_chain(category, amount))

    def convert_range(self, category: str, ranges: Iterable[range]) -> tuple[str, list[range]]:
        return self.category_map[category], [
            output_range
            for input_range in ranges
            for output_range in self.range_maps[category].translate_range(input_range)
        ]

    def convert_chain_range(
        self, category: str, ranges: Iterable[range]
    ) -> Iterable[tuple[str, list[range]]]:
        ranges_list = list(ranges)
        yield category, ranges_list
        while category in self.category_map:
            category, ranges_list = self.convert_range(category, ranges_list)
            yield category, ranges_list

    def convert_through_range(
        self, category: str, ranges: Iterable[range]
    ) -> tuple[str, list[range]]:
        return last(self.convert_chain_range(category, ranges))

    def print_map_table(self, category: str, ranges: Iterable[range]) -> None:
        src, dest = category, self.category_map[category]
        print(src + '  ' + dest)
        for rng_no, rng in enumerate(ranges):
            if rng_no > 0:
                print('...'.ljust(len(src)) + '  ' + '...')
            for src_value in rng:
                _, dest_value = self.convert(category, src_value)
                print(str(src_value).ljust(len(src)) + '  ' + str(dest_value))

    @classmethod
    def from_file(cls, fn: str) -> 'Almanac':
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_text(cls, text: str) -> 'Almanac':
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Almanac':
        groups = line_groups(lines)
        seeds_line, = next(groups)
        seeds = [int(val) for val in parse_line(seeds_line, 'seeds: $')[0].split(' ')]

        def maps() -> Iterable[tuple[tuple[str, str], RangeMap]]:
            for map_group in groups:
                assert len(map_group) > 1
                src, dest = parse_line(map_group[0], '$-to-$ map:')
                yield (src, dest), RangeMap.from_lines(map_group[1:])

        return cls(seeds=seeds, maps=maps())


def main(input_fn: str = 'data/05-input.txt') -> tuple[int, int]:
    almanac = Almanac.from_file(input_fn)
    result_1 = part_1(almanac)
    result_2 = part_2(almanac)
    return result_1, result_2


if __name__ == '__main__':
    main()
