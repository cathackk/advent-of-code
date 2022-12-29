"""
Advent of Code 2022
Day 17: Pyroclastic Flow
https://adventofcode.com/2022/day/17
"""

import itertools
from collections import defaultdict
from enum import IntEnum
from typing import Iterable
from typing import Iterator
from typing import Literal

from tqdm import tqdm

from common.rect import Rect
from common.utils import ro
from meta.aoc_tools import data_path


def part_1(moves: list['Move'], target_shapes_count: int = 2022) -> int:
    r"""
    Your handheld device has located an alternative exit from the cave for you and the elephants.
    The ground is rumbling almost continuously now, but the strange valves bought you some time.
    It's definitely getting warmer in here, though.

    The tunnels eventually open into a very tall, narrow chamber. Large, oddly-shaped rocks are
    falling into the chamber from above, presumably due to all the rumbling. If you can't work out
    where the rocks will fall next, you might be crushed!

    The five types of rocks have the following peculiar shapes, where `#` is rock and `·` is empty
    space:

        >>> print("\n".join(f"== {i} ==\n{shape}" for i, shape in enumerate(SHAPES, start=1)))
        == 1 ==
        ####
        == 2 ==
        ·#·
        ###
        ·#·
        == 3 ==
        ··#
        ··#
        ###
        == 4 ==
        #
        #
        #
        #
        == 5 ==
        ##
        ##
        >>> [len(shape) for shape in SHAPES]
        [4, 5, 5, 4, 4]
        >>> SHAPES  # doctest: +NORMALIZE_WHITESPACE
        [Shape([(0, 0), (1, 0), (2, 0), (3, 0)]),
         Shape([(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)]),
         Shape([(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)]),
         Shape([(0, 0), (0, 1), (0, 2), (0, 3)]),
         Shape([(0, 0), (1, 0), (0, 1), (1, 1)])]

    The rocks fall in the order shown above: first the `-` shape, then the `+` shape, and so on.
    Once the end of the list is reached, the same order repeats: the `-` shape falls first, sixth,
    11th, 16th, etc.

    The rocks don't spin, but they do get pushed around by jets of hot gas coming out of the walls
    themselves. A quick scan reveals the effect the jets of hot gas will have on the rocks as they
    fall (your puzzle input).

    For example, suppose this was the jet pattern in your cave:

        >>> ms = moves_from_text('>>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>')

    In jet patterns, `<` means a push to the left, while `>` means a push to the right. The pattern
    above means that the jets will push a falling rock right, then right, then right, then left,
    then left, then right, and so on. If the end of the list is reached, it repeats.

        >>> ms  # doctest: +ELLIPSIS
        [Move.RIGHT, Move.RIGHT, Move.RIGHT, Move.LEFT, Move.LEFT, Move.RIGHT, ...]

    The tall, vertical chamber is exactly **seven units wide**. Each rock appears so that its left
    edge is two units away from the left wall and its bottom edge is three units above the highest
    rock in the room (or the floor, if there isn't one).

    After a rock appears, it alternates between **being pushed by a jet of hot gas** one unit (in
    the direction indicated by the next symbol in the jet pattern) and then **falling one unit
    down**. If any movement would cause any part of the rock to move into the walls, floor, or
    a stopped rock, the movement instead does not occur. If a **downward** movement would have
    caused a falling rock to move into the floor or an already-fallen rock, the falling rock stops
    where it is (having landed on something) and a new rock immediately begins falling.

    Drawing falling rocks with `@` and stopped rocks with `#`, the jet pattern in the example above
    manifests as follows:

        >>> game = play(ms, logging='moves')
        >>> turn_1 = next(game)
        The first rock begins falling:
        |··@@@@·|
        |·······|
        |·······|
        |·······|
        +-------+
        <BLANKLINE>
        Jet of gas pushes rock right:
        |···@@@@|
        |·······|
        |·······|
        |·······|
        +-------+
        <BLANKLINE>
        Rock falls 1 unit:
        |···@@@@|
        |·······|
        |·······|
        +-------+
        <BLANKLINE>
        Jet of gas pushes rock right, but nothing happens:
        |···@@@@|
        |·······|
        |·······|
        +-------+
        <BLANKLINE>
        Rock falls 1 unit:
        |···@@@@|
        |·······|
        +-------+
        <BLANKLINE>
        Jet of gas pushes rock right, but nothing happens:
        |···@@@@|
        |·······|
        +-------+
        <BLANKLINE>
        Rock falls 1 unit:
        |···@@@@|
        +-------+
        <BLANKLINE>
        Jet of gas pushes rock left:
        |··@@@@·|
        +-------+
        <BLANKLINE>
        Rock falls 1 unit, causing it to come to rest:
        |··####·|
        +-------+

        >>> turn_1.height
        1
        >>> turn_1.shapes_count
        1
        >>> print(turn_1)
        |··####·|
        +-------+

        >>> turn_2 = next(game)
        A new rock begins falling:
        |···@···|
        |··@@@··|
        |···@···|
        |·······|
        |·······|
        |·······|
        |··####·|
        +-------+
        <BLANKLINE>
        Jet of gas pushes rock left:
        |··@····|
        |·@@@···|
        |··@····|
        |·······|
        |·······|
        |·······|
        |··####·|
        +-------+
        <BLANKLINE>
        Rock falls 1 unit:
        |··@····|
        |·@@@···|
        |··@····|
        |·······|
        |·······|
        |··####·|
        +-------+
        <BLANKLINE>
        Jet of gas pushes rock right:
        |···@···|
        |··@@@··|
        |···@···|
        |·······|
        |·······|
        |··####·|
        +-------+
        <BLANKLINE>
        Rock falls 1 unit:
        |···@···|
        |··@@@··|
        |···@···|
        |·······|
        |··####·|
        +-------+
        <BLANKLINE>
        Jet of gas pushes rock left:
        |··@····|
        |·@@@···|
        |··@····|
        |·······|
        |··####·|
        +-------+
        <BLANKLINE>
        Rock falls 1 unit:
        |··@····|
        |·@@@···|
        |··@····|
        |··####·|
        +-------+
        <BLANKLINE>
        Jet of gas pushes rock right:
        |···@···|
        |··@@@··|
        |···@···|
        |··####·|
        +-------+
        <BLANKLINE>
        Rock falls 1 unit, causing it to come to rest:
        |···#···|
        |··###··|
        |···#···|
        |··####·|
        +-------+

        >>> turn_2.height
        4
        >>> turn_2.shapes_count
        2
        >>> print(turn_2)
        |···#···|
        |··###··|
        |···#···|
        |··####·|
        +-------+

    The moment each of the next few rocks begins falling, you would see this:

        >>> game = play(ms, logging='turn start')
        >>> states = [next(game)]
        |··@@@@·|
        |·······|
        |·······|
        |·······|
        +-------+
        >>> states.append(next(game))
        |···@···|
        |··@@@··|
        |···@···|
        |·······|
        |·······|
        |·······|
        |··####·|
        +-------+
        >>> states.append(next(game))
        |····@··|
        |····@··|
        |··@@@··|
        |·······|
        |·······|
        |·······|
        |···#···|
        |··###··|
        |···#···|
        |··####·|
        +-------+
        >>> states.extend(next(game) for _ in range(8))
        |··@····|
        |··@····|
        |··@····|
        |··@····|
        |·······|
        |·······|
        |·······|
        |··#····|
        |··#····|
        |####···|
        |··###··|
        |···#···|
        |··####·|
        +-------+
        |··@@···|
        |··@@···|
        |·······|
        |·······|
        |·······|
        |····#··|
        |··#·#··|
        |··#·#··|
        |#####··|
        |··###··|
        |···#···|
        |··####·|
        +-------+
        |··@@@@·|
        |·······|
        |·······|
        |·······|
        |····##·|
        |····##·|
        |····#··|
        |··#·#··|
        |··#·#··|
        |#####··|
        |··###··|
        |···#···|
        |··####·|
        +-------+
        |···@···|
        |··@@@··|
        |···@···|
        |·······|
        |·······|
        |·······|
        |·####··|
        |····##·|
        |····##·|
        |····#··|
        |··#·#··|
        |··#·#··|
        |#####··|
        |··###··|
        |···#···|
        |··####·|
        +-------+
        |····@··|
        |····@··|
        |··@@@··|
        |·······|
        |·······|
        |·······|
        |··#····|
        |·###···|
        |··#····|
        |·####··|
        |····##·|
        |····##·|
        |····#··|
        |··#·#··|
        |··#·#··|
        |#####··|
        |··###··|
        |···#···|
        |··####·|
        +-------+
        |··@····|
        |··@····|
        |··@····|
        |··@····|
        |·······|
        |·······|
        |·······|
        |·····#·|
        |·····#·|
        |··####·|
        |·###···|
        |··#····|
        |·####··|
        |····##·|
        |····##·|
        |····#··|
        |··#·#··|
        |··#·#··|
        |#####··|
        |··###··|
        |···#···|
        |··####·|
        +-------+
        |··@@···|
        |··@@···|
        |·······|
        |·······|
        |·······|
        |····#··|
        |····#··|
        |····##·|
        |····##·|
        |··####·|
        |·###···|
        |··#····|
        |·####··|
        |····##·|
        |····##·|
        |····#··|
        |··#·#··|
        |··#·#··|
        |#####··|
        |··###··|
        |···#···|
        |··####·|
        +-------+
        |··@@@@·|
        |·······|
        |·······|
        |·······|
        |····#··|
        |····#··|
        |····##·|
        |##··##·|
        |######·|
        |·###···|
        |··#····|
        |·####··|
        |····##·|
        |····##·|
        |····#··|
        |··#·#··|
        |··#·#··|
        |#####··|
        |··###··|
        |···#···|
        |··####·|
        +-------+
        >>> print(states[-1])
        |···####|
        |····#··|
        |····#··|
        |····##·|
        |##··##·|
        |######·|
        |·###···|
        |··#····|
        |·####··|
        |····##·|
        |····##·|
        |····#··|
        |··#·#··|
        |··#·#··|
        |#####··|
        |··###··|
        |···#···|
        |··####·|
        +-------+
        >>> [state.height for state in states]
        [1, 4, 6, 7, 9, 10, 13, 15, 17, 17, 18]

    To prove to the elephants your simulation is accurate, they want to know how tall the tower will
    get after 2022 rocks have stopped (but before the 2023rd rock begins falling). In this example,
    the tower of rocks will be **3068** units tall.

        >>> final_height(ms, target_shapes_count=2022)
        3068

    **How many units tall will the tower of rocks be after 2022 rocks have stopped falling?**

        >>> part_1(ms)
        part 1: after 2022 rocks, the tower will be 3068 tall
        3068
    """

    result = final_height(moves, target_shapes_count)

    print(f"part 1: after {target_shapes_count} rocks, the tower will be {result} tall")
    return result


