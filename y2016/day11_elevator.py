"""
Advent of Code 2016
Day 11: Radioisotope Thermoelectric Generators
https://adventofcode.com/2016/day/11
"""

from itertools import combinations
from typing import Iterable

from common.file import relative_path
from common.graph import shortest_path
from common.text import abc_rot
from common.text import parse_line


def part_1(initial_state: 'State') -> int:
    r"""
    You come upon a column of four floors that have been entirely sealed off from the rest of
    the building except for a small dedicated lobby. There are some radiation warnings and a big
    sign which reads "Radioisotope Testing Facility".

    According to the project status board, this facility is currently being used to experiment with
    Radioisotope Thermoelectric Generators (RTGs, or simply "generators") that are designed to be
    paired with specially-constructed microchips. Basically, an RTG is a highly radioactive rock
    that generates electricity through heat.

    The experimental RTGs have poor radiation containment, so they're dangerously radioactive.
    The chips are prototypes and don't have normal radiation shielding, but they do have the ability
    to **generate an electromagnetic radiation shield when powered**. Unfortunately, they can only
    be powered by their corresponding RTG. An RTG powering a microchip is still dangerous to other
    microchips.

    In other words, if a chip is ever left in the same area as another RTG, and it's not connected
    to its own RTG, the chip will be **fried**. Therefore, it is assumed that you will follow
    procedure and keep chips connected to their corresponding RTG when they're in the same room,
    and away from other RTGs otherwise.

    These microchips sound very interesting and useful to your current activities, and you'd like to
    try to retrieve them. The fourth floor of the facility has an assembling machine which can make
    a self-contained, shielded computer for you to take with you - that is, if you can bring it all
    of the RTGs and microchips.

    Within the radiation-shielded part of the facility (in which it's safe to have these pre-
    -assembly RTGs), there is an elevator that can move between the four floors. Its capacity rating
    means it can carry at most yourself and two RTGs or microchips in any combination. (They're
    rigged to some heavy diagnostic equipment - the assembling machine will detach it for you.)
    As a security measure, the elevator will only function if it contains at least one RTG or
    microchip. The elevator always stops on each floor to recharge, and this takes long enough that
    the items within it and the items on that floor can irradiate each other. (You can prevent this
    if a Microchip and its Generator end up on the same floor in this way, as they can be connected
    while the elevator is recharging.)

    You make some notes of the locations of each component of interest (your puzzle input). Before
    you don a hazmat suit and start moving things around, you'd like to have an idea of what you
    need to do.

    When you enter the containment area, you and the elevator will start on the first floor.

    For example, suppose the isolated area has the following arrangement:

        >>> (st_0 := State.from_text('''
        ...     The first floor contains a H-compatible microchip and a Li-compatible microchip.
        ...     The second floor contains a H generator.
        ...     The third floor contains a Li generator.
        ...     The fourth floor contains nothing relevant.
        ... '''))
        State({'E': 1, 'HM': 1, 'LM': 1, 'HG': 2, 'LG': 3})
        >>> (st_final := final_state(st_0))
        State({'E': 4, 'HM': 4, 'LM': 4, 'HG': 4, 'LG': 4})
        >>> st_0 == st_final
        False

    As a diagram (`F#` for a Floor number, `E` for Elevator, `H` for Hydrogen, `L` for Lithium,
    `M` for Microchip, and `G` for Generator), the initial state looks like this:

        >>> print(st_0)
        F4 .  .  .  .  .
        F3 .  .  .  LG .
        F2 .  HG .  .  .
        F1 E  .  HM .  LM

    Then, to get everything up to the assembling machine on the fourth floor, the following steps
    could be taken:

      - Bring the Hydrogen-compatible Microchip to the second floor, which is safe because it can
        get power from the Hydrogen Generator:

        >>> print(st_1 := st_0.move(+1, 'HM'))
        F4 .  .  .  .  .
        F3 .  .  .  LG .
        F2 E  HG HM .  .
        F1 .  .  .  .  LM

      - Bring both Hydrogen-related items to the third floor, which is safe because the Hydrogen-
        -compatible microchip is getting power from its generator:

        >>> print(st_2 := st_1.move(+1, 'HG', 'HM'))
        F4 .  .  .  .  .
        F3 E  HG HM LG .
        F2 .  .  .  .  .
        F1 .  .  .  .  LM

      - Leave the Hydrogen Generator on floor three, but bring the Hydrogen-compatible Microchip
        back down with you so you can still use the elevator:

        >>> print(st_3 := st_2.move(-1, 'HM'))
        F4 .  .  .  .  .
        F3 .  HG .  LG .
        F2 E  .  HM .  .
        F1 .  .  .  .  LM

      - At the first floor, grab the Lithium-compatible Microchip, which is safe because Microchips
        don't affect each other:

        >>> print(st_4 := st_3.move(-1, 'HM'))
        F4 .  .  .  .  .
        F3 .  HG .  LG .
        F2 .  .  .  .  .
        F1 E  .  HM .  LM

      - Bring both Microchips up one floor, where there is nothing to fry them:

        >>> print(st_5 := st_4.move(+1, 'HM', 'LM'))
        F4 .  .  .  .  .
        F3 .  HG .  LG .
        F2 E  .  HM .  LM
        F1 .  .  .  .  .

      - Bring both Microchips up again to floor three, where they can be temporarily connected to
        their corresponding generators while the elevator recharges, preventing either of them from
        being fried:

        >>> print(st_6 := st_5.move(+1, 'HM', 'LM'))
        F4 .  .  .  .  .
        F3 E  HG HM LG LM
        F2 .  .  .  .  .
        F1 .  .  .  .  .

      - Bring both Microchips to the fourth floor:

        >>> print(st_7 := st_6.move(+1, 'HM', 'LM'))
        F4 E  .  HM .  LM
        F3 .  HG .  LG .
        F2 .  .  .  .  .
        F1 .  .  .  .  .

      - Leave the Lithium-compatible microchip on the fourth floor, but bring the Hydrogen-
        -compatible one so you can still use the elevator; this is safe because although the Lithium
        Generator is on the destination floor, you can connect Hydrogen-compatible microchip to
        the Hydrogen Generator there:

        >>> print(st_8 := st_7.move(-1, 'HM'))
        F4 .  .  .  .  LM
        F3 E  HG HM LG .
        F2 .  .  .  .  .
        F1 .  .  .  .  .

      - Bring both Generators up to the fourth floor, which is safe because you can connect
        the Lithium-compatible Microchip to the Lithium Generator upon arrival:

        >>> print(st_9 := st_8.move(+1, 'HG', 'LG'))
        F4 E  HG .  LG LM
        F3 .  .  HM .  .
        F2 .  .  .  .  .
        F1 .  .  .  .  .

      - Bring the Lithium Microchip with you to the third floor so you can use the elevator:

        >>> print(st_10 := st_9.move(-1, 'LM'))
        F4 .  HG .  LG .
        F3 E  .  HM .  LM
        F2 .  .  .  .  .
        F1 .  .  .  .  .

      - Bring both Microchips to the fourth floor:

        >>> print(st_11 := st_10.move(+1, 'HM', 'LM'))
        F4 E  HG HM LG LM
        F3 .  .  .  .  .
        F2 .  .  .  .  .
        F1 .  .  .  .  .
        >>> st_11 == st_final
        True

    In this arrangement, it takes `11` steps to collect all of the objects at the fourth floor for
    assembly. (Each elevator stop counts as one step, even if nothing is added to or removed from
    it.)

    In your situation, what is the **minimum number of steps** required to bring all of the objects
    to the fourth floor?

        >>> part_1(st_0)
        part 1: shortest path takes 11 steps
        11
    """
    steps_count, _ = search(initial_state)
    print(f"part 1: shortest path takes {steps_count} steps")
    return steps_count


