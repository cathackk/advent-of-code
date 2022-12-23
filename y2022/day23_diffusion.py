"""
Advent of Code 2022
Day 23: Unstable Diffusion
https://adventofcode.com/2022/day/23
"""
from collections import Counter
from enum import Enum
from typing import Iterable

from tqdm import tqdm

from common.file import relative_path
from common.rect import Rect


def part_1(init_state: 'State', stop_at_round: int = 10) -> int:
    """
    You enter a large crater of gray dirt where the grove is supposed to be. All around you, plants
    you imagine were expected to be full of fruit are instead withered and broken. A large group of
    Elves has formed in the middle of the grove.

    "...but this volcano has been dormant for months. Without ash, the fruit can't grow!"

    You look up to see a massive, snow-capped mountain towering above you.

    "It's not like there are other active volcanoes here; we've looked everywhere."

    "But our scanners show active magma flows; clearly it's going somewhere."

    They finally notice you at the edge of the grove, your pack almost overflowing from the random
    star fruit you've been collecting. Behind you, elephants and monkeys explore the grove, looking
    concerned. Then, the Elves recognize the ash cloud slowly spreading above your recent detour.

    "Why do you--" "How is--" "Did you just--"

    Before any of them can form a complete question, another Elf speaks up: "Okay, new plan. We have
    almost enough fruit already, and ash from the plume should spread here eventually. If we quickly
    plant new seedlings now, we can still make it to the extraction point. Spread out!"

    The Elves each reach into their pack and pull out a tiny plant. The plants rely on important
    nutrients from the ash, so they can't be planted too close together.

    There isn't enough time to let the Elves figure out where to plant the seedlings themselves;
    you quickly scan the grove (your puzzle input) and note their positions.

    For example:

        >>> state_big_0 = State.from_text('''
        ...     ....#..
        ...     ..###.#
        ...     #...#.#
        ...     .#...##
        ...     #.###..
        ...     ##.#.##
        ...     .#..#..
        ... ''')
        >>> len(state_big_0.elves)
        22
        >>> sorted(state_big_0.elves)  # doctest: +ELLIPSIS
        [(0, 2), (0, 4), (0, 5), (1, 3), (1, 5), (1, 6), (2, 1), (2, 4), (3, 1), ...]

    The scan shows Elves `#` and empty ground `.`; outside your scan, more empty ground extends
    a long way in every direction. The scan is oriented so that north is up; orthogonal directions
    are written N (north), S (south), W (west), and E (east), while diagonal directions are written
    NE, NW, SE, SW.

    The Elves follow a time-consuming process to figure out where they should each go; you can speed
    up this process considerably. The process consists of some number of **rounds** during which
    Elves alternate between considering where to move and actually moving.

    During the **first half** of each round, each Elf considers the eight positions adjacent to
    themselves. If no other Elves are in one of those eight positions, the Elf **does not do
    anything** during this round. Otherwise, the Elf looks in each of four directions in the
    following order and **proposes** moving one step in the **first valid direction**:

      - If there is no Elf in the N, NE, or NW adjacent positions,
        the Elf proposes moving **north** one step.
      - If there is no Elf in the S, SE, or SW adjacent positions,
        the Elf proposes moving **south** one step.
      - If there is no Elf in the W, NW, or SW adjacent positions,
        the Elf proposes moving **west** one step.
      - If there is no Elf in the E, NE, or SE adjacent positions,
        the Elf proposes moving **east** one step.

    After each Elf has had a chance to propose a move, the **second half** of the round can begin.
    Simultaneously, each Elf moves to their proposed destination tile if they were the **only** Elf
    to propose moving to that position. If two or more Elves propose moving to the same position,
    **none** of those Elves move.

    Finally, at the end of the round, the **first direction** the Elves considered is moved to the
    end of the list of directions. For example, during the second round, the Elves would try
    proposing a move to the south first, then west, then east, then north. On the third round,
    the Elves would first consider west, then east, then north, then south.

    As a smaller example, consider just these five Elves:

        >>> state_small_0 = State.from_text('''
        ...     .....
        ...     ..##.
        ...     ..#..
        ...     .....
        ...     ..##.
        ...     .....
        ... ''')
        >>> sorted(state_small_0.elves)
        [(2, 1), (2, 2), (2, 4), (3, 1), (3, 4)]
        >>> state_small_0.round_
        0

    The northernmost two Elves and southernmost two Elves all propose moving north, while the middle
    Elf cannot move north and proposes moving south. The middle Elf proposes the same destination as
    the southwest Elf, so neither of them move, but the other three do:

        >>> view_small = Rect.at_origin(5, 6)
        >>> (state_small_1 := state_small_0.next_state()).draw(bounds=view_small)
        ··##·
        ·····
        ··#··
        ···#·
        ··#··
        ·····
        >>> state_small_1.round_
        1

    Next, the northernmost two Elves and the southernmost Elf all propose moving south. Of the
    remaining middle two Elves, the west one cannot move south and proposes moving west, while the
    east one cannot move south **or** west and proposes moving east. All five Elves succeed in
    moving to their proposed positions:

        >>> (state_small_2 := state_small_1.next_state()).draw(bounds=view_small)
        ·····
        ··##·
        ·#···
        ····#
        ·····
        ··#··
        >>> state_small_2.round_
        2

    Finally, the southernmost two Elves choose not to move at all. Of the remaining three Elves,
    the west one proposes moving west, the east one proposes moving east, and the middle one
    proposes moving north; all three succeed in moving:

        >>> (state_small_3 := state_small_2.next_state()).draw(bounds=view_small)
        ··#··
        ····#
        #····
        ····#
        ·····
        ··#··
        >>> state_small_3.round_
        3

    At this point, no Elves need to move, and so the process ends.

        >>> state_small_3.next_state().elves == state_small_3.elves
        True

    The larger example above proceeds as follows:

        >>> view_big = Rect((-3, -2), (10, 9))
        >>> state_big_5 = state_big_0.run(stop_at_round=5, draw_in=view_big)
        == Initial State ==
        ··············
        ··············
        ·······#······
        ·····###·#····
        ···#···#·#····
        ····#···##····
        ···#·###······
        ···##·#·##····
        ····#··#······
        ··············
        ··············
        ··············
        == End of Round 1 ==
        ··············
        ·······#······
        ·····#···#····
        ···#··#·#·····
        ·······#··#···
        ····#·#·##····
        ··#··#·#······
        ··#·#·#·##····
        ··············
        ····#··#······
        ··············
        ··············
        == End of Round 2 ==
        ··············
        ·······#······
        ····#·····#···
        ···#··#·#·····
        ·······#···#··
        ···#··#·#·····
        ·#···#·#·#····
        ··············
        ··#·#·#·##····
        ····#··#······
        ··············
        ··············
        == End of Round 3 ==
        ··············
        ·······#······
        ·····#····#···
        ··#··#···#····
        ·······#···#··
        ···#··#·#·····
        ·#··#·····#···
        ·······##·····
        ··##·#····#···
        ···#··········
        ·······#······
        ··············
        == End of Round 4 ==
        ··············
        ·······#······
        ······#····#··
        ··#···##······
        ···#·····#·#··
        ·········#····
        ·#···###··#···
        ··#······#····
        ····##····#···
        ····#·········
        ·······#······
        ··············
        == End of Round 5 ==
        ·······#······
        ··············
        ··#··#·····#··
        ·········#····
        ······##···#··
        ·#·#·####·····
        ···········#··
        ····##··#·····
        ··#···········
        ··········#···
        ····#··#······
        ··············
        >>> state_big_5.round_
        5

    After a few more rounds...

        >>> state_big_10 = state_big_5.run(stop_at_round=10)
        >>> state_big_10.round_
        10
        >>> state_big_10.draw(bounds=view_big)
        ·······#······
        ···········#··
        ··#·#··#······
        ······#·······
        ···#·····#··#·
        ·#······##····
        ·····##·······
        ··#········#··
        ····#·#··#····
        ··············
        ····#··#··#···
        ··············

    To make sure they're on the right track, the Elves like to check after round 10 that they're
    making good progress toward covering enough ground. To do this, count the number of empty ground
    tiles contained by the smallest rectangle that contains every Elf. (The edges of the rectangle
    should be aligned to the N/S/E/W directions; the Elves do not have the patience to calculate
    arbitrary rectangles.) In the above example, that rectangle is:

        >>> state_big_10.draw()
        ······#·····
        ··········#·
        ·#·#··#·····
        ·····#······
        ··#·····#··#
        #······##···
        ····##······
        ·#········#·
        ···#·#··#···
        ············
        ···#··#··#··

    In this region, the number of empty ground tiles is 110.

        >>> state_big_10.bounds().area - len(state_big_10.elves)
        110

    Simulate the Elves' process and find the smallest rectangle that contains the Elves after 10
    rounds. **How many empty ground tiles does that rectangle contain?**

        >>> part_1(state_big_0)
        part 1: after 10 rounds, there are 110 empty tiles
        110
    """

    result = init_state.run(stop_at_round).bounds().area - len(init_state.elves)

    print(f"part 1: after {stop_at_round} rounds, there are {result} empty tiles")
    return result


