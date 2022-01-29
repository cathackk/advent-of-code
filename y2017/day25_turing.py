"""
Advent of Code 2017
Day 25: The Halting Problem
https://adventofcode.com/2017/day/25
"""

from dataclasses import dataclass
from typing import Iterable

from tqdm import tqdm

from common.file import relative_path
from common.text import parse_line


def part_1(machine: 'Machine') -> int:
    """
    Following the twisty passageways deeper and deeper into the CPU, you finally reach the core of
    the computer. Here, in the expansive central chamber, you find a grand apparatus that fills the
    entire room, suspended nanometers above your head.

    You had always imagined CPUs to be noisy, chaotic places, bustling with activity. Instead, the
    room is quiet, motionless, and dark.

    Suddenly, you and the CPU's **garbage collector** startle each other. "It's not often we get
    many visitors here!", he says. You inquire about the stopped machinery.

    "It stopped milliseconds ago; not sure why. I'm a garbage collector, not a doctor." You ask what
    the machine is for.

    "Programs these days, don't know their origins. That's the **Turing machine**! It's what makes
    the whole computer work." You try to explain that Turing machines are merely models of
    computation, but he cuts you off. "No, see, that's just what they **want** you to think.
    Ultimately, inside every CPU, there's a Turing machine driving the whole thing! Too bad this
    one's broken. We're doomed!"

    You ask how you can help. "Well, unfortunately, the only way to get the computer running again
    would be to create a whole new Turing machine from scratch, but there's no **way** you can-"
    He notices the look on your face, gives you a curious glance, shrugs, and goes back to sweeping
    the floor.

    You find the **Turing machine blueprints** (your puzzle input) on a tablet in a nearby pile of
    debris. Looking back up at the broken Turing machine above, you can start to identify its parts:

      - A **tape** which contains `0` repeated infinitely to the left and right.
      - A **cursor**, which can move left or right along the tape and read or write values at its
        current position.
      - A set of **states**, each containing rules about what to do based on the current value under
        the cursor.

    Each slot on the tape has two possible values: `0` (the starting value for all slots) and `1`.
    Based on whether the cursor is pointing at a `0` or a `1`, the current state says **what value
    to write** at the current position of the cursor, whether to **move the cursor** left or right
    one slot, and **which state to use next**.

    For example, suppose you found the following blueprint:

        >>> example_machine = Machine.from_text('''
        ...     Begin in state A.
        ...     Perform a diagnostic checksum after 6 steps.
        ...
        ...     In state A:
        ...       If the current value is 0:
        ...         - Write the value 1.
        ...         - Move one slot to the right.
        ...         - Continue with state B.
        ...       If the current value is 1:
        ...         - Write the value 0.
        ...         - Move one slot to the left.
        ...         - Continue with state B.
        ...
        ...     In state B:
        ...       If the current value is 0:
        ...         - Write the value 1.
        ...         - Move one slot to the left.
        ...         - Continue with state A.
        ...       If the current value is 1:
        ...         - Write the value 1.
        ...         - Move one slot to the right.
        ...         - Continue with state A.
        ... ''')
        >>> example_machine  # doctest: +NORMALIZE_WHITESPACE
        Machine(init_state='A', steps=6,
                rules={('A', 0): Action(write=1, move=+1, next_state='B'),
                       ('A', 1): Action(write=0, move=-1, next_state='B'),
                       ('B', 0): Action(write=1, move=-1, next_state='A'),
                       ('B', 1): Action(write=1, move=+1, next_state='A')})

    Running it until the number of steps required to take the listed **diagnostic checksum** would
    result in the following tape configurations (with the **cursor** marked in square brackets):

        >>> checksum = example_machine.run(log=True)
        .. 0  0  0 [0] 0  0 .. (before any steps; about to run state A)
        .. 0  0  0  1 [0] 0 .. (after 1 step;     about to run state B)
        .. 0  0  0 [1] 1  0 .. (after 2 steps;    about to run state A)
        .. 0  0 [0] 0  1  0 .. (after 3 steps;    about to run state B)
        .. 0 [0] 1  0  1  0 .. (after 4 steps;    about to run state A)
        .. 0  1 [1] 0  1  0 .. (after 5 steps;    about to run state B)
        .. 0  1  1 [0] 1  0 .. (after 6 steps;    about to run state A)

    The CPU can confirm that the Turing machine is working by taking a **diagnostic checksum** after
    a specific number of steps (given in the blueprint). Once the specified number of steps have
    been executed, the Turing machine should pause; once it does, count the number of times `1`
    appears on the tape. In the above example, the **diagnostic checksum** is **`3`**.

        >>> checksum
        3

    Recreate the Turing machine and save the computer! **What is the diagnostic checksum** it
    produces once it's working again?

        >>> part_1(example_machine)
        part 1: diagnostic checksum is 3
        3
    """

    result = machine.run()
    print(f"part 1: diagnostic checksum is {result}")
    return result


