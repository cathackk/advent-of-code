import functools

from machine import load_tape
from machine import Machine
from machine import MachineIO


def part_1():
    m = Machine(load_tape("data/17-program.txt"))
    screen_output = list(m.run_output_only())
    print(screen_output)
    lines = [
        line.strip()
        for line in ''.join(chr(v) for v in screen_output).split('\n')
        if line.strip()
    ]

    height = len(lines)
    width = len(lines[0])
    assert all(len(line) == width for line in lines)
    print(f"width={width}, height={height}")

    def cross(x, y):
        yield x, y
        yield x + 1, y
        yield x - 1, y
        yield x, y + 1
        yield x, y - 1

    intersections = {
        (x, y)
        for x in range(1, width-1)
        for y in range(1, height-1)
        if all(
            lines[cy][cx] == '#'
            for cx, cy in cross(x, y)
        )
    }

    print('\n'.join(
        ''.join(
            'O' if (x, y) in intersections else lines[y][x]
            for x in range(width)
        ) for y in range(height)
    ))

    alignment = sum(x * y for x, y in intersections)

    print("intersections:")
    for x, y in intersections:
        print(f"> {x:2}, {y:2} -> {x*y:4}")
    print(f"total:     {alignment:5}")


def in_console(fn):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        import curses
        try:
            scr = curses.initscr()
            curses.noecho()
            curses.cbreak()

            try:
                result = fn(*args, **kwargs, screen=scr)
                scr.getkey()
                return result

            finally:
                curses.nocbreak()
                curses.echo()
                curses.endwin()

        except Exception:
            return fn(*args, **kwargs, screen=None)

    return wrapped


def draw_screen(io: MachineIO, screen) -> int:
    if screen:
        x, y = 0, 0
        for c in io.read():
            if c > 255:
                return c
            elif c == ord('\n'):
                screen.refresh()
                y = y + 1 if x > 0 else 0
                x = 0
            else:
                screen.addch(y, x, c)
                x += 1
    else:
        buffer = []
        for c in io.read():
            buffer.append(c)
            if c == ord('\n'):
                print(''.join(chr(c) for c in buffer), end='')
                buffer.clear()
        return buffer[-1] if buffer else -1


@in_console
def part_2(screen):
    tape = load_tape("data/17-program.txt")
    assert tape[0] == 1
    tape[0] = 2  # control robot

    m = Machine(tape)
    io = m.run_io()

    script = """
        A,A,B,C,B,C,B,C,A,C
        R,6,L,8,R,8
        R,4,R,6,R,6,R,4,R,4
        L,8,R,6,L,10,L,10
    """

    lines = [line.strip()+'\n' for line in script.split('\n') if line.strip()]
    assert len(lines) == 4

    draw_screen(io, screen)
    io.write(lines[0])  # main

    assert io.read_str() == "Function A:\n"
    io.write(lines[1])  # move function A

    assert io.read_str() == "Function B:\n"
    io.write(lines[2])  # move function B

    assert io.read_str() == "Function C:\n"
    io.write(lines[3])  # move function C

    assert io.read_str() == "Continuous video feed?\n"
    io.write("y\n" if screen else "n\n")  # video feed?

    dust = draw_screen(io, screen)
    print(f"dust: {dust}")


@in_console
def scr_test(screen):
    screen.addch(1, 1, 'X')
    screen.addch(2, 2, 'Y')
    screen.addch(3, 10, 'Z')
    screen.refresh()

if __name__ == '__main__':
    # part_1()
    part_2()
    # scr_test()
