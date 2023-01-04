"""
Advent of Code 2018
Day 12: Subterranean Sustainability
https://adventofcode.com/2018/day/12
"""

from itertools import count
from typing import Iterable
from typing import Iterator

from common.iteration import minmax
from common.text import parse_line
from meta.aoc_tools import data_path


def part_1(initial_state: 'State', rules: 'Rules', generations: int = 20) -> int:
    """
    The year 518 is significantly more underground than your history books implied. Either that, or
    you've arrived in a vast cavern network under the North Pole.

    After exploring a little, you discover a long tunnel that contains a row of small pots as far as
    you can see to your left and right. A few of them contain plants - someone is trying to grow
    things in these geothermally-heated caves.

    The pots are numbered, with `0` in front of you. To the left, the pots are numbered `-1`, `-2`,
    `-3`, and so on; to the right, `1`, `2`, `3`.... Your puzzle input contains a list of pots from
    `0` to the right and whether they do (`#`) or do not (`.`) currently contain a plant, the
    **initial state**. (No other pots currently contain plants.) For example, an initial state of
    `#..##....` indicates that pots `0`, `3`, and `4` currently contain plants.

        >>> State.from_line('#..##....')
        State([0, 3, 4])

    Your puzzle input also contains some notes you find on a nearby table: someone has been trying
    to figure out how these plants **spread** to nearby pots. Based on the notes, for each
    generation of plants, a given pot has or does not have a plant based on whether that pot (and
    the two pots on either side of it) had a plant in the last generation. These are written as
    `LLCRR => N`, where `L` are pots to the left, `C` is the current pot being considered, `R` are
    the pots to the right, and `N` is whether the current pot will have a plant in the next
    generation. For example:

      - A note like `..#.. => .` means that a pot that contains a plant but with no plants within
        two pots of it will not have a plant in it during the next generation.
      - A note like `##.## => .` means that an empty pot with two plants on each side of it will
        remain empty in the next generation.
      - A note like `.##.# => #` means that a pot has a plant in a given generation if, in the
        previous generation, there were plants in that pot, the one immediately to the left, and the
        one two pots to the right, but not in the ones immediately to the right and two to the left.

    It's not clear what these plants are for, but you're sure it's important, so you'd like to make
    sure the current configuration of plants is sustainable by determining what will happen after
    **`20` generations**.

    For example, given the following input:

        >>> example_state, example_rules = input_from_text('''
        ...     initial state: #..#.#..##......###...###
        ...
        ...     ...## => #
        ...     ..#.. => #
        ...     .#... => #
        ...     .#.#. => #
        ...     .#.## => #
        ...     .##.. => #
        ...     .#### => #
        ...     #.#.# => #
        ...     #.### => #
        ...     ##.#. => #
        ...     ##.## => #
        ...     ###.. => #
        ...     ###.# => #
        ...     ####. => #
        ... ''')
        >>> example_state
        State([0, 3, 5, 8, 9, 16, 17, 18, 22, 23, 24])
        >>> sorted(example_rules)
        [3, 4, 8, 10, 11, 12, 15, 21, 23, 26, 27, 28, 29, 30]

    For brevity, in this example, only the combinations which do produce a plant are listed. (Your
    input includes all possible combinations.) Then, the next 20 generations will look like this:

        >>> final_state = run(example_state, example_rules, generations=20, log_range=range(-3, 36))
                         1         2         3
               0         0         0         0
         0: ...#..#.#..##......###...###...........
         1: ...#...#....#.....#..#..#..#...........
         2: ...##..##...##....#..#..#..##..........
         3: ..#.#...#..#.#....#..#..#...#..........
         4: ...#.#..#...#.#...#..#..##..##.........
         5: ....#...##...#.#..#..#...#...#.........
         6: ....##.#.#....#...#..##..##..##........
         7: ...#..###.#...##..#...#...#...#........
         8: ...#....##.#.#.#..##..##..##..##.......
         9: ...##..#..#####....#...#...#...#.......
        10: ..#.#..#...#.##....##..##..##..##......
        11: ...#...##...#.#...#.#...#...#...#......
        12: ...##.#.#....#.#...#.#..##..##..##.....
        13: ..#..###.#....#.#...#....#...#...#.....
        14: ..#....##.#....#.#..##...##..##..##....
        15: ..##..#..#.#....#....#..#.#...#...#....
        16: .#.#..#...#.#...##...#...#.#..##..##...
        17: ..#...##...#.#.#.#...##...#....#...#...
        18: ..##.#.#....#####.#.#.#...##...##..##..
        19: .#..###.#..#.#.#######.#.#.#..#.#...#..
        20: .#....##....#####...#######....#.#..##.

    The generation is shown along the left, where `0` is the initial state. The pot numbers are
    shown along the top, where `0` labels the center pot, negative-numbered pots extend to the left,
    and positive pots extend toward the right. Remember, the initial state begins at pot `0`, which
    is not the leftmost pot used in this example.

    After one generation, only seven plants remain. The one in pot `0` matched the rule looking for
    `..#..`, the one in pot `4` matched the rule looking for `.#.#.`, pot `9` matched `.##..`, and
    so on.

    In this example, after 20 generations, the pots shown as `#` contain plants, the furthest left
    of which is pot `-2`, and the furthest right of which is pot `34`. Adding up all the numbers of
    plant-containing pots after the 20th generation produces `325`.

        >>> final_state
        State([-2, 3, 4, 9, 10, 11, 12, 13, 17, 18, 19, 20, 21, 22, 23, 28, 30, 33, 34])
        >>> final_state.score()
        325

    **After `20` generations, what is the sum of the numbers of all pots which contain a plant?**

        >>> part_1(example_state, example_rules)
        part 1: after 20 generations, plants have score 325
        325
    """

    final_score = run(initial_state, rules, generations).score()

    print(f"part 1: after {generations} generations, plants have score {final_score}")
    return final_score


