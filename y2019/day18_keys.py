"""
Advent of Code 2019
Day 18: Many-Worlds Interpretation
https://adventofcode.com/2019/day/18
"""

from itertools import chain
from typing import Iterable

from common.graph import shortest_path
from common.rect import Rect
from meta.aoc_tools import data_path


def part_1(map_: 'Map') -> int:
    """
    As you approach Neptune, a planetary security system detects you and activates a giant tractor
    beam on Triton! You have no choice but to land.

    A scan of the local area reveals only one interesting feature: a massive underground vault.
    You generate a map of the tunnels (your puzzle input). The tunnels are too narrow to move
    diagonally.

    Only one **entrance** (marked `@`) is present among the **open passages** (marked `.`) and
    **stone walls** (`#`), but you also detect an assortment of **keys** (shown as lowercase
    letters) and **doors** (shown as uppercase letters). Keys of a given letter open the door of the
    same letter: `a` opens `A`, `b` opens `B`, and so on. You aren't sure which key you need to
    disable the tractor beam, so you'll need to **collect all of them**.

    For example, suppose you have the following map:

        >>> example_1 = Map.from_text('''
        ...     #########
        ...     #b.A.@.a#
        ...     #########
        ... ''')

    Starting from the entrance (`@`), you can only access a large door (`A`) and a key (`a`). Moving
    toward the door doesn't help you, but you can move `2` steps to collect the key, unlocking `A`
    in the process:

        >>> example_1.destinations['<']
        [('a', [], 2), ('b', ['a'], 4)]
        >>> list(example_1.reachable_destinations())
        [('<', 'a', 2)]
        >>> keys_1 = example_1.initial_key_collection()
        >>> keys_1.add('a')
        >>> example_1.draw(keys_1)
        #########
        #b...<.@#
        #########

    Then, you can move `6` steps to collect the only other key, `b`:

        >>> example_1.destinations['a']
        [('b', ['a'], 6)]
        >>> list(example_1.reachable_destinations(keys_1))
        [('a', 'b', 6)]
        >>> keys_1.add('b')
        >>> example_1.draw(keys_1)
        #########
        #@...<..#
        #########

    So, collecting every key took a total of **`8`** steps.

        >>> example_1.collect_all()
        (8, ['a', 'b'])

    Here is a larger example:

        >>> example_2 = Map.from_text('''
        ...     ########################
        ...     #f.D.E.e.C.b.A.@.a.B.c.#
        ...     ######################.#
        ...     #d.....................#
        ...     ########################
        ... ''')

    The only reasonable move is to take key `a` and unlock door `A`:

        >>> example_2.destinations['<']  # doctest: +NORMALIZE_WHITESPACE
        [('a', [], 2), ('b', ['a'], 4), ('c', ['a', 'b'], 6), ('d', ['a', 'b', 'c'], 30),
         ('e', ['a', 'b', 'c'], 8), ('f', ['a', 'b', 'c', 'e', 'd'], 14)]
        >>> keys_2, total_steps = example_2.initial_key_collection(), 0
        >>> list(example_2.reachable_destinations(keys_2))
        [('<', 'a', 2)]
        >>> keys_2.add('a')
        >>> total_steps += 2
        >>> example_2.draw(keys_2)
        ########################
        #f.D.E.e.C.b...<.@.B.c.#
        ######################.#
        #d.....................#
        ########################

    Then, do the same with key `b`:

        >>> list(example_2.reachable_destinations(keys_2))
        [('a', 'b', 6)]
        >>> keys_2.add('b')
        >>> total_steps += 6
        >>> example_2.draw(keys_2)
        ########################
        #f.D.E.e.C.@...<.....c.#
        ######################.#
        #d.....................#
        ########################

    ...and the same with key `c`:

        >>> list(example_2.reachable_destinations(keys_2))
        [('b', 'c', 10)]
        >>> keys_2.add('c')
        >>> total_steps += 10
        >>> example_2.draw(keys_2)
        ########################
        #f.D.E.e.......<.....@.#
        ######################.#
        #d.....................#
        ########################

    Now, you have a choice between keys `d` and `e`. While key `e` is closer, collecting it now
    would be slower in the long run than collecting key `d` first, so that's the best choice:

        >>> list(example_2.reachable_destinations(keys_2))
        [('c', 'd', 24), ('c', 'e', 14)]
        >>> keys_2.add('d')
        >>> total_steps += 24
        >>> example_2.draw(keys_2)
        ########################
        #f...E.e.......<.......#
        ######################.#
        #@.....................#
        ########################

    Finally, collect key `e` to unlock door `E`, ...

        >>> list(example_2.reachable_destinations(keys_2))
        [('d', 'e', 38)]
        >>> keys_2.add('e')
        >>> total_steps += 38
        >>> example_2.draw(keys_2)
        ########################
        #f.....@.......<.......#
        ######################.#
        #......................#
        ########################

    ... then collect key `f`, taking a grand total of **`86`** steps:

        >>> list(example_2.reachable_destinations(keys_2))
        [('e', 'f', 6)]
        >>> keys_2.add('f')
        >>> total_steps += 6
        >>> example_2.draw(keys_2)
        ########################
        #@.............<.......#
        ######################.#
        #......................#
        ########################
        >>> total_steps
        86

        >>> example_2.collect_all()
        (86, ['a', 'b', 'c', 'd', 'e', 'f'])

    Here are a few more examples:

        >>> example_3 = Map.from_text('''
        ...     ########################
        ...     #...............b.C.D.f#
        ...     #.######################
        ...     #.....@.a.B.c.d.A.e.F.g#
        ...     ########################
        ... ''')
        >>> example_3.collect_all()
        (132, ['b', 'a', 'c', 'd', 'f', 'e', 'g'])

        >>> example_4 = Map.from_text('''
        ...     #################
        ...     #i.G..c...e..H.p#
        ...     ########.########
        ...     #j.A..b...f..D.o#
        ...     ########@########
        ...     #k.E..a...g..B.n#
        ...     ########.########
        ...     #l.F..d...h..C.m#
        ...     #################
        ... ''')
        >>> example_4.collect_all()
        (136, ['c', 'e', 'a', 'k', 'b', 'j', 'f', 'g', 'n', 'd', 'l', 'h', 'm', 'o', 'p', 'i'])

        >>> example_5 = Map.from_text('''
        ...     ########################
        ...     #@..............ac.GI.b#
        ...     ###d#e#f################
        ...     ###A#B#C################
        ...     ###g#h#i################
        ...     ########################
        ... ''')
        >>> example_5.collect_all()
        (81, ['a', 'c', 'd', 'g', 'f', 'i', 'b', 'e', 'h'])

    **How many steps is the shortest path that collects all of the keys?**

        >>> part_1(example_5)
        part 1: it takes 81 steps to collect all keys
        81
    """

    result, _ = map_.collect_all()

    print(f"part 1: it takes {result} steps to collect all keys")
    return result


