"""
Advent of Code 2021
Day 11: Dumbo Octopus
https://adventofcode.com/2021/day/11
"""

from typing import Iterable

from common.rect import Rect
from common.utils import relative_path


def part_1(octopuses: 'Map', steps: int = 100) -> int:
    """
    You enter a large cavern full of rare bioluminescent dumbo octopuses! They seem to not like
    the Christmas lights on your submarine, so you turn them off for now.

    There are 100 octopuses arranged neatly in a 10 by 10 grid. Each octopus slowly gains **energy**
    over time and **flashes** brightly for a moment when its energy is full. Although your lights
    are off, maybe you could navigate through the cave without disturbing the octopuses if you could
    predict when the flashes of light will happen.

    Each octopus has an **energy level** - your submarine can remotely measure the energy level of
    each octopus (your puzzle input). For example:

        >>> example = Map.from_text('''
        ...
        ...     5483143223
        ...     2745854711
        ...     5264556173
        ...     6141336146
        ...     6357385478
        ...     4167524645
        ...     2176841721
        ...     6882881134
        ...     4846848554
        ...     5283751526
        ...
        ... ''')

    The energy level of each octopus is a value between `0` and `9`.

        >>> example[(0, 0)]
        5
        >>> example[(1, 2)]
        2

    You can model the energy levels and flashes of light in **steps**. During a single step,
    the following occurs:

    - First, the energy level of each octopus increases by `1`.
    - Then, any octopus with an energy level greater than `9` **flashes**. This increases the energy
      level of all adjacent octopuses by `1`, including octopuses that are diagonally adjacent. If
      this causes an octopus to have an energy level greater than `9`, it **also flashes**. This
      process continues as long as new octopuses keep having their energy level increased beyond 9.
      (An octopus can only flash **at most once per step**.)
    - Finally, any octopus that flashed during this step has its energy level set to `0`, as it used
      all of its energy to flash.

    Adjacent flashes can cause an octopus to flash on a step even if it begins that step with very
    little energy. Consider the middle octopus with `1` energy in this situation:

        >>> smaller_example = Map.from_text('''
        ...
        ...     11111
        ...     19991
        ...     19191
        ...     19991
        ...     11111
        ...
        ... ''')
        >>> _ = smaller_example.run(steps=2, log=True)
        Before any steps:
        11111
        19991
        19191
        19991
        11111
        -----
        After step 1:
        34543
        4███4
        5███5
        4███4
        34543
        -----
        After step 2:
        45654
        51115
        61116
        51115
        45654

    An octopus is **highlighted** when it flashed during the given step.

    Here is how the larger example above progresses:

        >>> _, flashes_10 = example.run(steps=10, log=True)
        Before any steps:
        5483143223
        2745854711
        5264556173
        6141336146
        6357385478
        4167524645
        2176841721
        6882881134
        4846848554
        5283751526
        ----------
        After step 1:
        6594254334
        3856965822
        6375667284
        7252447257
        7468496589
        5278635756
        3287952832
        7993992245
        5957959665
        6394862637
        ----------
        After step 2:
        88█7476555
        5█89█87█54
        85978896█8
        84857696██
        87██9█88██
        66███88989
        68████5943
        ██████7456
        9██████876
        87████6848
        ----------
        After step 3:
        ██5█9██866
        85██8██575
        99██████39
        97██████41
        9935█8██63
        77123█████
        791125███9
        221113████
        █421125███
        ██21119███
        ----------
        After step 4:
        2263█31977
        █923█31697
        ██3222115█
        ██41111163
        ██76191174
        ██53411122
        ██4236112█
        5532241122
        1532247211
        113223█211
        ----------
        After step 5:
        4484144███
        2█44144███
        2253333493
        1152333274
        11873█3285
        1164633233
        1153472231
        6643352233
        2643358322
        2243341322
        ----------
        After step 6:
        5595255111
        3155255222
        33644446█5
        2263444496
        2298414396
        2275744344
        2264583342
        7754463344
        3754469433
        3354452433
        ----------
        After step 7:
        67█7366222
        4377366333
        4475555827
        34966557█9
        35██6256█9
        35█9955566
        3486694453
        8865585555
        486558█644
        4465574644
        ----------
        After step 8:
        7818477333
        5488477444
        5697666949
        46█876683█
        473494673█
        474██97688
        69████7564
        ██████9666
        8█████4755
        68████7755
        ----------
        After step 9:
        9█6████644
        78█████976
        69██████8█
        584█████82
        5858████93
        69624█████
        8█2125███9
        222113███9
        9111128█97
        7911119976
        ----------
        After step 10:
        █481112976
        ██31112██9
        ██411125█4
        ██811114█6
        ██991113█6
        ██93511233
        █44236113█
        553225235█
        █53225█6██
        ██3224████
        >>> flashes_10
        204

    After step 10, there have been a total of `204` flashes. Fast forwarding, here is the same
    configuration every 10 steps:

        >>> _, flashes_100 = example.run(steps=100, log=range(20, 101, 10))
        After step 20:
        3936556452
        56865568█6
        449655569█
        444865558█
        445686557█
        568██86577
        7█████9896
        ███████344
        6██████364
        46████9543
        ----------
        After step 30:
        █643334118
        4253334611
        3374333458
        2225333337
        2229333338
        2276733333
        2754574565
        5544458511
        9444447111
        7944446119
        ----------
        After step 40:
        6211111981
        █421111119
        ██42111115
        ███3111115
        ███3111116
        ██65611111
        █532351111
        3322234597
        2222222976
        2222222762
        ----------
        After step 50:
        9655556447
        48655568█5
        448655569█
        445865558█
        457486557█
        57███86566
        6█████9887
        8██████533
        68█████633
        568████538
        ----------
        After step 60:
        25333342██
        274333464█
        2264333458
        2225333337
        2225333338
        2287833333
        3854573455
        1854458611
        1175447111
        1115446111
        ----------
        After step 70:
        8211111164
        █421111166
        ██42111114
        ███4211115
        ████211116
        ██65611111
        █532351111
        7322235117
        5722223475
        4572222754
        ----------
        After step 80:
        1755555697
        59655556█9
        448655568█
        445865558█
        457█86557█
        57███86566
        7█████8666
        ███████99█
        ███████8██
        ██████████
        ----------
        After step 90:
        7433333522
        2643333522
        2264333458
        2226433337
        2222433338
        2287833333
        2854573333
        4854458333
        3387779333
        3333333333
        ----------
        After step 100:
        █397666866
        █749766918
        ██53976933
        ███4297822
        ███4229892
        ██53222877
        █532222966
        9322228966
        7922286866
        6789998766
        >>> flashes_100
        1656

    After 100 steps, there have been a total of **`1656`** flashes.

    Given the starting energy levels of the dumbo octopuses in your cavern, simulate 100 steps.
    **How many total flashes are there after 100 steps?**

        >>> part_1(example)
        part 1: after 100 steps there are 1656 flashes
        1656
    """

    steps_performed, flashes = octopuses.run(steps=steps)
    assert steps_performed == steps

    print(f"part 1: after {steps} steps there are {flashes} flashes")
    return flashes


