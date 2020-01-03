from typing import Iterable
from typing import Set
from typing import Tuple


Pos = Tuple[int, int]


class Display:
    def __init__(self, width: int, height: int, active: Iterable[Pos] = None):
        self.width = width
        self.height = height
        self.active: Set[Pos] = set(active) if active else set()

    def __len__(self):
        return len(self.active)

    def commands_from_file(self, fn: str):
        for line in open(fn):
            self.command(line.strip())

    def command(self, cmd: str):
        # rect 2x1
        if cmd.startswith("rect "):
            rw, rh = cmd[5:].split('x')
            self.rect(int(rw), int(rh))

        # rotate row y=0 by 3
        elif cmd.startswith("rotate row y="):
            y, right = cmd[13:].split(" by ")
            self.rotate_row(int(y), int(right))

        # rotate column x=8 by 2
        elif cmd.startswith("rotate column x="):
            x, down = cmd[16:].split(" by ")
            self.rotate_column(int(x), int(down))

        else:
            raise ValueError(cmd)

    def rect(self, rwidth: int, rheight: int):
        self.active.update(
            (x, y)
            for x in range(rwidth)
            for y in range(rheight)
        )

    def rotate_row(self, y: int, right: int):
        self.active = {
            ((cx + right) % self.width, cy) if cy == y else (cx, cy)
            for cx, cy in self.active
        }

    def rotate_column(self, x: int, down: int):
        self.active = {
            (cx, (cy + down) % self.height) if cx == x else (cx, cy)
            for cx, cy in self.active
        }

    def draw(self):
        def c(cx: int, cy: int) -> str:
            return '#' if (cx, cy) in self.active else '.'
        for y in range(self.height):
            print(''.join(c(x, y) for x in range(self.width)))
        print()


if __name__ == '__main__':
    fn_ = "data/08-input.txt"
    display = Display(width=50, height=6)
    display.commands_from_file(fn_)
    on_count = len(display)
    print(f"part 1: {on_count} pixels are on")
    print("part 2:")
    display.draw()
