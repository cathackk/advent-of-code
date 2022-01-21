"""
Advent of Code 2020
Day 11: Seating System
https://adventofcode.com/2020/day/11
"""

from collections import Counter
from collections import defaultdict
from functools import cached_property
from typing import Iterable

from common.file import relative_path
from common.rect import Rect


def part_1(seats_map: 'SeatsMap') -> int:
    """
    By modeling the process people use to choose (or abandon) their seat in the waiting area,
    you're pretty sure you can predict the best place to sit. You make a quick map of the seat
    layout (your puzzle input).

    The seat layout fits neatly on a grid. Each position is either floor (`.`), an empty seat
    (`L`), or an occupied seat (`#`). For example, the initial seat layout might look like this:

        >>> seats = SeatsMap.from_text('''
        ...
        ...     L.LL.LL.LL
        ...     LLLLLLL.LL
        ...     L.L.L..L..
        ...     LLLL.LL.LL
        ...     L.LL.LL.LL
        ...     L.LLLLL.LL
        ...     ..L.L.....
        ...     LLLLLLLLLL
        ...     L.LLLLLL.L
        ...     L.LLLLL.LL
        ...
        ... ''')
        >>> seats.width, seats.height
        (10, 10)
        >>> seats.count('L')
        71

    Now, you just need to model the people who will be arriving shortly. Fortunately, people are
    entirely predictable and always follow a simple set of rules. All decisions are based on the
    *number of occupied seats* adjacent to a given seat (one of the eight positions immediately up,
    down, left, right, or diagonal from the seat). The following rules are applied to every seat
    simultaneously:

        - If a seat is *empty* (`L`) and there are no occupied seats adjacent to it, the seat
          becomes *occupied*.
        - If a seat is *occupied* (`#`) and four or more seats adjacent to it are also occupied,
          the seat becomes *empty*.
        - Otherwise, the seat's state does not change.

    Floor (`.`) never changes; seats don't move, and nobody sits on the floor.

    After one round of these rules, every seat in the example layout becomes occupied:

        >>> seats.advance_1()
        True
        >>> print(seats)
        #.##.##.##
        #######.##
        #.#.#..#..
        ####.##.##
        #.##.##.##
        #.#####.##
        ..#.#.....
        ##########
        #.######.#
        #.#####.##

    After a second round, the seats with four or more occupied adjacent seats become empty again:

        >>> seats.advance_1()
        True
        >>> print(seats)
        #.LL.L#.##
        #LLLLLL.L#
        L.L.L..L..
        #LLL.LL.L#
        #.LL.LL.LL
        #.LLLL#.##
        ..L.L.....
        #LLLLLLLL#
        #.LLLLLL.L
        #.#LLLL.##

    This process continues for three more rounds:

        >>> seats.advance_1()
        True
        >>> print(seats)
        #.##.L#.##
        #L###LL.L#
        L.#.#..#..
        #L##.##.L#
        #.##.LL.LL
        #.###L#.##
        ..#.#.....
        #L######L#
        #.LL###L.L
        #.#L###.##

        >>> seats.advance_1()
        True
        >>> print(seats)
        #.#L.L#.##
        #LLL#LL.L#
        L.L.L..#..
        #LLL.##.L#
        #.LL.LL.LL
        #.LL#L#.##
        ..L.L.....
        #L#LLLL#L#
        #.LLLLLL.L
        #.#L#L#.##

        >>> seats.advance_1()
        True
        >>> print(seats)
        #.#L.L#.##
        #LLL#LL.L#
        L.#.L..#..
        #L##.##.L#
        #.#L.LL.LL
        #.#L#L#.##
        ..L.L.....
        #L#L##L#L#
        #.LLLLLL.L
        #.#L#L#.##

    At this point, something interesting happens: the chaos stabilizes and further applications of
    these rules cause no seats to change state!

        >>> seats.advance_1()
        False

    Once people stop moving around, you count *37* occupied seats.

        >>> seats.count('#')
        37

    Simulate your seating area by applying the seating rules repeatedly until no seats change
    state. *How many seats end up occupied?*

        >>> part_1(seats)
        part 1: seats stabilize after 5 rounds with 37 occupied seats
        37
    """

    seats_map.reset()
    while seats_map.advance_1():
        pass
    occupied_count = seats_map.count(SeatsMap.OCCUPIED_SEAT)

    print(f"part 1: seats stabilize after {seats_map.rounds} rounds "
          f"with {occupied_count} occupied seats")
    return occupied_count


