from collections import defaultdict
from itertools import count
from typing import Generator
from typing import Iterable

from common.utils import dgroupby_set
from common.utils import exhaust
from common.utils import parse_line

Dependency = tuple[str, str]


def load_dependencies(fn: str) -> Iterable[Dependency]:
    # Step Y must be finished before step M can begin.
    for line in open(fn):
        yield parse_line(line, "Step $ must be finished before step $ can begin.\n")


def step_length(step: str) -> int:
    return 61 + ord(step) - ord('A')


def build(
        dependencies: Iterable[Dependency],
        workers_count: int,
        debug: bool = False
) -> Generator[str, None, int]:
    requirements: dict[str, set[str]] = dgroupby_set(
        dependencies,
        key=lambda ab: ab[1],
        value=lambda ab: ab[0]
    )

    steps_unprocessed: set[str] = set(s for d in dependencies for s in d)
    steps_count = len(steps_unprocessed)
    steps_in_progress: dict[int, set[str]] = defaultdict(set)
    steps_finished: set[str] = set()

    def log(msg: str = ""):
        if debug:
            print(f"[{tick:4}] {msg}")

    for tick in count(0):
        if tick in steps_in_progress:
            for step in sorted(steps_in_progress.pop(tick)):
                assert step not in steps_finished
                steps_finished.add(step)
                yield step
                log(f"finishing {step} ({len(steps_finished)}/{steps_count})")

        if len(steps_finished) == steps_count:
            log("done!")
            return tick

        free_workers_count = workers_count - len(steps_in_progress)
        assert free_workers_count >= 0
        if free_workers_count > 0:
            possible_steps = {
                step
                for step in steps_unprocessed
                if step not in requirements
                or steps_finished.issuperset(requirements[step])
            }
            selected_steps = sorted(possible_steps)[:free_workers_count]
            for step in selected_steps:
                step_finished_tick = tick + step_length(step)
                steps_in_progress[step_finished_tick].add(step)
                log(f"started working on {step}, will finish at {step_finished_tick}")
            steps_unprocessed.difference_update(selected_steps)


def part_1(dependencies: set[Dependency], debug=False) -> str:
    steps = ''.join(build(dependencies, workers_count=1, debug=debug))
    print(f"part 1: sequence is {steps}")
    return steps


def part_2(dependencies: set[Dependency], debug=False) -> int:
    seconds = exhaust(build(dependencies, workers_count=5, debug=debug))
    print(f"part 2: it takes {seconds} seconds to finish all the steps")
    return seconds


if __name__ == '__main__':
    dependencies_ = set(load_dependencies("data/07-input.txt"))
    part_1(dependencies_)
    part_2(dependencies_)
