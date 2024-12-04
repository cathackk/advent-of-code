"""
Advent of Code 2019
Day 13: Care Package
https://adventofcode.com/2019/day/13
"""

from enum import Enum
from typing import Callable, Self

from tqdm import tqdm

from common.math import sgn
from common.rect import Rect
from meta.aoc_tools import data_path
from y2019.intcode import load_tape, Machine, Tape


def part_1(tape: Tape) -> int:
    """
    As you ponder the solitude of space and the ever-increasing three-hour roundtrip for messages
    between you and Earth, you notice that the Space Mail Indicator Light is blinking. To help keep
    you sane, the Elves have sent you a care package.

    It's a new game for the ship's arcade cabinet! Unfortunately, the arcade is **all the way** on
    the other end of the ship. Surely, it won't be hard to build your own - the care package even
    comes with schematics.

    The arcade cabinet runs Intcode software like the game the Elves sent (your puzzle input). It
    has a primitive screen capable of drawing square tiles on a grid. The software draws tiles to
    the screen with output instructions: every three output instructions specify the `x` position
    (distance from the left), `y` position (distance from the top), and `tile id`. The `tile id` is
    interpreted as follows:

      - `0` is an **empty** tile. No game object appears in this tile.
      - `1` is a **wall** tile. Walls are indestructible barriers.
      - `2` is a **block** tile. Blocks can be broken by the ball.
      - `3` is a **horizontal paddle** tile. The paddle is indestructible.
      - `4` is a **ball** tile. The ball moves diagonally and bounces off objects.

    For example, a sequence of output values like `1,2,3,6,5,4` would draw a **horizontal paddle
    tile** (`1` tile from the left and `2` tiles from the top) and a **ball tile** (`6` tiles from
    the left and `5` tiles from the top).

    Start the game. **How many block tiles are on the screen when the game exits?**

        >>> dummy_tape = [1, 0, 0, 0, 104, 0, 104, 0, 104, 2, 104, 1, 104, 1, 104, 2, 99]
        >>> part_1(dummy_tape)
        part 1: screen shows 2 block tiles
        2
    """

    result = Arcade(tape).play().blocks_count

    print(f"part 1: screen shows {result} block tiles")
    return result


def part_2(tape: Tape) -> int:
    """
    The game didn't run because you didn't put in any quarters. Unfortunately, you did not bring any
    quarters. Memory address `0` represents the number of quarters that have been inserted; set it
    to `2` to play for free.

    The arcade cabinet has a joystick that can move left and right. The software reads the position
    of the joystick with input instructions:

      - If the joystick is in the **neutral position**, provide `0`.
      - If the joystick is **tilted to the left**, provide `-1`.
      - If the joystick is **tilted to the right**, provide `1`.

    The arcade cabinet also has a segment display capable of showing a single number that represents
    the player's current score. When three output instructions specify `X=-1, Y=0`, the third output
    instruction is not a tile; the value instead specifies the new score to show in the segment
    display. For example, a sequence of output values like `-1,0,12345` would show `12345` as the
    player's current score.

    Beat the game by breaking all the blocks. **What is your score after the last block is broken?**

        >>> dummy_tape = [1, 0, 0, 0, 104, -1, 104, 0, 104, 12345, 99]
        >>> part_2(dummy_tape)
        part 2: final score is 12345
        12345
    """

    result = Arcade(tape, quarters=2).play().score

    print(f"part 2: final score is {result}")
    return result


class Tile(Enum):
    EMPTY = (0, '·')
    WALL = (1, '█')
    BLOCK = (2, '#')
    PADDLE = (3, '=')
    BALL = (4, 'o')

    def __init__(self, code: int, char: str):
        self.code = code
        self.char = char

    @classmethod
    def from_code(cls, code: int) -> Self:
        try:
            return next(tile for tile in cls if tile.code == code)
        except StopIteration as stop:
            raise KeyError(code) from stop


Pos = tuple[int, int]
Screen = dict[Pos, Tile]

SCORE_POS = (-1, 0)


class Arcade():
    def __init__(self, tape: Tape, quarters: int = 1):
        self.machine = Machine([quarters] + tape[1:])
        self.screen: Screen = {}
        self.score: int = 0
        self.blocks_count: int = 0
        self.paddle_pos: Pos | None = None
        self.ball_pos: Pos | None = None

    def perfect_joystick(self) -> int | None:
        if self.paddle_pos is None or self.ball_pos is None:
            return None

        paddle_x, _ = self.paddle_pos
        ball_x, _ = self.ball_pos
        return sgn(ball_x - paddle_x)

    def play(
        self,
        joystick: Callable[[Self], int | None] = None,
        draw: bool = False,
    ) -> Self:

        if joystick is None:
            joystick = self.perfect_joystick

        game = self.machine.run_control()
        progress = tqdm(desc="playing", unit=" blocks", delay=1.0)

        try:
            while True:
                pos = game.send(joystick()), next(game)
                code = next(game)

                if pos == SCORE_POS:
                    # update score
                    self.score = code

                else:
                    # update screen
                    previous_tile = self.screen.get(pos)
                    new_tile = Tile.from_code(code)
                    self.screen[pos] = new_tile

                    # update blocks count
                    if new_tile is Tile.BLOCK:
                        self.blocks_count += 1
                        progress.total = self.blocks_count
                    elif previous_tile is Tile.BLOCK:
                        progress.update()

                    # update ball position
                    if new_tile is Tile.BALL:
                        self.ball_pos = pos
                    elif previous_tile is Tile.BALL:
                        self.ball_pos = None

                    # update paddle position
                    if new_tile is Tile.PADDLE:
                        self.paddle_pos = pos
                    elif previous_tile is Tile.PADDLE:
                        self.paddle_pos = None

                # redraw screen
                if draw and self.ball_pos and self.paddle_pos:
                    self.draw_screen()

        except StopIteration:
            return self

    def draw_screen(self) -> None:
        print(f"Score: {self.score}")

        def char(pos: Pos) -> str:
            if pos not in self.screen:
                return ' '

            return self.screen[pos].char

        bounds = Rect.with_all(self.screen)

        for y in bounds.range_y():
            print(''.join(char((x, y)) for x in bounds.range_x()))


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    tape = load_tape(input_path)
    result_1 = part_1(tape)
    result_2 = part_2(tape)
    return result_1, result_2


if __name__ == '__main__':
    main()
