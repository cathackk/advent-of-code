"""
Advent of Code 2024
Day 12: Garden Groups
https://adventofcode.com/2024/day/12
"""

from typing import Iterable, Self

from common.file import relative_path
from common.heading import Heading
from common.iteration import dgroupby_pairs, zip1
from common.rect import Rect
from common.utils import ro


def part_1(garden: 'Map') -> int:
    """
    Why not search for the Chief Historian near the gardener (y2023/day05_almanac.py) and his
    massive farm (y2023/day21_steps.py)? There's plenty of food, so The Historians grab something
    to eat while they search.

    You're about to settle near a complex arrangement of garden plots when some Elves ask if you can
    lend a hand. They'd like to set up fences around each region of garden plots, but they can't
    figure out how much fence they need to order or how much it will cost. They hand you a map (your
    puzzle input) of the garden plots.

    Each garden plot grows only a single type of plant and is indicated by a single letter on your
    map. When multiple garden plots are growing the same type of plant and are touching
    (horizontally or vertically), they form a **region**. For example:

        >>> example_0 = Map.from_text('''
        ...     AAAA
        ...     BBCD
        ...     BBCC
        ...     EEEC
        ... ''')
        >>> example_0.bounds.shape
        (4, 4)

    This 4x4 arrangement includes garden plots growing five different types of plants
    (labeled `A`, `B`, `C`, `D`, and `E`), each grouped into their own region:

        >>> regions_0 = list(example_0.regions())
        >>> [r.plant for r in regions_0]
        ['A', 'B', 'C', 'D', 'E']

    In order to accurately calculate the cost of the fence around a single region, you need to know
    that region's **area** and **perimeter**.

    The **area** of a region is simply the number of garden plots the region contains:

        >>> {r.plant: r.area for r in regions_0}
        {'A': 4, 'B': 4, 'C': 4, 'D': 1, 'E': 3}

    Each garden plot is a square and so has **four sides**. The perimeter of a region is the number
    of sides of garden plots in the region that do not touch another garden plot in the same region:

        >>> {r.plant: r.perimeter for r in regions_0}
        {'A': 10, 'B': 8, 'C': 10, 'D': 4, 'E': 8}

    Visually indicating the sides of plots in each region that contribute to the perimeter using
    `-` and `|`, the above map's regions' perimeters are measured as follows:

        +-+-+-+-+
        |A A A A|
        +-+-+-+-+     +-+
                      |D|
        +-+-+   +-+   +-+
        |B B|   |C|
        +   +   + +-+
        |B B|   |C C|
        +-+-+   +-+ +
                  |C|
        +-+-+-+   +-+
        |E E E|
        +-+-+-+

    Plants of the same type can appear in multiple separate regions, and regions can even appear
    within other regions. For example:

        >>> example_1 = Map.from_text('''
        ...     OOOOO
        ...     OXOXO
        ...     OOOOO
        ...     OXOXO
        ...     OOOOO
        ... ''')
        >>> example_1.bounds.area
        25

    The above map contains **five** regions, one containing all of the `O` garden plots, and the
    other four each containing a single `X` plot:

        >>> regions_1 = list(example_1.regions())
        >>> [r.plant for r in regions_1]
        ['O', 'X', 'X', 'X', 'X']

    The four `X` regions each have area `1` and perimeter `4`. The region containing `21` type `O`
    plants is more complicated; in addition to its outer edge contributing a perimeter of `20`,
    its boundary with each `X` region contributes an additional `4` to its perimeter, for a total
    perimeter of `36`:

        >>> [(r.plant, r.area, r.perimeter) for r in regions_1]
        [('O', 21, 36), ('X', 1, 4), ('X', 1, 4), ('X', 1, 4), ('X', 1, 4)]

    Due to "modern" business practices, the **price** of fence required for a region is found by
    **multiplying** that region's area by its perimeter. The **total price** of fencing all regions
    on a map is found by adding together the price of fence for every region on the map:

    The total price for the first example is **`140`**:

        >>> example_0.print_price_info()
        A: area 4 * perimeter 10 = 40
        B: area 4 * perimeter 8 = 32
        C: area 4 * perimeter 10 = 40
        D: area 1 * perimeter 4 = 4
        E: area 3 * perimeter 8 = 24
        ----
        total price: 140

    The second example has a total price **`772`**:

        >>> example_1.print_price_info()
        O: area 21 * perimeter 36 = 756
        X: area 1 * perimeter 4 = 4
        X: area 1 * perimeter 4 = 4
        X: area 1 * perimeter 4 = 4
        X: area 1 * perimeter 4 = 4
        ----
        total price: 772

    Here's a larger example:

        >>> example_2 = Map.from_text('''
        ...     RRRRIICCFF
        ...     RRRRIICCCF
        ...     VVRRRCCFFF
        ...     VVRCCCJFFF
        ...     VVVVCJJCFE
        ...     VVIVCCJJEE
        ...     VVIIICJJEE
        ...     MIIIIIJJEE
        ...     MIIISIJEEE
        ...     MMMISSJEEE
        ... ''')
        >>> example_2.print_price_info()
        R: area 12 * perimeter 18 = 216
        I: area 4 * perimeter 8 = 32
        C: area 14 * perimeter 28 = 392
        F: area 10 * perimeter 18 = 180
        V: area 13 * perimeter 20 = 260
        J: area 11 * perimeter 20 = 220
        C: area 1 * perimeter 4 = 4
        E: area 13 * perimeter 18 = 234
        I: area 14 * perimeter 22 = 308
        M: area 5 * perimeter 12 = 60
        S: area 3 * perimeter 8 = 24
        ----
        total price: 1930

    **What is the total price of fencing all regions on your map?**

        >>> part_1(example_2)
        part 1: total price of fencing in all regions is 1930
        1930
    """

    result = garden.total_price()

    print(f"part 1: total price of fencing in all regions is {result}")
    return result


