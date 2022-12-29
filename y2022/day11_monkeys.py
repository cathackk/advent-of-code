"""
Advent of Code 2022
Day 11: Monkey in the Middle
https://adventofcode.com/2022/day/11
"""

import math
from dataclasses import dataclass
from typing import Callable
from typing import Iterable
from typing import Iterator

from common.math import lcm
from common.text import line_groups
from common.text import parse_line
from meta.aoc_tools import data_path


def part_1(monkeys: list['Monkey'], rounds_count: int = 20) -> int:
    r"""
    As you finally start making your way upriver, you realize your pack is much lighter than you
    remember. Just then, one of the items from your pack goes flying overhead. Monkeys are playing
    Keep Away with your missing things!

    To get your stuff back, you need to be able to predict where the monkeys will throw your items.
    After some careful observation, you realize the monkeys operate based on **how worried you are
    about each item**.

    You take some notes (your puzzle input) on the items each monkey currently has, how worried you
    are about those items, and how the monkey makes decisions based on your worry level.

    For example:

        >>> ms = monkeys_from_text('''
        ...     Monkey 0:
        ...       Starting items: 79, 98
        ...       Operation: new = old * 19
        ...       Test: divisible by 23
        ...         If true: throw to monkey 2
        ...         If false: throw to monkey 3
        ...
        ...     Monkey 1:
        ...       Starting items: 54, 65, 75, 74
        ...       Operation: new = old + 6
        ...       Test: divisible by 19
        ...         If true: throw to monkey 2
        ...         If false: throw to monkey 0
        ...
        ...     Monkey 2:
        ...       Starting items: 79, 60, 97
        ...       Operation: new = old * old
        ...       Test: divisible by 13
        ...         If true: throw to monkey 1
        ...         If false: throw to monkey 3
        ...
        ...     Monkey 3:
        ...       Starting items: 74
        ...       Operation: new = old + 3
        ...       Test: divisible by 17
        ...         If true: throw to monkey 0
        ...         If false: throw to monkey 1
        ... ''')
        >>> len(ms)
        4

    Each monkey has several attributes:

      - `Starting items` lists your **worry level** for each item the monkey is currently holding in
        the order they will be inspected.

        >>> [m.starting_items for m in ms]
        [[79, 98], [54, 65, 75, 74], [79, 60, 97], [74]]

      - `Operation` shows how your worry level changes as that monkey inspects an item.
        (An operation like `new = old * 5` means that your worry level after the monkey inspected
        the item is five times whatever your worry level was before inspection.)

        >>> (op_0 := ms[0].operation)
        Operation('old', '*', 19)
        >>> op_0(1), op_0(6), op_0(20)
        (19, 114, 380)
        >>> (op_1 := ms[1].operation)
        Operation('old', '+', 6)
        >>> op_1(1), op_1(10), op_1(100)
        (7, 16, 106)
        >>> (op_2 := ms[2].operation)
        Operation('old', '*', 'old')
        >>> op_2(1), op_2(2), op_2(9)
        (1, 4, 81)
        >>> ms[3].operation
        Operation('old', '+', 3)

      - `Test` shows how the monkey uses your worry level to decide where to throw an item next.
        - `If true` shows what happens with an item if the `Test` was true.
        - `If false` shows what happens with an item if the `Test` was false.

        >>> (test_0 := ms[0].test)
        Test(divisible_by=23, if_true=2, if_false=3)
        >>> test_0(10), test_0(23), test_0(45), test_0(46)
        (3, 2, 3, 2)
        >>> (test_1 := ms[1].test)
        Test(divisible_by=19, if_true=2, if_false=0)
        >>> test_1(0), test_1(10), test_1(40), test_1(190)
        (2, 0, 0, 2)
        >>> ms[2].test
        Test(divisible_by=13, if_true=1, if_false=3)
        >>> ms[3].test
        Test(divisible_by=17, if_true=0, if_false=1)

    After each monkey inspects an item but before it tests your worry level, your relief that the
    monkey's inspection didn't damage the item causes your worry level to be **divided by three**
    and rounded down to the nearest integer.

    The monkeys take turns inspecting and throwing items. On a single monkey's **turn**, it inspects
    and throws all of the items it is holding one at a time and in the order listed. Monkey `0` goes
    first, then monkey `1`, and so on until each monkey has had one turn. The process of each monkey
    taking a single turn is called a round.

    When a monkey throws an item to another monkey, the item goes on the **end** of the recipient
    monkey's list. A monkey that starts a round with no items could end up inspecting and throwing
    many items by the time its turn comes around. If a monkey is holding no items at the start of
    its turn, its turn ends.

    In the above example, the first round proceeds into:

        >>> game = play(ms)
        >>> (state_1 := next(game)) # doctest: +NORMALIZE_WHITESPACE
        State(round_num=1,
              items=([20, 23, 27, 26], [2080, 25, 167, 207, 401, 1046], [], []),
              inspect_counts=(2, 4, 3, 5))
        >>> print(state_1)
        After round 1, the monkeys are holding items with these worry levels:
        Monkey 0: 20, 23, 27, 26
        Monkey 1: 2080, 25, 167, 207, 401, 1046
        Monkey 2:
        Monkey 3:

    Monkeys 2 and 3 aren't holding any items at the end of the round; they both inspected items
    during the round and threw them all before the round ended.

    This process continues for a few more rounds:

        >>> print(next(game))
        After round 2, the monkeys are holding items with these worry levels:
        Monkey 0: 695, 10, 71, 135, 350
        Monkey 1: 43, 49, 58, 55, 362
        Monkey 2:
        Monkey 3:
        >>> print(next(game))
        After round 3, the monkeys are holding items with these worry levels:
        Monkey 0: 16, 18, 21, 20, 122
        Monkey 1: 1468, 22, 150, 286, 739
        Monkey 2:
        Monkey 3:
        >>> print(next(game))
        After round 4, the monkeys are holding items with these worry levels:
        Monkey 0: 491, 9, 52, 97, 248, 34
        Monkey 1: 39, 45, 43, 258
        Monkey 2:
        Monkey 3:
        >>> print(next(game))
        After round 5, the monkeys are holding items with these worry levels:
        Monkey 0: 15, 17, 16, 88, 1037
        Monkey 1: 20, 110, 205, 524, 72
        Monkey 2:
        Monkey 3:
        >>> print(next(game))
        After round 6, the monkeys are holding items with these worry levels:
        Monkey 0: 8, 70, 176, 26, 34
        Monkey 1: 481, 32, 36, 186, 2190
        Monkey 2:
        Monkey 3:
        >>> print(next(game))
        After round 7, the monkeys are holding items with these worry levels:
        Monkey 0: 162, 12, 14, 64, 732, 17
        Monkey 1: 148, 372, 55, 72
        Monkey 2:
        Monkey 3:
        >>> print(next(game))
        After round 8, the monkeys are holding items with these worry levels:
        Monkey 0: 51, 126, 20, 26, 136
        Monkey 1: 343, 26, 30, 1546, 36
        Monkey 2:
        Monkey 3:
        >>> print(next(game))
        After round 9, the monkeys are holding items with these worry levels:
        Monkey 0: 116, 10, 12, 517, 14
        Monkey 1: 108, 267, 43, 55, 288
        Monkey 2:
        Monkey 3:
        >>> print(next(game))
        After round 10, the monkeys are holding items with these worry levels:
        Monkey 0: 91, 16, 20, 98
        Monkey 1: 481, 245, 22, 26, 1092, 30
        Monkey 2:
        Monkey 3:

    ...

        >>> print(run_until_round(game, 15))
        After round 15, the monkeys are holding items with these worry levels:
        Monkey 0: 83, 44, 8, 184, 9, 20, 26, 102
        Monkey 1: 110, 36
        Monkey 2:
        Monkey 3:

    ...

        >>> print(state_20 := run_until_round(game, 20))
        After round 20, the monkeys are holding items with these worry levels:
        Monkey 0: 10, 12, 14, 26, 34
        Monkey 1: 245, 93, 53, 199, 115
        Monkey 2:
        Monkey 3:

    Chasing all of the monkeys at once is impossible; you're going to have to focus on the **two
    most active** monkeys if you want any hope of getting your stuff back. Count the **total number
    of times each monkey inspects items** over 20 rounds:

        >>> state_20.inspect_counts
        (101, 95, 7, 105)

    In this example, the two most active monkeys inspected items `101` and `105` times. The level of
    **monkey business** in this situation can be found by multiplying these together: **`10605`**.

        >>> state_20.monkey_business()
        10605

    Figure out which monkeys to chase by counting how many items they inspect over 20 rounds.
    **What is the level of monkey business after 20 rounds of stuff-slinging simian shenanigans?**

        >>> part_1(ms)
        part 1: after 20 rounds, monkey business is 10605
        10605
    """

    result = run_until_round(play(monkeys), rounds_count).monkey_business()

    print(f"part 1: after {rounds_count} rounds, monkey business is {result}")
    return result