def part_2(initial_state: 'State') -> int:
    """
    You step into the cleanroom separating the lobby from the isolated area and put on the hazmat
    suit.

    Upon entering the isolated containment area, however, you notice some extra parts on the first
    floor that weren't listed on the record outside:

      - An elerium generator.
      - An elerium-compatible microchip.
      - A dilithium generator.
      - A dilithium-compatible microchip.

    These work just like the other generators and microchips. You'll have to get them up to assembly
    as well.

        >>> st_0 = State({'E': 1, 'AG': 2, 'AM': 2})
        >>> print(st_0)
        F4 .  .  .
        F3 .  .  .
        F2 .  AG AM
        F1 E  .  .
        >>> (stx_0 := extended_for_part_2(st_0))
        State({'E': 1, 'AG': 2, 'AM': 2, 'FG': 1, 'FM': 1, 'DG': 1, 'DM': 1})
        >>> print(stx_0)
        F4 .  .  .  .  .  .  .
        F3 .  .  .  .  .  .  .
        F2 .  AG AM .  .  .  .
        F1 E  .  .  DG DM FG FM


    What is the **minimum number of steps** required to bring all of the objects, including these
    four new ones, to the fourth floor?

        >>> part_2(st_0)
        part 2: shortest path takes 23 steps
        23
    """

    steps, _ = search(extended_for_part_2(initial_state))
    print(f"part 2: shortest path takes {steps} steps")
    return steps