def part_2(initial_state: 'State', rules: 'Rules', generations: int = 50_000_000_000) -> int:
    """
    You realize that 20 generations aren't enough. After all, these plants will need to last another
    1500 years to even reach your timeline, not to mention your future.

    **After fifty billion (`50_000_000_000`) generations, what is the sum of the numbers of all pots
    which contain a plant?**

        >>> example_state, example_rules = input_from_file(data_path(__file__, 'example.txt'))
        >>> part_2(example_state, example_rules)
        part 2: after 50000000000 generations, plants have score 999999999374
        999999999374
    """

    # calculate only until generations start to repeat -> score deltas is constant for some time
    gen, current_score, score_delta = run_until_constant_score_delta(initial_state, rules)
    # extrapolate final score
    final_score = current_score + ((generations - gen) * score_delta)

    print(f"part 2: after {generations} generations, plants have score {final_score}")
    return final_score


Rule = tuple[int, bool]
Rules = set[int]


class State:
    def __init__(self, alive: Iterable[int]):
        self.alive = set(alive)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({sorted(self.alive)})'

    @classmethod
    def from_line(cls, line: str) -> 'State':
        return cls(x for x, c in enumerate(line) if c == '#')

    def __str__(self) -> str:
        return format(self)

    def __format__(self, format_spec: str):
        if format_spec:
            start, stop = format_spec.split(",")
            range_ = range(int(start), int(stop))
        else:
            range_ = self._xrange()

        return "".join("#" if p in self.alive else "." for p in range_)

    def __bool__(self) -> bool:
        return bool(self.alive)

    def __len__(self) -> int:
        return len(self.alive)

    def score(self) -> int:
        return sum(self.alive)

    def _xrange(self, margin: int = 3) -> range:
        xmin, xmax = minmax(self.alive)
        return range(xmin - margin, xmax + margin + 1)

    def __iter__(self) -> Iterator[tuple[int, bool]]:
        return ((plant, plant in self.alive) for plant in self._xrange())

    def next_generation(self, rules: Rules) -> 'State':
        def neighborhood() -> Iterator[tuple[int, int]]:
            nh_num = 0
            for rightmost_plant, alive in self:
                nh_num = ((nh_num << 1) | alive) & 0b11111
                yield rightmost_plant - 2, nh_num

        return type(self)(
            plant
            for plant, nh_num in neighborhood()
            if nh_num in rules
        )


def run(initial_state: State, rules: Rules, generations: int, log_range: range = None) -> State:
    state_fmt = f"{log_range.start},{log_range.stop}" if log_range else ""
    state = initial_state

    if log_range:
        for row in zip(*(str(x).rjust(2) if x % 10 == 0 else "  " for x in log_range)):
            print("    " + "".join(row).rstrip())

        print(f"{0:2}: {state:{state_fmt}}")

    for generation in range(1, generations + 1):
        state = state.next_generation(rules)
        if log_range:
            print(f"{generation:2}: {state:{state_fmt}}")

    return state


def run_until_constant_score_delta(
    state: State,
    rules: Rules,
    const_length: int = 10
) -> tuple[int, int, int]:
    deltas = []

    for generation in count(1):
        new_state = state.next_generation(rules)
        deltas.append(new_state.score() - state.score())

        if len(deltas) >= const_length and len(set(deltas[-const_length:])) == 1:
            return generation, new_state.score(), deltas[-1]

        state = new_state

    # unreachable
    assert False


def input_from_text(text: str) -> tuple[State, Rules]:
    return input_from_lines(text.strip().splitlines())


def input_from_file(fn: str) -> tuple[State, Rules]:
    return input_from_lines(open(fn))


def input_from_lines(lines: Iterable[str]) -> tuple[State, Rules]:
    lines_it = (line.strip() for line in lines)
    # initial state
    initial_state_str, = parse_line(next(lines_it), "initial state: $")
    initial_state = State.from_line(initial_state_str)
    # empty line
    assert not next(lines_it)
    # rules
    rules = {rule[0] for line in lines_it if (rule := rule_from_line(line))[1]}

    return initial_state, rules


def rule_from_line(line: str) -> Rule:
    rule_in, rule_out = parse_line(line, "$ => $")
    assert len(rule_in) == 5
    return int(rule_in.replace('.', '0').replace('#', '1'), 2), rule_out == '#'


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    initial_state, rules = input_from_file(input_path)
    result_1 = part_1(initial_state, rules)
    result_2 = part_2(initial_state, rules)
    return result_1, result_2


if __name__ == '__main__':
    main()
