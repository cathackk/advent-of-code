"""
Advent of Code 2018
Day 15: Beverage Bandits
https://adventofcode.com/2018/day/15
"""

from collections import Counter
from itertools import count
from typing import Iterable, Optional, Self

from common.utils import ro, some
from meta.aoc_tools import data_path


def part_1(battle: 'Battle') -> int:
    """
    Having perfected their hot chocolate, the Elves have a new problem: the Goblins that live in
    these caves will do anything to steal it. Looks like they're here for a fight.

    You scan the area, generating a map of the walls (`#`), open cavern (`.`), and starting position
    of every Goblin (`G`) and Elf (`E`) (your puzzle input).

    Combat proceeds in **rounds**; in each round, each unit that is still alive takes a **turn**,
    resolving all of its actions before the next unit's turn begins. On each unit's turn, it tries
    to **move** into range of an enemy (if it isn't already) and then **attack** (if it's in range).

    ## Order of moves

    All units are very disciplined and always follow very strict combat rules. Units never move or
    attack diagonally, as doing so would be dishonorable. When multiple choices are equally valid,
    ties are broken in **reading order**: top-to-bottom, then left-to-right. For instance, the order
    in which units take their turns within a round is the **reading order of their starting
    positions** in that round, regardless of the type of unit or whether other units have moved
    after the round started. For example:

                         would take their
        These units:   turns in this order:
          #######           #######
          #.G.E.#           #.1.2.#
          #E.G.E#           #3.4.5#
          #.G.E.#           #.6.7.#
          #######           #######

    ## Targeting

    Each unit begins its turn by identifying all possible **targets** (enemy units). If no targets
    remain, combat ends.

    Then, the unit identifies all of the open squares (`.`) that are **in range** of each target;
    these are the squares which are **adjacent** (immediately up, down, left, or right) to any
    target and which aren't already occupied by a wall or another unit. Alternatively, the unit
    might **already** be in range of a target. If the unit is not already in range of a target, and
    there are no open squares which are in range of a target, the unit ends its turn.

    If the unit is already in range of a target, it does not **move**, but continues its turn with
    an **attack**. Otherwise, since it is not in range of a target, it **moves**.

    ## Movement

    To **move**, the unit first considers the squares that are **in range** and determines **which
    of those squares it could reach in the fewest steps**. A **step** is a single movement to any
    adjacent (immediately up, down, left, or right) open (`.`) square. Units cannot move into walls
    or other units. The unit does this while considering the **current positions of units** and does
    not do any prediction about where units will be later. If the unit cannot reach (find an open
    path to) any of the squares that are in range, it ends its turn. If multiple squares are in
    range and **tied** for being reachable in the fewest steps, the square which is first in
    **reading order** is chosen. For example:

        Targets:      In range:     Reachable:    Nearest:      Chosen:
        #######       #######       #######       #######       #######
        #E..G.#       #E.?G?#       #E.@G.#       #E.!G.#       #E.+G.#
        #...#.#  -->  #.?.#?#  -->  #.@.#.#  -->  #.!.#.#  -->  #...#.#
        #.G.#G#       #?G?#G#       #@G@#G#       #!G.#G#       #.G.#G#
        #######       #######       #######       #######       #######

    In the above scenario, the Elf has three targets (the three Goblins):

      - Each of the Goblins has open, adjacent squares which are **in range* (marked with a `?` on
        the map).
      - Of those squares, four are **reachable** (marked `@`); the other two (on the right) would
        require moving through a wall or unit to reach.
      - Three of these reachable squares are **nearest**, requiring the fewest steps (only 2) to
        reach (marked `!`).
      - Of those, the square which is first in reading order is **chosen** (`+`).

    The unit then takes a single **step** toward the chosen square along **the shortest path** to
    that square. If multiple steps would put the unit equally closer to its destination, the unit
    chooses the step which is first in reading order. (This requires knowing when there is **more
    than one shortest path** so that you can consider the first step of each such path.) For
    example:

        In range:     Nearest:      Chosen:       Distance:     Step:
        #######       #######       #######       #######       #######
        #.E...#       #.E...#       #.E...#       #4E212#       #..E..#
        #...?.#  -->  #...!.#  -->  #...+.#  -->  #32101#  -->  #.....#
        #..?G?#       #..!G.#       #...G.#       #432G2#       #...G.#
        #######       #######       #######       #######       #######

    The Elf sees three squares in range of a target (`?`), two of which are nearest (`!`), and so
    the first in reading order is chosen (`+`). Under "Distance", each open square is marked with
    its distance from the destination square; the two squares to which the Elf could move on this
    turn (down and to the right) are both equally good moves and would leave the Elf `2` steps from
    being in range of the Goblin. Because the step which is first in reading order is chosen, the
    Elf moves **right** one square.

    Here's a larger example of movement:

        >>> example_map = Battle.from_file(data_path(__file__, 'example-movement.txt'))
        >>> print(format(example_map, '!status'))
        Initially:
        #########
        #G..G..G#
        #.......#
        #.......#
        #G..E..G#
        #.......#
        #.......#
        #G..G..G#
        #########
        >>> example_map.do_round()
        >>> print(format(example_map, '!status'))
        After 1 round:
        #########
        #.G...G.#
        #...G...#
        #...E..G#
        #.G.....#
        #.......#
        #G..G..G#
        #.......#
        #########
        >>> example_map.do_round()
        >>> print(format(example_map, '!status'))
        After 2 rounds:
        #########
        #..G.G..#
        #...G...#
        #.G.E.G.#
        #.......#
        #G..G..G#
        #.......#
        #.......#
        #########
        >>> example_map.do_round()
        >>> print(format(example_map, '!status'))
        After 3 rounds:
        #########
        #.......#
        #..GGG..#
        #..GEG..#
        #G..G...#
        #......G#
        #.......#
        #.......#
        #########

    Once the Goblins and Elf reach the positions above, they all are either in range of a target or
    cannot find any square in range of a target, and so none of the units can move until a unit
    dies.

        >>> example_map.do_round()
        >>> print(format(example_map, '!status'))
        After 4 rounds:
        #########
        #.......#
        #..GGG..#
        #..GEG..#
        #G..G...#
        #......G#
        #.......#
        #.......#
        #########

    After moving (or if the unit began its turn in range of a target), the unit **attacks**.

    ## Attacking

    To **attack**, the unit first determines **all** of the targets that are **in range** of it by
    being immediately **adjacent** to it. If there are no such targets, the unit ends its turn.
    Otherwise, the adjacent target with **the fewest hit points** is selected; in a tie, the
    adjacent target with the fewest hit points which is first in reading order is selected.

    The unit deals damage equal to its **attack power** to the selected target, reducing its hit
    points by that amount. If this reduces its hit points to `0` or fewer, the selected target
    **dies**: its square becomes `.` and it takes no further turns.

    Each **unit**, either Goblin or Elf, has `3` **attack power** and starts with `200` **hit
    points**.

    For example, suppose the only Elf is about to attack:

               HP:            HP:
        G....  9       G....  9
        ..G..  4       ..G..  4
        ..EG.  2  -->  ..E..
        ..G..  2       ..G..  2
        ...G.  1       ...G.  1

    The "HP" column shows the hit points of the Goblin to the left in the corresponding row. The Elf
    is in range of three targets: the Goblin above it (with `4` hit points), the Goblin to its right
    (with `2` hit points), and the Goblin below it (also with `2` hit points). Because three targets
    are in range, the ones with the lowest hit points are selected: the two Goblins with `2` hit
    points each (one to the right of the Elf and one below the Elf). Of those, the Goblin first in
    reading order (the one to the right of the Elf) is selected. The selected Goblin's hit points
    (`2`) are reduced by the Elf's attack power (`3`), reducing its hit points to `-1`, killing it.

    After attacking, the unit's turn ends. Regardless of how the unit's turn ends, the next unit in
    the round takes its turn. If all units have taken turns in this round, the round ends, and a new
    round begins.

    ## Combat

    The Elves look quite outnumbered. You need to determine the **outcome** of the battle: the
    **number of full rounds that were completed** (not counting the round in which combat ends)
    multiplied by **the sum of the hit points of all remaining units** at the moment combat ends.
    (Combat only ends when a unit finds no targets during its turn.)

    Below is an entire sample combat. Next to each map, each row's units' hit points are listed from
    left to right.

        >>> example_combat = Battle.from_file(data_path(__file__, 'example-0.txt'))
        >>> print(example_combat)
        Initially:
        #######
        #.G...#   G1(200)
        #...EG#   E1(200), G2(200)
        #.#.#G#   G3(200)
        #..G#E#   G4(200), E2(200)
        #.....#
        #######
        >>> example_combat.do_round()
        >>> print(example_combat)
        After 1 round:
        #######
        #..G..#   G1(200)
        #...EG#   E1(197), G2(197)
        #.#G#G#   G4(200), G3(197)
        #...#E#   E2(197)
        #.....#
        #######
        >>> example_combat.do_round()
        >>> print(example_combat)
        After 2 rounds:
        #######
        #...G.#   G1(200)
        #..GEG#   G4(200), E1(188), G2(194)
        #.#.#G#   G3(194)
        #...#E#   E2(194)
        #.....#
        #######

    Combat ensues ...

        >>> while example_combat.round < 23:
        ...     example_combat.do_round()

    Eventually, the top Elf dies:

        >>> print(example_combat)
        After 23 rounds:
        #######
        #...G.#   G1(200)
        #..G.G#   G4(200), G2(131)
        #.#.#G#   G3(131)
        #...#E#   E2(131)
        #.....#
        #######
        >>> example_combat.do_round()
        >>> print(example_combat)
        After 24 rounds:
        #######
        #..G..#   G1(200)
        #...G.#   G2(131)
        #.#G#G#   G4(200), G3(128)
        #...#E#   E2(128)
        #.....#
        #######
        >>> example_combat.do_round()
        >>> print(example_combat)
        After 25 rounds:
        #######
        #.G...#   G1(200)
        #..G..#   G2(131)
        #.#.#G#   G3(125)
        #..G#E#   G4(200), E2(125)
        #.....#
        #######
        >>> example_combat.do_round()
        >>> print(example_combat)
        After 26 rounds:
        #######
        #G....#   G1(200)
        #.G...#   G2(131)
        #.#.#G#   G3(122)
        #...#E#   E2(122)
        #..G..#   G4(200)
        #######
        >>> example_combat.do_round()
        >>> print(example_combat)
        After 27 rounds:
        #######
        #G....#   G1(200)
        #.G...#   G2(131)
        #.#.#G#   G3(119)
        #...#E#   E2(119)
        #...G.#   G4(200)
        #######
        >>> example_combat.do_round()
        >>> print(example_combat)
        After 28 rounds:
        #######
        #G....#   G1(200)
        #.G...#   G2(131)
        #.#.#G#   G3(116)
        #...#E#   E2(113)
        #....G#   G4(200)
        #######

    More combat ensues ...

        >>> while example_combat.round < 47:
        ...     _ = example_combat.do_round()

    Eventually, the bottom Elf dies:

        >>> print(example_combat)
        After 47 rounds:
        #######
        #G....#   G1(200)
        #.G...#   G2(131)
        #.#.#G#   G3(59)
        #...#.#
        #....G#   G4(200)
        #######

    Before the 48th round can finish, the top-left Goblin finds that there are no targets remaining,
    and so combat ends.

        >>> example_combat.winning_team
        Team(name='Goblins', code='G', attack=3, hp=200)

    So, the number of full rounds that were completed is **`47`**, and the sum of the hit points of
    all remaining units is `200+131+59+200 = **590**`:

        >>> sum(u.hp for u in example_combat.active_units())
        590

    From these, the outcome of the battle is:

        >>> 47 * 590
        27730

    Here are a few example summarized combats:

        >>> Battle.from_file(data_path(__file__, 'example-1.txt')).finish()
        #######       #######
        #G..#E#       #...#E#   E(200)
        #E#E.E#       #E#...#   E(197)
        #G.##.#  -->  #.E##.#   E(185)
        #...#E#       #E..#E#   E(200), E(200)
        #...E.#       #.....#
        #######       #######
        <BLANKLINE>
        Combat ends after 37 full rounds
        Elves win with 982 total hit points left
        Outcome: 37 * 982 = 36334

        >>> Battle.from_file(data_path(__file__, 'example-2.txt')).finish()
        #######       #######
        #E..EG#       #.E.E.#   E(164), E(197)
        #.#G.E#       #.#E..#   E(200)
        #E.##E#  -->  #E.##.#   E(98)
        #G..#.#       #.E.#.#   E(200)
        #..E#.#       #...#.#
        #######       #######
        <BLANKLINE>
        Combat ends after 46 full rounds
        Elves win with 859 total hit points left
        Outcome: 46 * 859 = 39514

        >>> Battle.from_file(data_path(__file__, 'example-3.txt')).finish()
        #######       #######
        #E.G#.#       #G.G#.#   G(200), G(98)
        #.#G..#       #.#G..#   G(200)
        #G.#.G#  -->  #..#..#
        #G..#.#       #...#G#   G(95)
        #...E.#       #...G.#   G(200)
        #######       #######
        <BLANKLINE>
        Combat ends after 35 full rounds
        Goblins win with 793 total hit points left
        Outcome: 35 * 793 = 27755

        >>> Battle.from_file(data_path(__file__, 'example-4.txt')).finish()
        #######       #######
        #.E...#       #.....#
        #.#..G#       #.#G..#   G(200)
        #.###.#  -->  #.###.#
        #E#G#G#       #.#.#.#
        #...#G#       #G.G#G#   G(98), G(38), G(200)
        #######       #######
        <BLANKLINE>
        Combat ends after 54 full rounds
        Goblins win with 536 total hit points left
        Outcome: 54 * 536 = 28944

        >>> Battle.from_file(data_path(__file__, 'example-5.txt')).finish()
        #########       #########
        #G......#       #.G.....#   G(137)
        #.E.#...#       #G.G#...#   G(200), G(200)
        #..##..G#       #.G##...#   G(200)
        #...##..#  -->  #...##..#
        #...#...#       #.G.#...#   G(200)
        #.G...G.#       #.......#
        #.....G.#       #.......#
        #########       #########
        <BLANKLINE>
        Combat ends after 20 full rounds
        Goblins win with 937 total hit points left
        Outcome: 20 * 937 = 18740

    **What is the outcome** of the combat described in your puzzle input?

        >>> part_1(Battle.from_file(data_path(__file__, 'example-5.txt')))
        part 1:
            Combat ends after 20 full rounds
            Goblins win with 937 total hit points left
            Outcome: 20 * 937 = 18740
        18740
    """

    battle = battle.copy()
    print("part 1:")
    battle.finish(print_map=False, result_padding=4)
    return some(battle.final_score())