def part_2(garden: 'Map') -> int:
    r"""
    Fortunately, the Elves are trying to order so much fence that they qualify for
    a **bulk discount**!

    Under the bulk discount, instead of using the perimeter to calculate the price, you need to use
    the **number of sides** each region has. Each straight section of fence counts as a side,
    regardless of how long it is.

    Consider this example again:

        >>> example_0 = Map.from_text('''
        ...     AAAA
        ...     BBCD
        ...     BBCC
        ...     EEEC
        ... ''')

    The region containing type `A` plants has `4` sides, as does each of the regions containing
    plants of type `B`, `D`, and `E`. However, the more complex region containing the plants of type
    `C` has `8` sides!

        >>> regions_0 = list(example_0.regions())
        >>> {r.plant: r.sides_count() for r in regions_0}
        {'A': 4, 'B': 4, 'C': 8, 'D': 4, 'E': 4}

    Using the new method of calculating the per-region price by multiplying the region's area by its
    number of sides, regions have prices:

        >>> {r.plant: r.price(discount=True) for r in regions_0}
        {'A': 16, 'B': 16, 'C': 32, 'D': 4, 'E': 12}

    For a total price of:

        >>> example_0.total_price(discount=True)
        80

    The second example above (full of type `X` and `O` plants) would have a total price of:

        >>> Map.from_file('data/12-example-xo.txt').total_price(discount=True)
        436

    Here's a map that includes an E-shaped region full of type E plants:

        >>> example_2 = Map.from_text('''
        ...     EEEEE
        ...     EXXXX
        ...     EEEEE
        ...     EXXXX
        ...     EEEEE
        ... ''')
        >>> example_2.print_price_info(discount=True)
        E: area 17 * 12 sides = 204
        X: area 4 * 4 sides = 16
        X: area 4 * 4 sides = 16
        ----
        total price: 236

    This map has a total price of:

        >>> example_3 = Map.from_text('''
        ...     AAAAAA
        ...     AAABBA
        ...     AAABBA
        ...     ABBAAA
        ...     ABBAAA
        ...     AAAAAA
        ... ''')
        >>> example_3.total_price(discount=True)
        368

    It includes two regions full of type `B` plants (each with `4` sides) and a single region full
    of type `A` plants (with `4` sides on the outside and `8` more sides on the inside, a total of
    `12` sides):

        >>> example_3.print_price_info(discount=True)
        A: area 28 * 12 sides = 336
        B: area 4 * 4 sides = 16
        B: area 4 * 4 sides = 16
        ----
        total price: 368

    Be especially careful when counting the fence around regions like the one full of type `A`
    plants; in particular, each section of fence has an in-side and an out-side, so the fence does
    not connect across the middle of the region (where the two `B` regions touch diagonally).
    (The Elves would have used the Möbius Fencing Company instead, but their contract terms were too
    one-sided.)

    The larger example from before now has the following updated prices:

        >>> example_4 = Map.from_file('data/12-example-larger.txt')
        >>> example_4.print_price_info(discount=True)
        R: area 12 * 10 sides = 120
        I: area 4 * 4 sides = 16
        C: area 14 * 22 sides = 308
        F: area 10 * 12 sides = 120
        V: area 13 * 10 sides = 130
        J: area 11 * 12 sides = 132
        C: area 1 * 4 sides = 4
        E: area 13 * 8 sides = 104
        I: area 14 * 16 sides = 224
        M: area 5 * 6 sides = 30
        S: area 3 * 6 sides = 18
        ----
        total price: 1206

    **What is the new total price of fencing all regions on your map?**

        >>> part_2(example_4)
        part 2: total price of fencing after discount is 1206
        1206
    """

    result = garden.total_price(discount=True)

    print(f"part 2: total price of fencing after discount is {result}")
    return result


