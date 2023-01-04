"""
Advent of Code 2018
Day 7: The Sum of Its Parts
https://adventofcode.com/2018/day/7
"""

from collections import defaultdict
from dataclasses import dataclass
from itertools import count
from typing import Generator
from typing import Iterable
from typing import Iterator

from common.iteration import dgroupby_pairs_set
from common.iteration import exhaust
from common.iteration import last
from common.text import parse_line
from meta.aoc_tools import data_path


def part_1(instructions: Iterable['Dependency']) -> str:
    r"""
    You find yourself standing on a snow-covered coastline; apparently, you landed a little off
    course. The region is too hilly to see the North Pole from here, but you do spot some Elves that
    seem to be trying to unpack something that washed ashore. It's quite cold out, so you decide to
    risk creating a paradox by asking them for directions.

    "Oh, are you the search party?" Somehow, you can understand whatever Elves from the year 1018
    speak; you assume it's Ancient Nordic Elvish. Could the device on your wrist also be
    a translator? "Those clothes don't look very warm; take this." They hand you a heavy coat.

    "We do need to find our way back to the North Pole, but we have higher priorities at the moment.
    You see, believe it or not, this box contains something that will solve all of Santa's
    transportation problems - at least, that's what it looks like from the pictures in the
    instructions." It doesn't seem like they can read whatever language it's in, but you can:
    "Sleigh kit. Some assembly required."

    "'Sleigh'? What a wonderful name! You must help us assemble this 'sleigh' at once!" They start
    excitedly pulling more parts out of the box.

    The instructions specify a series of **steps** and requirements about which steps must be
    finished before others can begin (your puzzle input). Each step is designated by a single
    letter. For example, suppose you have the following instructions:

        >>> example = instructions_from_text('''
        ...     Step C must be finished before step A can begin.
        ...     Step C must be finished before step F can begin.
        ...     Step A must be finished before step B can begin.
        ...     Step A must be finished before step D can begin.
        ...     Step B must be finished before step E can begin.
        ...     Step D must be finished before step E can begin.
        ...     Step F must be finished before step E can begin.
        ... ''')
        >>> example
        [('C', 'A'), ('C', 'F'), ('A', 'B'), ('A', 'D'), ('B', 'E'), ('D', 'E'), ('F', 'E')]

    Visually, these requirements look like this:

          -->A--->B--
         /    \      \
        C      -->D----->E
         \           /
          ---->F-----

    Your first goal is to determine the order in which the steps should be completed. If more than
    one step is ready, choose the step which is first alphabetically. In this example, the steps
    would be completed as follows:

      - Only **`C`** is available, and so it is done first.
      - Next, both `A` and `F` are available. **`A`** is first alphabetically, so it is done next.
      - Then, even though `F` was available earlier, steps `B` and `D` are now also available, and
        **`B`** is the first alphabetically of the three.
      - After that, only `D` and `F` are available. `E` is not available because only some of its
        prerequisites are complete. Therefore, **`D`** is completed next.
      - **`F`** is the only choice, so it is done next.
      - Finally, **`E`** is completed.

    So, in this example, the correct order is `CABDFE`:

        >>> build_sequence(example)
        'CABDFE'

    **In what order should the steps in your instructions be completed?**

        >>> part_1(example)
        part 1: build sequence is 'CABDFE'
        'CABDFE'
    """

    steps = build_sequence(instructions)
    print(f"part 1: build sequence is {steps!r}")
    return steps


