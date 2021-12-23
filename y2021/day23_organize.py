"""
Advent of Code 2021
Day 23: Amphipod
https://adventofcode.com/2021/day/23
"""
from itertools import chain
from typing import Iterable

from tqdm import tqdm

from utils import eprint
from utils import parse_line
from utils import zip1


def part_1(initial_state: 'State') -> int:
    """
    A group of amphipods notice your fancy submarine and flag you down. "With such an impressive
    shell," one amphipod says, "surely you can help us with a question that has stumped our best
    scientists."

    They go on to explain that a group of timid, stubborn amphipods live in a nearby burrow. Four
    types of amphipods live there: **Amber** (`A`), **Bronze** (`B`), **Copper** (`C`), and
    **Desert** (`D`). They live in a burrow that consists of a **hallway** and four **side rooms**.
    The side rooms are initially full of amphipods, and the hallway is initially empty.

    They give you a **diagram of the situation** (your puzzle input), including locations of each
    amphipod (`A`, `B`, `C`, or `D`, each of which is occupying an otherwise open space),
    walls (`#`), and open space (`.`).

    For example:

        >>> state_0 = State.from_text('''
        ...
        ...     #############
        ...     #...........#
        ...     ###B#C#B#D###
        ...       #A#D#C#A#
        ...       #########
        ...
        ... ''')
        >>> state_0
        State(rooms=('AB', 'DC', 'CB', 'AD'))
        >>> print(state_0)
        #############
        #...........#
        ###B#C#B#D###
          #A#D#C#A#
          #########

    The amphipods would like a method to organize every amphipod into side rooms so that each side
    room contains one type of amphipod and the types are sorted `A`-`D` going left to right, like
    this:

        >>> print(TARGET_STATE)
        #############
        #...........#
        ###A#B#C#D###
          #A#B#C#D#
          #########
        >>> TARGET_STATE
        State(rooms=('AA', 'BB', 'CC', 'DD'))

    Amphipods can move up, down, left, or right so long as they are moving into an unoccupied open
    space. Each type of amphipod requires a different amount of **energy** to move one step:
    Amber amphipods require `1` energy per step, Bronze amphipods require `10` energy, Copper
    amphipods require `100`, and Desert ones require `1000`.

        >>> State.MOVE_COSTS
        {'A': 1, 'B': 10, 'C': 100, 'D': 1000}

    The amphipods would like you to find a way to organize the amphipods that requires the **least
    total energy**.

    However, because they are timid and stubborn, the amphipods have some extra rules:

      - Amphipods will never **stop on the space immediately outside any room**. They can move into
        that space so long as they immediately continue moving. (Specifically, this refers to the
        four open spaces in the hallway that are directly above an amphipod starting position.)
      - Amphipods will never move **from the hallway into a room** unless that room is their
        destination room and that room contains no amphipods which do not also have that room as
        their own destination. If an amphipod's starting room is not its destination room, it can
        stay in that room until it leaves the room. (For example, an Amber amphipod will not move
        from the hallway into the right three rooms, and will only move into the leftmost room if
        that room is empty or if it only contains other Amber amphipods.)
      - Once an amphipod stops moving in the hallway, **it will stay in that spot until it can move
        into a room**. (That is, once any amphipod starts moving, any other amphipods currently in
        the hallway are locked in place and will not move again until they can move fully into
        a room.)

    In the above example, the amphipods can be organized using a minimum of **`12521`** energy.
    One way to do this is shown below.

    Starting configuration:

        >>> print(state_0)
        #############
        #...........#
        ###B#C#B#D###
          #A#D#C#A#
          #########

    Implementation note - the `move()` method uses these space indexes to indicate where from and to
    the amphipod should move:

        #############
        #45 6 7 8 9X# <- X=10
        ###0#1#2#3###
          #0#1#2#3#
          #########

    One Bronze amphipod moves into the hallway, taking 4 steps and using `40` energy:

        >>> cost_1, state_1 = state_0.move(from_=2, to=6)
        >>> cost_1, state_1
        (40, State(rooms=('AB', 'DC', 'C', 'AD'), hallway=('', '', 'B', '', '', '', '')))
        >>> print(state_1)
        #############
        #...B.......#
        ###B#C#.#D###
          #A#D#C#A#
          #########

    The only Copper amphipod not in its side room moves there, taking 4 steps and using `400`
    energy:

        >>> cost_2, state_2 = state_1.move(1, 2)
        >>> cost_2, state_2
        (400, State(rooms=('AB', 'D', 'CC', 'AD'), hallway=('', '', 'B', '', '', '', '')))
        >>> print(state_2)
        #############
        #...B.......#
        ###B#.#C#D###
          #A#D#C#A#
          #########

    A Desert amphipod moves out of the way, taking 3 steps and using `3000` energy, ...

        >>> cost_3, state_3 = state_2.move(1, 7)
        >>> cost_3, state_3
        (3000, State(rooms=('AB', '', 'CC', 'AD'), hallway=('', '', 'B', 'D', '', '', '')))

    ... and then the Bronze amphipod takes its place, taking 3 steps and using `30` energy:

        >>> cost_4, state_4 = state_3.move(6, 1)
        >>> cost_4, state_4
        (30, State(rooms=('AB', 'B', 'CC', 'AD'), hallway=('', '', '', 'D', '', '', '')))
        >>> print(state_4)
        #############
        #.....D.....#
        ###B#.#C#D###
          #A#B#C#A#
          #########

    The leftmost Bronze amphipod moves to its room using `40` energy:

        >>> cost_5, state_5 = state_4.move(0, 1)
        >>> cost_5, state_5
        (40, State(rooms=('A', 'BB', 'CC', 'AD'), hallway=('', '', '', 'D', '', '', '')))
        >>> print(state_5)
        #############
        #.....D.....#
        ###.#B#C#D###
          #A#B#C#A#
          #########

    Both amphipods in the rightmost room move into the hallway, using `2003` energy in total:

        >>> cost_6, state_6 = state_5.move(3, 8)
        >>> cost_6, state_6
        (2000, State(rooms=('A', 'BB', 'CC', 'A'), hallway=('', '', '', 'D', 'D', '', '')))
        >>> cost_7, state_7 = state_6.move(3, 9)
        >>> cost_7, state_7
        (3, State(rooms=('A', 'BB', 'CC', ''), hallway=('', '', '', 'D', 'D', 'A', '')))
        >>> print(state_7)
        #############
        #.....D.D.A.#
        ###.#B#C#.###
          #A#B#C#.#
          #########

    Both Desert amphipods move into the rightmost room using `7000` energy:

        >>> cost_8, state_8 = state_7.move(8, 3)
        >>> cost_8, state_8
        (3000, State(rooms=('A', 'BB', 'CC', 'D'), hallway=('', '', '', 'D', '', 'A', '')))
        >>> cost_9, state_9 = state_8.move(7, 3)
        >>> cost_9, state_9
        (4000, State(rooms=('A', 'BB', 'CC', 'DD'), hallway=('', '', '', '', '', 'A', '')))
        >>> print(state_9)
        #############
        #.........A.#
        ###.#B#C#D###
          #A#B#C#D#
          #########

    Finally, the last Amber amphipod moves into its room, using `8` energy:

        >>> cost_10, state_10 = state_9.move(9, 0)
        >>> cost_10, state_10
        (8, State(rooms=('AA', 'BB', 'CC', 'DD')))
        >>> print(state_10)
        #############
        #...........#
        ###A#B#C#D###
          #A#B#C#D#
          #########
        >>> state_10 == TARGET_STATE
        True
        >>> cost_1 + cost_2 + cost_3 + cost_4 + cost_5 + cost_6 + cost_7 + cost_8 + cost_9 + cost_10
        12521

    **What is the least energy required to organize the amphipods?**

        >>> part_1(state_0)
        part 1: it takes 12521 energy to organize the amphipods
        12521
    """

    cost, moves = initial_state.find_cheapest_reordering(TARGET_STATE)
    eprint(moves)

    print(f"part 1: it takes {cost} energy to organize the amphipods")
    return cost