def part_2(init_state: 'State') -> int:
    """
    It seems you're on the right track. Finish simulating the process and figure out where the Elves
    need to go. How many rounds did you save them?

    In the example above, the **first round where no Elf moved** was round **20**:

        >>> state_0 = State.from_file('data/23-example.txt')
        >>> state_final = state_0.run()
        >>> state_final.round_
        20
        >>> state_final.draw()
        ·······#······
        ····#······#··
        ··#·····#·····
        ······#·······
        ···#····#·#··#
        #·············
        ····#·····#···
        ··#·····#·····
        ····#·#····#··
        ·········#····
        ····#······#··
        ·······#······

    Figure out where the Elves need to go.
    **What is the number of the first round where no Elf moves?**

        >>> part_2(state_0)
        part 2: no elves move on round 20
        20
    """

    result = init_state.run().round_

    print(f"part 2: no elves move on round {result}")
    return result


Pos = tuple[int, int]


class Direction(Enum):
    NORTH = (0, -1)
    SOUTH = (0, +1)
    WEST = (-1, 0)
    EAST = (+1, 0)

    def __init__(self, dx: int, dy: int):
        self.dx = dx
        self.dy = dy

    def __add__(self, other):
        if not isinstance(other, tuple):
            return NotImplemented
        x, y = other
        return x + self.dx, y + self.dy

    __radd__ = __add__