State = str


@dataclass(frozen=True)
class Action:
    write: int
    move: int
    next_state: State

    def __repr__(self) -> str:
        tn = type(self).__name__
        return f'{tn}(write={self.write!r}, move={self.move:+}, next_state={self.next_state!r})'


StateValue = tuple[State, int]
Rule = tuple[StateValue, Action]


class Machine:
    def __init__(self, init_state: State, steps: int, rules: Iterable[Rule]):
        self.init_state = init_state
        self.steps = steps
        self.rules = dict(rules)

    def __repr__(self) -> str:
        tn = type(self).__name__
        return f'{tn}(init_state={self.init_state!r}, steps={self.steps!r}, rules={self.rules!r})'

    def run(self, log: bool = False) -> int:
        tape_ones: set[int] = set()
        current_state = self.init_state
        cursor = 0

        def read(pos: int) -> int:
            return int(pos in tape_ones)

        def write(pos: int, value: int) -> None:
            if value:
                tape_ones.add(pos)
            else:
                tape_ones.discard(pos)

        def log_state(steps: int, curs: int, state: str) -> None:
            if not log:
                return

            def char(pos: int) -> str:
                value = read(pos)
                return f"[{value}]" if pos == curs else f" {value} "

            tape_str = "".join(char(p) for p in range(-3, 3))

            if steps == 0:
                steps_taken = "before any steps;"
            elif steps == 1:
                steps_taken = "after 1 step;"
            else:
                steps_taken = f"after {steps} steps;"

            print(f"..{tape_str}.. ({steps_taken:18}about to run state {state})")

        for step in tqdm(
            range(self.steps), desc="running", unit=" steps", unit_scale=True, delay=0.5
        ):
            log_state(step, cursor, current_state)
            action = self.rules[current_state, read(cursor)]
            write(cursor, action.write)
            cursor += action.move
            current_state = action.next_state

        log_state(self.steps, cursor, current_state)

        return len(tape_ones)

    @classmethod
    def from_text(cls, text: str) -> 'Machine':
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_file(cls, fn: str) -> 'Machine':
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Machine':
        lines_it = (line.strip() for line in lines)

        init_state, = parse_line(next(lines_it), "Begin in state $.")
        steps, = parse_line(next(lines_it), "Perform a diagnostic checksum after $ steps.")

        def rules() -> Iterable[Rule]:
            moves = {'left': -1, 'right': +1}
            while True:
                try:
                    empty_line = next(lines_it)
                    assert not empty_line
                except StopIteration:
                    # all rules read
                    return

                try:
                    current_state, = parse_line(next(lines_it), "In state $:")
                    for current_value in range(2):
                        assert next(lines_it) == f"If the current value is {current_value}:"
                        write, = parse_line(next(lines_it), "- Write the value $.")
                        move_dir, = parse_line(next(lines_it), "- Move one slot to the $.")
                        next_state, = parse_line(next(lines_it), "- Continue with state $.")
                        action = Action(int(write), moves[move_dir], next_state)
                        yield (current_state, current_value), action
                except StopIteration as stop:
                    # unexpected end of file/lines
                    raise EOFError() from stop

        return cls(init_state=init_state, steps=int(steps), rules=rules())


if __name__ == '__main__':
    machine_ = Machine.from_file('data/25-input.txt')
    part_1(machine_)
