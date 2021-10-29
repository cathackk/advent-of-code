from abc import ABC
from abc import abstractmethod
from copy import copy
from typing import Dict
from typing import Iterable
from typing import List

from typing import NamedTuple
from typing import Optional

from utils import ilog


class Character(NamedTuple):
    hit_points: int
    damage: int = 0
    armor: int = 0
    mana: int = 0


class Spell(ABC):
    name = "Spell"
    cost = 0
    lasts = 0

    @abstractmethod
    def when_cast(self, battle: 'Battle'):
        pass

    def when_turn_starts(self, battle: 'Battle', timer: int) -> int:
        pass

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, Spell) and self.name == other.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'{type(self).__name__}()'


class SpellMagicMissile(Spell):
    name = "Missile"
    cost = 53
    damage = 4

    def when_cast(self, battle: 'Battle'):
        battle.boss_hp -= self.damage
        battle.log(f"Player casts {self.name}, dealing {self.damage} damage.")


class SpellDrain(Spell):
    name = "Drain"
    cost = 73
    damage = 2

    def when_cast(self, battle: 'Battle'):
        battle.boss_hp -= self.damage
        battle.player_hp += self.damage
        battle.log(
            f"Player casts {self.name}, "
            f"dealing {self.damage} damage, and healing {self.damage} hit points."
        )


class SpellShield(Spell):
    name = "Shield"
    cost = 113
    lasts = 6
    armor = 7

    def when_cast(self, battle: 'Battle'):
        battle.player_armor += self.armor
        battle.log(f"Player casts {self.name}, increasing armor by {self.armor}.")

    def when_turn_starts(self, battle: 'Battle', timer: int) -> int:
        timer -= 1
        battle.log(f"{self.name}'s timer is now {timer}.")
        if timer <= 0:
            battle.player_armor -= self.armor
            battle.log(f"{self.name} wears off, decreasing armor by {self.armor}.")
        return timer


class SpellPoison(Spell):
    name = "Poison"
    cost = 173
    lasts = 6
    damage = 3

    def when_cast(self, battle: 'Battle'):
        battle.log(f"Player casts {self.name}.")

    def when_turn_starts(self, battle: 'Battle', timer: int) -> int:
        battle.boss_hp -= self.damage
        timer -= 1
        battle.log(f"{self.name} deals {self.damage} damage; its timer is now {timer}.")
        if timer <= 0:
            battle.log(f"{self.name} wears off.")
        return timer


class SpellRecharge(Spell):
    name = "Recharge"
    cost = 229
    lasts = 5
    mana = 101

    def when_cast(self, battle: 'Battle'):
        battle.log(f"Player casts {self.name}.")

    def when_turn_starts(self, battle: 'Battle', timer: int) -> int:
        battle.player_mana += self.mana
        timer -= 1
        battle.log(f"{self.name} provides {self.mana} mana; its timer is now {timer}.")
        if timer <= 0:
            battle.log(f"{self.name} wears off.")
        return timer


spell_missile = SpellMagicMissile()
spell_drain = SpellDrain()
spell_shield = SpellShield()
spell_poison = SpellPoison()
spell_recharge = SpellRecharge()
spell_book: List[Spell] = [spell_missile, spell_drain, spell_shield, spell_poison, spell_recharge]


class BattleEnd(Exception):
    def __init__(self, player_wins: bool):
        super().__init__(f"{'Player' if player_wins else 'Boss'} wins!")
        self.player_wins = player_wins


