from collections import Counter
from itertools import count
from typing import Dict
from typing import Iterable
from typing import Optional
from typing import Set

from utils import ro

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

    def __repr__(self):
        return (
            f'{type(self).__name__}('
            f'name={self.name!r}, '
            f'code={self.code!r}, '
            f'attack={self.attack!r}, '
            f'hp={self.hp!r})'
        )


def default_teams(elves_attack: int = 3) -> list[Team]:
    return [
        Team("Elves", attack=elves_attack, hp=200),
        Team("Goblins", attack=3, hp=200)
    ]


class Unit:
    def __init__(self, code: str, num: int, *, pos: Pos, attack: int, hp: int):
        assert len(code) == 1
        assert num >= 0
        assert attack > 0
        assert hp > 0

        self.code = code
        self.num = num
        self.pos = pos
        self.attack = attack
        self.hp = hp

    def is_alive(self) -> bool:
        return self.hp > 0

    def __repr__(self):
        return (
            f'{type(self).__name__}('
            f'{self.code!r}, {self.num!r}, '
            f'pos={self.pos!r}, '
            f'attack={self.attack!r}, '
            f'hp={self.hp!r})'
        )

    def __str__(self):
        return f"{self.code}{self.num}({self.hp})"


class Game:
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
        self.teams: Dict[str, Team] = {team.code: team for team in teams}
        self.floors: Set[Pos] = set(floors)
        self.units_by_pos: Dict[Pos, Unit] = {unit.pos: unit for unit in units}

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

    def final_score(self) -> Optional[int]:
        if self.winning_team:
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
        for nx, ny in [(x, y-1), (x-1, y), (x+1, y), (x, y+1)]:
            if not include_walls and (nx, ny) not in self.floors:
                continue
            if not include_units and (nx, ny) in self.units_by_pos:
                continue
            yield nx, ny

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
                if self.winning_team:
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
            key=lambda t: (t.hp, ro(t.pos)),
            default=None
        )

    def path_to_closest_enemy(self, unit: Unit) -> Optional[Path]:
        path_to: Dict[Pos, Path] = {unit.pos: []}
        layer: list[Pos] = [unit.pos]
        seen: Set[Pos] = {unit.pos}

        while layer:
            next_layer: Set[Pos] = set()
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

        target.hp -= attacker.attack

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

    def draw(self):
        if self.round == 0:
            print("Initially:")
        elif self.round == 1:
            print("After 1 round:")
        else:
            print(f"After {self.round} rounds:")

        def t(pos: Pos) -> str:
            if pos in self.units_by_pos:
                return self.units_by_pos[pos].code
            elif pos in self.floors:
                return '.'
            else:
                return '#'

        for y in range(self.height):
            # map
            print(''.join(t((x, y)) for x in range(self.width)), end='')
            # units status
            y_units = (
                self.units_by_pos[(x, y)]
                for x in range(self.width)
                if (x, y) in self.units_by_pos
            )
            units_line = ', '.join(str(unit) for unit in y_units)
            if units_line:
                print('   ' + units_line)
            else:
                print()

        print()

    @classmethod
    def load(cls, fn: str, teams: Iterable[Team]) -> 'Game':
        teams: Dict[str, Team] = {team.code: team for team in teams}
        team_unit_count: Dict[str, int] = {c: 0 for c in teams}
        floors: list[Pos] = []
        units: list[Unit] = []

        for y, line in enumerate(open(fn)):
            for x, c in enumerate(line.strip()):
                if c == '.':
                    floors.append((x, y))
                elif c == '#':
                    pass
                elif c in teams:
                    floors.append((x, y))
                    team = teams[c]
                    num = team_unit_count[c] = team_unit_count[c] + 1
                    units.append(
                        Unit(code=c, num=num, pos=(x, y), attack=team.attack, hp=team.hp)
                    )
                else:
                    raise KeyError(c)

        return cls(
            width=max(x for x, _ in floors) + 2,
            height=max(y for _, y in floors) + 2,
            teams=teams.values(),
            floors=floors,
            units=units
        )


def test_movement_single_unit():
    game = Game.load("data/15-test-movement.txt", default_teams())
    game.draw()

    elves = [unit for unit in game.active_units() if unit.code == 'E']
    assert len(elves) == 1
    elf = elves[0]
    assert elf.pos == (4, 4)
    game.do_unit_movement(elf)
    assert elf.pos == (4, 3)
    game.do_unit_movement(elf)
    assert elf.pos == (4, 2)
    game.do_unit_movement(elf)
    assert elf.pos == (4, 2)
    game.draw()


