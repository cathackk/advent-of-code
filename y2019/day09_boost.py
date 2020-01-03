from machine import load_tape
from machine import Machine

if __name__ == '__main__':
    tape = load_tape("data/09-program.txt")
    m = Machine(tape, debug=False)
    # print(m.runl([1]))
    result_1 = next(m.run_fixed_input([1]))
    print(f"part 1: {result_1}")

    result_2 = next(m.run_fixed_input([2]))
    print(f"part 2: {result_2}")