def part_2(moves: list['Move'], target_shapes_count: int = 1_000_000_000_000) -> int:
    """
    The elephants are not impressed by your simulation. They demand to know how tall the tower will
    be after **1_000_000_000_000** rocks have stopped! Only then will they feel confident enough to
    proceed through the cave.

    In the example above, the tower would be **1_514_285_714_288** units tall!

        >>> ms = moves_from_file(data_path(__file__, 'example.txt'))
        >>> final_height(ms, target_shapes_count=1_000_000_000_000)
        1514285714288

    **How tall will the tower be after 1_000_000_000_000 rocks have stopped?**

        >>> part_2(ms)
        part 2: after 1000000000000 rocks, the tower will be 1514285714288 tall
        1514285714288
    """

    result = final_height(moves, target_shapes_count)

    print(f"part 2: after {target_shapes_count} rocks, the tower will be {result} tall")
    return result


Pos = tuple[int, int]


class Bounds(Rect):
    """
    Rect with reversed Y:

        >>> b = Bounds.with_all([(0, 0), (2, 0), (0, 3)])
        >>> b
        Bounds((0, 3), (2, 0))
        >>> b.top_y, b.bottom_y
        (3, 0)
        >>> list(b.range_y())
        [3, 2, 1, 0]
    """

    def __init__(self, corner1: Pos, corner2: Pos):
        super().__init__(corner1, corner2)
        # reverse y -> rewrite corners
        x1, y1 = self.top_left
        x2, y2 = self.bottom_right
        self.top_left = (x1, y2)
        self.bottom_right = (x2, y1)

    def range_y(self) -> range:
        return range(self.top_y, self.bottom_y - 1, -1)

    @property
    def height(self) -> int:
        return self.top_y - self.bottom_y + 1