ADJ = range(-1, 2)  # -1, 0, +1


def neighbors(pos: Pos, direction: Direction = None) -> Iterable[Pos]:
    x, y = pos

    if direction is None:
        # all 8 neighbors
        return ((x + dx, y + dy) for dx in ADJ for dy in ADJ if dx or dy)

    if direction.dx != 0:
        # only three WEST or EAST neighbors
        assert direction.dy == 0
        return ((x + direction.dx, y + dy) for dy in ADJ)

    if direction.dy != 0:
        # only the three NORTH or SOUTH neighbors
        assert direction.dx == 0
        return ((x + dx, y + direction.dy) for dx in ADJ)

    assert False


class State:

    def __init__(self, elves: Iterable[Pos], round_: int = 0):
        self.elves = set(elves)
        self.round_ = round_

    def bounds(self) -> Rect:
        return Rect.with_all(self.elves)

    def next_state(self) -> 'State':
        dir_offset = self.round_ % len(Direction)
        directions = list(Direction)[dir_offset:] + list(Direction)[:dir_offset]

        def proposal(elf: Pos) -> Pos | None:
            # no other elves are in one of the adjacent positions -> does not do anything
            if not any(npos in self.elves for npos in neighbors(elf)):
                return None

            valid_proposals = (
                elf + direction
                for direction in directions
                if not any(npos in self.elves for npos in neighbors(elf, direction))
            )
            return next(valid_proposals, None)

        proposals = {elf: proposal(elf) for elf in self.elves}
        proposals_counts = Counter(proposals.values())

        return type(self)(
            elves=(
                elf_new if (elf_new and proposals_counts[elf_new] == 1) else elf_old
                for elf_old, elf_new in proposals.items()
            ),
            round_=self.round_ + 1,
        )


    def run(self, stop_at_round: int = None, draw_in: Rect = None) -> 'State':
        state = self
        if draw_in:
            print("== Initial State ==")
            state.draw(draw_in)

        progress = tqdm(desc="running", unit=" rounds", delay=1.0)

        while True:
            if stop_at_round is not None and state.round_ >= stop_at_round:
                return state

            new_state = state.next_state()
            assert len(new_state.elves) == len(state.elves)
            progress.update(1)

            if new_state.elves == state.elves:
                # nobody moved
                return new_state

            if draw_in:
                print(f"== End of Round {new_state.round_} ==")
                new_state.draw(draw_in)

            state = new_state


    def draw(self, bounds: Rect = None) -> None:
        if bounds is None:
            bounds = self.bounds()

        def char(pos: Pos) -> str:
            return '#' if pos in self.elves else '·'

        for y in bounds.range_y():
            print(''.join(char((x, y)) for x in bounds.range_x()))

    @classmethod
    def from_file(cls, fn: str) -> 'State':
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_text(cls, text: str) -> 'State':
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'State':
        return cls(
            (x, y)
            for y, line in enumerate(lines)
            for x, char in enumerate(line.strip())
            if char == '#'
        )


def main(input_fn: str = 'data/23-input.txt') -> tuple[int, int]:
    init_state = State.from_file(input_fn)
    result_1 = part_1(init_state)
    result_2 = part_2(init_state)
    return result_1, result_2


if __name__ == '__main__':
    main()
