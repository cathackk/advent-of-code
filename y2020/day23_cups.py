"""
Advent of Code 2020
Day 23: Crab Cups
https://adventofcode.com/2020/day/23
"""

from itertools import chain
from typing import Iterable
from typing import List
from typing import Optional

from tqdm import tqdm

from chain import Link


def part_1(cups: 'Cups', moves: int = 100) -> str:
    """
    The small crab challenges *you* to a game! The crab is going to mix up some cups, and you have
    to predict where they'll end up.

    The cups will be arranged in a circle and labeled *clockwise* (your puzzle input). For example,
    if your labeling were `32415`, there would be five cups in the circle; going clockwise around
    the circle from the first cup, the cups would be labeled `3`, `2`, `4`, `1`, `5`, and then back
    to 3 again.

    Before the crab starts, it will designate the first cup in your list as the *current cup*. The
    crab is then going to do *100 moves*.

    Each move, the crab does the following actions:

        - The crab picks up the *three cups* that are immediately *clockwise* of the current cup.
          They are removed from the circle; cup spacing is adjusted as necessary to maintain the
          circle.
        - The crab selects a *destination cup*: the cup with a *label* equal to the *current cup's*
          label minus one. If this would select one of the cups that was just picked up, the crab
          will keep subtracting one until it finds a cup that wasn't just picked up. If at any
          point in this process the value goes below the lowest value on any cup's label, it *wraps
          around* to the highest value on any cup's label instead.
        - The crab places the cups it just picked up so that they are *immediately clockwise* of
          the destination cup. They keep the same order as when they were picked up.
        - The crab selects a new *current cup*: the cup which is immediately clockwise of the
          current cup.

    For example, suppose your cup labeling were `389125467`.

        >>> cups = Cups.from_line('389125467')
        >>> cups
        Cups([3, 8, 9, 1, 2, 5, 4, 6, 7])

    If the crab were to do merely 10 moves, the following changes would occur:

        >>> cups.play(moves=10, print_progress=True)
        -- move 1 --
        cups: (3) 8  9  1  2  5  4  6  7
        pick up: 8, 9, 1
        destination: 2
        -- move 2 --
        cups:  3 (2) 8  9  1  5  4  6  7
        pick up: 8, 9, 1
        destination: 7
        -- move 3 --
        cups:  3  2 (5) 4  6  7  8  9  1
        pick up: 4, 6, 7
        destination: 3
        -- move 4 --
        cups:  7  2  5 (8) 9  1  3  4  6
        pick up: 9, 1, 3
        destination: 7
        -- move 5 --
        cups:  3  2  5  8 (4) 6  7  9  1
        pick up: 6, 7, 9
        destination: 3
        -- move 6 --
        cups:  9  2  5  8  4 (1) 3  6  7
        pick up: 3, 6, 7
        destination: 9
        -- move 7 --
        cups:  7  2  5  8  4  1 (9) 3  6
        pick up: 3, 6, 7
        destination: 8
        -- move 8 --
        cups:  8  3  6  7  4  1  9 (2) 5
        pick up: 5, 8, 3
        destination: 1
        -- move 9 --
        cups:  7  4  1  5  8  3  9  2 (6)
        pick up: 7, 4, 1
        destination: 5
        -- move 10 --
        cups: (5) 7  4  1  8  3  9  2  6
        pick up: 7, 4, 1
        destination: 3
        -- final --
        cups:  5 (8) 3  7  4  1  9  2  6
        Cups([8, 3, 7, 4, 1, 9, 2, 6, 5])

    In the above example, the cups' values are the labels as they appear moving clockwise around
    the circle; the *current cup* is marked with `( )`.

    After the crab is done, what order will the cups be in? Starting *after the cup labeled 1*,
    collect the other cups' labels clockwise into a single string with no extra characters; each
    number except `1` should appear exactly once. In the above example, after 10 moves, the cups
    clockwise from 1 are labeled `9`, `2`, `6`, `5`, and so on, producing `92658374`.

        >>> cups.collect(after=1)
        '92658374'

    If the crab were to complete all 100 moves, the order after cup 1 would be `67384529`.

        >>> Cups.from_line('389125467').play(moves=100).collect(after=1)
        '67384529'

    Using your labeling, simulate 100 moves. *What are the labels on the cups after cup 1?*

        >>> part_1(Cups.from_line('389125467'))
        part 1: after 100 moves, cups after `1` are labeled: 67384529
        '67384529'
    """

    result = Cups(cups).play(moves).collect()

    print(f"part 1: after {moves} moves, cups after `1` are labeled: {result}")
    return result


