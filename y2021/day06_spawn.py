"""
Advent of Code 2021
Day 6: Lanternfish
https://adventofcode.com/2021/day/6
"""

from collections import Counter
from itertools import chain
from itertools import islice
from typing import Iterable
from typing import Iterator

from meta.aoc_tools import data_path


def part_1(state: Iterable[int], days: int = 80) -> int:
    """
    A massive school of glowing lanternfish swims past. They must spawn quickly to reach such large
    numbers - maybe **exponentially** quickly? You should model their growth rate to be sure.

    Although you know nothing about this specific species of lanternfish, you make some guesses
    about their attributes. Surely, each lanternfish creates a new lanternfish once every 7 days.

    However, this process isn't necessarily synchronized between every lanternfish - one lanternfish
    might have 2 days left until it creates another lanternfish, while another might have 4. So, you
    can model each fish as a single number that represents **the number of days until it creates
    a new lanternfish**.

    Furthermore, you reason, a **new** lanternfish would surely need slightly longer before it's
    capable of producing more lanternfish: two more days for its first cycle.

    So, suppose you have a lanternfish with an internal timer value of `3`:

        >>> State([3])
        State([3])

    - After one day, its internal timer would become `2`:

        >>> _.next_state()
        State([2])

    - After another day, its internal timer would become `1`:

        >>> _.next_state()
        State([1])

    - After another day, its internal timer would become `0`:

        >>> _.next_state()
        State([0])

    - After another day, its internal timer would reset to `6`, and it would create a new lantern-
      fish with an internal timer of `8`:

        >>> _.next_state()
        State([6, 8])

    - After another day, the first lanternfish would have an internal timer of `5`, and the second
      lanternfish would have an internal timer of `7`:

        >>> _.next_state()
        State([5, 7])

    A lanternfish that creates a new fish resets its timer to `6`, not `7` (because `0` is included
    as a valid timer value). The new lanternfish starts with an internal timer of `8` and does not
    start counting down until the next day.

    Realizing what you're trying to do, the submarine automatically produces a list of the ages of
    several hundred nearby lanternfish (your puzzle input). For example, suppose you were given
    the following list:

        >>> fish = [3, 4, 3, 1, 2]

    This list means that the first fish has an internal timer of `3`, the second fish has an inter-
    nal timer of `4`, and so on until the fifth fish, which has an internal timer of `2`. Simulating
    these fish over several days would proceed as follows:

        >>> fish_18 = simulate(fish, days=18, log=True)
        Initial state: 3,4,3,1,2
        After  1 day:  2,3,2,0,1
        After  2 days: 1,2,1,6,0,8
        After  3 days: 0,1,0,5,6,7,8
        After  4 days: 6,0,6,4,5,6,7,8,8
        After  5 days: 5,6,5,3,4,5,6,7,7,8
        After  6 days: 4,5,4,2,3,4,5,6,6,7
        After  7 days: 3,4,3,1,2,3,4,5,5,6
        After  8 days: 2,3,2,0,1,2,3,4,4,5
        After  9 days: 1,2,1,6,0,1,2,3,3,4,8
        After 10 days: 0,1,0,5,6,0,1,2,2,3,7,8
        After 11 days: 6,0,6,4,5,6,0,1,1,2,6,7,8,8,8
        After 12 days: 5,6,5,3,4,5,6,0,0,1,5,6,7,7,7,8,8
        After 13 days: 4,5,4,2,3,4,5,6,6,0,4,5,6,6,6,7,7,8,8
        After 14 days: 3,4,3,1,2,3,4,5,5,6,3,4,5,5,5,6,6,7,7,8
        After 15 days: 2,3,2,0,1,2,3,4,4,5,2,3,4,4,4,5,5,6,6,7
        After 16 days: 1,2,1,6,0,1,2,3,3,4,1,2,3,3,3,4,4,5,5,6,8
        After 17 days: 0,1,0,5,6,0,1,2,2,3,0,1,2,2,2,3,3,4,4,5,7,8
        After 18 days: 6,0,6,4,5,6,0,1,1,2,6,0,1,1,1,2,2,3,3,4,6,7,8,8,8,8

    Each day, a `0` becomes a `6` and adds a new `8` to the end of the list, while each other number
    decreases by `1` if it was present at the start of the day.

    In this example, after 18 days, there are a total of `26` fish.

        >>> len(fish_18)
        26

    After 80 days, there would be a total of **`5934`**.

        >>> fish_80 = simulate(fish, days=80)
        >>> len(fish_80)
        5934

    Find a way to simulate lanternfish. **How many lanternfish would there be after 80 days?**

        >>> part_1(fish)
        part 1: after 80 days, there will be 5934 fish
        5934
    """

    result = len(simulate(state, days=days))

    print(f"part 1: after {days} days, there will be {result} fish")
    return result


