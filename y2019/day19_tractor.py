from common.file import relative_path
from y2019.intcode import load_tape
from y2019.intcode import Machine


scan_machine = Machine(load_tape(relative_path(__file__, "data/19-program.txt")))
scan = scan_machine.as_function_scalar(restarting=True)


def part_1():
    total = 0
    for y in range(50):
        line = [scan(x, y) for x in range(50)]
        total += sum(line)
        print(''.join('#' if r else '.' for r in line))
    print(f"total: {total}")


def find_square(
        y_start: int = 20,
        x_start: tuple[int, int] = (14, 16),
        square_size: int = 100,
        debug: bool = False
) -> tuple[int, int]:
    y = y_start
    x_min, x_max = x_start
    assert not scan(x_min-1, y)
    assert scan(x_min, y)
    assert scan(x_max, y)
    assert not scan(x_max+1, y)

    xs = {y: (x_min, x_max)}

    while True:
        y += 1
        if not scan(x_min, y):
            x_min += 1
        if scan(x_max+1, y):
            x_max += 1
        xs[y] = (x_min, x_max)

        if debug:
            assert not scan(x_min-1, y)
            assert scan(x_min, y)
            assert scan(x_min+1, y)

            assert scan(x_max-1, y)
            assert scan(x_max, y)
            assert not scan(x_max+1, y)

        width = x_max - x_min + 1
        print('.' * (x_min % 100) + '#' * width + '...')

        y0 = y - square_size + 1
        if y0 in xs:
            x0 = x_min + square_size - 1
            x0_min, x0_max = xs[y0]
            if (x0_min <= x_min <= x0_max) and (x0_min <= x0 <= x0_max):
                return x_min, y0


def part_2():
    x, y = find_square(square_size=100)
    print(f"result: x={x}, y={y}")
    print(f"output: {x*10000 + y}")


if __name__ == '__main__':
    part_1()
    part_2()