def part_2(instructions: Iterable['Dependency']) -> int:
    """
    As you're about to begin construction, four of the Elves offer to help. "The sun will set soon;
    it'll go faster if we work together." Now, you need to account for multiple people working on
    steps simultaneously. If multiple steps are available, workers should still begin them in
    alphabetical order.

    Each step takes 60 seconds plus an amount corresponding to its letter: A=1, B=2, C=3, and so on.
    So, step A takes `60+1=61` seconds, while step Z takes `60+26=86` seconds.

        >>> step_length('A')
        61
        >>> step_length('Z')
        86

    No time is required between steps.

    To simplify things for the example, however, suppose you only have help from one Elf (a total of
    two workers) and that each step takes 60 fewer seconds (so that step A takes 1 second and step Z
    takes 26 seconds). Then, using the same instructions as above, this is how each second would be
    spent:

        >>> example = instructions_from_file('data/07-example.txt')
        >>> print_schedule(build(example, workers_count=2, step_length_base=0))
        Second   Worker 1   Worker 2   Done
           0        C          .
           1        C          .
           2        C          .
           3        A          F       C
           4        B          F       CA
           5        B          F       CA
           6        D          F       CAB
           7        D          F       CAB
           8        D          F       CAB
           9        D          .       CABF
          10        E          .       CABFD
          11        E          .       CABFD
          12        E          .       CABFD
          13        E          .       CABFD
          14        E          .       CABFD
          15        .          .       CABFDE

    Each row represents one second of time. The *Second* column identifies how many seconds have
    passed as of the beginning of that second. Each worker column shows the step that worker is
    currently doing (or `.` if they are idle). The *Done* column shows completed steps.

    Note that the order of the steps has changed; this is because steps now take time to finish and
    multiple workers can begin multiple steps simultaneously.

    In this example, it would take **15** seconds for two workers to complete these steps.

        >>> exhaust(build(example, workers_count=2, step_length_base=0))
        15

    With **5** workers and the **60+ second** step durations described above, **how long will it
    take to complete all of the steps?**

        >>> part_2(example)
        part 2: it takes 253 seconds to complete all the steps
        253
    """

    seconds = exhaust(build(instructions, workers_count=5))
    print(f"part 2: it takes {seconds} seconds to complete all the steps")
    return seconds


Dependency = tuple[str, str]


def step_length(step: str, base: int = 60) -> int:
    return base + ord(step) - ord('A') + 1


@dataclass(frozen=True)
class BuildState:
    second: int
    working_on: list[str]
    finished: list[str]


def build_sequence(dependencies: Iterable[Dependency]) -> str:
    return ''.join(last(build(dependencies)).finished)


def build(
    instructions: Iterable[Dependency],
    workers_count: int = 1,
    step_length_base: int = 60,
) -> Generator[BuildState, None, int]:
    instructions_list = list(instructions)

    # to finish step -> set of steps required to be finished first
    requirements = dgroupby_pairs_set((after, before) for before, after in instructions_list)
    steps_unprocessed: set[str] = set(step for dep in instructions_list for step in dep)
    # second -> steps finished at that moment
    steps_in_progress: dict[int, set[str]] = defaultdict(set)
    steps_finished: list[str] = []

    for second in count(0):
        # update finished steps with those whose work ends this second
        steps_finished.extend(sorted(steps_in_progress.pop(second, [])))

        # anybody free to work?
        free_workers_count = workers_count - len(steps_in_progress)
        assert free_workers_count >= 0
        if free_workers_count > 0:
            # let's give them something to do! these steps can be worked on:
            available_steps = {
                step
                for step in steps_unprocessed
                if step not in requirements  # initial step
                or requirements[step].issubset(steps_finished)  # requirements satisfied
            }
            # selected as many as possible:
            selected_steps = sorted(available_steps)[:free_workers_count]
            # note when each of the selected step is finished
            for step in selected_steps:
                step_finished_second = second + step_length(step, base=step_length_base)
                steps_in_progress[step_finished_second].add(step)

            steps_unprocessed.difference_update(selected_steps)

        # report
        working_on: list[str] = sorted(
            step
            for steps in steps_in_progress.values()
            for step in steps
        )
        working_on.extend([''] * (workers_count - len(working_on)))
        yield BuildState(second, working_on, steps_finished)

        # is all done?
        if not steps_unprocessed and not steps_in_progress:
            return second

    # unreachable
    assert False


def print_schedule(build_states: Iterator[BuildState]):
    for state in build_states:
        if state.second == 0:
            # print header
            workers_count = len(state.working_on)
            header = ["Second"] + [f"Worker {n + 1}" for n in range(workers_count)] + ["Done"]
            print("   ".join(header))

        # print data row
        print(
            "   ".join(
                [str(state.second).rjust(3).center(6)] +
                [(step or ".").center(8) for step in state.working_on] +
                ["".join(state.finished)]
            ).rstrip()
        )


def instructions_from_text(text: str) -> list[Dependency]:
    return list(dependencies_from_lines(text.strip().splitlines()))


def instructions_from_file(fn: str) -> list[Dependency]:
    return list(dependencies_from_lines(open(fn)))


def dependencies_from_lines(lines: Iterable[str]) -> Iterable[Dependency]:
    for line in lines:
        before, after = parse_line(line.strip(), "Step $ must be finished before step $ can begin.")
        yield before, after


def main(input_path: str = data_path(__file__)) -> tuple[str, int]:
    instructions = instructions_from_file(input_path)
    result_1 = part_1(instructions)
    result_2 = part_2(instructions)
    return result_1, result_2


if __name__ == '__main__':
    main()
