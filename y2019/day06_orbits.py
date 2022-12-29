"""
Advent of Code 2019
Day 6: Universal Orbit Map
https://adventofcode.com/2019/day/6
"""

import functools
from itertools import zip_longest
from typing import Iterable

from common.file import relative_path
from common.iteration import dgroupby_pairs


def part_1(orbit_map: 'OrbitMap') -> int:
    """
    You've landed at the Universal Orbit Map facility on Mercury. Because navigation in space often
    involves transferring between orbits, the orbit maps here are useful for finding efficient
    routes between, for example, you and Santa. You download a map of the local orbits (your puzzle
    input).

    Except for the universal Center of Mass (COM), every object in space is in orbit around exactly
    one other object. An orbit looks roughly like this:

                          \
                           \
                            |
                            |
        AAA--> o            o <--BBB
                            |
                            |
                           /
                          /

    In this diagram, the object `BBB` is in orbit around `AAA`. The path that `BBB` takes around
    `AAA` (drawn with lines) is only partly shown. In the map data, this orbital relationship is
    written `AAA)BBB`, which means "`BBB` is in orbit around `AAA`".

    Before you use your map data to plot a course, you need to make sure it wasn't corrupted during
    the download. To verify maps, the Universal Orbit Map facility uses **orbit count checksums**
    - the total number of **direct orbits** (like the one shown above) and **indirect orbits**.

    Whenever `A` orbits `B` and `B` orbits `C`, then `A` **indirectly orbits** `C`. This chain can
    be any number of objects long: if `A` orbits `B`, `B` orbits `C`, and `C` orbits `D`, then `A`
    indirectly orbits `D`.

    For example, suppose you have the following map:

        >>> omap = OrbitMap.from_text('''
        ...     COM)B
        ...     B)C
        ...     C)D
        ...     D)E
        ...     E)F
        ...     B)G
        ...     G)H
        ...     D)I
        ...     E)J
        ...     J)K
        ...     K)L
        ... ''')
        >>> omap  # doctest: +NORMALIZE_WHITESPACE
        OrbitMap({'COM': ['B'], 'B': ['C', 'G'], 'C': ['D'], 'D': ['E', 'I'], 'E': ['F', 'J'],
                  'G': ['H'], 'J': ['K'], 'K': ['L']})

    Visually, the above map of orbits looks like this:

        >>> omap.draw()
        COM ─ B ┬ C ─ D ┬ E ┬ F
                │       │   └ J ─ K ─ L
                │       └ I
                └ G ─ H

    In this visual representation, when two objects are connected by a line, the one on the right
    directly orbits the one on the left.

    Here, we can count the total number of orbits as follows:

      - `D` directly orbits `C` and indirectly orbits `B` and `COM`, a total of 3 orbits:

        >>> omap.orbit_depth('D')
        3

      - `L` directly orbits `K` and indirectly orbits `J`, `E`, `D`, `C`, `B`, and `COM`,
        a total of 7 orbits:

        >>> omap.orbit_depth('L')
        7

      - `COM` orbits nothing:

        >>> omap.orbit_depth('COM')
        0

    The total number of direct and indirect orbits in this example is 42.

        >>> omap.total_orbits_count()
        42

    **What is the total number of direct and indirect orbits** in your map data?

        >>> part_1(omap)
        part 1: total 42 direct and indirect orbits
        42
    """

    result = orbit_map.total_orbits_count()

    print(f"part 1: total {result} direct and indirect orbits")
    return result


def part_2(orbit_map: 'OrbitMap') -> int:
    """
    Now, you just need to figure out how many **orbital transfers** you (`YOU`) need to take to get
    to Santa (`SAN`).

    You start at the object `YOU` are orbiting; your destination is the object `SAN` is orbiting.
    An orbital transfer lets you move from any object to an object orbiting or orbited by that
    object.

    For example, suppose you have the following map:

        >>> omap = OrbitMap.from_text('''
        ...     COM)B
        ...     B)C
        ...     C)D
        ...     D)E
        ...     E)F
        ...     B)G
        ...     G)H
        ...     D)I
        ...     E)J
        ...     J)K
        ...     K)L
        ...     K)YOU
        ...     I)SAN
        ... ''')
        >>> omap  # doctest: +NORMALIZE_WHITESPACE
        OrbitMap({'COM': ['B'], 'B': ['C', 'G'], 'C': ['D'], 'D': ['E', 'I'], 'E': ['F', 'J'],
                  'G': ['H'], 'J': ['K'], 'K': ['L', 'YOU'], 'I': ['SAN']})

    Visually, the above map of orbits looks like this:

        >>> omap.draw()
        COM ─ B ┬ C ─ D ┬ E ┬ F
                │       │   └ J ─ K ┬ L
                │       │           └ YOU
                │       └ I ─ SAN
                └ G ─ H

    In this example, `YOU` are in orbit around `K`, and `SAN` is in orbit around `I`.

        >>> omap.parent_body('YOU')
        'K'
        >>> omap.parent_body('SAN')
        'I'

    To move from `K` to `I`, a minimum of 4 orbital transfers are required:

        >>> omap.path_between('K', 'I')
        ['K', 'J', 'E', 'D', 'I']
        >>> omap.transfer_steps_required('YOU', 'SAN')
        4
        >>> (omap2 := omap.make_transfer('YOU', 'SAN'))  # doctest: +NORMALIZE_WHITESPACE
        OrbitMap({'COM': ['B'], 'B': ['C', 'G'], 'C': ['D'], 'D': ['E', 'I'], 'E': ['F', 'J'],
                   'G': ['H'], 'J': ['K'], 'K': ['L'], 'I': ['SAN', 'YOU']})


    Afterward, the map of orbits looks like this:

        >>> omap2.draw()
        COM ─ B ┬ C ─ D ┬ E ┬ F
                │       │   └ J ─ K ─ L
                │       └ I ┬ SAN
                │           └ YOU
                └ G ─ H

    **What is the minimum number of orbital transfers required** to move from the object `YOU` are
    orbiting to the object `SAN` is orbiting? (Between the objects they are orbiting - not between
    `YOU` and `SAN`.)

        >>> part_2(omap)
        part 2: 4 transfers required
        4
    """

    result = orbit_map.transfer_steps_required('YOU', 'SAN')

    print(f"part 2: {result} transfers required")
    return result