class Shape:
    def __init__(self, rocks: Iterable[Pos]):
        self.rocks = sorted(rocks, key=ro)
        self.bounds = Bounds.with_all(self.rocks)
        assert self.bounds.bottom_left == (0, 0)

    def __str__(self) -> str:
        return "\n".join(
            "".join("#" if (x, y) in self.rocks else "·" for x in self.bounds.range_x())
            for y in self.bounds.range_y()
        )

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.rocks})'

    def __len__(self) -> int:
        return len(self.rocks)

    @property
    def width(self) -> int:
        return self.bounds.width

    @property
    def height(self) -> int:
        return self.bounds.height

    def rocks_translated(self, pos: Pos) -> Iterable[Pos]:
        p_x, p_y = pos
        return ((r_x + p_x, r_y + p_y) for r_x, r_y in self.rocks)

    @classmethod
    def from_text(cls, text: str) -> 'Shape':
        lines = text.splitlines()
        return cls(
            (x, len(lines) - y1)
            for y1, line in enumerate(text.splitlines(), start=1)
            for x, char in enumerate(line)
            if char == '#'
        )


SHAPES = [
    Shape.from_text('####'),
    Shape.from_text('·#·\n###\n·#·'),
    Shape.from_text('··#\n··#\n###'),
    Shape.from_text('#\n#\n#\n#'),
    Shape.from_text('##\n##'),
]


