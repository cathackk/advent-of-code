from itertools import permutations
from typing import Iterable
from typing import List
from typing import Optional

from machine import load_tape
from machine import Machine


def find_best_phases(tape: Iterable[int], phases_range: range = range(5), debug=False):
    amps = [
        Machine(tape, name=f"Amp {n+1}", debug=debug)
        for n in range(len(phases_range))
    ]

    def run_amps(phases):
        signal = 0
        for amp, phase in zip(amps, phases):
            amp_f = amp.as_function_scalar(init=[phase])
            signal = amp_f(signal)
        # print(f"{phases} -> {signal}")
        return signal

    best_phases = max(permutations(phases_range), key=run_amps)
    best_signal = run_amps(best_phases)
    print(f"best: {best_phases} -> {best_signal}")
    return best_phases, best_signal


def test_examples_part1():
    assert find_best_phases([
        3, 15,
        3, 16,
        1002, 16, 10, 16,
        1, 16, 15, 15,
        4, 15,
        99,
        0, 0
    ]) == ((4,3,2,1,0), 43210)
    print("passed examples_part1 no 1")

    assert find_best_phases([
        3, 23,
        3, 24,
        1002, 24, 10, 24,
        1002, 23, -1, 23,
        101, 5, 23, 23,
        1, 24, 23, 23,
        4, 23,
        99,
        0, 0
    ]) == ((0,1,2,3,4), 54321)
    print("passed examples_part1 no 2")

    assert find_best_phases([
        3, 31,
        3, 32,
        1002, 32, 10, 32,
        1001, 31, -2, 31,
        1007, 31, 0, 33,
        1002, 33, 7, 33,
        1, 33, 31, 31,
        1, 32, 31, 31,
        4, 31,
        99,
        0, 0, 0
    ]) == ((1,0,4,3,2), 65210)
    print("passed examples_part1 no 3")


def find_best_phases_loop(tape: Iterable[int], phases_range: range = range(5, 10), debug=False):
    amps = [
        Machine(tape, name=f"Amp {n+1}", debug=debug)
        for n in range(len(phases_range))
    ]

    def run_amps_loop(phases: List[int]) -> Optional[int]:
        amp_fs = [amp.as_function_scalar(init=[phase]) for amp, phase in zip(amps, phases)]
        signal = 0
        final_signal = None
        while True:
            try:
                for amp_f in amp_fs:
                    signal = amp_f(signal)
                final_signal = signal
            except StopIteration:
                return final_signal

    best_phases = max(permutations(phases_range), key=run_amps_loop)
    best_signal = run_amps_loop(best_phases)
    print(f"best: {best_phases} -> {best_signal}")
    return best_phases, best_signal


def test_examples_part2():
    assert find_best_phases_loop([
        3, 26,             # input P -> [26]
        1001, 26, -4, 26,  # [26] - 4 -> [26]
        # [6]
        3, 27,             # input X -> [27]
        1002, 27, 2, 27,   # [27] * 2 -> [27]
        1, 27, 26, 27,     # [27] + [26] -> [27]
        4, 27,             # out <- [27]  (P-4 + X*2)
        1001, 28, -1, 28,  # [28] - 1 -> [28]
        1005, 28, 6,       # [28] ?>> [6]
        99,
        # [26..28]
        0, 0, 5
    ]) == ((9,8,7,6,5), 139629729)
    print("passed examples_part2 no 1")

    assert find_best_phases_loop([
        3, 52,             # input P -> [52]
        1001, 52, -5, 52,  # [52] - 5 -> [52]
        # [6]
        3, 53,             # input X -> [53]
        1, 52, 56, 54,     # [52] + [56] -> [54]
        # [12]
        1007, 54, 5, 55,   # [54] < 5 -> [55]
        1005, 55, 26,      # [55] ?>> 26
        1001, 54, -5, 54,  # [54] - 5 -> [54]
        1105, 1, 12,       # >> [12]
        # [26]
        1, 53, 54, 53,     # [53] + [54] -> [53]
        1008, 54, 0, 55,   # [54] = 0 -> [55]
        1001, 55, 1, 55,   # [55] + 1 -> [55]
        2, 53, 55, 53,     # [53] * [55] -> [53]
        4, 53,             # output <- [53]
        1001, 56, -1, 56,  # [56] - 1 -> [56]
        1005, 56, 6,       # [56] ?>> 6
        99,                # HALT
        # [52]
        0, 0, 0, 0, 10
    ]) == ((9,7,8,5,6), 18216)
    print("passed examples_part2 no 2")


if __name__ == '__main__':
    print("part 1")
    find_best_phases(load_tape("data/07-program.txt"))
    print("part 2")
    find_best_phases_loop(load_tape("data/07-program.txt"))