class State:
    def __init__(self, positions: Iterable[tuple[str, int]] | dict[str, int], top_floor: int = 4):
        self.positions = dict(positions)
        self.top_floor = top_floor
        self.floors_range = range(1, self.top_floor + 1)

        # basic asserts
        assert top_floor > 1
        assert all(pos in self.floors_range for pos in self.positions.values())
        assert 'E' in self.positions

        # for hashing
        self._key = self._create_key()

        # make sure no chip is fried
        # uses _key ^^ as optimization
        self._check_microchip_safety()

    def _create_key(self) -> tuple[int, int, tuple[int, int], ...]:
        """
        State is not changed by mere renaming or reordering of elements:

            >>> (s1 := State({'E': 1, 'AG': 1, 'AM': 1, 'BG': 2, 'BM': 3}))._key
            (4, 1, (1, 1), (2, 3))
            >>> (s2 := State({'E': 1, 'BG': 1, 'BM': 1, 'AG': 2, 'AM': 3}))._key
            (4, 1, (1, 1), (2, 3))
            >>> (s3 := State({'XM': 3, 'YG': 1, 'E': 1, 'XG': 2, 'YM': 1}))._key
            (4, 1, (1, 1), (2, 3))
            >>> s1 == s2 == s3
            True

        However generator and microchip cannot be swapped:

            >>> (s4 := State({'E': 1, 'AG': 1, 'AM': 1, 'BG': 3, 'BM': 2}))._key
            (4, 1, (1, 1), (3, 2))
            >>> s1 == s4
            False
        """

        elements = {item[0] for item in self.positions if len(item) == 2}
        gm_pairs = sorted((self.positions[e+'G'], self.positions[e+'M']) for e in elements)
        return (self.top_floor, self.elevator_floor) + tuple(gm_pairs)

    def _check_microchip_safety(self) -> None:
        generators_at = {g for g, _ in self._key[2:]}
        unshielded_microchips_at = (m for g, m in self._key[2:] if m != g)
        for m in unshielded_microchips_at:
            if m in generators_at:
                raise ValueError(f"fried microchip at floor {m}")

    def __repr__(self) -> str:
        tf_repr = f', top_floor={self.top_floor!r}' if self.top_floor != 4 else ''
        return f'{type(self).__name__}({self.positions!r}{tf_repr})'

    def __str__(self) -> str:
        def lines() -> Iterable[str]:
            items_ordered = ['E'] + sorted(item for item in self.positions if item != 'E')
            for floor in range(self.top_floor, 0, -1):
                floor_label = f"F{floor}"
                items_str = " ".join(
                    (item.ljust(2) if self.positions[item] == floor else ". ")
                    for item in items_ordered
                )
                yield f"{floor_label} {items_str}".rstrip()

        return "\n".join(lines())

    def __hash__(self) -> int:
        return hash(self._key)

    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and self._key == other._key

    def __contains__(self, item: str):
        return item in self.positions

    def microchips(self) -> Iterable[tuple[str, int]]:
        return (
            (item, floor)
            for item, floor in self.positions.items()
            if is_microchip(item)
        )

    def generators(self) -> Iterable[tuple[str, int]]:
        return (
            (item, floor)
            for item, floor in self.positions.items()
            if is_generator(item)
        )

    @property
    def elevator_floor(self) -> int:
        return self.positions['E']

    def pickable_items(self) -> Iterable[str]:
        return (
            item
            for item, floor in self.positions.items()
            if item != 'E'
            if floor == self.elevator_floor
        )

    def move(self, direction: int, *carried_items: str) -> 'State':
        if direction not in (-1, +1):
            raise ValueError(f"direction cannot be {direction}")

        elevator_before = self.positions['E']
        elevator_after = elevator_before + direction
        if elevator_after not in self.floors_range:
            raise ValueError(f"elevator cannot go to floor {elevator_after}")

        if len(carried_items) not in (1, 2):
            raise ValueError(f"cannot carry {len(carried_items)} items")

        for item in carried_items:
            if self.positions[item] != elevator_before:
                raise ValueError(f"{item!r} not at elevator floor {elevator_before}")

        def new_floor(key: str) -> int:
            if key == 'E' or key in carried_items:
                return elevator_after
            else:
                return self.positions[key]

        return type(self)(
            positions=((item, new_floor(item)) for item in self.positions),
            top_floor=self.top_floor,
        )

    @classmethod
    def from_text(cls, text: str) -> 'State':
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_file(cls, fn: str) -> 'State':
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'State':
        # "The first floor contains
        #  a hydrogen-compatible microchip, a plutonium generator, and a strontium generator."
        # "The third floor contains a lithium generator."
        # "The fourth floor contains nothing relevant."

        lines = list(lines)
        elements: dict[str, str] = {}
        taken_element_letters: set[str] = {'E'}  # not to confuse with elevator

        def element_letter(element_name: str) -> str:
            if element_name not in elements:
                letter = element_name[0].upper()
                while letter in taken_element_letters:
                    letter = abc_rot(letter, +1)
                elements[element_name] = letter
                taken_element_letters.add(letter)
                assert len(elements) < 26

            return elements[element_name]

        def parse_items(items_str: str) -> Iterable[str]:
            parts = [p2 for p1 in items_str.split(" and ") for p2 in p1.rstrip(",").split(", ")]
            for part in parts:
                if "generator" in part:
                    element, = parse_line(part, "a $ generator")
                    yield element_letter(element) + 'G'
                elif "microchip" in part:
                    element, = parse_line(part, "a $-compatible microchip")
                    yield element_letter(element) + 'M'
                elif "nothing relevant" in part:
                    pass
                else:
                    raise ValueError("part")

        def positions() -> Iterable[tuple[str, int]]:
            yield 'E', 1  # elevator always starts at floor 1
            for index, line in enumerate(lines):
                floor_ord, items = parse_line(line.strip(), "The $ floor contains $.")
                assert floor_ord == ["first", "second", "third", "fourth"][index]
                floor_number = index + 1
                for item in parse_items(items):
                    yield item, floor_number

        return cls(positions(), top_floor=len(lines))