def part_2(monkeys: list['Monkey'], rounds_count: int = 10_000) -> int:
    """
    You're worried you might not ever get your items back. So worried, in fact, that your relief
    that a monkey's inspection didn't damage an item **no longer causes your worry level to be
    divided by three**.

    Unfortunately, that relief was all that was keeping your worry levels from reaching
    **ridiculous levels**. You'll need to **find another way to keep your worry levels manageable**.

    At this rate, you might be putting up with these monkeys for a **very long time**
    - possibly **10_000 rounds**!

    With these new rules, you can still figure out the monkey business after 10_000 rounds.
    Using the same example above:

        >>> ms = monkeys_from_file(data_path(__file__, 'example.txt'))
        >>> game = play(ms, worry_func=monkeys_modulo_func(ms))
        >>> next(game).inspect_counts
        (2, 4, 3, 6)
        >>> run_until_round(game, 20).inspect_counts
        (99, 97, 8, 103)
        >>> run_until_round(game, 1000).inspect_counts
        (5204, 4792, 199, 5192)
        >>> run_until_round(game, 2000).inspect_counts
        (10419, 9577, 392, 10391)
        >>> run_until_round(game, 3000).inspect_counts
        (15638, 14358, 587, 15593)
        >>> run_until_round(game, 4000).inspect_counts
        (20858, 19138, 780, 20797)
        >>> run_until_round(game, 5000).inspect_counts
        (26075, 23921, 974, 26000)
        >>> run_until_round(game, 6000).inspect_counts
        (31294, 28702, 1165, 31204)
        >>> run_until_round(game, 7000).inspect_counts
        (36508, 33488, 1360, 36400)
        >>> run_until_round(game, 8000).inspect_counts
        (41728, 38268, 1553, 41606)
        >>> run_until_round(game, 9000).inspect_counts
        (46945, 43051, 1746, 46807)
        >>> run_until_round(game, 10_000).inspect_counts
        (52166, 47830, 1938, 52013)

    After 10_000 rounds, the two most active monkeys inspected items `52166` and `52013` times.
    Multiplying these together, the level of **monkey business** in this situation is now
    **`2713310158`**.

    Worry levels are no longer divided by three after each item is inspected; you'll need to find
    another way to keep your worry levels manageable. Starting again from the initial state in your
    puzzle input, **what is the level of monkey business after 10000 rounds?**

        >>> part_2(ms)
        part 2: after 10000 rounds, monkey business is 2713310158
        2713310158
    """

    result = run_until_round(
        game=play(monkeys, worry_func=monkeys_modulo_func(monkeys)),
        round_num=rounds_count
    ).monkey_business()

    print(f"part 2: after {rounds_count} rounds, monkey business is {result}")
    return result


