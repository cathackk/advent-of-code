"""
Advent of Code 2021
Day 8: Seven Segment Search
https://adventofcode.com/2021/day/8
"""

from itertools import permutations
from typing import Iterable

from tqdm import tqdm

from common.utils import relative_path


def part_1(entries: Iterable['Entry']) -> int:
    """
    You barely reach the safety of the cave when the whale smashes into the cave mouth, collapsing
    it. Sensors indicate another exit to this cave at a much greater depth, so you have no choice
    but to press on.

    As your submarine slowly makes its way through the cave system, you notice that the four-digit
    seven-segment displays in your submarine are malfunctioning; they must have been damaged during
    the escape. You'll be in a lot of trouble without them, so you'd better figure out what's wrong.

    Each digit of a seven-segment display is rendered by turning on or off any of seven segments
    named `a` through `g`:

          0:      1:      2:      3:      4:
         aaaa    ····    aaaa    aaaa    ····
        b    c  ·    c  ·    c  ·    c  b    c
        b    c  ·    c  ·    c  ·    c  b    c
         ····    ····    dddd    dddd    dddd
        e    f  ·    f  e    ·  ·    f  ·    f
        e    f  ·    f  e    ·  ·    f  ·    f
         gggg    ····    gggg    gggg    ····

          5:      6:      7:      8:      9:
         aaaa    aaaa    aaaa    aaaa    aaaa
        b    ·  b    ·  ·    c  b    c  b    c
        b    ·  b    ·  ·    c  b    c  b    c
         dddd    dddd    ····    dddd    dddd
        ·    f  e    f  ·    f  e    f  ·    f
        ·    f  e    f  ·    f  e    f  ·    f
         gggg    gggg    ····    gggg    gggg

    So, to render a `1`, only segments `c` and `f` would be turned on; the rest would be off.
    To render a `7`, only segments `a`, `c`, and `f` would be turned on.

    The problem is that the signals which control the segments have been mixed up on each display.
    The submarine is still trying to display numbers by producing output on signal wires `a` through
    `g`, but those wires are connected to segments **randomly**. Worse, the wire/segment connections
    are mixed up separately for each four-digit display! (All of the digits within a display use the
    same connections, though.)

    So, you might know that only signal wires `b` and `g` are turned on, but that doesn't mean
    segments `b` and `g` are turned on: the only digit that uses two segments is `1`, so it must
    mean segments c and f are meant to be on. With just that information, you still can't tell which
    wire (`b`/`g`) goes to which segment (`c`/`f`). For that, you'll need to collect more
    information.

    For each display, you watch the changing signals for a while, make a note of **all ten unique
    signal patterns** you see, and then write down a single **four digit output value** (your puzzle
    input). Using the signal patterns, you should be able to work out which pattern corresponds to
    which digit.

    For example, here is what you might see in a single entry in your notes:

        >>> e = Entry.from_line(
        ...     'acedgfb cdfbe gcdfa fbcad dab cefabd cdfgeb eafb cagedb ab | '
        ...     'cdfeb fcadb cdfeb cdbaf'
        ... )
        >>> e.unique_patterns
        ('acedgfb', 'cdfbe', 'gcdfa', 'fbcad', 'dab', 'cefabd', 'cdfgeb', 'eafb', 'cagedb', 'ab')
        >>> e.output_patterns
        ('cdfeb', 'fcadb', 'cdfeb', 'cdbaf')

    Each entry consists of ten **unique signal patterns**, a `|` delimiter, and finally the **four
    digit output value**. Within an entry, the same wire/segment connections are used (but you don't
    know what the connections actually are). The unique signal patterns correspond to the ten
    different ways the submarine tries to render a digit using the current wire/segment connections.
    Because `7` is the only digit that uses three segments, `dab` in the above example means that to
    render a `7`, signal lines `d`, `a`, and `b` are on. Because `4` is the only digit that uses
    four segments, `eafb` means that to render a `4`, signal lines `e`, `a`, `f`, and `b` are on.

    Using this information, you should be able to work out which combination of signal wires
    corresponds to each of the ten digits. Then, you can decode the four digit output value.
    Unfortunately, in the above example, all of the digits in the output value (`cdfeb fcadb cdfeb
    cdbaf`) use five segments and are more difficult to deduce.

    For now, **focus on the easy digits**. Consider this larger example:

        >>> example = entries_from_text('''
        ...
        ...   be cfbegad cbdgef fgaecd cgeb fdcge agebfd fecdb fabcd edb | fdgacbe cefdb cefbgd gcbe
        ...   edbfga begcd cbg gc gcadebf fbgde acbgfd abcde gfcbed gfec | fcgedb cgb dgebacf gc
        ...   fgaebd cg bdaec gdafb agbcfd gdcbef bgcad gfac gcb cdgabef | cg cg fdcagb cbg
        ...   fbegcd cbd adcefb dageb afcb bc aefdc ecdab fgdeca fcdbega | efabcd cedba gadfec cb
        ...   aecbfdg fbg gf bafeg dbefa fcge gcbea fcaegb dgceab fcbdga | gecf egdcabf bgf bfgea
        ...   fgeab ca afcebg bdacfeg cfaedg gcfdb baec bfadeg bafgc acf | gebdcfa ecba ca fadegcb
        ...   dbcfg fgd bdegcaf fgec aegbdf ecdfab fbedc dacgb gdcebf gf | cefg dcbef fcge gbcadfe
        ...   bdfegc cbegaf gecbf dfcage bdacg ed bedf ced adcbefg gebcd | ed bcgafe cdgba cbgef
        ...   egadfb cdbfeg cegd fecab cgb gbdefca cg fgcdab egfdb bfceg | gbdfcae bgc cg cgb
        ...   gcafb gcf dcaebfg ecagb gf abcdeg gaef cafbge fdbac fegbdc | fgae cfgab fg bagce
        ...
        ... ''')
        >>> len(example)
        10

    Because the digits `1`, `4`, `7`, and `8` each use a unique number of segments, you should be
    able to tell which combinations of signals correspond to those digits. Counting **only digits in
    the output values** (the part after `|` on each line), in the above example, there are **`26`**
    instances of digits that use a unique number of segments (highlighted above).

    **In the output values, how many times do digits 1, 4, 7, or 8 appear?**

        >>> part_1(example)
        part 1: easy digits appear 26 times
        26
    """

    easy_lengths = {len(DIGIT_TO_SEGMENTS[d]) for d in (1, 4, 7, 8)}
    result = sum(
        1
        for entry in entries
        for pattern in entry.output_patterns
        if len(pattern) in easy_lengths
    )

    print(f"part 1: easy digits appear {result} times")
    return result