def is_microchip(key: str) -> bool:
    return len(key) == 2 and key[1] == 'M'


def is_generator(key: str) -> bool:
    return len(key) == 2 and key[1] == 'G'


def final_state(state: State) -> State:
    return type(state)(
        positions=((item, state.top_floor) for item in state.positions),
        top_floor=state.top_floor
    )


def extended_for_part_2(
    state: State,
    new_items: Iterable[tuple[str, int]] = (
        # elerium generator and chip
        ('FG', 1), ('FM', 1),
        # dilithium generator and chip
        ('DG', 1), ('DM', 1)
    )
) -> 'State':
    new_items = list(new_items)
    assert all(new_item not in state for new_item in new_items)
    return type(state)(
        positions=state.positions | dict(new_items),
        top_floor=state.top_floor
    )


Move = tuple[int, str, ...]


def generate_moves(state: State) -> Iterable[Move]:
    pickable_items = list(state.pickable_items())

    def item_combinations() -> Iterable[tuple[str, ...]]:
        yield from combinations(pickable_items, 1)
        yield from combinations(pickable_items, 2)

    def directions() -> Iterable[int]:
        if state.elevator_floor > 1:
            yield -1
        if state.elevator_floor < state.top_floor:
            yield +1

    for item_combination in item_combinations():
        for direction in directions():
            yield (direction,) + item_combination


def following_states(state: State) -> Iterable[tuple[State, Move, int]]:
    for move in generate_moves(state):
        try:
            yield state.move(*move), move, 1
        except ValueError:
            pass


def search(initial_state: State) -> tuple[int, list[Move]]:
    return shortest_path(
        start=initial_state,
        target=final_state(initial_state),
        edges=following_states
    )


if __name__ == '__main__':
    initial_state_ = State.from_file('data/11-input.txt')
    part_1(initial_state_)
    part_2(initial_state_)
