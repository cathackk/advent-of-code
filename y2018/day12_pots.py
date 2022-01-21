from itertools import count
from typing import Iterable
from typing import Iterator

from common.iteration import minmax
from common.text import strip_line

Rule = tuple[int, bool]
Rules = set[int]


class State:
    @classmethod
    def from_line(cls, line: str):
        return cls(x for x, c in enumerate(line) if c == '#')

    def __init__(self, alive: Iterable[int]):
        self.alive = set(alive)

    def __bool__(self):
        return bool(self.alive)

    def score(self) -> int:
        return sum(self.alive)

    def _xrange(self) -> range:
        xmin, xmax = minmax(self.alive)
        return range(xmin-3, xmax+4)

    def __iter__(self) -> Iterator[tuple[int, bool]]:
        return (
            (x, x in self.alive)
            for x in self._xrange()
        )

    def __repr__(self):
        return f'{type(self).__name__}({list(x for x, a in self if a)})'

    def __str__(self):
        return ''.join('#' if a else '.' for _, a in self)

    def next_generation(self, rules: Rules):
        def neighborhood() -> Iterator[tuple[int, int]]:
            n = 0
            for x, a in self:
                n = (n*2 + int(a)) % 32
                yield x - 2, n

        return State(x for x, n in neighborhood() if n in rules)


def load(fn: str) -> tuple[State, Rules]:
    f = open(fn)
    initial_state = State.from_line(strip_line(next(f), "initial state: ", "\n"))
    assert next(f) == "\n"

    rules: Rules = set()
    for line in f:
        line_from, line_to = line.strip().split(" => ")
        if line_to == '#':
            assert len(line_from) == 5
            rules.add(sum(1 << (4-x) for x, c in enumerate(line_from) if c == '#'))

    return initial_state, rules


def part_1(fn: str, generations: int = 20) -> int:
    state, rules = load(fn)
    for _ in range(generations):
        state = state.next_generation(rules)
    print(f"part 1: after {generations} generations, score is {state.score()}")
    return state.score()


def run_until_constant_score_delta(
        state: State,
        rules: Rules,
        const_length: int = 10
) -> tuple[int, int, int]:
    deltas = []
    for gen in count(1):
        new_state = state.next_generation(rules)
        deltas.append(new_state.score() - state.score())
        if len(deltas) >= const_length and len(set(deltas[-const_length:])) == 1:
            return gen, new_state.score(), deltas[-1]
        state = new_state


def part_2(fn: str, generations: int = 50_000_000_000) -> int:
    state, rules = load(fn)
    # calculate only until generations start to repeat -> score deltas is constant for some time
    gen, current_score, score_delta = run_until_constant_score_delta(state, rules)
    # extrapolate final score
    final_score = current_score + ((generations - gen) * score_delta)
    print(f"part 2: after {generations} generations, score is {final_score}")
    return final_score


if __name__ == '__main__':
    fn_ = "data/12-input.txt"
    part_1(fn_)
    part_2(fn_)
