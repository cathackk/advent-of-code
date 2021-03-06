from collections import defaultdict
from itertools import zip_longest
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Tuple

from utils import create_logger
from utils import single_value

Pos = Tuple[int, int]
Transformation = Callable[[int, int], Pos]


class Grid:
    def __init__(self, size: int, pixels: Iterable[Pos]):
        self.size = size
        self.pixels = set(pixels)
        for x, y in self.pixels:
            assert 0 <= x < self.size
            assert 0 <= y < self.size

    def str_lines(self) -> Iterable[str]:
        return (
            ''.join('#' if (x, y) in self.pixels else '.' for x in range(self.size))
            for y in range(self.size)
        )

    def __str__(self):
        return '\n'.join(self.str_lines())

    def __int__(self):
        return sum(
            1 << (x + y * self.size)
            for x, y in self.pixels
        )

    def __eq__(self, other):
        return (
            isinstance(other, type(self))
            and self.size == other.size
            and int(self) == int(other)
        )

    def __hash__(self):
        return hash((self.size, int(self)))

    def _transformed(self, tr: Transformation):
        def trm(x: int, y: int) -> Pos:
            x, y = tr(x, y)
            return x % self.size, y % self.size

        return Grid(
            size=self.size,
            pixels=(trm(x, y) for x, y in self.pixels)
        )

    def rotated(self, rotations: int) -> 'Grid':
        """
        0 -> no rotation
        1 -> 90° clockwise
        2 -> 180°
        3 -> 90° counter-clockwise
        """
        rotations %= 4
        if rotations == 0:
            return self
        elif rotations == 1:
            return self._transformed(lambda x, y: (-y-1, x))
        elif rotations == 2:
            return self._transformed(lambda x, y: (-x-1, -y-1))
        elif rotations == 3:
            return self._transformed(lambda x, y: (y, -x-1))
        else:
            raise ValueError(rotations)

    def flipped_x(self) -> 'Grid':
        return self._transformed(lambda x, y: (-x-1, y))

    def flipped_y(self) -> 'Grid':
        return self._transformed(lambda x, y: (x, -y-1))

    def variants(self) -> Iterable['Grid']:
        flipped = self.flipped_x()
        for r in range(4):
            yield self.rotated(r)
            yield flipped.rotated(r)

    def normalized(self) -> 'Grid':
        return min(self.variants(), key=lambda g: int(g))

    def split(self) -> Iterable[Tuple[Pos, 'Grid']]:
        if self.size % 2 == 0:
            return self.subgrids(2)
        elif self.size % 3 == 0:
            return self.subgrids(3)
        else:
            raise ValueError(f"grid size {self.size} not divisible by 2 or 3")

    def subgrids(self, subsize: int) -> Iterable[Tuple[Pos, 'Grid']]:
        assert self.size % subsize == 0

        if self.size == subsize:
            yield (0, 0), self
            return

        subpixels: Dict[Pos, List[Pos]] = defaultdict(list)
        for x, y in self.pixels:
            # top-left corner of the subgrid
            cx, cy = ((x // subsize) * subsize), ((y // subsize) * subsize)
            # position in the new subgrid
            dx, dy = x - cx, y - cy
            subpixels[(cx, cy)].append((dx, dy))

        for cy in range(0, self.size, subsize):
            for cx in range(0, self.size, subsize):
                yield (cx, cy), Grid(subsize, subpixels[(cx, cy)])

    @classmethod
    def join(cls, subgrids: Iterable[Tuple[Pos, 'Grid']]) -> 'Grid':
        subgrids = dict(subgrids)

        sub_size = single_value(set(sg.size for sg in subgrids.values()))
        max_x = max(x for x, _ in subgrids.keys())
        max_y = max(y for _, y in subgrids.keys())
        assert max_x % sub_size == 0
        assert max_y % sub_size == 0

        return cls(
            size=max(max_x, max_y) + sub_size,
            pixels=(
                (cx + x, cy + y)
                for (cx, cy), sg in subgrids.items()
                for x, y in sg.pixels
            )
        )

    @classmethod
    def create_starting(cls):
        #  .#.
        #  ..#
        #  ###
        return cls(3, [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)])


class Rule:
    def __init__(self, no: int, grid_from: Grid, grid_to: Grid):
        assert grid_from.size + 1 == grid_to.size
        self.no = no
        self.grid_from = grid_from
        self.grid_to = grid_to

    def str_lines(self):
        l1_pad = ' ' * self.grid_from.size
        lines = zip_longest(self.grid_from.str_lines(), self.grid_to.str_lines())
        for li, (l1, l2) in enumerate(lines):
            yield f"{l1 or l1_pad} {'=>' if li == 1 else '  '} {l2}"

    def __str__(self):
        # return '\n'.join(self.str_lines())
        gf = '/'.join(self.grid_from.str_lines())
        gt = '/'.join(self.grid_to.str_lines())
        return f"({self.no}) {gf} => {gt}"


def load_rules(fn: str) -> Iterable[Rule]:
    # '##/## => #.#/#../###'
    # '###/#../... => #..#/...#/..#./##.#'

    def create_grid(s: str) -> Grid:
        return Grid(
            size=s.count('/') + 1,
            pixels=(
                (x, y)
                for y, row in enumerate(s.split('/'))
                for x, c in enumerate(row)
                if c == '#'
            )
        )

    for no, line in enumerate(open(fn)):
        gfrom, gto = line.strip().split(' => ')
        yield Rule(
            no=no + 1,
            grid_from=create_grid(gfrom),
            grid_to=create_grid(gto)
        )


class RuleBook:
    def __init__(self, rules: Iterable[Rule]):
        self.rdict: Dict[int, Rule] = {
            hash(rule.grid_from.normalized()): rule
            for rule in rules
        }

    def __len__(self):
        return len(self.rdict)

    def matching_rule(self, grid: Grid) -> Rule:
        h = hash(grid.normalized())
        if h not in self.rdict:
            raise KeyError(f"no rule for\n{grid}")
        return self.rdict[h]

    def expand(self, grid: Grid) -> Grid:
        return grid.join(self._expanded_subgrids(grid))

    def _expanded_subgrids(self, grid: Grid) -> Iterable[Tuple[Pos, Grid]]:
        for (cx, cy), subgrid in grid.split():
            matching_rule = self.matching_rule(subgrid)
            expanded_subgrid = matching_rule.grid_to
            assert expanded_subgrid.size == subgrid.size + 1
            ecx = (cx // subgrid.size) * expanded_subgrid.size
            ecy = (cy // subgrid.size) * expanded_subgrid.size
            yield (ecx, ecy), expanded_subgrid

    @classmethod
    def load(cls, fn: str):
        return cls(load_rules(fn))


def count_pixels(grid: Grid, rulebook: RuleBook, steps: int, debug: bool = False) -> int:
    """
    Optimized method for recursively calculating pixels count
    after large number of expansion steps (tested up to 900).

    Note: Working only for starting grids 3x3 and steps divisible by 3.
    """
    log = create_logger(debug)

    # currently optimized only for these values:
    assert grid.size == 3
    assert steps % 3 == 0

    # dictionary of grids by their codes
    code_to_grid: Dict[int, Grid] = {int(grid): grid}
    # code of 3x3 grid -> 9 subresult codes (nine 3x3 subresults after three-steps expansion)
    expand_cache: Dict[int, List[int]] = dict()
    # (code, steps) -> pixels_count
    pixels_count_cache: Dict[Tuple[int, int], int] = {(int(grid), 0): len(grid.pixels)}
    log(f">>> pxl: {int(grid)} -> {len(grid.pixels)}")

    def _expand_to_nine_subgrids(grid3: Grid) -> List[Grid]:
        key = int(grid3)
        if key not in expand_cache:
            # expand in three steps from 3x3 -> 9x9
            assert grid.size == 3
            grid4 = rulebook.expand(grid3)
            assert grid4.size == 4
            grid6 = rulebook.expand(grid4)
            assert grid6.size == 6
            grid9 = rulebook.expand(grid6)
            assert grid9.size == 9
            # ... yielding nine 3x3 subresults
            subgrids = list(sg for _, sg in grid9.split())
            assert len(subgrids) == 9

            # store subresults codes
            subgrids_codes = [int(sg) for sg in subgrids]
            # ... into expansion cache,
            expand_cache[key] = subgrids_codes
            log(f">>> exp: {key} -> {subgrids_codes}")
            for h, sg in zip(subgrids_codes, subgrids):
                if h not in code_to_grid:
                    # ... dictionary,
                    code_to_grid[h] = sg
                    # ... and pixels count cache
                    pixels_count_cache[(h, 0)] = len(sg.pixels)
                    log(f">>> pxl: {(h, 0)} -> {len(sg.pixels)}")

        return [code_to_grid[h] for h in expand_cache[key]]

    def _pixels_count(grid3: Grid, in_steps: int) -> int:
        key = (int(grid3), in_steps)
        if key not in pixels_count_cache:
            assert in_steps % 3 == 0
            assert in_steps >= 0
            pixels_count_cache[key] = sum(
                _pixels_count(sg, in_steps - 3)
                for sg in _expand_to_nine_subgrids(grid3)
            )
            log(f">>> pxl: {key} -> {pixels_count_cache[key]}")
        return pixels_count_cache[key]

    return _pixels_count(grid, steps)


def test_grid_rotated():
    grid = Grid.create_starting()
    assert grid.size == 3
    assert grid.pixels == {(0, 2), (1, 0), (1, 2), (2, 1), (2, 2)}

    grid_cw = grid.rotated(1)
    assert grid_cw.size == grid.size
    assert grid_cw.pixels == {(0, 0), (0, 1), (0, 2), (1, 2), (2, 1)}

    grid_180 = grid.rotated(2)
    assert grid_180.size == grid.size
    assert grid_180.pixels == {(0, 0), (0, 1), (1, 0), (1, 2), (2, 0)}

    grid_ccw = grid.rotated(3)
    assert grid_ccw.size == grid.size
    assert grid_ccw.pixels == {(0, 1), (1, 0), (2, 0), (2, 1), (2, 2)}


def test_grid_flipped():
    grid = Grid.create_starting()
    assert grid.size == 3
    assert grid.pixels == {(0, 2), (1, 0), (1, 2), (2, 1), (2, 2)}

    grid_fx = grid.flipped_x()
    assert grid_fx.size == grid.size
    assert grid_fx.pixels == {(0, 1), (0, 2), (1, 0), (1, 2), (2, 2)}

    grid_fy = grid.flipped_y()
    assert grid_fy.size == grid.size
    assert grid_fy.pixels == {(0, 0), (1, 0), (1, 2), (2, 0), (2, 1)}


def test_grid_to_int():
    grid = Grid.create_starting()
    """
    .#.
    ..#
    ###
    
    1, 5, 6, 7, 8 -> 2 + 32 + 64 + 128 + 256 = 482
    """
    assert int(grid) == 482
    """
    #..
    #.#
    ##.
    
    0, 3, 5, 6, 7 -> 1 + 8 + 32 + 64 + 128 = 233 
    """
    assert int(grid.rotated(1)) == 233


def test_grid_split_4x4():
    #  #.|.#
    #  .#|..
    #  --+--
    #  #.|..
    #  #.|##
    grid = Grid(4, [(0, 0), (0, 2), (0, 3), (1, 1), (2, 3), (3, 0), (3, 3)])
    subgrids = dict(grid.split())
    assert len(subgrids) == 4
    assert all(subgrid.size == 2 for subgrid in subgrids.values())

    # (0, 0)  #.
    # NW      .#
    assert subgrids[(0, 0)].pixels == {(0, 0), (1, 1)}

    # (2, 0)  .#
    # NE      ..
    assert subgrids[(2, 0)].pixels == {(1, 0)}

    # (0, 2)  #.
    # SW      #.
    assert subgrids[(0, 2)].pixels == {(0, 0), (0, 1)}

    # (2, 2)  ..
    # SE      ##
    assert subgrids[(2, 2)].pixels == {(0, 1), (1, 1)}


def test_grid_split_9x9():
    #  #..|.#.|..#
    #  .##|.##|.#.
    #  ...|.#.|...
    #  ---+---+---
    #  ...|.#.|...
    #  ##.|.#.|.##
    #  ..#|...|..#
    #  ---+---+---
    #  ...|#..|##.
    #  .##|.##|.#.
    #  #..|.#.|..#
    grid = Grid(9, [
        (0, 0), (4, 0), (8, 0),
        (1, 1), (2, 1), (4, 1), (5, 1), (7, 1),
        (4, 2),
        (4, 3),
        (0, 4), (1, 4), (4, 4), (7, 4), (8, 4),
        (2, 5), (8, 5),
        (3, 6), (6, 6), (7, 6),
        (1, 7), (2, 7), (4, 7), (5, 7), (7, 7),
        (0, 8), (4, 8), (8, 8)
    ])
    assert len(grid.pixels) == 28

    subgrids = dict(grid.split())
    assert len(subgrids) == 9
    assert sum(len(sg.pixels) for sg in subgrids.values()) == len(grid.pixels)

    assert subgrids[(0, 0)].pixels == {(0, 0), (1, 1), (2, 1)}          # NW
    assert subgrids[(0, 3)].pixels == {(0, 1), (1, 1), (2, 2)}          # W
    assert subgrids[(0, 6)].pixels == {(1, 1), (2, 1), (0, 2)}          # SW
    assert subgrids[(3, 0)].pixels == {(1, 0), (1, 1), (2, 1), (1, 2)}  # N
    assert subgrids[(3, 3)].pixels == {(1, 0), (1, 1)}                  # central
    assert subgrids[(3, 6)].pixels == {(0, 0), (1, 1), (2, 1), (1, 2)}  # S
    assert subgrids[(6, 0)].pixels == {(2, 0), (1, 1)}                  # NE
    assert subgrids[(6, 3)].pixels == {(1, 1), (2, 1), (2, 2)}          # E
    assert subgrids[(6, 6)].pixels == {(0, 0), (1, 0), (1, 1), (2, 2)}  # SE


def test_grid_join():
    #  ###|#..
    #  ...|...
    #  .##|##.
    #  ---+---
    #  ...|...
    #  ..#|###
    #  ...|...
    subgrids = {
        (0, 0): Grid(3, [(0, 0), (1, 0), (2, 0), (1, 2), (2, 2)]),  # NW
        (3, 0): Grid(3, [(0, 0), (0, 2), (1, 2)]),                  # NE
        (0, 3): Grid(3, [(2, 1)]),                                  # SW
        (3, 3): Grid(3, [(0, 1), (1, 1), (2, 1)])                   # SE
    }
    assert sum(len(sg.pixels) for sg in subgrids.values()) == 12

    grid = Grid.join((pos, sg) for pos, sg in subgrids.items())
    assert grid.size == 6
    assert len(grid.pixels) == 12
    assert grid.pixels == {
        (0, 0), (1, 0), (2, 0), (3, 0),
        (1, 2), (2, 2), (3, 2), (4, 2),
        (2, 4), (3, 4), (4, 4), (5, 4)
    }


def test_expand_3x3():
    #
    #  ##.    #..#
    #  #.# => ....
    #  #..    ....
    #         #..#
    #
    # first is a variant of the starting grid
    rule = Rule(
        no=0,
        grid_from=Grid(3, [(0, 0), (1, 0), (0, 1), (2, 1), (0, 2)]),
        grid_to=Grid(4, [(0, 0), (0, 3), (3, 0), (3, 3)])
    )
    rulebook = RuleBook([rule])

    grid1 = Grid.create_starting()
    assert grid1 != rule.grid_from

    grid2 = rulebook.expand(grid1)
    assert grid2 == rule.grid_to


def test_expand_4x4():
    # first rule:
    #
    #  ..    ##.
    #  #. => #..
    #        ...
    rule1 = Rule(
        no=1,
        grid_from=Grid(2, [(0, 1)]),
        grid_to=Grid(3, [(0, 0), (1, 0), (0, 1)])
    )
    # second rule:
    #
    #  ..    .#.
    #  ## => #.#
    #        ..#
    #
    rule2 = Rule(
        no=2,
        grid_from=Grid(2, [(1, 0), (1, 1)]),
        grid_to=Grid(3, [(1, 0), (0, 1), (2, 1), (2, 2)])
    )
    # plus one bogus rule that won't be used:
    #
    #  .#    ...
    #  #. => .#.
    #        ...
    #
    rule3 = Rule(
        no=3,
        grid_from=Grid(2, [(1, 0), (0, 1)]),
        grid_to=Grid(3, [(1, 1)])
    )

    rulebook = RuleBook([rule1, rule2, rule3])

    # will be applied like this:
    #
    # #..#    #.|.#    ##.|.#.    ##..#.
    # ...#    ..|.#    #..|#.#    #..#.#
    # .... => --+-- => ...|..# => .....#
    # #..#    ..|..    ---+---    ##.##.
    #         #.|.#    ##.|##.    #..#..
    #                  #..|#..    ......
    #                  ...|...

    grid1 = Grid(4, [(0, 0), (3, 0), (3, 1), (0, 3), (3, 3)])
    assert len(grid1.pixels) == 5

    grid2 = rulebook.expand(grid1)
    assert grid2.size == 6
    assert len(grid2.pixels) == 13
    assert grid2.pixels == {
        (0, 0), (1, 0), (4, 0),
        (0, 1), (3, 1), (5, 1),
        (5, 2),
        (0, 3), (1, 3), (3, 3), (4, 3),
        (0, 4), (3, 4)
    }


def test_expand_4x4_with_empty_subgrids():
    # first rule:
    #
    # #.    ...
    # .. => .#.
    #       ...
    #
    rule1 = Rule(
        no=1,
        grid_from=Grid(2, [(0, 0)]),
        grid_to=Grid(3, [(1, 1)])
    )

    # second rule:
    #
    # ##    ...
    # .. => #.#
    #       ...
    #
    rule2 = Rule(
        no=2,
        grid_from=Grid(2, [(0, 0), (1, 0)]),
        grid_to=Grid(3, [(0, 1), (2, 1)])
    )

    # and third rule, matching empty subgrid
    #
    # ..    #.#
    # .. => .#.
    #       #.#
    rule3 = Rule(
        no=3,
        grid_from=Grid(2, []),
        grid_to=Grid(3, [(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)])
    )

    rulebook = RuleBook([rule1, rule2, rule3])

    # apply rules on the grid like this:
    #
    #  ....    ..|..    ...|#.#    ...#.#
    #  .#.. => .#|.. => .#.|.#. => .#..#.
    #  ..##    --+--    ...|#.#    ...#.#
    #  ....    ..|##    ---+---    #.#...
    #          ..|..    #.#|...    .#.#.#
    #                   .#.|#.#    #.#...
    #                   #.#|...

    grid1 = Grid(4, [(1, 1), (2, 2), (3, 2)])
    grid2 = rulebook.expand(grid1)
    assert grid2.size == 6
    assert len(grid2.pixels) == 13


def part_1(fn: str, steps: int = 5, debug: bool = False) -> int:
    log = create_logger(debug)

    rulebook = RuleBook.load(fn)
    grid = Grid.create_starting()

    log("==== Initial ====")
    log(grid)
    log("")

    for step in range(1, steps + 1):
        grid = rulebook.expand(grid)
        log(f"==== Expansion # {step} ====")
        log(f"size: {grid.size}, pixels: {len(grid.pixels)}")
        log(grid)
        log("")

    print(f"part 1: {len(grid.pixels)} pixels after {steps} steps")
    return len(grid.pixels)


def part_2(fn: str, steps: int = 18, debug: bool = False) -> int:
    rulebook = RuleBook.load(fn)
    grid = Grid.create_starting()
    pixels = count_pixels(grid, rulebook, steps, debug)
    print(f"part 2: {pixels} pixels after {steps} steps")
    return pixels


if __name__ == '__main__':
    fn_ = "data/21-input.txt"
    debug_ = False
    part_1(fn_, debug=debug_)
    part_2(fn_, debug=debug_)
