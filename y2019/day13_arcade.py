from typing import Iterable

from common.math import sgn
from common.xy import Point
from y2019.intcode import load_tape
from y2019.intcode import Machine

TILES = {
    0: '.',
    1: '#',
    2: 'X',
    3: '=',
    4: 'o',
    None: ' '
}

SCORE_POINT = Point(-1, 0)
SCREEN_WIDTH = 40
SCREEN_HEIGHT = 24


def draw_screen(contents: Iterable[tuple[Point, int]]) -> None:
    screen = dict(contents)
    if not screen:
        print("no screen signal")
        return

    min_x, max_x = 0, max(p.x for p in screen.keys())
    min_y, max_y = 0, max(p.y for p in screen.keys())

    for y in range(min_y, max_y+1):
        print(''.join(
            TILES[screen.get(Point(x, y))]
            for x in range(min_x, max_x+1)
        ))

    if SCORE_POINT in screen:
        score = screen[SCORE_POINT]
        print(f"Score: {score}")


def part_1():
    m = Machine(load_tape('data/13-program.txt'))

    def load_screen():
        seq = list(m.run_output_only())
        for h in range(0, len(seq), 3):
            x, y, t = seq[h:h+3]
            yield Point(x, y), t

    screen = list(load_screen())
    draw_screen(screen)
    blocks_count = sum(1 for p, t in screen if t == 2)
    print(f"part 1: blocks count is {blocks_count}")


def part_2():
    tape = load_tape('data/13-program.txt')
    tape[0] = 2  # 2 quarters cheat
    m = Machine(tape, debug=False)
    game = m.run_control()

    screen = [[' ' for _ in range(SCREEN_WIDTH)] for _ in range(SCREEN_HEIGHT)]
    score = None

    paddle_x = None
    ball_x = None

    def joystick():
        if paddle_x is not None and ball_x is not None:
            return sgn(ball_x - paddle_x)
        else:
            return None

    try:
        while True:
            x = game.send(joystick())
            y = game.send(joystick())
            t = game.send(joystick())

            if x == -1 and y == 0:
                score = t
            elif 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
                prev = screen[y][x]
                screen[y][x] = TILES[t]

                if t == 4:
                    ball_x = x
                elif prev == TILES[4]:
                    ball_x = None

                if t == 3:
                    paddle_x = x
                elif prev == TILES[3]:
                    paddle_x = None

                if prev == TILES[2] and t != 2:
                    print(f"destroyed ({x}, {y})")

            else:
                raise ValueError(f"out of bounds: x={x}, y{y}")

            if ball_x is not None and paddle_x is not None and score is not None:
                print()
                print(f"score: {score}")
                print('\n'.join(''.join(row) for row in screen))
                # time.sleep(.05)

    except StopIteration:
        pass


if __name__ == '__main__':
    # part_1()
    part_2()