class State:
    def __init__(self, rocks: Iterable[Pos], shapes_count: int, moves_count: int, width: int):
        self.rocks = frozenset(rocks)
        self.shapes_count = shapes_count
        self.moves_count = moves_count
        self.bounds = Bounds.at_origin(width, 1).grow_to_fit(self.rocks)
        assert self.bounds.bottom_y == 0

    @property
    def width(self) -> int:
        return self.bounds.width

    @property
    def height(self) -> int:
        return self.bounds.height if self.rocks else 0

    def can_place_shape_at(self, shape: Shape, pos: Pos) -> bool:
        x_left, y_bottom = pos

        # collision with wall?
        if x_left < 0:
            return False
        if x_left + shape.width - 1 >= self.width:
            return False

        # collision with floor?
        if y_bottom < 0:
            return False

        # collision with another rock?
        if any(rock in self.rocks for rock in shape.rocks_translated(pos)):
            return False

        # all is fine!
        return True

    def __str__(self) -> str:
        return self.draw()

    def str_with_shape(self, shape: Shape, pos: Pos) -> str:
        return self.draw(falling_rocks=shape.rocks_translated(pos))

    def draw(self, falling_rocks: Iterable[Pos] = ()) -> str:
        falling_rocks = set(falling_rocks)
        bounds = self.bounds.grow_to_fit(falling_rocks)

        def char(pos: Pos) -> str:
            if pos in falling_rocks:
                return "@"
            elif pos in self.rocks:
                return "#"
            else:
                return "·"

        lines = (
            "|" + "".join(char((x, y)) for x in bounds.range_x()) + "|"
            for y in bounds.range_y()
        )
        floor = "+" + "-" * self.width + "+"
        return "\n".join(itertools.chain(lines, [floor]))


class Move(IntEnum):
    LEFT = -1
    RIGHT = +1

    def __str__(self) -> str:
        return self.name.lower()

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"

    @classmethod
    def from_char(cls, char: str) -> 'Move':
        if char == '<':
            return Move.LEFT
        elif char == '>':
            return Move.RIGHT
        else:
            raise ValueError(char)


LogLevel = Literal['', 'moves', 'turn start']