def part_2(battle: 'Battle') -> int:
    """
    According to your calculations, the Elves are going to lose badly. Surely, you won't mess up the
    timeline too much if you give them just a little advanced technology, right?

    You need to make sure the Elves not only **win**, but also suffer **no losses**: even the death
    of a single Elf is unacceptable.

    However, you can't go too far: larger changes will be more likely to permanently alter
    spacetime.

    So, you need to **find the outcome** of the battle in which the Elves have **the lowest integer
    attack power** (at least `4`) that allows them to **win without a single death**. The Goblins
    always have an attack power of `3`.

    In the first summarized example above, the lowest attack power the Elves need to win without
    losses is `15`:

        >>> Battle.from_file(
        ...     data_path(__file__, 'example-0.txt'), teams=default_teams(elves_attack=15)
        ... ).finish()
        #######       #######
        #.G...#       #..E..#   E(158)
        #...EG#       #...E.#   E(14)
        #.#.#G#  -->  #.#.#.#
        #..G#E#       #...#.#
        #.....#       #.....#
        #######       #######
        <BLANKLINE>
        Combat ends after 29 full rounds
        Elves win with 172 total hit points left
        Outcome: 29 * 172 = 4988

    Because with attack power 14, the elves would win, but with a single loss:

        >>> Battle.from_file(
        ...     data_path(__file__, 'example-0.txt'), teams=default_teams(elves_attack=14)
        ... ).finish()
        #######       #######
        #.G...#       #..E..#   E(152)
        #...EG#       #.....#
        #.#.#G#  -->  #.#.#.#
        #..G#E#       #...#.#
        #.....#       #.....#
        #######       #######
        <BLANKLINE>
        Combat ends after 33 full rounds
        Elves win with 152 total hit points left
        Outcome: 33 * 152 = 5016

    In the second example above, the Elves need only 4 attack power:

        >>> example_2 = Battle.from_file(data_path(__file__, 'example-2.txt'))
        >>> lowest_elf_attack_without_losses(example_2)
        4
        >>> example_2.with_attack('E', 4).finish()
        #######       #######
        #E..EG#       #.E.E.#   E(200), E(23)
        #.#G.E#       #.#E..#   E(200)
        #E.##E#  -->  #E.##E#   E(125), E(200)
        #G..#.#       #.E.#.#   E(200)
        #..E#.#       #...#.#
        #######       #######
        <BLANKLINE>
        Combat ends after 33 full rounds
        Elves win with 948 total hit points left
        Outcome: 33 * 948 = 31284

    In the third example above, the Elves need 15 attack power:

        >>> example_3 = Battle.from_file(data_path(__file__, 'example-3.txt'))
        >>> lowest_elf_attack_without_losses(example_3)
        15
        >>> example_3.with_attack('E', 15).finish()
        #######       #######
        #E.G#.#       #.E.#.#   E(8)
        #.#G..#       #.#E..#   E(86)
        #G.#.G#  -->  #..#..#
        #G..#.#       #...#.#
        #...E.#       #.....#
        #######       #######
        <BLANKLINE>
        Combat ends after 37 full rounds
        Elves win with 94 total hit points left
        Outcome: 37 * 94 = 3478

    In the fourth example above, the Elves need 12 attack power:

        >>> example_4 = Battle.from_file(data_path(__file__, 'example-4.txt'))
        >>> lowest_elf_attack_without_losses(example_4)
        12
        >>> example_4.with_attack('E', 12).finish()
        #######       #######
        #.E...#       #...E.#   E(14)
        #.#..G#       #.#..E#   E(152)
        #.###.#  -->  #.###.#
        #E#G#G#       #.#.#.#
        #...#G#       #...#.#
        #######       #######
        <BLANKLINE>
        Combat ends after 39 full rounds
        Elves win with 166 total hit points left
        Outcome: 39 * 166 = 6474

    In the last example above, the lone Elf needs 34 attack power:

        >>> example_5 = Battle.from_file(data_path(__file__, 'example-5.txt'))
        >>> lowest_elf_attack_without_losses(example_5)
        34
        >>> example_5.with_attack('E', 34).finish()
        #########       #########
        #G......#       #.......#
        #.E.#...#       #.E.#...#   E(38)
        #..##..G#       #..##...#
        #...##..#  -->  #...##..#
        #...#...#       #...#...#
        #.G...G.#       #.......#
        #.....G.#       #.......#
        #########       #########
        <BLANKLINE>
        Combat ends after 30 full rounds
        Elves win with 38 total hit points left
        Outcome: 30 * 38 = 1140

    After increasing the Elves' attack power until it is just barely enough for them to win without
    any Elves dying, **what is the outcome** of the combat described in your puzzle input?

        >>> part_2(example_5)
        part 2: increasing the Elves' attack to 34 saves them all:
            Combat ends after 30 full rounds
            Elves win with 38 total hit points left
            Outcome: 30 * 38 = 1140
        1140
    """

    elves_attack = lowest_elf_attack_without_losses(battle)
    print(f"part 2: increasing the Elves' attack to {elves_attack} saves them all:")
    modified_battle = battle.with_attack('E', elves_attack)
    modified_battle.finish(print_map=False, result_padding=4)
    return modified_battle.final_score()


