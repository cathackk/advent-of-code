from machine import load_tape
from machine import Machine


def run_diagnostic(code):
    m = Machine(load_tape("data/05-program.txt"))
    f = m.as_function()
    return next(v for v in f(code) if v != 0)


if __name__ == '__main__':
    print(f"part 1: result={run_diagnostic(1)}")
    print(f"part 2: result={run_diagnostic(5)}")
