from typing import Iterable


Pos = tuple[int, int]


class Disk:
    def __init__(self, pos: Pos, size: int, used: int):
        assert size > 0
        assert size >= used

        self.pos = pos
        self.size = size
        self.used = used

    @property
    def available(self) -> int:
        return self.size - self.used

    @property
    def x(self) -> int:
        return self.pos[0]

    @property
    def y(self) -> int:
        return self.pos[1]

    def __repr__(self):
        return f'{type(self).__name__}(pos={self.pos!r}, size={self.size!r}, used={self.used!r})'

    def __str__(self):
        return f'[x{self.x}-y{self.y} {self.used}T/{self.size}T]'

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.pos == other.pos

    def __hash__(self):
        return hash(self.pos)


def load_disks(fn: str) -> Iterable[Disk]:
    f = open(fn)
    assert "Filesystem" in next(f)  # header
    for line in f:
        # '/dev/grid/node-x0-y2     85T   73T    12T   85%'
        name, size, used, _, _ = [p for p in line.strip().split(' ') if p]
        assert name.startswith("/dev/grid/node-x")
        x, y = name[16:].split('-y')
        yield Disk(
            pos=(int(x), int(y)),
            size=int(size.rstrip('T')),
            used=int(used.rstrip('T'))
        )


def part_1(disks: list[Disk]) -> int:
    disks = list(disks)
    viable_pair_count = sum(
        1
        for d1 in disks
        for d2 in disks
        if d1 != d2 and 0 < d1.used <= d2.available
    )
    print(f"part 1: there are {viable_pair_count} viable pairs")
    return viable_pair_count


def part_2(disks: list[Disk]):
    tx = max(d.x for d in disks if d.y == 0)
    empty_disk = next(d for d in disks if d.used == 0)
    ex, ey = empty_disk.pos
    moves = (
        # move empty to (0, ey) because of barrier with hole at x=0,
        ey
        # then move empty to (tx-1, 0),
        + ex + (tx - 1)
        # then move tx left by shuffling to x=1
        + 5 * (tx - 1)
        # then one final step
        + 1
    )
    print(f"part 2: takes {moves} moves to reach the data at {(tx, 0)}, empty={(ex, ey)}")
    return moves


if __name__ == '__main__':
    disks_ = list(load_disks("data/22-input.txt"))
    part_1(disks_)
    part_2(disks_)
    # 190 too low