def part_2() -> int:
    """
    Instructions for part 2.
    """

    result = 2

    print(f"part 2: {result}")
    return result


Move = tuple[int, int]


class State:
    MOVE_COSTS = {'A': 1, 'B': 10, 'C': 100, 'D': 1000}

    def __init__(self, rooms: Iterable[str], hallway: Iterable[str] = ('',) * 7):
        self.rooms = tuple(rooms)
        self.hallway = tuple(hallway)
        assert len(self.rooms) == 4
        assert len(self.hallway) == 7
        self._hash = hash((self.rooms, self.hallway))  # precomputed hash for faster comparison

    def __repr__(self) -> str:
        hallway_repr = f', hallway={self.hallway!r}' if any(self.hallway) else ''
        return f'{type(self).__name__}(rooms={self.rooms!r}{hallway_repr})'

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and self._hash == other._hash

    def __str__(self) -> str:
        def hch(pos: int) -> str:
            return self.hallway[pos - 4] or '.'

        def rch(pos: int, upper: bool) -> str:
            return room[upper] if upper < len(room := self.rooms[pos]) else '.'

        def lines() -> Iterable[str]:
            yield '#############'
            yield '#' + '.'.join((hch(4) + hch(5), hch(6), hch(7), hch(8), hch(9) + hch(10))) + '#'
            yield '###' + '#'.join(rch(n, upper=True) for n in range(4)) + '###'
            yield '  #' + '#'.join(rch(n, upper=False) for n in range(4)) + '#'
            yield '  #########'

        return '\n'.join(lines())

    @classmethod
    def from_text(cls, text: str) -> 'State':
        return cls.from_lines(text.strip().split('\n'))

    @classmethod
    def from_file(cls, fn: str) -> 'State':
        return cls.from_lines(open(fn))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'State':
        lines = [line.strip() for line in lines]
        assert len(lines) == 5
        assert lines[0] == '#############'

        # hallway
        assert len(lines[1]) == 13
        assert lines[1][0] == lines[1][-1] == '#'
        assert all(lines[1][n] == '.' for n in (3, 5, 7, 9))
        hallway_chars = (lines[1][n] for n in (1, 2, 4, 6, 8, 10, 11))
        hallway = tuple(hch if hch != '.' else '' for hch in hallway_chars)

        # rooms
        rooms_upper = parse_line(lines[2], '###$#$#$#$###')
        rooms_lower = parse_line(lines[3], '#$#$#$#$#')
        assert lines[4] == '#########'

        def room(lower: str, upper: str) -> str:
            assert lower in ('A', 'B', 'C', 'D', '.')
            assert upper in ('A', 'B', 'C', 'D', '.')
            if lower == '.':
                assert upper == '.'
                return ''
            elif upper == '.':
                return lower
            else:
                return lower + upper

        rooms = tuple(room(low, up) for low, up in zip(rooms_lower, rooms_upper))

        return cls(rooms, hallway)

    def move(self, from_: int, to: int) -> tuple[int, 'State'] | None:
        """
        #############
        #45.6.7.8.9X# <- X=10
        ###0#1#2#3###
          #0#1#2#3#
          #########
        """

        # assert 0 <= from_ <= 10
        # assert 0 <= to <= 10
        # assert from_ != to

        # cannot move from hallway to hallway
        if from_ >= 4 and to >= 4:
            return None

        pawn_moved = self._pawn_at(from_)

        # no pawn to move
        if pawn_moved is None:
            return None

        pawns_target_room = ord(pawn_moved) - ord('A')

        # cannot move into non-target room
        if to < 4 and to != pawns_target_room:
            return None

        # # cannot move if already in target room with no foreigners
        # if from_ == pawns_target_room and all(pawn_moved == p for p in self.rooms[from_]):
        #     return None

        # cannot move into room occupied by a foreigner (non-matching pawn)
        if to < 4 and any(pawn_moved != p for p in self.rooms[to]):
            return None

        # destination is already full
        if self._capacity_at(to) < 1:
            return None

        # path is blocked by other pawns
        if not self._path_is_free(from_, to):
            return None

        cost = self.MOVE_COSTS[pawn_moved] * self._distance(from_, to)

        def new_room(pos: int) -> str:
            old_room = self.rooms[pos]
            if pos == from_:
                return old_room[:-1]
            elif pos == to:
                return old_room + pawn_moved
            else:
                return old_room

        def new_hallway(pos: int) -> str:
            old_hw = self.hallway[pos - 4]
            if pos == from_:
                return ''
            elif pos == to:
                return pawn_moved
            else:
                return old_hw

        new_state = State(
            rooms=(new_room(r) for r in range(4)),
            hallway=(new_hallway(h) for h in range(4, 11))
        )

        return cost, new_state

    def _pawn_at(self, pos: int) -> str | None:
        if pos < 4:
            # rooms
            return room[-1] if (room := self.rooms[pos]) else None
        else:
            # hallway
            return self.hallway[pos - 4] or None

    def _capacity_at(self, pos: int) -> int:
        if pos < 4:
            # rooms
            return 2 - len(self.rooms[pos])
        else:
            # hallway
            return 1 - len(self.hallway[pos - 4])

    def _path_is_free(self, from_: int, to: int) -> bool:
        return all(self._pawn_at(pos) is None for pos in path(from_, to))

    def _distance(self, from_: int, to: int) -> int:
        base_distance = len(_PATHS[from_, to]) + 1
        # full room -> 0, half-full room -> 1, hallway -> 0
        extra_room_from_steps = (2 - len(self.rooms[from_])) if from_ in range(4) else 0
        # half-full room -> 0, empty room -> 1, hallway -> 0
        extra_room_to_steps = (1 - len(self.rooms[to])) if to in range(4) else 0
        return base_distance + extra_room_from_steps + extra_room_to_steps

    def find_cheapest_reordering(self, destination: 'State') -> tuple[int, list[Move]]:
        # Dijkstra's algorithm

        # state -> cheapest known reordering from starting state
        # (stored as total cost up to here, previous state, move from previous state to this one)
        visited_states: dict[State, tuple[int, State | None, Move | None]] = dict()
        # unvisited states neighboring those that are visited (stored as the one above)
        states_to_visit: dict[State, tuple[int, State, Move]] = dict()

        def visit(state: State, total_cost: int, previous_state: State | None, move: Move | None):
            visited_states[state] = total_cost, previous_state, move
            states_to_visit.update(
                (state1, (total_cost + cost1, state, move1))
                # add following states of this one
                for cost1, state1, move1 in generate_following_states(state)
                # that were not visited yet
                if state1 not in visited_states
                if (
                    # that were not following a visited state before
                    state1 not in states_to_visit
                    # or ones for which we just found a cheaper reordering
                    or total_cost + cost1 < states_to_visit[state1][0]
                )
            )

        def generate_following_states(state: State) -> Iterable[tuple[int, State, Move]]:
            from_to: Iterable[tuple[int, int]] = chain(
                # room to room
                ((from_r, to_r) for from_r in range(4) for to_r in range(4) if from_r != to_r),
                # room to hallway
                ((from_r, to_hw) for from_r in range(4) for to_hw in range(4, 11)),
                # hallway to room
                ((from_hw, to_r) for from_hw in range(4, 11) for to_r in range(4))
            )

            return (
                new_cost_and_state + ((from_, to),)
                for from_, to in from_to
                if (new_cost_and_state := state.move(from_, to)) is not None
            )

        # start by visiting origin = self ...
        origin = self
        visit(origin, total_cost=0, previous_state=None, move=None)
        # ... then adding following states until the destination is visited
        progress = tqdm(desc="finding cheapest reordering", unit="states", initial=1, delay=1.0)
        while destination not in visited_states:
            # visit the cheapest unvisited state adjacent to one visited
            new_state = min(states_to_visit, key=lambda s: states_to_visit[s][0])
            visit(new_state, *states_to_visit.pop(new_state))
            progress.update()

        # construct the final move sequence by backtracking
        def backtrack(state: State) -> Iterable[Move]:
            while state != origin:
                _, prev_state, move = visited_states[state]
                yield move
                state = prev_state

        final_cost = visited_states[destination][0]
        final_moves = list(backtrack(destination))[::-1]
        return final_cost, final_moves