def part_2(seats_map: 'SeatsMap') -> int:
    """
    As soon as people start to arrive, you realize your mistake. People don't just care about
    adjacent seats - they care about *the first seat they can see* in each of those eight
    directions!

    Now, instead of considering just the eight immediately adjacent seats, consider the *first
    seat* in each of those eight directions. For example, the empty seat below would see *eight*
    occupied seats:

        >>> example_1 = SeatsMap.from_text('''
        ...
        ...     .......#.
        ...     ...#.....
        ...     .#.......
        ...     .........
        ...     ..#L....#
        ...     ....#....
        ...     .........
        ...     #........
        ...     ...#.....
        ...
        ... ''')
        >>> example_1.tile_at((3, 4))
        'L'
        >>> example_1.occupied_visibles()[(3, 4)]
        8

    The leftmost empty seat below would only see *one* empty seat, but cannot see any of the
    occupied ones:

        >>> example_2 = SeatsMap.from_text('''
        ...
        ...     .............
        ...     .L.L.#.#.#.#.
        ...     .............
        ...
        ... ''')
        >>> sorted(example_2.occupied_visibles().items())
        [((3, 1), 1), ((5, 1), 1), ((7, 1), 2), ((9, 1), 2), ((11, 1), 1)]

    The empty seat below would see *no* occupied seats:

        >>> example_3 = SeatsMap.from_text('''
        ...
        ...     .##.##.
        ...     #.#.#.#
        ...     ##...##
        ...     ...L...
        ...     ##...##
        ...     #.#.#.#
        ...     .##.##.
        ...
        ... ''')
        >>> example_3.tile_at((3, 3))
        'L'
        >>> example_3.occupied_visibles()[(3, 3)]
        0

    Also, people seem to be more tolerant than you expected: it now takes *five or more* visible
    occupied seats for an occupied seat to become empty (rather than *four or more* from the
    previous rules). The other rules still apply: empty seats that see no occupied seats become
    occupied, seats matching no rule don't change, and floor never changes.

    Given the same starting layout as above, these new rules cause the seating area to shift around
    as follows:

        >>> seats = SeatsMap.from_text('''
        ...
        ...     L.LL.LL.LL
        ...     LLLLLLL.LL
        ...     L.L.L..L..
        ...     LLLL.LL.LL
        ...     L.LL.LL.LL
        ...     L.LLLLL.LL
        ...     ..L.L.....
        ...     LLLLLLLLLL
        ...     L.LLLLLL.L
        ...     L.LLLLL.LL
        ...
        ... ''')

        >>> seats.advance_2()
        True
        >>> print(seats)
        #.##.##.##
        #######.##
        #.#.#..#..
        ####.##.##
        #.##.##.##
        #.#####.##
        ..#.#.....
        ##########
        #.######.#
        #.#####.##

        >>> seats.advance_2()
        True
        >>> print(seats)
        #.LL.LL.L#
        #LLLLLL.LL
        L.L.L..L..
        LLLL.LL.LL
        L.LL.LL.LL
        L.LLLLL.LL
        ..L.L.....
        LLLLLLLLL#
        #.LLLLLL.L
        #.LLLLL.L#

        >>> seats.advance_2()
        True
        >>> print(seats)
        #.L#.##.L#
        #L#####.LL
        L.#.#..#..
        ##L#.##.##
        #.##.#L.##
        #.#####.#L
        ..#.#.....
        LLL####LL#
        #.L#####.L
        #.L####.L#

        >>> seats.advance_2()
        True
        >>> print(seats)
        #.L#.L#.L#
        #LLLLLL.LL
        L.L.L..#..
        ##LL.LL.L#
        L.LL.LL.L#
        #.LLLLL.LL
        ..L.L.....
        LLLLLLLLL#
        #.LLLLL#.L
        #.L#LL#.L#

        >>> seats.advance_2()
        True
        >>> print(seats)
        #.L#.L#.L#
        #LLLLLL.LL
        L.L.L..#..
        ##L#.#L.L#
        L.L#.#L.L#
        #.L####.LL
        ..#.#.....
        LLL###LLL#
        #.LLLLL#.L
        #.L#LL#.L#

        >>> seats.advance_2()
        True
        >>> print(seats)
        #.L#.L#.L#
        #LLLLLL.LL
        L.L.L..#..
        ##L#.#L.L#
        L.L#.LL.L#
        #.LLLL#.LL
        ..#.L.....
        LLL###LLL#
        #.LLLLL#.L
        #.L#LL#.L#

    Again, at this point, people stop shifting around and the seating area reaches equilibrium.

        >>> seats.advance_2()
        False

    Once this occurs, you count *26* occupied seats.

        >>> seats.count('#')
        26

    Given the new visibility method and the rule change for occupied seats becoming empty, once
    equilibrium is reached, *how many seats end up occupied?*

        >>> part_2(seats)
        part 2: seats stabilize after 6 rounds with 26 occupied seats
        26
    """

    seats_map.reset()
    while seats_map.advance_2():
        pass
    occupied_count = seats_map.count(SeatsMap.OCCUPIED_SEAT)

    print(f"part 2: seats stabilize after {seats_map.rounds} rounds "
          f"with {occupied_count} occupied seats")
    return occupied_count


Pos = tuple[int, int]