def test_movement_all_units():
    game = Game.load("data/15-test-movement.txt", default_teams())
    game.draw()
    assert set(game.units_by_pos) == {
        (1, 1), (4, 1), (7, 1),
        (1, 4), (4, 4), (7, 4),
        (1, 7), (4, 7), (7, 7)
    }

    game.do_round()
    game.draw()
    assert set(game.units_by_pos) == {
        (2, 1), (4, 2), (6, 1),
        (2, 4), (4, 3), (7, 3),
        (1, 6), (4, 6), (7, 6)
    }

    game.do_round()
    game.draw()
    assert set(game.units_by_pos) == {
        (3, 1), (4, 2), (5, 1),
        (2, 3), (4, 3), (6, 3),
        (1, 5), (4, 5), (7, 5)
    }

    game.do_round()
    game.draw()
    assert set(game.units_by_pos) == {
        (3, 2), (4, 2), (5, 2),
        (3, 3), (4, 3), (5, 3),
        (1, 4), (4, 4), (7, 5)
    }
    last_positions = set(game.units_by_pos)

    game.do_round()
    # no change since last round
    assert set(game.units_by_pos) == last_positions


def test_combat():
    game = Game.load("data/15-test-combat.txt", default_teams())
    elves = [unit for unit in game.active_units() if unit.code == 'E']
    assert [e.num for e in elves] == [1, 2]
    goblins = [unit for unit in game.active_units() if unit.code == 'G']
    assert [g.num for g in goblins] == [1, 2, 3, 4]

    # initially
    game.draw()
    assert game.round == 0
    assert game.teams_unit_count == {'E': 2, 'G': 4}
    assert game.winning_team is None
    assert [e.pos for e in elves] == [(4, 2), (5, 4)]
    assert [e.hp for e in elves] == [200, 200]
    assert [g.pos for g in goblins] == [(2, 1), (5, 2), (5, 3), (3, 4)]
    assert [g.hp for g in goblins] == [200, 200, 200, 200]

    # after 1 round:
    game.do_round()
    game.draw()
    assert game.round == 1
    assert game.full_rounds_completed == 1
    assert [e.pos for e in elves] == [(4, 2), (5, 4)]
    assert [e.hp for e in elves] == [197, 197]
    assert [g.pos for g in goblins] == [(3, 1), (5, 2), (5, 3), (3, 3)]
    assert [g.hp for g in goblins] == [200, 197, 197, 200]

    # after 2 rounds:
    game.do_round()
    game.draw()
    assert game.round == 2
    assert [e.pos for e in elves] == [(4, 2), (5, 4)]
    assert [e.hp for e in elves] == [188, 194]
    assert [g.pos for g in goblins] == [(4, 1), (5, 2), (5, 3), (3, 2)]
    assert [g.hp for g in goblins] == [200, 194, 194, 200]

    # after 23 rounds:
    while game.round < 23:
        game.do_round()
    game.draw()
    assert game.round == 23
    assert game.full_rounds_completed == 23
    assert game.teams_unit_count == {'E': 1, 'G': 4}
    assert game.winning_team is None
    assert [e.pos for e in elves] == [(4, 2), (5, 4)]
    assert [e.hp for e in elves] == [-1, 131]
    assert [g.pos for g in goblins] == [(4, 1), (5, 2), (5, 3), (3, 2)]
    assert [g.hp for g in goblins] == [200, 131, 131, 200]

    # after 24 rounds:
    game.do_round()
    game.draw()
    assert game.round == 24
    elf = elves[1]
    assert elf.pos == (5, 4)
    assert elf.hp == 128
    assert [g.pos for g in goblins] == [(3, 1), (4, 2), (5, 3), (3, 3)]
    assert [g.hp for g in goblins] == [200, 131, 128, 200]

    # after 25 rounds:
    game.do_round()
    game.draw()
    assert game.round == 25
    assert elf.pos == (5, 4)
    assert elf.hp == 125
    assert [g.pos for g in goblins] == [(2, 1), (3, 2), (5, 3), (3, 4)]
    assert [g.hp for g in goblins] == [200, 131, 125, 200]

    # after 26 rounds:
    game.do_round()
    game.draw()
    assert game.round == 26
    assert elf.pos == (5, 4)
    assert elf.hp == 122
    assert [g.pos for g in goblins] == [(1, 1), (2, 2), (5, 3), (3, 5)]
    assert [g.hp for g in goblins] == [200, 131, 122, 200]

    # after 27 rounds:
    game.do_round()
    game.draw()
    assert game.round == 27
    assert elf.pos == (5, 4)
    assert elf.hp == 119
    assert [g.pos for g in goblins] == [(1, 1), (2, 2), (5, 3), (4, 5)]
    assert [g.hp for g in goblins] == [200, 131, 119, 200]

    # after 28 rounds:
    game.do_round()
    game.draw()
    assert game.round == 28
    assert elf.pos == (5, 4)
    assert elf.hp == 113
    assert [g.pos for g in goblins] == [(1, 1), (2, 2), (5, 3), (5, 5)]
    assert [g.hp for g in goblins] == [200, 131, 116, 200]

    # after 47 rounds (46 full):
    while game.winning_team is None:
        game.do_round()
    game.draw()
    assert game.round == 47
    assert game.full_rounds_completed == 46
    assert game.teams_unit_count == {'E': 0, 'G': 4}
    assert game.winning_team.name == "Goblins"
    assert [g.hp for g in goblins] == [200, 131, 59, 200]