def part_2(entries: Iterable['Entry']) -> int:
    """
    Through a little deduction, you should now be able to determine the remaining digits. Consider
    again the first example above:

        >>> en = Entry.from_line(
        ...     'acedgfb cdfbe gcdfa fbcad dab cefabd cdfgeb eafb cagedb ab | '
        ...     'cdfeb fcadb cdfeb cdbaf'
        ... )

    After some careful analysis, the mapping between signal wires and segments only make sense in
    the following configuration:

        >>> sol = solve(en)
        >>> sol.permutation
        ('d', 'e', 'a', 'f', 'g', 'b', 'c')
        >>> sol.draw()
         dddd
        e    a
        e    a
         ffff
        g    b
        g    b
         cccc

    So, the unique signal patterns would correspond to the following digits:

        >>> print(sol)
        acedgfb: 8
        cdfbe: 5
        gcdfa: 2
        fbcad: 3
        dab: 7
        cefabd: 9
        cdfgeb: 6
        eafb: 4
        cagedb: 0
        ab: 1

    Then, the four digits of the output value can be decoded:

        >>> for op in sol.entry.output_patterns:
        ...     print(f'{op}: {sol.decode(op)}')
        cdfeb: 5
        fcadb: 3
        cdfeb: 5
        cdbaf: 3

    Therefore, the output value for this entry is:

        >>> sol.output_value
        5353

    Following this same process for each entry in the second, larger example above, the output value
    of each entry can be determined:

        >>> example = entries_from_file('data/08-example.txt')
        >>> for en in example:
        ...     ops = ' '.join(en.output_patterns)
        ...     sol = solve(en)
        ...     print(f'{ops}: {sol.output_value}')
        fdgacbe cefdb cefbgd gcbe: 8394
        fcgedb cgb dgebacf gc: 9781
        cg cg fdcagb cbg: 1197
        efabcd cedba gadfec cb: 9361
        gecf egdcabf bgf bfgea: 4873
        gebdcfa ecba ca fadegcb: 8418
        cefg dcbef fcge gbcadfe: 4548
        ed bcgafe cdgba cbgef: 1625
        gbdfcae bgc cg cgb: 8717
        fgae cfgab fg bagce: 4315

    Adding all of the output values in this larger example produces:

        >>> sum(solve(en).output_value for en in example)
        61229

    For each entry, determine all of the wire/segment connections and decode the four-digit output
    values. **What do you get if you add up all of the output values?**

        >>> part_2(example)
        part 2: sum of all output values is 61229
        61229
    """

    result = sum(solve(e).output_value for e in tqdm(entries, unit="entries", delay=1.0))

    print(f"part 2: sum of all output values is {result}")
    return result