class Battle:
    @classmethod
    def with_characters(
            cls, *,
            player: Character,
            boss: Character,
            hard: bool = False,
            logging: bool = False
    ):
        assert player.hit_points > 0
        assert player.damage == 0
        assert player.armor >= 0
        assert player.mana > 0
        assert boss.hit_points > 0
        assert boss.damage > 0
        assert boss.armor == 0
        assert boss.mana == 0

        return cls(
            player_hp=player.hit_points,
            player_armor=player.armor,
            player_mana=player.mana,
            boss_hp=boss.hit_points,
            boss_damage=boss.damage,
            active_spells=dict(),
            hard=hard,
            logging=logging
        )

    def __init__(
            self, *,
            player_hp: int,
            player_armor: int = 0,
            player_mana: int,
            boss_hp: int,
            boss_damage: int,
            active_spells: Dict[Spell, int] = None,
            hard: bool = False,
            logging: bool = False
    ):
        self.player_hp = player_hp
        self.player_armor = player_armor
        self.player_mana = player_mana
        self.boss_hp = boss_hp
        self.boss_damage = boss_damage
        self.active_spells = dict(active_spells) if active_spells else dict()
        self.hard = hard
        self.logging = logging

    def __copy__(self):
        return type(self)(
            player_hp=self.player_hp,
            player_armor=self.player_armor,
            player_mana=self.player_mana,
            boss_hp=self.boss_hp,
            boss_damage=self.boss_damage,
            active_spells=self.active_spells,
            hard=self.hard,
            logging=self.logging
        )

    def log(self, message: str = ""):
        if self.logging:
            print(message)

    def print_status(self, active: str) -> None:
        if self.logging:
            print(f"-- {active} turn --")
            print(
                f"- Player has "
                f"{self.player_hp} hit points, "
                f"{self.player_armor} armor, "
                f"{self.player_mana} mana"
            )
            print(f"- Boss has {self.boss_hp} hit points")

    def apply_handicap(self):
        if self.hard:
            self.player_hp -= 1
            self.log(f"Player loses 1 hit point because of hard difficulty.")
            if self.player_hp <= 0:
                self.log("... This kills the player, and the boss wins.")
                raise BattleEnd(player_wins=False)

    def apply_spell_effects(self):
        for spell, timer in self.active_spells.items():
            timer = spell.when_turn_starts(self, timer)
            self.active_spells[spell] = timer

        self.active_spells = {
            spell: timer
            for spell, timer in self.active_spells.items()
            if timer > 0
        }

        if self.boss_hp <= 0:
            self.log("... This kills the boss, and the player wins.")
            raise BattleEnd(player_wins=True)

    def possible_spells(self) -> Iterable[Spell]:
        return (
            spell
            for spell in spell_book
            if spell.cost <= self.player_mana and spell not in self.active_spells
        )

    def cast_spell(self, spell: Spell):
        assert spell not in self.active_spells
        assert self.player_mana >= spell.cost

        self.player_mana -= spell.cost
        spell.when_cast(self)
        if spell.lasts > 0:
            self.active_spells[spell] = spell.lasts

        if self.boss_hp <= 0:
            self.log("... This kills the boss, and the player wins.")
            raise BattleEnd(player_wins=True)

    def deal_boss_damage(self):
        damage_dealt = max(self.boss_damage - self.player_armor, 1)
        self.player_hp -= damage_dealt
        if self.player_armor > 0:
            self.log(f"Boss attacks for {self.boss_damage} - {self.player_armor} = {damage_dealt} damage!")
        else:
            self.log(f"Boss attacks for {damage_dealt} damage!")

        if self.player_hp <= 0:
            self.log("... This kills the player, and the boss wins.")
            raise BattleEnd(player_wins=False)

    def turn(self, spell: Optional[Spell]):
        if spell:
            self.cast_spell(spell)
        self.log()
        self.print_status("Boss")
        self.apply_spell_effects()
        self.deal_boss_damage()
        self.log()
        self.apply_handicap()
        self.print_status("Player")
        self.apply_spell_effects()


def interactive(battle: Battle):
    while True:
        spells = list(battle.possible_spells())
        if spells:
            for n, spell in enumerate(spells):
                print(f"[{n+1}] {spell.name} (-{spell.cost})")
            spell_index = input()
            spell = spells[int(spell_index)-1] if spell_index else None
        else:
            spell = None

        battle.turn(spell)


def victory_sequence(battle: Battle) -> tuple[int, List[Spell]]:
    for spell in battle.possible_spells():
        battle_c = copy(battle)
        try:
            battle_c.turn(spell)
        except BattleEnd as be:
            if be.player_wins:
                yield spell.cost, [spell]
        else:
            for ss_cost, ss_spells in victory_sequence(battle_c):
                yield spell.cost + ss_cost, [spell] + ss_spells


def test_1():
    battle = Battle(
        player_hp=10,
        player_mana=250,
        boss_hp=13,
        boss_damage=8,
        logging=True
    )

    battle.turn(spell_poison)
    assert battle.player_hp == 2
    assert battle.player_mana == 77 == 250 - spell_poison.cost
    assert battle.boss_hp == 7 == 13 - 2 * spell_poison.damage
    assert battle.active_spells[spell_poison] == 4 == spell_poison.lasts - 2

    try:
        assert battle.turn(spell_missile)
    except BattleEnd as be:
        assert be.player_wins is True
    else:
        assert False, "battle didn't end"

    assert battle.player_hp == 2
    assert battle.player_mana == 24
    assert battle.boss_hp == 0
    assert battle.active_spells[spell_poison] == 3