def part_2(state: Iterable[int], days: int = 256) -> int:
    """
    Suppose the lanternfish live forever and have unlimited food and space. Would they take over
    the entire ocean?

    After 256 days in the example above, there would be a total of `26984457539` lanternfish!

        >>> fish = [3, 4, 3, 1, 2]
        >>> fish_256 = simulate(fish, days=256)
        >>> len(fish_256)
        26984457539

    **How many lanternfish would there be after 256 days?**

        >>> part_2(fish)
        part 2: after 256 days, there will be 26984457539 fish
        26984457539
    """

    result = len(simulate(state, days=days))

    print(f"part 2: after {days} days, there will be {result} fish")
    return result


SPAWN_DAYS = 7
MATURING_DAYS = 2


class State:
    def __init__(self, values: Iterable[int]):
        self.values = list(values)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.values})'

    def __str__(self) -> str:
        return ','.join(str(val) for val in self.values)

    def __iter__(self) -> Iterator[int]:
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)

    def next_state(self) -> 'State':
        """
            >>> State([1, 2, 3, 3])
            State([1, 2, 3, 3])
            >>> _.next_state()
            State([0, 1, 2, 2])
            >>> _.next_state()
            State([6, 0, 1, 1, 8])
            >>> _.next_state()
            State([5, 6, 0, 0, 7, 8])
            >>> _.next_state()
            State([4, 5, 6, 6, 6, 7, 8, 8])
        """
        new_fish_count = sum(1 for val in self.values if val == 0)
        new_fish = (SPAWN_DAYS + MATURING_DAYS - 1 for _ in range(new_fish_count))
        existing_fish = (val - 1 if val > 0 else SPAWN_DAYS - 1 for val in self.values)
        return type(self)(chain(existing_fish, new_fish))


class StateOptimized:
    def __init__(self, values: Iterable[int] | Counter[int]):
        self.by_day = Counter(values)

    VALUES_ENUM_LIMIT = 100

    def __repr__(self) -> str:
        if len(self) < self.VALUES_ENUM_LIMIT:
            return f'{type(self).__name__}({list(self)})'
        else:
            return f'{type(self).__name__}({self.by_day})'

    def __str__(self) -> str:
        if len(self) < self.VALUES_ENUM_LIMIT:
            return ','.join(str(val) for val in self)
        else:
            return ','.join(str(val) for val in islice(iter(self), self.VALUES_ENUM_LIMIT)) + ',...'

    def __iter__(self) -> Iterator[int]:
        return self.by_day.elements()

    def __len__(self) -> int:
        return sum(self.by_day.values())

    def next_state(self) -> 'StateOptimized':
        """
            >>> StateOptimized([1, 2, 3, 3])
            StateOptimized([1, 2, 3, 3])
            >>> _.next_state()
            StateOptimized([0, 1, 2, 2])
            >>> _.next_state()
            StateOptimized([0, 1, 1, 6, 8])
            >>> _.next_state()
            StateOptimized([0, 0, 5, 6, 7, 8])
        """
        new_counts = Counter({
            day - 1: self.by_day[day]
            for day in range(1, SPAWN_DAYS + MATURING_DAYS)
        })
        new_counts[SPAWN_DAYS - 1] += self.by_day[0]
        new_counts[SPAWN_DAYS + MATURING_DAYS - 1] += self.by_day[0]
        return type(self)(new_counts)


def simulate(state_numbers: Iterable[int], days: int, log: bool = False) -> State | StateOptimized:
    state_cls: type[State | StateOptimized] = State if days < 100 else StateOptimized
    state = state_cls(state_numbers)

    days_width = len(str(days))

    if log:
        print(f'Initial state: {state}')

    for day in range(days):
        state = state.next_state()
        if log:
            print(f'After {day+1:{days_width}} {"days:" if day else "day: "} {state}')

    return state


def state_from_file(fn: str) -> State:
    return State(int(v) for v in next(open(fn)).strip().split(','))


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    state = state_from_file(input_path)
    result_1 = part_1(state)
    result_2 = part_2(state)
    return result_1, result_2


if __name__ == '__main__':
    main()
