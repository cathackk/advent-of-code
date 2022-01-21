"""
Advent of Code 2016
Day 10: Balance Bots
https://adventofcode.com/2016/day/10
"""

import math
from collections import defaultdict
from typing import Generator
from typing import Iterable

from common.file import relative_path
from common.iteration import exhaust
from common.iteration import single_value
from common.text import join_and
from common.text import parse_line


def part_1(instructions: 'Instructions', watch_for: tuple[int, int] = (61, 17)) -> int:
    """
    You come upon a factory in which many robots are zooming around handing small microchips to each
    other.

    Upon closer examination, you notice that each bot only proceeds when it has **two** microchips,
    and once it does, it gives each one to a different bot or puts it in a marked "output" bin.
    Sometimes, bots take microchips from "input" bins, too.

    Inspecting one of the microchips, it seems like they each contain a single number; the bots must
    use some logic to decide what to do with each chip. You access the local control computer and
    download the bots' instructions (your puzzle input).

    Some of the instructions specify that a specific-valued microchip should be given to a specific
    bot; the rest of the instructions indicate what a given bot should do with its **lower-value**
    or **higher-value** chip.

    For example, consider the following instructions:

        >>> example_init, example_comparisons = instructions_from_text('''
        ...     value 5 goes to bot 2
        ...     bot 2 gives low to bot 1 and high to bot 0
        ...     value 3 goes to bot 1
        ...     bot 1 gives low to output 1 and high to bot 0
        ...     bot 0 gives low to output 2 and high to output 0
        ...     value 2 goes to bot 2
        ... ''')
        >>> example_init
        {'bot 2': (5, 2), 'bot 1': (3,)}
        >>> example_comparisons  # doctest: +NORMALIZE_WHITESPACE
        {'bot 2': ('bot 1', 'bot 0'),
         'bot 1': ('output 1', 'bot 0'),
         'bot 0': ('output 2', 'output 0')}

      - Initially, bot `1` starts with a value-`3` chip,
        and bot `2` starts with a value-`2` chip and a value-`5` chip:

        >>> simulation = run_bots(example_init, example_comparisons)
        >>> next(simulation)
        {'bot 2': (5, 2), 'bot 1': (3,)}

      - Because bot `2` has two microchips,
        it gives its lower one (`2`) to bot `1` and its higher one (`5`) to bot `0`:

        >>> next(simulation)
        {'bot 1': (3, 2), 'bot 0': (5,)}

      - Then, bot `1` has two microchips;
        it puts the value-`2` chip in output `1` and gives the value-`3` chip to bot `0`:

        >>> next(simulation)
        {'bot 0': (5, 3), 'output 1': (2,)}

      - Finally, bot `0` has two microchips;
        it puts the `3` in output `2` and the `5` in output `0`:

        >>> next(simulation)
        {'output 1': (2,), 'output 2': (3,), 'output 0': (5,)}

    In the end, output bin `0` contains a value-`5` microchip, output bin `1` contains a value-`2`
    microchip, and output bin `2` contains a value-`3` microchip.

    In this configuration, bot number `2` is responsible for comparing value-`5` microchips with
    value-`2` microchips.

    Based on your instructions, **what is the number of the bot** that is responsible for comparing
    value-`61` microchips with value-`17` microchips?

        >>> part_1((example_init, example_comparisons), watch_for=(2, 5))
        part 1: chips 2 and 5 are compared by bot 2
        2
    """

    result = bot_number(watch_for_comparison(run_bots(*instructions), watch_for))
    print(f"part 1: chips {watch_for[0]} and {watch_for[1]} are compared by bot {result}")
    return result


def part_2(instructions: 'Instructions', considered_outputs: Iterable[int] = (0, 1, 2)) -> int:
    """
    What do you get if you **multiply together the values** of one chip in each of outputs `0`, `1`,
    and `2`?

        >>> example_instructions = instructions_from_file('data/10-example.txt')
        >>> exhaust(run_bots(*example_instructions))
        {1: 2, 2: 3, 0: 5}
        >>> part_2(example_instructions)
        part 2: product of outputs 0, 1, and 2 is: 5 * 2 * 3 = 30
        30
    """

    considered_outputs = list(considered_outputs)
    considered_outputs_str = join_and(considered_outputs, oxford_comma=True)

    simulation_result = dict(exhaust(run_bots(*instructions)))
    considered_values = {output: simulation_result[output] for output in considered_outputs}

    result = math.prod(considered_values.values())
    prod_str = " * ".join(str(val) for val in considered_values.values())

    print(f"part 2: product of outputs {considered_outputs_str} is: {prod_str} = {result}")
    return result


State = dict[str, tuple[int, ...]]
Comparisons = dict[str, tuple[str, str]]
Instructions = tuple[State, Comparisons]
Outputs = dict[int, int]
Simulation = Generator[State, None, Outputs]
MutableState = defaultdict[str, list[int]]


def run_bots(init: State, comparisons: Comparisons) -> Simulation:
    state = mutable_state(init)

    try:
        while True:
            yield frozen_state(state)

            active_bot = next(key for key, chips in state.items() if is_bot(key) and len(chips) > 1)
            distributed_chips = state.pop(active_bot)
            assert len(distributed_chips) == 2

            low_chip, high_chip = sorted(distributed_chips)
            low_target, high_target = comparisons[active_bot]
            state[low_target].append(low_chip)
            state[high_target].append(high_chip)

    except StopIteration:
        return {output_number(key): single_value(chips) for key, chips in state.items()}


def frozen_state(state: MutableState) -> State:
    return {key: tuple(values) for key, values in state.items()}


def mutable_state(state: State) -> MutableState:
    return defaultdict(list, {key: list(values) for key, values in state.items()})


def is_bot(key: str) -> bool:
    return key.startswith('bot ')


def bot_number(key: str) -> int:
    assert is_bot(key)
    return int(key.lstrip('bot '))


def is_output(key: str) -> bool:
    return key.startswith('output ')


def output_number(key: str) -> int:
    assert is_output(key)
    return int(key.lstrip('output '))


def watch_for_comparison(simulation: Simulation, watched_chips: tuple[int, int]) -> str:
    watched_chips = sorted(watched_chips)

    for state in simulation:
        matching_bots = (
            key
            for key, chips in state.items()
            if is_bot(key)
            if len(chips) == 2
            if sorted(chips) == watched_chips
        )

        if (matching_bot := next(matching_bots, None)):
            return matching_bot

    else:
        raise ValueError(f"chips {watched_chips} were not compared")


def instructions_from_text(text: str) -> Instructions:
    return instructions_from_lines(text.strip().splitlines())


def instructions_from_file(fn: str) -> Instructions:
    return instructions_from_lines(open(relative_path(__file__, fn)))


def instructions_from_lines(lines: Iterable[str]) -> Instructions:
    # 'value 5 goes to bot 2'
    # 'bot 2 gives low to bot 1 and high to bot 0'

    init: MutableState = defaultdict(list)
    comparisons: Comparisons = {}

    for line in lines:
        line = line.strip()

        if "goes to" in line:
            value, target = parse_line(line, "value $ goes to $")
            init[target].append(int(value))

        elif "gives low" in line:
            bot, low, high = parse_line(line, "$ gives low to $ and high to $")
            assert bot.startswith("bot ")
            assert bot not in comparisons
            comparisons[bot] = (low, high)

        else:
            raise ValueError(line)

    return frozen_state(init), comparisons


if __name__ == '__main__':
    instructions_ = instructions_from_file('data/10-input.txt')
    part_1(instructions_)
    part_2(instructions_)