def test_2():
    battle = Battle(
        player_hp=10,
        player_mana=250,
        boss_hp=14,
        boss_damage=8,
        logging=True
    )

    # turn 1
    battle.turn(spell_recharge)
    assert battle.player_hp == 2 == 10 - battle.boss_damage
    assert battle.player_armor == 0
    assert battle.player_mana == 223 == 250 - spell_recharge.cost + 2 * spell_recharge.mana
    assert battle.boss_hp == 14
    assert battle.active_spells[spell_recharge] == 3 == spell_recharge.lasts - 2

    # turn 2
    battle.turn(spell_shield)
    assert battle.player_hp == 1 == 2 + spell_shield.armor - battle.boss_damage
    assert battle.player_armor == 7 == spell_shield.armor
    assert battle.player_mana == 312 == 223 - spell_shield.cost + 2 * spell_recharge.mana
    assert battle.boss_hp == 14
    assert len(battle.active_spells) == 2
    assert battle.active_spells[spell_recharge] == 1 == spell_recharge.lasts - 4
    assert battle.active_spells[spell_shield] == 4 == spell_shield.lasts - 2

    # turn 3
    battle.turn(spell_drain)
    assert battle.player_hp == 2 == 1 + spell_drain.damage + spell_shield.armor - battle.boss_damage
    assert battle.player_armor == 7 == spell_shield.armor
    assert battle.player_mana == 340 == 312 - spell_drain.cost + spell_recharge.mana
    assert battle.boss_hp == 12 == 14 - spell_drain.damage
    assert len(battle.active_spells) == 1
    assert battle.active_spells[spell_shield] == 2 == 4 - 2

    # turn 4
    battle.turn(spell_poison)
    assert battle.player_hp == 1 == 2 + spell_shield.armor - battle.boss_damage
    assert battle.player_armor == 0
    assert battle.player_mana == 167 == 340 - spell_poison.cost
    assert battle.boss_hp == 6 == 12 - 2 * spell_poison.damage
    assert len(battle.active_spells) == 1
    assert battle.active_spells[spell_poison] == 4 == spell_poison.lasts - 2

    # turn 5
    try:
        battle.turn(spell_missile)
    except BattleEnd as be:
        assert be.player_wins is True
    else:
        assert False, "battle didn't end"

    assert battle.player_hp == 1
    assert battle.player_armor == 0
    assert battle.player_mana == 114 == 167 - spell_missile.cost
    assert battle.boss_hp == -1 == 6 - spell_missile.damage - spell_poison.damage


def test_hard():
    battle = Battle(
        player_hp=10,
        player_mana=500,
        boss_hp=14,
        boss_damage=8,
        hard=True,
        logging=True
    )

    # turn 1
    battle.turn(spell_shield)
    assert battle.player_hp == 8 == 10 + spell_shield.armor - battle.boss_damage - 1
    assert battle.player_armor == 7 == spell_shield.armor
    assert battle.player_mana == 387 == 500 - spell_shield.cost
    assert battle.boss_hp == 14
    assert battle.active_spells[spell_shield] == 4 == spell_shield.lasts - 2

    # turn 2
    battle.turn(spell_recharge)
    assert battle.player_hp == 6 == 8 + spell_shield.armor - battle.boss_damage - 1
    assert battle.player_armor == 7 == spell_shield.armor
    assert battle.player_mana == 360 == 387 - spell_recharge.cost + 2 * spell_recharge.mana
    assert battle.boss_hp == 14
    assert len(battle.active_spells) == 2
    assert battle.active_spells[spell_shield] == 2 == spell_shield.lasts - 4
    assert battle.active_spells[spell_recharge] == 3 == spell_recharge.lasts - 2

    # turn 3
    battle.turn(spell_drain)
    assert battle.player_hp == 6 == 6 + spell_shield.armor - battle.boss_damage - 1 + spell_drain.damage
    assert battle.player_armor == 0
    assert battle.player_mana == 489 == 360 - spell_drain.cost + 2 * spell_recharge.mana
    assert battle.boss_hp == 12 == 14 - spell_drain.damage
    assert len(battle.active_spells) == 1
    assert battle.active_spells[spell_recharge] == 1 == spell_recharge.lasts - 4



def part_1(player: Character, boss: Character) -> int:
    battle = Battle.with_characters(
        player=player,
        boss=boss
    )
    best_cost, best_ss = min(ilog(victory_sequence(battle)), key=lambda p: p[0])
    print(f"part 1: best mana cost is {best_cost} ({', '.join(str(s) for s in best_ss)})")
    return best_cost


def part_2(player: Character, boss: Character) -> int:
    battle = Battle.with_characters(
        player=player,
        boss=boss,
        hard=True
    )

    # battle.player_hp -= 1  # pre-handicap

    best_cost, best_ss = min(ilog(victory_sequence(battle)), key=lambda p: p[0])
    print(f"part 2: best mana cost is {best_cost} ({', '.join(str(s) for s in best_ss)})")
    return best_cost


if __name__ == '__main__':
    ch_player = Character(hit_points=50, mana=500)
    ch_boss = Character(hit_points=71, damage=10)

    # part_1(ch_player, ch_boss)
    part_2(ch_player, ch_boss)