Pos = tuple[int, int]
Path = list[Pos]


class Team:
    def __init__(self, name: str, *, code: str = None, attack: int, hp: int):
        assert len(name) > 0
        assert code is None or len(code) == 1
        assert attack > 0
        assert hp > 0

        self.name = name
        self.code = code or name[0]
        self.attack = attack
        self.hp = hp

    def __str__(self) -> str:
        return self.name

    def __repr__(self):
        return (
            f'{type(self).__name__}('
            f'name={self.name!r}, '
            f'code={self.code!r}, '
            f'attack={self.attack!r}, '
            f'hp={self.hp!r})'
        )


def default_teams(elves_attack: int = 3) -> Iterable[Team]:
    yield Team("Elves", attack=elves_attack, hp=200)
    yield Team("Goblins", attack=3, hp=200)


class Unit:
    def __init__(self, code: str, num: int, *, pos: Pos, hp: int):
        assert len(code) == 1
        assert num >= 0
        assert hp > 0

        self.code = code
        self.num = num
        self.pos = pos
        self.hp = hp

    def __repr__(self) -> str:
        return (
            f'{type(self).__name__}('
            f'{self.code!r}, {self.num!r}, '
            f'pos={self.pos!r}, '
            f'hp={self.hp!r})'
        )

    def copy(self) -> Self:
        return type(self)(self.code, self.num, pos=self.pos, hp=self.hp)

    def is_alive(self) -> bool:
        return self.hp > 0

    def __str__(self) -> str:
        return format(self)

    def __format__(self, format_spec: str) -> str:
        include_number = ('!num' != format_spec)
        return f"{self.code}{self.num if include_number else ''}({self.hp})"