def part_2(cups: 'Cups', moves=10_000_000) -> int:
    """
    Due to what you can only assume is a mistranslation (you're not exactly fluent in Crab), you
    are quite surprised when the crab starts arranging *many* cups in a circle on your raft - *one
    million* (1_000_000) in total.

    Your labeling is still correct for the first few cups; after that, the remaining cups are just
    numbered in an increasing fashion starting from the number after the highest number in your
    list and proceeding one by one until one million is reached. (For example, if your labeling
    were `54321`, the cups would be numbered `5`, `4`, `3`, `2`, `1`, and then start counting up
    from `6` until one million is reached.) In this way, every number from one through one million
    is used exactly once.

        >>> cups = Cups.from_line('54321').grown_to(1_000_000)
        >>> len(cups)
        1000000
        >>> cups.find(1)
        Link(1, prev_link=Link(2, ...), next_link=Link(6, ...))
        >>> cups.find(10)
        Link(10, prev_link=Link(9, ...), next_link=Link(11, ...))
        >>> cups.find(1_000_000)
        Link(1000000, prev_link=Link(999999, ...), next_link=Link(5, ...))


    After discovering where you made the mistake in translating Crab Numbers, you realize the small
    crab isn't going to do merely 100 moves; the crab is going to do *ten million* (`10_000_000`)
    moves!

    The crab is going to hide your stars - one each - under the *two cups that will end up
    immediately clockwise of cup `1`*. You can have them if you predict what the labels on those
    cups will be when the crab is finished.

    In the above example (`389125467`), this would be `934001` and then `159792`:

        >>> cups = Cups.from_line('389125467').grown_to(1_000_000)
        >>> len(cups)
        1000000
        >>> cup_1 = cups.play(moves=10_000_000).find(label=1)
        >>> (cup_1.next_link.value, cup_1.next_link.next_link.value)
        (934001, 159792)

    Multiplying these together produces:

        >>> 934001 * 159792
        149245887792

    Determine which two cups will end up immediately clockwise of cup `1`.
    *What do you get if you multiply their labels together?*

        >>> part_2(Cups.from_line('389125467'))
        part 2: after 10000000 moves, two cups after `1` are 934001, 159792 -> 149245887792
        149245887792
    """

    cup_1 = cups.grown_to(1_000_000).play(moves).find(label=1)
    value_a = cup_1.next_link.value
    value_b = cup_1.next_link.next_link.value
    result = value_a * value_b

    print(f"part 2: after {moves} moves, two cups after `1` are {value_a}, {value_b} -> {result}")
    return result


class Cups:
    def __init__(self, labels: Iterable[int]):
        self.current, last, length = Link.build_chain(labels)
        self.current.connect_to(prev_link=last)
        self.index = Cups._build_index(self.current, length)

    @classmethod
    def from_line(cls, line: str):
        return cls(int(c) for c in line.strip())

    @classmethod
    def from_file(cls, fn: str):
        return cls.from_line(next(open(fn)))

    @staticmethod
    def _build_index(current: Link, length: int) -> List[Link]:
        index: List[Optional[Link]] = [None] * length
        head = current
        while True:
            assert 1 <= head.value <= length, head
            index[head.value - 1] = head
            head = head.next_link
            if head is current:
                break

        assert all(link is not None for link in index)
        return index

    def grown_to(self, count: int) -> 'Cups':
        return type(self)(chain(
            self,
            range(len(self) + 1, count + 1)
        ))

    def play(self, moves: int, print_progress: bool = False) -> 'Cups':
        for move in tqdm(range(moves)):
            if print_progress:
                self._print_cups(move)

            # pick three cups
            picked_cups = self.pick_up(3)
            if print_progress:
                picked_up_text = ", ".join(str(v) for v in picked_cups)
                print(f"pick up: {picked_up_text}")

            # determine destination label
            destination_label = self.wrap_label(self.current.value - 1)
            while destination_label in picked_cups:
                destination_label = self.wrap_label(destination_label - 1)

            # find the destination cup
            destination = self.find(label=destination_label)
            assert destination is not None
            if print_progress:
                print(f"destination: {destination}")

            # insert the picked cups
            after_destination = destination.next_link
            first_picked = picked_cups
            first_picked.connect_to(prev_link=destination)
            last_picked = first_picked.follow(steps=2)
            last_picked.connect_to(next_link=after_destination)

            # shift the current cup
            self.current = self.current.next_link

        # game over
        if print_progress:
            self._print_cups(moves, final=True)
        return self

    def _print_cups(self, move: int, final: bool = False):
        if not final:
            print(f"-- move {move + 1} --")
        else:
            print(f"-- final --")

        first = self.current.follow(-(move % len(self)))

        cups_text = "".join(
            f"({v})" if v == self.current.value else f" {v} "
            for v in first
        ).rstrip()

        print(f"cups: {cups_text}")

    def wrap_label(self, label: int) -> int:
        wrapped = label % len(self)
        return wrapped if wrapped > 0 else len(self)

    def pick_up(self, count: int) -> Link:
        first_picked = self.current.next_link
        last_picked = first_picked.follow(count - 1)
        before_first = first_picked.prev_link
        after_last = last_picked.next_link

        first_picked.prev_link = None
        last_picked.next_link = None
        before_first.next_link = after_last
        after_last.prev_link = before_first

        return first_picked

    def find(self, label: int) -> Optional[Link]:
        return self.index[label - 1]

    def collect(self, after: int = 1) -> str:
        return ''.join(str(v) for v in list(self.find(label=after))[1:])

    def __len__(self):
        return len(self.index)

    def __iter__(self):
        return iter(self.current)

    def __repr__(self):
        return f'{type(self).__name__}({list(self)!r})'


if __name__ == '__main__':
    cups_ = Cups.from_file("data/23-input.txt")
    assert len(cups_) == 9

    part_1(cups_)
    part_2(cups_)