@dataclass(frozen=True)
class Operation:
    arg_1: str | int
    op: str
    arg_2: str | int

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.arg_1!r}, {self.op!r}, {self.arg_2!r})'

    # TODO: remove when pylint starts to understand match-case properly
    # pylint: disable=used-before-assignment, invalid-str-returned
    def __str__(self) -> str:
        match self.arg_1, self.op, self.arg_2:
            case 'old', '+', x if isinstance(x, int):
                return f"increases by {x}"
            case 'old', '*', x if isinstance(x, int):
                return f"is multiplied by {x}"
            case 'old', '*', 'old':
                return "is multiplied by itself"
            case _:
                raise ValueError(self.arg_1, self.op, self.arg_2)

        # TODO: remove when mypy realizes this is unreachable
        assert False

    def __call__(self, old: int) -> int:
        match self.arg_1, self.op, self.arg_2:
            case 'old', '+', x if isinstance(x, int):
                return old + x
            case 'old', '*', x if isinstance(x, int):
                return old * x
            case 'old', '*', 'old':
                return old * old
            case _:
                raise ValueError(self.arg_1, self.op, self.arg_2)

        # TODO: remove when mypy realizes this is unreachable
        assert False

    @classmethod
    def from_line(cls, line: str):
        arg_1, op, arg_2 = parse_line(line, 'new = $ $ $')

        def maybe_int(val: str) -> str | int:
            try:
                return int(val)
            except ValueError:
                return val

        return cls(maybe_int(arg_1), op, maybe_int(arg_2))


