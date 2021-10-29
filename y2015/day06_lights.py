from collections import defaultdict
from typing import Iterable

from rect import Pos
from rect import Rect


class LightsPanel:
    def __init__(self, width: int, height: int):
        self.bounds = Rect.at_origin(width, height)
        self.brightness: dict[Pos, int] = defaultdict(int)
        self.min_brightness = 0

    @property
    def total_brightness(self) -> int:
        return sum(self.brightness.values())

    def set_brightness(self, value: int, rect: Rect):
        assert rect in self.bounds
        for pos in rect:
            self.brightness[pos] = value

    def add_brightness(self, value: int, rect: Rect):
        assert rect in self.bounds
        for pos in rect:
            self.brightness[pos] = max(self.brightness[pos] + value, self.min_brightness)

    def toggle(self, value: int, rect: Rect):
        assert rect in self.bounds
        for pos in rect:
            self.brightness[pos] = value if not self.brightness[pos] else 0

    def instruction(self, instr: str, mode: int):
        assert len(instr) >= 23
        assert mode in (1, 2)

        command, c1, through, c2 = instr.rsplit(" ", 3)
        assert through == "through"

        x1, y1 = (int(v) for v in c1.split(","))
        x2, y2 = (int(v) for v in c2.split(","))
        rect = Rect((x1, y1), (x2, y2))

        if command == "turn on":
            if mode == 1:
                self.set_brightness(1, rect)
            elif mode == 2:
                self.add_brightness(+1, rect)

        elif command == "turn off":
            if mode == 1:
                self.set_brightness(0, rect)
            elif mode == 2:
                self.add_brightness(-1, rect)

        elif command == "toggle":
            if mode == 1:
                self.toggle(1, rect)
            elif mode == 2:
                self.add_brightness(+2, rect)

        else:
            raise ValueError(command)

    def draw(self):
        gradient = ' .:;+=xX$&'

        def c(v: int) -> str:
            return gradient[min(v, len(gradient)-1)]

        for y in self.bounds.range_y():
            print(''.join(
                c(self.brightness[(x, y)])
                for x in self.bounds.range_x()
            ))


def part_1(instructions: Iterable[str]) -> int:
    p = LightsPanel(1000, 1000)
    for instr in instructions:
        p.instruction(instr, mode=1)
    # p.draw()

    result = p.total_brightness
    print(f"part 1: total {result} lights on")
    return result


def part_2(instructions: Iterable[str]) -> int:
    p = LightsPanel(1000, 1000)
    for instr in instructions:
        p.instruction(instr, mode=2)
    p.draw()

    result = p.total_brightness
    print(f"part 2: total {result} brightness")
    return result


if __name__ == '__main__':
    instructions = [line.strip() for line in open("data/06-input.txt") if line.strip()]
    part_1(instructions)
    part_2(instructions)