Pos = tuple[int, int]
Fence = tuple[Heading, Pos]


class Region:
    def __init__(self, plant: str, plots: Iterable[Pos]):
        self.plant = plant
        self.plots = frozenset(plots)
        self.fences = frozenset(
            (heading, plot)
            for plot in self.plots
            for heading in Heading
            if heading.move(plot) not in self.plots
        )

    @property
    def area(self) -> int:
        return len(self.plots)

    @property
    def perimeter(self) -> int:
        return len(self.fences)

    def price(self, discount: bool = False) -> int:
        if not discount:
            return self.area * self.perimeter
        else:
            return self.area * self.sides_count()

    def sides_count(self) -> int:
        def fence_runs() -> Iterable[list[int]]:
            heading_to_fences = dgroupby_pairs(self.fences)

            # fences on the west and east sides of a plot are vertical
            for vertical in (Heading.WEST, Heading.EAST):
                # going by columns -> group by x
                x_to_ys = dgroupby_pairs(heading_to_fences[vertical])
                for _, ys in sorted(x_to_ys.items()):
                    yield sorted(ys)

            # fences on the north and south sides of a plot are horizontal
            for horizontal in (Heading.NORTH, Heading.SOUTH):
                # going by rows -> group by y
                y_to_xs = dgroupby_pairs(ro(pos) for pos in heading_to_fences[horizontal])
                # and order by x (reading order)
                for _, xs in sorted(y_to_xs.items()):
                    yield sorted(xs)

        def count_sequences(run: list[int]) -> int:
            # count occurences of number runs that do not align:
            # [1, 2, 3, 5, 6] -> [1, 2, 3] [5, 6] -> 2
            return 1 + sum(1 for a, b in zip1(run) if a + 1 != b)

        return sum(count_sequences(run) for run in fence_runs())


class Map:
    def __init__(self, plots: dict[Pos, str] | Iterable[tuple[Pos, str]]):
        self.plots: dict[Pos, str] = dict(plots)
        self.bounds = Rect.with_all(self.plots)
        # map is rectangular without gaps
        assert self.bounds.area == len(self.plots)

    def regions(self) -> Iterable[Region]:
        unprocessed_plots = set(self.plots.keys())

        for region_start, region_plant in self.plots.items():
            if region_start not in unprocessed_plots:
                continue

            region_plots: list[Pos] = []
            to_explore: list[Pos] = [region_start]

            while to_explore:
                pos = to_explore.pop()
                if self.plots.get(pos) == region_plant and pos in unprocessed_plots:
                    region_plots.append(pos)
                    to_explore.extend(h.move(pos) for h in Heading)
                    unprocessed_plots.remove(pos)

            yield Region(region_plant, region_plots)

            if not unprocessed_plots:
                return

    def total_price(self, discount: bool = False) -> int:
        return sum(region.price(discount) for region in self.regions())

    def print_price_info(self, discount: bool = False) -> None:
        total_price = 0
        for r in self.regions():
            mult_str = f"perimeter {r.perimeter}" if not discount else f"{r.sides_count()} sides"
            print(f"{r.plant}: area {r.area} * {mult_str} = {r.price(discount)}")
            total_price += r.price(discount)
        print("----")
        print("total price:", total_price)

    @classmethod
    def from_file(cls, fn: str) -> Self:
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_text(cls, text: str) -> Self:
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        return cls(
            ((x, y), char)
            for y, line in enumerate(lines)
            for x, char in enumerate(line.strip())
        )


def main(input_fn: str = 'data/12-input.txt') -> tuple[int, int]:
    garden = Map.from_file(input_fn)
    result_1 = part_1(garden)
    result_2 = part_2(garden)
    return result_1, result_2


if __name__ == '__main__':
    main()
