from collections import defaultdict
from typing import Dict
from typing import Iterable
from typing import NamedTuple
from typing import Tuple

from utils import strip_line


RuleKey = Tuple[str, int]


class Rule(NamedTuple):
    current_state: str
    current_value: int
    next_state: str
    next_value: int
    jump: int

    @property
    def key(self) -> RuleKey:
        return self.current_state, self.current_value

    @property
    def value(self) -> Tuple[str, int, int]:
        return self.next_state, self.next_value, self.jump

    def __str__(self):
        return f"{self.key} -> {self.value}"


def load(fn: str) -> Tuple[str, int, Dict[RuleKey, Rule]]:
    jd = {"left": -1, "right": +1}

    f = open(fn)

    def load_rules() -> Iterable[Rule]:
        while True:
            assert len(f.readline().strip()) == 0
            # 'In state A:'
            state_line = f.readline()
            if not state_line:
                return
            current_state = strip_line(state_line, "In state ", ":")
            for _ in range(2):
                yield Rule(
                    current_state=current_state,
                    # 'If the current value is 0:'
                    current_value=int(strip_line(f.readline(), "If the current value is ", ":")),
                    # '- Write the value 1.'
                    next_value=int(strip_line(f.readline(), "- Write the value ", ".")),
                    # '- Move one slot to the right.'
                    jump=jd[strip_line(f.readline(), "- Move one slot to the ", ".")],
                    # '- Continue with state B.'
                    next_state=strip_line(f.readline(), "- Continue with state ", "."),
                )

    return (
        # 'Begin in state A.'
        strip_line(f.readline(), "Begin in state ", "."),
        # 'Perform a diagnostic checksum after 12919244 steps.'
        int(strip_line(f.readline(), "Perform a diagnostic checksum after ", " steps.")),
        # (rules)
        {r.key: r for r in load_rules()}
    )


def run(fn: str) -> int:
    state, ticks, rules = load(fn)
    tape: Dict[int, int] = defaultdict(int)
    head = 0
    for tick in range(ticks):
        value = tape[head]
        state, tape[head], jump = rules[(state, value)].value
        head += jump
    return sum(tape.values())


if __name__ == '__main__':
    result = run("data/25-input.txt")
    print(f"part 1: diagnostic checksum is {result}")