#
#  aaaa
# b    c
# b    c
#  dddd
# e    f
# e    f
#  gggg
#
DIGIT_TO_SEGMENTS = {
    0: 'abcefg',
    1: 'cf',
    2: 'acdeg',
    3: 'acdfg',
    4: 'bcdf',
    5: 'abdfg',
    6: 'abdefg',
    7: 'acf',
    8: 'abcdefg',
    9: 'abcdfg',
}

SEGMENTS_TO_DIGIT = {segments: digit for digit, segments in DIGIT_TO_SEGMENTS.items()}


class Entry:
    def __init__(self, unique_patterns: Iterable[str], output_patterns: Iterable[str]):
        self.unique_patterns = tuple(unique_patterns)
        self.output_patterns = tuple(output_patterns)

        assert len(self.unique_patterns) == 10
        for pattern in self.unique_patterns + self.output_patterns:
            assert 1 <= len(pattern) <= 7
            pattern_set = set(pattern)
            assert len(pattern_set) == len(pattern)
            assert pattern_set.issubset('abcdefg')

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.unique_patterns!r}, {self.output_patterns!r})'

    def __str__(self) -> str:
        ups = ' '.join(self.unique_patterns)
        ops = ' '.join(self.output_patterns)
        return f'{ups} | {ops}'

    @classmethod
    def from_line(cls, line: str) -> 'Entry':
        ups, ops = line.strip().split('|')
        return cls(ups.split(), ops.split())


class EntrySolution:
    def __init__(self, entry: Entry, permutation: Iterable[str]):
        self.entry = entry
        self.permutation = tuple(permutation)
        self.decoder_dict = dict(zip(self.permutation, 'abcdefg'))
        assert ''.join(sorted(self.permutation)) == 'abcdefg'

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.entry!r}, {self.permutation!r})'

    def __str__(self) -> str:
        return '\n'.join(
            f'{pattern}: {self.decode(pattern)}'
            for pattern in self.entry.unique_patterns
        )

    def decode(self, pattern: str) -> int:
        return SEGMENTS_TO_DIGIT[''.join(sorted(self.decoder_dict[s] for s in pattern))]

    @property
    def output_value(self) -> int:
        return int(''.join(str(self.decode(pattern)) for pattern in self.entry.output_patterns))

    def draw(self, seg_width: int = 4, seg_height: int = 2) -> None:
        print(' ' + self.permutation[0] * seg_width)
        for _ in range(seg_height):
            print(self.permutation[1] + ' ' * seg_width + self.permutation[2])
        print(' ' + self.permutation[3] * seg_width)
        for _ in range(seg_height):
            print(self.permutation[4] + ' ' * seg_width + self.permutation[5])
        print(' ' + self.permutation[6] * seg_width)


def solve(entry: Entry) -> EntrySolution:
    # brute force time! try each segment permutation - 5040 is low enough
    for perm in permutations('abcdefg'):
        # create the solution and then test it:
        solution = EntrySolution(entry, perm)
        try:
            # try decoding each unique pattern in the entry with it
            for pattern in entry.unique_patterns:
                solution.decode(pattern)
        except KeyError:
            # something went wrong -> incorrect permutation
            continue
        else:
            # managed to decode everything! -> correct solution!
            return solution

    else:
        raise ValueError(f'failed to find solution for {entry}')


def entries_from_text(text: str) -> list[Entry]:
    return list(entries_from_lines(text.strip().split('\n')))


def entries_from_file(fn: str) -> list[Entry]:
    return list(entries_from_lines(open(relative_path(__file__, fn))))


def entries_from_lines(lines: Iterable[str]) -> Iterable[Entry]:
    return (Entry.from_line(line.strip()) for line in lines)


if __name__ == '__main__':
    entries_ = entries_from_file('data/08-input.txt')
    part_1(entries_)
    part_2(entries_)