def part_2(octopuses: 'Map') -> int:
    """
    It seems like the individual flashes aren't bright enough to navigate. However, you might have
    a better option: the flashes seem to be **synchronizing**!

    In the example above, the first time all octopuses flash simultaneously is step **`195`**:

        >>> example = Map.from_file('data/11-example.txt')
        >>> _, steps = example.run(log=range(193, 200))
        After step 193:
        5877777777
        8877777777
        7777777777
        7777777777
        7777777777
        7777777777
        7777777777
        7777777777
        7777777777
        7777777777
        ----------
        After step 194:
        6988888888
        9988888888
        8888888888
        8888888888
        8888888888
        8888888888
        8888888888
        8888888888
        8888888888
        8888888888
        ----------
        After step 195:
        ██████████
        ██████████
        ██████████
        ██████████
        ██████████
        ██████████
        ██████████
        ██████████
        ██████████
        ██████████

    If you can calculate the exact moments when the octopuses will all flash simultaneously, you
    should be able to navigate through the cavern. **What is the first step during which all
    octopuses flash?**

        >>> part_2(example)
        part 2: all octopuses flash simultaneously on step 195
        195
    """

    step, _ = octopuses.run()

    print(f"part 2: all octopuses flash simultaneously on step {step}")
    return step


Pos = tuple[int, int]


def adjacent(pos: Pos) -> Iterable[Pos]:
    x, y = pos
    return ((x+dx, y+dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not dx == dy == 0)


class Map:

    def __init__(self, values: Iterable[tuple[Pos, int]]):
        self.values = dict(values)
        self.bounds = Rect.with_all(self.values.keys())
        assert len(self.values) == self.bounds.area

    @classmethod
    def from_text(cls, text: str) -> 'Map':
        return cls.from_lines(text.strip().split('\n'))

    @classmethod
    def from_file(cls, fn: str) -> 'Map':
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Map':
        return cls(
            ((x, y), int(v))
            for y, line in enumerate(lines)
            for x, v in enumerate(line.strip())
        )

    def __getitem__(self, pos: Pos) -> int:
        return self.values[pos]

    def __contains__(self, pos: Pos) -> bool:
        return pos in self.values

    def run(self, steps: int = 0, log: bool | range = False) -> tuple[int, int]:
        separator = '-' * self.bounds.width
        values = dict(self.values)

        def print_state(step: int):
            if isinstance(log, bool):
                if log is False:
                    return
                if step:
                    print(separator)
            elif isinstance(log, range):
                if step not in log:
                    return
                if step > log.start:
                    print(separator)

            print(f'After step {step}:' if step else 'Before any steps:')
            print('\n'.join(
                ''.join(str(values[(x, y)] or '█') for x in self.bounds.range_x())
                for y in self.bounds.range_y()
            ))

        def increment(*ps: Pos) -> None:
            for p in ps:
                values[p] += 1
                if values[p] == 10:
                    neighbors = (a for a in adjacent(p) if a in values)
                    increment(*neighbors)

        def reset() -> int:
            flashes = 0
            for pos in self.bounds:
                if values[pos] > 9:
                    values[pos] = 0
                    flashes += 1
            return flashes

        print_state(0)

        total_flashes = 0
        current_step = 0
        while not steps or current_step < steps:
            # increment and cascade flashes
            increment(*self.bounds)
            # reset flashing to 0 counting them
            step_flashes = reset()
            total_flashes += step_flashes
            # log state
            current_step += 1
            print_state(current_step)
            # simultaneous flash! -> end
            if step_flashes >= self.bounds.area:
                break

        return current_step, total_flashes


if __name__ == '__main__':
    octopuses_ = Map.from_file('data/11-input.txt')
    part_1(octopuses_)
    part_2(octopuses_)