def play(moves: list[Move], room_width: int = 7, logging: LogLevel = '') -> Iterator[State]:
    shapes_it = iter(enumerate(itertools.cycle(SHAPES), start=1))
    moves_it = iter(enumerate(itertools.cycle(moves), start=1))

    state = State(rocks=[], shapes_count=0, moves_count=0, width=room_width)
    assert state.height == 0

    for shapes_count, shape in shapes_it:
        shape_x, shape_y = 2, state.height + 3

        if logging == 'moves':
            rock_adj = "A new" if state.shapes_count else "The first"
            print(f"{rock_adj} rock begins falling:")

        if logging in ('moves', 'turn start'):
            print(state.str_with_shape(shape, (shape_x, shape_y)))

        while True:
            moves_count, move = next(moves_it)  # pylint: disable=stop-iteration-return
            can_move = state.can_place_shape_at(shape, (shape_x + move, shape_y))
            if can_move:
                shape_x += move

            if logging == 'moves':
                msg = f"Jet of gas pushes rock {move}"
                if not can_move:
                    msg += ", but nothing happens"
                print(f"\n{msg}:")
                print(state.str_with_shape(shape, (shape_x, shape_y)))

            can_fall = state.can_place_shape_at(shape, (shape_x, shape_y - 1))
            if not can_fall:
                state = State(
                    rocks=itertools.chain(
                        state.rocks,
                        set(shape.rocks_translated((shape_x, shape_y))),
                    ),
                    shapes_count=shapes_count,
                    moves_count=moves_count,
                    width=room_width,
                )

                if logging == 'moves':
                    print("\nRock falls 1 unit, causing it to come to rest:")
                    print(state)

                yield state
                break  # next shape

            shape_y -= 1

            if logging == 'moves':
                print("\nRock falls 1 unit:")
                print(state.str_with_shape(shape, (shape_x, shape_y)))


def final_height(moves: list[Move], target_shapes_count: int) -> int:
    states_by_last_indexes: defaultdict[tuple[int, int], list[State]] = defaultdict(list)
    optimized_height_delta = 0

    for state in tqdm(play(moves), delay=1.0, unit=' shapes'):
        if state.shapes_count >= target_shapes_count:
            return state.height + optimized_height_delta

        # optimization by finding cycles (periods) in the states:
        if optimized_height_delta:
            # (optimization already done, we are just iterating through the remainder)
            continue

        # remember states by what shape and what move was used last time
        last_shape_index = state.shapes_count % len(SHAPES)
        last_move_index = state.moves_count % len(moves)
        key = (last_shape_index, last_move_index)
        similar_states = states_by_last_indexes[key]
        similar_states.append(state)

        # if there are now at least three similar states available ...
        if len(similar_states) < 3:
            continue

        # ... we'll check if the height delta is the same among these three:
        state_1, state_2, state_3 = similar_states[-3:]
        height_per_cycle = state_3.height - state_2.height
        if height_per_cycle != state_2.height - state_1.height:
            continue
        cycle_length = state_3.shapes_count - state_2.shapes_count
        if cycle_length != state_2.shapes_count - state_1.shapes_count:
            continue

        # if so, we assume that we found a cycle and extrapolate the rest of simulation:
        shapes_remaining = target_shapes_count - state.shapes_count
        full_cycles_remaining = shapes_remaining // cycle_length
        optimized_height_delta = full_cycles_remaining * height_per_cycle

        # do we still need to run the remainder of the shapes?
        if shapes_remaining % cycle_length == 0:
            # no remainder -> we are done
            return state.height + optimized_height_delta
        else:
            # otherwise adjust the target shapes count
            target_shapes_count -= full_cycles_remaining * cycle_length
            # ... and continue calculating the remainder

    assert False


def moves_from_file(fn: str) -> list[Move]:
    return moves_from_text(open(fn).read())


def moves_from_text(text: str) -> list[Move]:
    return [Move.from_char(char) for char in text.strip()]


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    moves = moves_from_file(input_path)
    result_1 = part_1(moves)
    result_2 = part_2(moves)
    return result_1, result_2


if __name__ == '__main__':
    main()