class OrbitMap:
    def __init__(self, orbits: dict[str, list[str]]):
        # shallow copy
        self.orbits = dict(orbits)

        # find root
        bodies = self.orbits.keys()
        satellites = {sat for sats in self.orbits.values() for sat in sats}
        root, = bodies - satellites
        self.root = root

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.orbits!r})'

    def orbit_depth(self, body: str) -> int:
        return len(self.path_from_root(body)) - 1

    @functools.lru_cache(maxsize=1024)
    def moons_count(self, body: str) -> int:
        if body not in self.orbits:
            return 0

        satellites = self.orbits[body]

        # not using comprehension to save some stack for recursion
        total = len(satellites)
        for satellite in satellites:
            total += self.moons_count(satellite)
        return total

    def total_orbits_count(self) -> int:
        return sum(self.moons_count(body) for body in self.orbits)

    def path_from_root(self, body: str) -> list[str]:
        def find(current: str) -> list[str] | None:
            if current == body:
                return [current]

            if current not in self.orbits:
                return None

            for satellite in self.orbits[current]:
                subpath = find(satellite)
                if subpath is not None:
                    return [current] + subpath
            else:
                return None

        path = find(self.root)
        if not path:
            raise KeyError(body)

        return path

    def parent_body(self, body: str) -> str | None:
        if body == self.root:
            return None

        path = self.path_from_root(body)
        assert len(path) >= 2
        assert path[-1] == body
        return path[-2]

    def path_between(self, start: str, target: str) -> list[str]:
        root_to_start = self.path_from_root(start)
        root_to_target = self.path_from_root(target)
        common_count = sum(1 for p_1, p_2 in zip(root_to_start, root_to_target) if p_1 == p_2)
        assert common_count > 0
        return root_to_start[:common_count-1:-1] + root_to_target[common_count-1:]

    def transfer_steps_required(self, moved: str, target_sibling: str) -> int:
        """
        Number of steps needed so that `moved` orbits the same body as `target_satellite` does
        """

        # e.g.
        # path = [moved, A, B, C, target_sibling]
        # -> `moved` orbits `A`
        # -> `target_sibling` orbits `C`
        # -> A-B-C = 2 steps
        return len(self.path_between(moved, target_sibling)) - 3

    def make_transfer(self, body: str, target_sibling: str) -> 'OrbitMap':
        body_parent = self.parent_body(body)
        target_body = self.parent_body(target_sibling)
        # deep copy
        new_orbits = {body: list(satellites) for body, satellites in self.orbits.items()}
        new_orbits[body_parent].remove(body)
        new_orbits[target_body].append(body)
        return type(self)(new_orbits)

    def draw(self) -> None:
        def paths(body: str) -> Iterable[list[tuple[str, int]]]:
            if body in self.orbits:
                return (
                    [(body, len(self.orbits[body]) - moon_index - 1)] + subpath
                    for moon_index, moon in enumerate(self.orbits[body])
                    for subpath in paths(moon)
                )
            else:
                return ([(body, -1)],)

        def format_body(body_rem: tuple[str, int], prev_body_rem: tuple[str, int] | None) -> str:
            if body_rem is None:
                return ''
            body, rem = body_rem
            prev_body, prev_rem = prev_body_rem if prev_body_rem else (None, None)

            if body != prev_body:
                if rem > 0:
                    return body + ' ┬ '
                elif rem == 0:
                    return body + ' ─ '
                elif rem == -1:
                    return body

            elif body == prev_body:
                blank = ' ' * len(body)
                if rem == prev_rem == 0:
                    return blank + '   '
                elif rem == prev_rem == 1:
                    return blank + ' │ '
                elif rem == 0 and prev_rem > 0:
                    return blank + ' └ '

            raise ValueError(body, prev_body, rem, prev_rem)

        prev_path = []
        for path in paths(self.root):
            print(''.join(format_body(now, prev) for now, prev in zip_longest(path, prev_path)))
            prev_path = path

    @classmethod
    def from_text(cls, text: str) -> 'OrbitMap':
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'OrbitMap':
        def pair_from_line(line: str) -> tuple[str, str]:
            body_1, body_2 = line.strip().split(')')
            return body_1, body_2

        return cls(dgroupby_pairs(pair_from_line(line) for line in lines))

    @classmethod
    def from_file(cls, fn: str) -> 'OrbitMap':
        return cls.from_lines(open(relative_path(__file__, fn)))


def main(fn: str = 'data/06-orbits.txt') -> tuple[int, int]:
    orbit_map = OrbitMap.from_file(fn)
    # sys.setrecursionlimit(2048)  # max depth is ~ 350
    result_1 = part_1(orbit_map)
    result_2 = part_2(orbit_map)
    return result_1, result_2


if __name__ == '__main__':
    main()