class SeatsMap:
    FLOOR = '.'
    EMPTY_SEAT = 'L'
    OCCUPIED_SEAT = '#'

    def __init__(self, tiles: Iterable[tuple[Pos, str]]):
        self.tiles = {
            pos: ch
            for pos, ch in tiles
            if ch != self.FLOOR
        }
        self.bounds = Rect.with_all(self.tiles.keys())
        self.rounds = 0

        assert all(
            tile in (self.EMPTY_SEAT, self.OCCUPIED_SEAT)
            for tile in self.tiles.values()
        )

    @classmethod
    def from_file(cls, fn: str):
        return cls.from_lines(relative_path(__file__, fn))

    @classmethod
    def from_text(cls, text: str):
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]):
        return cls(
            ((x, y), ch)
            for y, line in enumerate(lines)
            for x, ch in enumerate(line.strip())
        )

    @property
    def width(self) -> int:
        return self.bounds.width

    @property
    def height(self) -> int:
        return self.bounds.height

    def count(self, tile: str) -> int:
        return sum(1 for t in self.tiles.values() if t == tile)

    @cached_property
    def adjacents(self) -> dict[Pos, set[Pos]]:
        """ Precompute adjacent seats pairs. """
        adjacents = defaultdict(set)

        for x, y in self.tiles.keys():
            for d_x, d_y in [(+1, 0), (0, +1), (+1, +1), (-1, +1)]:
                n_x, n_y = x + d_x, y + d_y
                if (n_x, n_y) in self.tiles:
                    adjacents[(x, y)].add((n_x, n_y))
                    adjacents[(n_x, n_y)].add((x, y))

        return dict(adjacents)

    @cached_property
    def visibles(self) -> dict[Pos, set[Pos]]:
        """ Precompute visible seat pairs. """

        def visible_from(pos_0: Pos, vector: tuple[int, int]) -> Pos | None:
            d_x, d_y = vector
            x_0, y_0 = pos_0
            x, y = x_0 + d_x, y_0 + d_y
            while (x, y) in self.bounds:
                if (x, y) in self.tiles:
                    return x, y
                x, y = x + d_x, y + d_y
            else:
                return None

        visibles = defaultdict(set)
        for pos in self.tiles.keys():
            for direction in [(+1, 0), (0, +1), (+1, +1), (-1, +1)]:
                visible_pos = visible_from(pos, direction)
                if visible_pos:
                    visibles[pos].add(visible_pos)
                    visibles[visible_pos].add(pos)

        return dict(visibles)

    def occupied_neighbors_count(self, neighbors: dict[Pos, set[Pos]]) -> Counter[Pos]:
        """
        Count the number occupied neighboring seats.
        Definition of "neighboring" is passed in `neighbors` arg.
        """
        return Counter(
            npos
            for pos, tile in self.tiles.items()
            if tile == self.OCCUPIED_SEAT
            for npos in neighbors[pos]
        )

    def occupied_adjacents(self) -> Counter[Pos]:
        return self.occupied_neighbors_count(self.adjacents)

    def occupied_visibles(self) -> Counter[Pos]:
        return self.occupied_neighbors_count(self.visibles)

    def advance(self, occupied_neighbors_count: Counter[Pos], max_neighbors_to_stay: int) -> bool:

        def next_tile(tile: str, occ_ns_count: int) -> str:
            if tile == self.EMPTY_SEAT and occ_ns_count == 0:
                return self.OCCUPIED_SEAT
            elif tile == self.OCCUPIED_SEAT and occ_ns_count > max_neighbors_to_stay:
                return self.EMPTY_SEAT
            else:
                return tile

        new_tiles = {
            pos: next_tile(old_tile, occupied_neighbors_count[pos])
            for pos, old_tile in self.tiles.items()
        }

        if new_tiles != self.tiles:
            self.tiles = new_tiles
            self.rounds += 1
            return True
        else:
            return False

    def advance_1(self) -> bool:
        """ One round with 'adjacent' rule (part 1) """
        return self.advance(self.occupied_adjacents(), max_neighbors_to_stay=3)

    def advance_2(self) -> bool:
        """ One round with 'visible' rule (part 2) """
        return self.advance(self.occupied_visibles(), max_neighbors_to_stay=4)

    def reset(self) -> None:
        self.tiles = {
            pos: self.EMPTY_SEAT
            for pos in self.tiles.keys()
        }
        self.rounds = 0

    def tile_at(self, pos: Pos) -> str:
        return self.tiles.get(pos, self.FLOOR)

    def __str__(self):
        return "\n".join(
            "".join(
                self.tile_at((x, y))
                for x in self.bounds.range_x()
            )
            for y in self.bounds.range_y()
        )


if __name__ == '__main__':
    seats_ = SeatsMap.from_file('data/11-input.txt')
    assert seats_.width == 92
    assert seats_.height == 94

    part_1(seats_)
    part_2(seats_)
