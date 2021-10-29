from itertools import combinations
from typing import Dict
from typing import Iterable
from typing import Optional

from utils import dgroupby


class State:
    def __init__(self, floors: int, elevator_at: int, items: Iterable[tuple[str, int]]):
        assert floors > 1
        assert 1 <= elevator_at <= floors

        self.floors = floors
        self.elevator_at = elevator_at
        self.items_by_floor: Dict[int, list[str]] = {floor: [] for floor in range(1, floors+1)}
        for item, floor in items:
            self.items_by_floor[floor].append(item)
        self._key: Optional[str] = None

        assert sum(len(fitems) for fitems in self.items_by_floor.values()) % 2 == 0
        for item, floor in self.ifs():
            assert len(item) == 2
            assert item[0] in {'G', 'M'}  # generator or microchip

    def ifs(self) -> Iterable[tuple[str, int]]:
        return (
            (item, floor)
            for floor, fitems in self.items_by_floor.items()
            for item in fitems
        )

    def key(self) -> str:
        if self._key is None:
            self._key = self._create_key()
        return self._key

    def _create_key(self) -> str:
        # self.items_by_floor = {1: ['GB'], 2: ['MA'], 3: ['MB', 'GA']}
        # self.items = [('GB', 1), ('MA', 2), ('MB', 3), ('GA', 3)]
        # g1 = {'A': [('M': 2), ('G', 3)], 'B': [('G', 1), ('M', 3)]}
        g1: Dict[str, list[tuple[str, int]]] = dgroupby(
            self.ifs(),
            key=lambda if_: if_[0][1],  # code
            value=lambda if_: (if_[0][0], if_[1])  # (type, floor)
        )
        # g2 = {'A': (3, 2), 'B': (1, 3)}  # (G, M)
        g2: Dict[str, tuple[int, int]] = {
            code: tuple(f for t, f in sorted(tfs))
            for code, tfs in g1.items()
        }
        # cs = ['B', 'A']  # sorted by values
        cs = sorted(g2.keys(), key=lambda code: g2[code])
        # tr = {'GB': 'G0', 'MB': 'M0', 'GA': 'G1', 'MA': 'M1'}
        tr = {t + code: t + str(n) for n, code in enumerate(cs) for t in ['G', 'M']}
        # return 'E1F1G0F2M1F3G1M0'
        return f'E{self.elevator_at}' + ''.join(
            f'F{f}' + ''.join(sorted(tr[item] for item in self.items_by_floor[f]))
            for f in range(1, self.floors + 1)
        )

    def __eq__(self, other):
        return isinstance(other, State) and self.key() == other.key()

    def __hash__(self):
        return hash(self.key())

    def draw(self) -> None:
        all_items = sorted(
            (item for item, _ in self.ifs()),
            key=lambda item: (item[1], item[0])
        )
        for floor in range(self.floors, 0, -1):
            print(f"F{floor}", end=" ")
            print("E" if self.elevator_at == floor else ".", end="  ")
            for item in all_items:
                print(item if item in self.items_by_floor[floor] else ". ", end=" ")
            print()

    def fried_chips(self) -> Iterable[tuple[str, int]]:
        for floor, fitems in self.items_by_floor.items():
            any_generator_on_floor = any(item[0] == 'G' for item in fitems)
            items_by_code = dgroupby(fitems, key=lambda item: item[1], value=lambda item: item[0])
            for item_code, item_types in items_by_code.items():
                if len(item_types) == 1 and item_types[0] == 'M' and any_generator_on_floor:
                    yield 'M'+item_code, floor

    def is_valid(self):
        return not any(self.fried_chips())

    def move(self, direction: int, *take_with: str) -> 'State':
        source_floor = self.elevator_at
        target_floor = self.elevator_at + direction
        take_with = set(take_with)

        assert direction in (-1, +1), f"cannot move in direction {direction:+}"
        assert 1 <= target_floor <= self.floors, f"cannot go to {target_floor}"
        assert len(take_with) > 0, f"must take any items with you"
        assert len(take_with) <= 2, f"cannot take more than 2 items with you ({len(take_with)})"
        for item in take_with:
            assert item in self.items_by_floor[source_floor], f"{item} not at current floor"

        return State(
            floors=self.floors,
            elevator_at=target_floor,
            items=(
                (item, target_floor if item in take_with else floor)
                for item, floor in self.ifs()
            )
        )


def following_states(state: State, previous_keys: set[str] = None) -> Iterable[State]:
    if previous_keys is None:
        previous_keys = set()

    current_items = state.items_by_floor[state.elevator_at]

    def items_combinations() -> Iterable[tuple[str, ...]]:
        yield from combinations(current_items, 1)
        yield from combinations(current_items, 2)

    def directions() -> Iterable[int]:
        if state.elevator_at > 1:
            yield -1
        if state.elevator_at < state.floors:
            yield +1

    for direction in directions():
        for take_with in items_combinations():
            new_state = state.move(direction, *take_with)
            if new_state.key() in previous_keys:
                continue
            previous_keys.add(new_state.key())
            if not new_state.is_valid():
                continue
            yield new_state


def end_state(state: State) -> State:
    return State(
        floors=state.floors,
        elevator_at=state.floors,
        items=(
            (item, state.floors)
            for item, _ in state.ifs()
        )
    )


def search(start: State, end: State = None, debug: bool = False) -> int:
    if end is None:
        end = end_state(start)

    buffer: list[tuple[State, int]] = [(start, 0)]
    known_keys = set(start.key())
    tick = 0

    while buffer:
        s0, steps = buffer.pop(0)
        if debug and tick % 1000 == 0:
            print(f"tick={tick}, step={steps}, buffer={len(buffer)}, known={len(known_keys)}")
            s0.draw()
            print()
        tick += 1

        for s1 in following_states(s0, known_keys):
            buffer.append((s1, steps+1))
            if s1 == end:
                if debug:
                    print(f"Found in {steps + 1} steps, {tick} ticks")
                    s1.draw()
                    print()
                return steps + 1


def part_1(state: State) -> int:
    steps = search(state)
    print(f"part 1: takes {steps} steps")
    return steps


def part_2(state: State) -> int:
    modified_state = State(
        floors=state.floors,
        elevator_at=state.elevator_at,
        items=list(state.ifs()) + [('GE', 1), ('ME', 1), ('GD', 1), ('MD', 1)]
    )
    steps = search(modified_state)
    print(f"part 2: takes {steps} steps")
    return steps


def test_eq():
    s1 = State(
        floors=4, elevator_at=1,
        items=[('GA', 1), ('MA', 1), ('GB', 2), ('MB', 2)]
    )
    s2 = State(
        floors=4, elevator_at=1,
        items=[('GA', 2), ('MA', 2), ('GB', 1), ('MB', 1)]
    )
    print(s1.key())
    print(s2.key())
    assert s1 == s2


if __name__ == '__main__':
    s_ = State(
        floors=4, elevator_at=1,
        items=[
            ('GT', 1), ('MT', 1), ('GU', 1), ('GS', 1),
            ('MU', 2), ('MS', 2),
            ('GP', 3), ('MP', 3), ('GR', 3), ('MR', 3)
        ]
    )
    part_1(s_)
    part_2(s_)