class Battle:
    def __init__(
        self, *,
        width: int,
        height: int,
        teams: Iterable[Team],
        floors: Iterable[Pos],
        units: Iterable[Unit]
    ):
        assert width > 0
        assert height > 0

        self.width = width
        self.height = height
        self.teams: dict[str, Team] = {team.code: team for team in teams}
        self.floors: set[Pos] = set(floors)
        self.units_by_pos: dict[Pos, Unit] = {unit.pos: unit for unit in units}

        self.round = 0
        self.full_rounds_completed = 0
        self.winning_team: Optional[Team] = None
        self.teams_unit_count = Counter(unit.code for unit in self.units_by_pos.values())

        assert len(self.teams) >= 2

        for x, y in self.floors:
            assert 0 <= x < self.width
            assert 0 <= y < self.height

        for unit_pos, unit in self.units_by_pos.items():
            assert unit_pos in self.floors
            assert unit_pos == unit.pos
            assert unit.code in self.teams

        for team in self.teams.values():
            assert self.teams_unit_count[team.code] > 0

    def copy(self) -> Self:
        return type(self)(
            width=self.width,
            height=self.height,
            teams=self.teams.values(),
            floors=self.floors,
            units=(unit.copy() for unit in self.units_by_pos.values())
        )

    def with_attack(self, team_code: str, new_attack: int) -> Self:
        copy = self.copy()
        old_team = copy.teams[team_code]
        copy.teams[team_code] = Team(
            name=old_team.name,
            code=team_code,
            attack=new_attack,
            hp=old_team.hp
        )
        return copy

    def final_score(self) -> int:
        assert self.winning_team is not None
        return self.full_rounds_completed * sum(u.hp for u in self.active_units())

    def active_units(self) -> Iterable[Unit]:
        return sorted(self.units_by_pos.values(), key=lambda u: ro(u.pos))

    def neighbors(
        self,
        pos: Pos, *,
        include_walls: bool = False,
        include_units: bool = False
    ) -> Iterable[Pos]:
        x, y = pos
        for n_x, n_y in [(x, y-1), (x-1, y), (x+1, y), (x, y+1)]:
            if not include_walls and (n_x, n_y) not in self.floors:
                continue
            if not include_units and (n_x, n_y) in self.units_by_pos:
                continue
            yield n_x, n_y

    def do_round(self) -> Optional[Team]:
        assert self.winning_team is None

        try:
            round_units_order = self.active_units()
            for unit in round_units_order:
                if not unit.is_alive():
                    continue
                if self.winning_team:
                    return self.winning_team
                self.do_unit_movement(unit)
                self.do_unit_combat(unit)
            else:
                self.full_rounds_completed += 1
                return self.winning_team
        finally:
            self.round += 1

    def do_unit_movement(self, unit: Unit) -> Optional[Pos]:
        if self.has_enemy_in_range(unit):
            # already in range to an enemy, no need to move
            return None

        path = self.path_to_closest_enemy(unit)
        if not path:
            # no path to an enemy found
            return None

        # move!
        target_pos = path[0]
        self.move_unit(unit, target_pos)
        return target_pos

    def do_unit_combat(self, unit: Unit) -> Optional[Unit]:
        target = self.weakest_enemy_in_range(unit)
        if not target:
            # no target in range
            return None

        # attack!
        self.attack_unit(unit, target)
        return target

    def enemies_in_range(self, unit: Unit) -> Iterable[Unit]:
        return (
            self.units_by_pos[npos]
            for npos in self.neighbors(unit.pos, include_units=True)
            if npos in self.units_by_pos
            and self.units_by_pos[npos].code != unit.code
        )

    def has_enemy_in_range(self, unit: Unit) -> bool:
        return any(self.enemies_in_range(unit))

    def weakest_enemy_in_range(self, unit: Unit) -> Optional[Unit]:
        return min(
            self.enemies_in_range(unit),
            key=lambda enemy: (enemy.hp, ro(enemy.pos)),  # type: ignore
            default=None
        )

    def path_to_closest_enemy(self, unit: Unit) -> Optional[Path]:
        # TODO: common.graph.shortest_path
        path_to: dict[Pos, Path] = {unit.pos: []}
        layer: list[Pos] = [unit.pos]
        seen: set[Pos] = {unit.pos}

        while layer:
            next_layer: set[Pos] = set()
            for pos in layer:
                for npos in self.neighbors(pos, include_units=True):
                    if npos in seen:
                        continue
                    seen.add(npos)
                    if npos in self.units_by_pos:
                        # unit found! return path to it if enemy
                        target_unit = self.units_by_pos[npos]
                        if target_unit.code != unit.code:
                            return path_to[pos] + [npos]
                    else:
                        # floor only
                        path_to[npos] = path_to[pos] + [npos]
                        next_layer.add(npos)
            layer = sorted(next_layer, key=ro)
        else:
            # no enemy found
            return None

    def move_unit(self, unit: Unit, target_pos: Pos):
        assert unit.is_alive()
        assert self.units_by_pos[unit.pos] is unit
        assert unit.pos != target_pos
        assert target_pos in self.neighbors(unit.pos, include_units=True)

        del self.units_by_pos[unit.pos]
        unit.pos = target_pos
        self.units_by_pos[unit.pos] = unit

    def attack_unit(self, attacker: Unit, target: Unit):
        assert attacker.is_alive()
        assert target.is_alive()
        assert attacker.code != target.code

        target.hp -= self.teams[attacker.code].attack

        if not target.is_alive():
            self.kill_unit(target)

    def kill_unit(self, unit: Unit) -> Optional[Team]:
        assert not unit.is_alive()
        del self.units_by_pos[unit.pos]
        self.teams_unit_count[unit.code] -= 1
        active_teams = [t for t in self.teams.values() if self.teams_unit_count[t.code] > 0]
        assert len(active_teams) >= 1
        if len(active_teams) == 1:
            self.winning_team = active_teams[0]
            return self.winning_team
        else:
            return None

    def __str__(self) -> str:
        return format(self)

    def __format__(self, format_spec: str) -> str:
        options = set(format_spec.split(":"))

        lines = self.drawn_lines(
            show_header='!header' not in options,
            show_unit_status='!status' not in options,
            show_unit_numbers='!unitnums' not in options,
        )

        return "\n".join(lines)

    def drawn_lines(
        self,
        *,
        show_header: bool = True,
        show_unit_status: bool = True,
        show_unit_numbers: bool = True
    ) -> Iterable[str]:

        if show_header:
            if self.round == 0:
                yield "Initially:"
            elif self.round == 1:
                yield "After 1 round:"
            else:
                yield f"After {self.round} rounds:"

        def char(pos: Pos) -> str:
            if pos in self.units_by_pos:
                return self.units_by_pos[pos].code
            elif pos in self.floors:
                return "."
            else:
                return "#"

        for y in range(self.height):
            # map
            map_line = "".join(char((x, y)) for x in range(self.width))

            # units status
            if show_unit_status:
                y_units = (
                    self.units_by_pos[(x, y)]
                    for x in range(self.width)
                    if (x, y) in self.units_by_pos
                )
                units_fmt = '!num' if not show_unit_numbers else ''
                units_line = ", ".join(format(unit, units_fmt) for unit in y_units)
            else:
                units_line = ""

            yield f"{map_line}   {units_line}".rstrip()

    @classmethod
    def from_file(cls, fn: str, teams: Iterable[Team] = tuple(default_teams())) -> Self:
        return cls.from_lines(open(fn), teams)

    @classmethod
    def from_lines(cls, lines: Iterable[str], teams: Iterable[Team]) -> Self:
        teams_dict: dict[str, Team] = {team.code: team for team in teams}
        team_unit_count: dict[str, int] = {c: 0 for c in teams_dict}
        floors: list[Pos] = []
        units: list[Unit] = []

        for y, line in enumerate(lines):
            for x, c in enumerate(line.strip()):
                if c == '.':
                    floors.append((x, y))
                elif c == '#':
                    pass
                elif c in teams_dict:
                    floors.append((x, y))
                    team = teams_dict[c]
                    num = team_unit_count[c] = team_unit_count[c] + 1
                    units.append(Unit(code=c, num=num, pos=(x, y), hp=team.hp))
                else:
                    raise KeyError(c)

        return cls(
            width=max(x for x, _ in floors) + 2,
            height=max(y for _, y in floors) + 2,
            teams=teams_dict.values(),
            floors=floors,
            units=units
        )

    def finish(
        self,
        *,
        print_map: bool = True,
        print_result: bool = True,
        result_padding: int = 0
    ) -> None:
        lines_initial = list(self.drawn_lines(show_header=False, show_unit_status=False))

        while self.winning_team is None:
            self.do_round()

        if print_map:
            lines_divider = [
                "  -->  " if y == self.height // 2 else "       "
                for y in range(self.height)
            ]
            lines_final = list(self.drawn_lines(show_header=False, show_unit_numbers=False))

            for lines in zip(lines_initial, lines_divider, lines_final):
                print("".join(lines))

            print()

        if print_result:
            padding = " " * result_padding
            rounds = self.full_rounds_completed
            winning_team = some(self.winning_team).name
            winning_hps = sum(u.hp for u in self.active_units())
            print(padding + f"Combat ends after {rounds} full rounds")
            print(padding + f"{winning_team} win with {winning_hps} total hit points left")
            print(padding + f"Outcome: {rounds} * {winning_hps} = {self.final_score()}")


def lowest_elf_attack_without_losses(battle: Battle) -> int:
    for attack_power in count(4):
        modified_battle = battle.with_attack('E', attack_power)
        initial_elves_count = modified_battle.teams_unit_count['E']
        while True:
            if modified_battle.teams_unit_count['E'] < initial_elves_count:
                # an elf died -> this attack power is not enough
                break

            elif modified_battle.winning_team:
                assert modified_battle.winning_team.code == 'E'
                # elves won!
                return attack_power

            else:
                # battle still on with all elves standing ...
                modified_battle.do_round()

    # unreachable
    assert False


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    battle = Battle.from_file(input_path)
    result_1 = part_1(battle)
    result_2 = part_2(battle)
    return result_1, result_2


if __name__ == '__main__':
    main()