def part_2(map_: 'Map') -> int:
    """
    You arrive at the vault only to discover that there is not one vault, but **four** - each with
    its own entrance.

    On your map, find the area in the middle that looks like this:

        ...
        .@.
        ...

    Update your map to instead use the correct data:

        @#@
        ###
        @#@

    This change will split your map into four separate sections, each with its own entrance:

        >>> example_1 = Map.from_text('''
        ...     #######
        ...     #a.#Cd#
        ...     ##...##
        ...     ##.@.##
        ...     ##...##
        ...     #cB#Ab#
        ...     #######
        ... ''').split()
        >>> example_1.draw()
        #######
        #a.#Cd#
        ##@#@##
        #######
        ##@#@##
        #cB#Ab#
        #######

    Because some of the keys are for doors in other vaults, it would take much too long to collect
    all of the keys by yourself. Instead, you deploy four remote-controlled robots. Each starts at
    one of the entrances (`@`).

    Your goal is still to **collect all of the keys in the fewest steps**, but now, each robot has
    its own position and can move independently. You can only remotely control a single robot at
    a time. Collecting a key instantly unlocks any corresponding doors, regardless of the vault in
    which the key or door is found.

    For example, in the map above, the top-left robot first collects key `a`, unlocking door `A` in
    the bottom-right vault:

        >>> keys_1, total_steps = example_1.initial_key_collection(), 0
        >>> list(example_1.reachable_destinations())
        [('1', 'a', 2)]
        >>> keys_1.add('a', start='1')
        >>> total_steps += 2
        >>> example_1.draw(keys_1)
        #######
        #@.#Cd#
        ##1#@##
        #######
        ##@#@##
        #cB#.b#
        #######

    Then, the bottom-right robot collects key `b`, unlocking door `B` in the bottom-left vault:

        >>> list(example_1.reachable_destinations(keys_1))
        [('4', 'b', 2)]
        >>> keys_1.add('b', start='4')
        >>> total_steps += 2
        >>> example_1.draw(keys_1)
        #######
        #@.#Cd#
        ##1#@##
        #######
        ##@#4##
        #c.#.@#
        #######

    Then, the bottom-left robot collects key `c`:

        >>> list(example_1.reachable_destinations(keys_1))
        [('2', 'c', 2)]
        >>> keys_1.add('c', start='2')
        >>> total_steps += 2
        >>> example_1.draw(keys_1)
        #######
        #@.#.d#
        ##1#@##
        #######
        ##2#4##
        #@.#.@#
        #######

    Finally, the top-right robot collects key `d`:

        >>> list(example_1.reachable_destinations(keys_1))
        [('3', 'd', 2)]
        >>> keys_1.add('d', start='3')
        >>> total_steps += 2
        >>> example_1.draw(keys_1)
        #######
        #@.#.@#
        ##1#3##
        #######
        ##2#4##
        #@.#.@#
        #######

    In this example, it only took **`8`** steps to collect all of the keys.

        >>> total_steps
        8
        >>> example_1.collect_all()
        (8, ['a', 'b', 'c', 'd'])

    Sometimes, multiple robots might have keys available, or a robot might have to wait for multiple
    keys to be collected:

        >>> example_2 = Map.from_text('''
        ...     ###############
        ...     #d.ABC.#.....b#
        ...     ######...######
        ...     ######.@.######
        ...     ######...######
        ...     #a.....#.....c#
        ...     ###############
        ... ''')
        >>> example_2.split().collect_all()
        (24, ['a', 'b', 'c', 'd'])

    Here's a more complex example:

        >>> example_3 = Map.from_text('''
        ...     #############
        ...     #DcBa.#.GhKl#
        ...     #.###...#I###
        ...     #e#d#.@.#j#k#
        ...     ###C#...###J#
        ...     #fEbA.#.FgHi#
        ...     #############
        ... ''')
        >>> example_3.split().collect_all()
        (32, ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l'])

    Here's an example with more choices:

        >>> example_4 = Map.from_text('''
        ...     #############
        ...     #g#f.D#..h#l#
        ...     #F###e#E###.#
        ...     #dCba...BcIJ#
        ...     #####.@.#####
        ...     #nK.L...G...#
        ...     #M###N#H###.#
        ...     #o#m..#i#jk.#
        ...     #############
        ... ''')
        >>> example_4.split().collect_all()
        (72, ['e', 'h', 'a', 'b', 'c', 'i', 'd', 'f', 'g', 'k', 'j', 'l', 'n', 'm', 'o'])

    After updating your map and using the remote-controlled robots, **what is the fewest steps
    necessary to collect all of the keys?**

        >>> part_2(example_4)
        part 2: it takes 72 steps to collect all keys with four robots
        72
    """

    result, _ = map_.split().collect_all()

    print(f"part 2: it takes {result} steps to collect all keys with four robots")
    return result