def test_result_1():
    game = Game.load("data/15-test-result-1.txt", default_teams())
    game.draw()
    assert game.teams_unit_count == {'E': 6, 'G': 2}

    while game.winning_team is None:
        game.do_round()

    game.draw()
    assert game.full_rounds_completed == 37
    assert game.teams_unit_count == {'E': 5, 'G': 0}
    assert game.winning_team.name == "Elves"
    assert [e.pos for e in game.active_units()] == [(5, 1), (1, 2), (2, 3), (1, 4), (5, 4)]
    assert [e.hp for e in game.active_units()] == [200, 197, 185, 200, 200]
    assert game.final_score() == 36334


def test_result_2():
    game = Game.load("data/15-test-result-2.txt", default_teams())
    game.draw()
    assert game.teams_unit_count == {'E': 6, 'G': 3}

    while game.winning_team is None:
        game.do_round()

    game.draw()
    assert game.full_rounds_completed == 46
    assert game.teams_unit_count == {'E': 5, 'G': 0}
    assert game.winning_team.name == "Elves"
    assert [e.pos for e in game.active_units()] == [(2, 1), (4, 1), (3, 2), (1, 3), (2, 4)]
    assert [e.hp for e in game.active_units()] == [164, 197, 200, 98, 200]
    assert game.final_score() == 39514


def test_result_3():
    game = Game.load("data/15-test-result-3.txt", default_teams())
    game.draw()
    assert game.teams_unit_count == {'E': 2, 'G': 5}

    while game.winning_team is None:
        game.do_round()

    game.draw()
    assert game.full_rounds_completed == 35
    assert game.teams_unit_count == {'E': 0, 'G': 5}
    assert game.winning_team.name == "Goblins"
    assert [g.pos for g in game.active_units()] == [(1, 1), (3, 1), (3, 2), (5, 4), (4, 5)]
    assert [g.hp for g in game.active_units()] == [200, 98, 200, 95, 200]
    assert game.final_score() == 27755


def test_result_4():
    game = Game.load("data/15-test-result-4.txt", default_teams())
    game.draw()
    assert game.teams_unit_count == {'E': 2, 'G': 4}

    while game.winning_team is None:
        game.do_round()

    game.draw()
    assert game.full_rounds_completed == 54
    assert game.teams_unit_count == {'E': 0, 'G': 4}
    assert game.winning_team.name == "Goblins"
    assert [g.pos for g in game.active_units()] == [(3, 2), (1, 5), (3, 5), (5, 5)]
    assert [g.hp for g in game.active_units()] == [200, 98, 38, 200]
    assert game.final_score() == 28944


def test_result_5():
    game = Game.load("data/15-test-result-5.txt", default_teams())
    game.draw()
    assert game.teams_unit_count == {'E': 1, 'G': 5}

    while game.winning_team is None:
        game.do_round()

    game.draw()
    assert game.full_rounds_completed == 20
    assert game.teams_unit_count == {'E': 0, 'G': 5}
    assert game.winning_team.name == "Goblins"
    assert [g.pos for g in game.active_units()] == [(2, 1), (1, 2), (3, 2), (2, 3), (2, 5)]
    assert [g.hp for g in game.active_units()] == [137, 200, 200, 200, 200]
    assert game.final_score() == 18740


def part_1(fn: str) -> int:
    game = Game.load(fn, default_teams())
    game.draw()
    while game.winning_team is None:
        game.do_round()

    game.draw()
    winning_hps = sum(u.hp for u in game.active_units())
    print(f"Combat ends after {game.full_rounds_completed} full rounds")
    print(f"{game.winning_team.name} win with {winning_hps} total hit points left")
    print(f"part 1: Outcome is {game.final_score()}")
    print()
    return game.final_score()


def part_2(fn: str) -> int:
    for elves_attack in count(4):
        game = Game.load(fn, default_teams(elves_attack=elves_attack))
        initial_elves_count = game.teams_unit_count['E']

        while game.winning_team is None:
            game.do_round()

        e = game.teams_unit_count['E']
        g = game.teams_unit_count['G']
        print(f"attack={elves_attack} -> E: {e}, G: {g}")
        game.draw()

        if game.winning_team.name == "Elves" and e == initial_elves_count:
            winning_hps = sum(u.hp for u in game.active_units())
            print(f"Combat ends after {game.full_rounds_completed} full rounds")
            print(f"Elves win with no losses, {winning_hps} total hit points left")
            print(f"part 2: Outcome is {game.final_score()}")
            print()
            return game.final_score()


if __name__ == '__main__':
    fn_ = "data/15-input.txt"
    part_1(fn_)
    part_2(fn_)
