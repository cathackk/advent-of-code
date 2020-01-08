from y2019.intcode import load_tape
from y2019.intcode import Machine


if __name__ == '__main__':
    m = Machine(load_tape("data/09-program.txt"))

    result_1 = next(m.run_fixed_input([1]))
    print(f"part 1: {result_1}")

    result_2 = next(m.run_fixed_input([2]))
    print(f"part 2: {result_2}")