TARGET_STATE = State(rooms=('AA', 'BB', 'CC', 'DD'))


def path(from_: int, to: int) -> Iterable[int]:
    return (pos for pos in _PATHS[from_, to] if isinstance(pos, int))


def _generate_paths() -> dict[tuple[int, int], list[int | str]]:
    # 4-5-H0-6-H1-7-H2-8-H3-9-10
    #     |    |    |    |
    #     0    1    2    3

    Node = int | str
    Edge = tuple[Node, Node]

    edges: set[Edge] = {(r, f'H{r}') for r in range(4)}
    edges.update((a, b) for a, b in zip1([4, 5, 'H0', 6, 'H1', 7, 'H2', 8, 'H3', 9, 10]))
    nodes = sorted(set(node for n1n2 in edges for node in n1n2), key=str)
    neighbors: dict[Node, list[Node]] = {
        node: [
            neighbor
            for neighbor in nodes
            if (node, neighbor) in edges or (neighbor, node) in edges
        ]
        for node in nodes
    }

    # (from, to): [from, intermediate nodes, to]
    full_paths: dict[tuple[Node, Node], list[Node]] = dict()
    for origin in nodes:
        full_paths[origin, origin] = [origin]
        visited: set[Node] = set()
        to_visit: list[Node] = [origin]
        while to_visit:
            current = to_visit.pop()
            visited.add(current)
            unvisited_neighbors = (
                neighbor
                for neighbor in neighbors[current]
                if neighbor not in visited
            )
            for neighbor in unvisited_neighbors:
                full_paths[origin, neighbor] = full_paths[origin, current] + [neighbor]
                to_visit.append(neighbor)

    # (from, to): [intermediate nodes]
    return {
        (from_, to): full_path[1:-1]
        for (from_, to), full_path in full_paths.items()
        if from_ != to
    }


_PATHS = _generate_paths()


if __name__ == '__main__':
    initial_state_ = State.from_file('data/23-input.txt')
    part_1(initial_state_)
    part_2()