Pos = tuple[int, int]


class KeysCollection:
    def __init__(self, keys: Iterable[str], current: Iterable[str]):
        self.keys = frozenset(keys)
        self.current = frozenset(current)

    def __len__(self) -> int:
        return len(self.keys)

    def __contains__(self, key: str) -> bool:
        return key in self.keys

    def __hash__(self) -> int:
        return hash((self.keys, self.current))

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, type(self)) and
            self.keys == other.keys and
            self.current == other.current
        )

    def unlocks_all(self, requirements: Iterable[str]) -> bool:
        return all(req in self.keys for req in requirements)

    def add(self, new_key: str, start: str = None):
        if start is None:
            if len(self.current) == 1:
                (start,) = self.current
            else:
                raise ValueError("must supply start for multi-entrance key collection")

        assert new_key not in self.keys
        assert start in self.current

        self.keys = self.keys | {new_key}
        self.current = self.current - {start} | {new_key}

    def __add__(self, other) -> 'KeysCollection':
        if not isinstance(other, tuple):
            return NotImplemented

        start, new_key = other

        assert new_key not in self.keys
        assert start in self.current

        return type(self)(
            keys=self.keys | {new_key},
            current=self.current - {start} | {new_key}
        )


class Map:

    def __init__(
        self,
        floors: Iterable[Pos],
        keys: dict[Pos, str],
        doors: dict[Pos, str],
        entrances: Iterable[Pos]
    ):
        self.floors = set(floors)
        self.keys = dict(keys)
        self.doors = dict(doors)

        entrances = sorted(entrances)
        if len(entrances) == 1:
            self.entrances = {entrances[0]: '<'}
        else:
            self.entrances = {pos: str(k) for k, pos in enumerate(entrances, start=1)}

        assert self.floors.issuperset(self.keys.keys())  # all keys are on floor
        assert self.floors.issuperset(self.doors.keys())  # all doors are on floor
        assert self.floors.issuperset(self.entrances)  # all entrances are on floor
        assert set(self.keys.keys()).isdisjoint(self.doors.keys())  # no key overlaps door
        assert set(self.keys.keys()).isdisjoint(self.entrances)  # no key overlaps entrance
        assert set(self.doors.keys()).isdisjoint(self.entrances)  # no door overlaps entrance
        assert len(self.keys.values()) == len(set(self.keys.values()))  # keys are unique
        assert len(self.doors.values()) == len(set(self.doors.values()))  # doors are unique
        # each door has a matching key
        assert set(self.keys.values()).issuperset(d.lower() for d in self.doors.values())

        self.destinations = self._calculate_destinations()
        self.bounds = Rect.with_all(floors).grow_by(1, 1)

    def _calculate_destinations(self) -> dict[str, list[tuple[str, list[str], int]]]:
        # flood the map from each entrance and each keys to each other key;
        # note the distance and doors (and keys) on the way

        def flood(origin_pos: Pos) -> Iterable[tuple[str, list[str], int]]:
            unvisited = set(self.floors) - {origin_pos}
            layer: list[tuple[Pos, list[str]]] = [(origin_pos, [])]
            distance = 0

            def neighbors(xy: Pos) -> Iterable[Pos]:
                x, y = xy
                return ((x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y))

            while layer:
                next_layer, next_distance = [], distance + 1
                for pos, req_keys in layer:
                    for pos1 in neighbors(pos):
                        if pos1 not in unvisited:
                            continue

                        req_keys1 = req_keys
                        if pos1 in self.keys:
                            yield (key := self.keys[pos1]), req_keys, next_distance
                            if key not in req_keys:
                                req_keys1 = req_keys + [key]
                        elif pos1 in self.doors:
                            door_key = self.doors[pos1].lower()
                            if door_key not in req_keys:
                                req_keys1 = req_keys + [door_key]

                        next_layer.append((pos1, req_keys1))
                        unvisited.remove(pos1)

                layer, distance = next_layer, next_distance

        origins: Iterable[tuple[Pos, str]] = chain(self.entrances.items(), self.keys.items())
        return {
            origin_name: sorted(flood(origin_pos))
            for origin_pos, origin_name in origins
        }

    def initial_key_collection(self) -> KeysCollection:
        return KeysCollection(keys=[], current=self.entrances.values())

    def reachable_destinations(
        self, keys_collected: KeysCollection = None
    ) -> Iterable[tuple[str, str, int]]:
        if keys_collected is None:
            keys_collected = self.initial_key_collection()

        return (
            (start, destination, distance)
            for start in sorted(keys_collected.current)
            for destination, keys_required, distance in self.destinations[start]
            if destination.lower() not in keys_collected
            if keys_collected.unlocks_all(keys_required)
        )

    def collect_all(self) -> tuple[int, list[str]]:
        def all_keys_collected(keys_collected: KeysCollection) -> bool:
            return len(keys_collected) >= len(self.keys)

        def collectable_keys(
            keys_collected: KeysCollection
        ) -> Iterable[tuple[KeysCollection, str, int]]:
            return (
                (keys_collected + (start, new_key), new_key, distance)
                for start, new_key, distance in self.reachable_destinations(keys_collected)
            )

        return shortest_path(
            start=self.initial_key_collection(),
            target=all_keys_collected,
            edges=collectable_keys,
        )

    def draw(self, keys_collected: KeysCollection = None) -> None:
        if keys_collected is None:
            keys_collected = self.initial_key_collection()

        def char(pos: Pos) -> str:
            if pos not in self.floors:
                return '#'  # wall
            elif pos in self.keys:
                if (key := self.keys[pos]) in keys_collected.current:
                    return '@'  # my current position as at this key
                elif key in keys_collected:
                    return '.'  # already picked up
                else:
                    return key  # key is here, ready to be picked up
            elif pos in self.doors:
                if (door := self.doors[pos]).lower() in keys_collected:
                    return '.'  # already unlocked
                else:
                    return door  # door is here and locked
            elif pos in self.entrances:
                if (entrance := self.entrances[pos]) in keys_collected.current:
                    return '@'  # my current position is at entrance
                else:
                    return entrance
            else:
                return '.'  # floor and nothing else

        for y in self.bounds.range_y():
            print(''.join(char((x, y)) for x in self.bounds.range_x()))

    def split(self) -> 'Map':
        if len(self.entrances) != 1:
            raise ValueError(f"cannot split map with {len(self.entrances)} entrances")

        (entrance,) = self.entrances.keys()

        # ...    @#@
        # .@. -> ###
        # ...    @#@

        x, y = entrance
        cross = {(x, y), (x+1, y), (x-1, y), (x, y+1), (x, y-1)}
        assert self.floors.issuperset(cross)
        new_floors = set(self.floors) - cross
        new_entrances = [(x + dx, y + dy) for dx in (-1, +1) for dy in (-1, +1)]

        return type(self)(
            floors=new_floors,
            keys=self.keys,
            doors=self.doors,
            entrances=new_entrances,
        )

    @classmethod
    def from_text(cls, text: str) -> 'Map':
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_file(cls, fn: str) -> 'Map':
        return cls.from_lines(open(fn))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Map':
        floors: list[Pos] = []
        keys: dict[Pos, str] = {}
        doors: dict[Pos, str] = {}
        entrances: list[Pos] = []

        for y, line in enumerate(lines):
            for x, char in enumerate(line.strip()):
                pos = (x, y)
                if char == '.':
                    floors.append(pos)
                elif char.isalpha():
                    floors.append(pos)
                    if char.islower():
                        keys[pos] = char
                    else:
                        doors[pos] = char
                elif char == '@':
                    floors.append(pos)
                    entrances.append(pos)
                elif char == '#':
                    pass
                else:
                    raise ValueError(char)

        return cls(floors=floors, keys=keys, doors=doors, entrances=entrances)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    map_ = Map.from_file(input_path)
    result_1 = part_1(map_)
    result_2 = part_2(map_)
    return result_1, result_2


if __name__ == '__main__':
    main()