@dataclass(frozen=True)
class Test:
    divisible_by: int
    if_true: int
    if_false: int

    def __call__(self, value: int) -> int:
        return self.if_true if value % self.divisible_by == 0 else self.if_false


@dataclass(frozen=True)
class Monkey:
    number: int
    starting_items: list[int]
    operation: Operation
    test: Test

    def __str__(self) -> str:
        return f"Monkey {self.number}"

    @classmethod
    def from_lines(cls, lines: Iterable[str]):
        lines = [line.strip() for line in lines]

        return cls(
            number=int(parse_line(lines[0], 'Monkey $:')[0]),
            starting_items=[
                int(item) for item in parse_line(lines[1], 'Starting items: $')[0].split(', ')
            ],
            operation=Operation.from_line(parse_line(lines[2], 'Operation: $')[0]),
            test=Test(
                divisible_by=int(parse_line(lines[3], 'Test: divisible by $')[0]),
                if_true=int(parse_line(lines[4], 'If true: throw to monkey $')[0]),
                if_false=int(parse_line(lines[5], 'If false: throw to monkey $')[0]),
            )
        )


IntFunc = Callable[[int], int]


@dataclass(frozen=True)
class State:
    round_num: int
    items: tuple[list[int], ...]
    inspect_counts: tuple[int, ...]

    def __str__(self) -> str:
        header = f"After round {self.round_num}, " \
                 f"the monkeys are holding items with these worry levels:"
        monkey_lines = (
            (f"Monkey {index}: " + ", ".join(str(item) for item in monkey_items)).rstrip()
            for index, monkey_items in enumerate(self.items)
        )
        return header + "\n" + "\n".join(monkey_lines)

    def next_state(self, monkeys: Iterable[Monkey], worry_func: IntFunc) -> 'State':
        items = [list(monkey_items) for monkey_items in self.items]
        inspect_counts = list(self.inspect_counts)
        for monkey, monkey_items in zip(monkeys, items):
            inspect_counts[monkey.number] += len(monkey_items)
            while monkey_items:
                item = worry_func(monkey.operation(monkey_items.pop(0)))
                target_monkey_number = monkey.test(item)
                items[target_monkey_number].append(item)

        return State(
            round_num=self.round_num + 1,
            items=tuple(items),
            inspect_counts=tuple(inspect_counts)
        )

    def monkey_business(self, top_count: int = 2) -> int:
        # product of top (two) inspect counts
        return math.prod(sorted(self.inspect_counts, reverse=True)[:top_count])


def play(monkeys: Iterable[Monkey], worry_func: IntFunc = lambda x: x // 3) -> Iterator[State]:
    monkeys = tuple(monkeys)

    # initial state
    state = State(
        round_num=0,
        items=tuple(monkey.starting_items for monkey in monkeys),
        inspect_counts=(0,) * len(monkeys),
    )

    while True:
        yield (state := state.next_state(monkeys, worry_func))


def run_until_round(game: Iterator[State], round_num: int) -> State:
    while True:
        state = next(game)
        if state.round_num >= round_num:
            return state


def monkeys_modulo_func(monkeys: Iterable[Monkey]) -> IntFunc:
    # common multiple of all monkey test constants
    # -> it's enough to keep worry levels at mod of this value
    mod = lcm(*(monkey.test.divisible_by for monkey in monkeys))
    return lambda x: x % mod


def monkeys_from_file(fn: str) -> list[Monkey]:
    return list(monkeys_from_lines(open(fn)))


def monkeys_from_text(text: str) -> list[Monkey]:
    return list(monkeys_from_lines(text.strip().splitlines()))


def monkeys_from_lines(lines: Iterable[str]) -> Iterable[Monkey]:
    return (Monkey.from_lines(line_group) for line_group in line_groups(lines))


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    monkeys = monkeys_from_file(input_path)
    result_1 = part_1(monkeys)
    result_2 = part_2(monkeys)
    return result_1, result_2


if __name__ == '__main__':
    main()
