"""
Advent of Code 2015
Day 22: Wizard Simulator 20XX
https://adventofcode.com/2015/day/22
"""

from typing import Iterable

import yaml

from common.graph import shortest_path
from common.utils import join_and
from common.utils import relative_path


def part_1(player: 'Character', boss: 'Character', spellbook: 'SpellBook') -> int:
    """
    Little Henry Case decides that defeating bosses with swords and stuff is boring. Now he's
    playing the game with a wizard. Of course, he gets stuck on another boss and needs your help
    again.

    In this version, combat still proceeds with the player and the boss taking alternating turns.
    The player still goes first. Now, however, you don't get any equipment; instead, you must choose
    one of your spells to cast. The first character at or below `0` hit points loses.

    Since you're a wizard, you don't get to wear armor, and you can't attack normally. However,
    since you do **magic damage**, your opponent's armor is ignored, and so the boss effectively has
    zero armor as well. As before, if armor (from a spell, in this case) would reduce damage below
    `1`, it becomes `1` instead - that is, the boss' attacks always deal at least `1` damage.

    On each of your turns, you must select one of your spells to cast. If you cannot afford to cast
    any spell, you lose. Spells cost **mana**; you start with **`500`** mana, but have no maximum
    limit. You must have enough mana to cast a spell, and its cost is immediately deducted when you
    cast it. Your spells are:

        >>> the_spellbook = SpellBook.from_file('data/22-spells.yaml')
        >>> list(the_spellbook.spell_names())
        ['Magic Missile', 'Drain', 'Shield', 'Poison', 'Recharge']

      - **Magic Missile** costs `53` mana. It instantly does `4` damage.

        >>> the_spellbook['Magic Missile']
        Spell('Magic Missile', cost=53, damage=4)

      - **Drain** costs `73` mana. It instantly does `2` damage and heals you for `2` hit points.

        >>> the_spellbook['Drain']
        Spell('Drain', cost=73, damage=2, heal=2)

      - **Shield** costs `113` mana. It starts an effect that lasts for `6` turns. While it is
        active, your armor is increased by `7`.

        >>> the_spellbook['Shield']
        Spell('Shield', cost=113, effect=Effect('Shield', lasts=6, armor=7))

      - **Poison** costs `173` mana. It starts an effect that lasts for `6` turns. At the start of
        each turn while it is active, it deals the boss `3` damage.

        >>> the_spellbook['Poison']
        Spell('Poison', cost=173, effect=Effect('Poison', lasts=6, damage=3))

      - **Recharge** costs 229 mana. It starts an effect that lasts for `5` turns. At the start of
        each turn while it is active, it gives you `101` new mana.

        >>> the_spellbook['Recharge']
        Spell('Recharge', cost=229, effect=Effect('Recharge', lasts=5, add_mana=101))

    **Effects** all work the same way. Effects apply at the start of both the player's turns and
    the boss' turns. Effects are created with a timer (the number of turns they last); at the start
    of each turn, after they apply any effect they have, their timer is decreased by one. If this
    decreases the timer to zero, the effect ends. You cannot cast a spell that would start an effect
    which is already active. However, effects can be started on the same turn they end.

    For example, consider this scenario:

        >>> example_player = Character(hit_points=10, mana=250)
        >>> example_boss_13hp = Character(hit_points=13, damage=8)
        >>> example_battle = Battle(example_player, example_boss_13hp, the_spellbook)
        >>> end = example_battle.run('Poison', 'Magic Missile', logging=True)
        -- Player turn --
        - Player has 10 hit points, 0 armor, 250 mana
        - Boss has 13 hit points
        Player casts Poison.
        -- Boss turn --
        - Player has 10 hit points, 0 armor, 77 mana
        - Boss has 13 hit points
        Poison deals 3 damage; its timer is now 5.
        Boss attacks for 8 damage!
        -- Player turn --
        - Player has 2 hit points, 0 armor, 77 mana
        - Boss has 10 hit points
        Poison deals 3 damage; its timer is now 4.
        Player casts Magic Missile, dealing 4 damage.
        -- Boss turn --
        - Player has 2 hit points, 0 armor, 24 mana
        - Boss has 3 hit points
        Poison deals 3 damage. This kills the boss, and the player wins.
        >>> end.player_wins
        True

    Now, suppose the same initial conditions, except that the boss has 14 hit points instead:

        >>> example_boss_14hp = Character(hit_points=14, damage=8)
        >>> example_battle_2 = Battle(example_player, example_boss_14hp, the_spellbook)
        >>> end_2 = example_battle_2.run(
        ...     'Recharge', 'Shield', 'Drain', 'Poison', 'Magic Missile',
        ...     logging=True
        ... )
        -- Player turn --
        - Player has 10 hit points, 0 armor, 250 mana
        - Boss has 14 hit points
        Player casts Recharge.
        -- Boss turn --
        - Player has 10 hit points, 0 armor, 21 mana
        - Boss has 14 hit points
        Recharge provides 101 mana; its timer is now 4.
        Boss attacks for 8 damage!
        -- Player turn --
        - Player has 2 hit points, 0 armor, 122 mana
        - Boss has 14 hit points
        Recharge provides 101 mana; its timer is now 3.
        Player casts Shield, increasing armor by 7.
        -- Boss turn --
        - Player has 2 hit points, 7 armor, 110 mana
        - Boss has 14 hit points
        Recharge provides 101 mana; its timer is now 2.
        Shield's timer is now 5.
        Boss attacks for 8 - 7 = 1 damage!
        -- Player turn --
        - Player has 1 hit point, 7 armor, 211 mana
        - Boss has 14 hit points
        Recharge provides 101 mana; its timer is now 1.
        Shield's timer is now 4.
        Player casts Drain, dealing 2 damage, and healing 2 hit points.
        -- Boss turn --
        - Player has 3 hit points, 7 armor, 239 mana
        - Boss has 12 hit points
        Recharge provides 101 mana; its timer is now 0.
        Recharge wears off.
        Shield's timer is now 3.
        Boss attacks for 8 - 7 = 1 damage!
        -- Player turn --
        - Player has 2 hit points, 7 armor, 340 mana
        - Boss has 12 hit points
        Shield's timer is now 2.
        Player casts Poison.
        -- Boss turn --
        - Player has 2 hit points, 7 armor, 167 mana
        - Boss has 12 hit points
        Shield's timer is now 1.
        Poison deals 3 damage; its timer is now 5.
        Boss attacks for 8 - 7 = 1 damage!
        -- Player turn --
        - Player has 1 hit point, 7 armor, 167 mana
        - Boss has 9 hit points
        Shield's timer is now 0.
        Shield wears off, decreasing armor by 7.
        Poison deals 3 damage; its timer is now 4.
        Player casts Magic Missile, dealing 4 damage.
        -- Boss turn --
        - Player has 1 hit point, 0 armor, 114 mana
        - Boss has 2 hit points
        Poison deals 3 damage. This kills the boss, and the player wins.
        >>> end_2.player_wins
        True

    You start with **`50` hit points** and **`500` mana points**. The boss's actual stats are in
    your puzzle input. What is the **least amount of mana** you can spend and still win the fight?
    (Do not include mana recharge effects as "spending" negative mana.)

        >>> part_1(example_player, example_boss_14hp, the_spellbook)
        part 1: you can spend only 641 mana: Recharge, Shield, Drain, Poison, Magic Missile
        641
    """

    cost, cheapest_spells = optimal_victory_sequence(Battle(player, boss, spellbook))
    spells_str = ", ".join(spell.name for spell in cheapest_spells)
    print(f"part 1: you can spend only {cost} mana: {spells_str}")
    return cost


def part_2(player: 'Character', boss: 'Character', spellbook: 'SpellBook') -> int:
    """
    On the next run through the game, you increase the difficulty to **hard**.

    At the start of each **player turn** (before any other effects apply), you lose `1` hit point.
    If this brings you to or below `0` hit points, you lose.

    With the same starting stats for you and the boss, what is the **least amount of mana** you can
    spend and still win the fight?

        >>> example_player = Character(hit_points=11, mana=250)
        >>> example_boss = Character(hit_points=13, damage=8)
        >>> the_spellbook = SpellBook.from_file('data/22-spells.yaml')
        >>> example_battle=Battle(example_player, example_boss, the_spellbook, hard=True)
        >>> end = example_battle.run('Poison', 'Magic Missile', logging=True)
        -- Player turn --
        - Player has 11 hit points, 0 armor, 250 mana
        - Boss has 13 hit points
        Player loses 1 hit point because of hard difficulty.
        Player casts Poison.
        -- Boss turn --
        - Player has 10 hit points, 0 armor, 77 mana
        - Boss has 13 hit points
        Poison deals 3 damage; its timer is now 5.
        Boss attacks for 8 damage!
        -- Player turn --
        - Player has 2 hit points, 0 armor, 77 mana
        - Boss has 10 hit points
        Player loses 1 hit point because of hard difficulty.
        Poison deals 3 damage; its timer is now 4.
        Player casts Magic Missile, dealing 4 damage.
        -- Boss turn --
        - Player has 1 hit point, 0 armor, 24 mana
        - Boss has 3 hit points
        Poison deals 3 damage. This kills the boss, and the player wins.
        >>> end.player_wins
        True

        >>> part_2(example_player, example_boss, the_spellbook)
        part 2: you can spend only 226 mana: Poison, Magic Missile
        226
    """

    cost, cheapest_spells = optimal_victory_sequence(Battle(player, boss, spellbook, hard=True))
    spells_str = ", ".join(spell.name for spell in cheapest_spells)
    print(f"part 2: you can spend only {cost} mana: {spells_str}")
    return cost


class Character:
    def __init__(self, hit_points, damage=0, mana=0):
        self.hit_points = int(hit_points)
        self.damage = int(damage)
        self.mana = int(mana)

    def __repr__(self) -> str:
        dmg = f', damage={self.damage!r}' if self.damage else ''
        mana = f', mana={self.mana!r}' if self.mana else ''
        return f'{type(self).__name__}(hit_points={self.hit_points!r}{dmg}{mana})'

    @classmethod
    def from_file(cls, fn: str) -> 'Character':
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Character':
        prefixes = dict(
            hit_points="Hit Points: ",
            damage="Damage: ",
            mana="Mana: "
        )

        def parse_line(line: str) -> tuple[str, int]:
            for key, prefix in prefixes.items():
                if line.startswith(prefix):
                    return key, int(line.removeprefix(prefix))
            else:
                raise ValueError(line)

        return cls(**dict(parse_line(line) for line in lines))


class SpellBook:
    def __init__(self, spells: Iterable['Spell']):
        self.spells = list(spells)
        self.spells_by_name = {spell.name: spell for spell in self.spells}

    @classmethod
    def from_file(cls, fn: str) -> 'SpellBook':
        return cls.from_dict(yaml.safe_load(open(relative_path(__file__, fn))))

    @classmethod
    def from_dict(cls, d: dict) -> 'SpellBook':
        return cls(Spell.from_dict(spell_d) for spell_d in d['spells'])

    def __getitem__(self, spell_name: str) -> 'Spell':
        return self.spells_by_name[spell_name]

    def spell_names(self) -> Iterable[str]:
        return (spell.name for spell in self.spells)


class Spell:
    def __init__(self, name, cost, damage=0, heal=0, effect=None):
        self.name = str(name)
        self.cost = int(cost)
        self.damage = int(damage)
        self.heal = int(heal)
        self.effect = effect

        assert self.cost > 0
        assert self.damage >= 0
        assert self.heal >= 0

    def __repr__(self) -> str:
        tn = type(self).__name__
        cost = f'cost={self.cost!r}'
        dmg = f', damage={self.damage!r}' if self.damage else ''
        heal = f', heal={self.heal!r}' if self.heal else ''
        effect = f', effect={self.effect!r}' if self.effect else ''
        return f'{tn}({self.name!r}, {cost}{dmg}{heal}{effect})'

    @classmethod
    def from_dict(cls, d: dict) -> 'Spell':
        if 'effect' in d:
            effect = Effect.from_dict(d['name'], d.pop('effect'))
        else:
            effect = None

        return cls(**d, effect=effect)


class Effect:
    def __init__(self, name, lasts, armor=0, damage=0, add_mana=0):
        self.name = str(name)
        self.lasts = int(lasts)
        self.armor = int(armor)
        self.damage = int(damage)
        self.add_mana = int(add_mana)

        assert self.lasts > 0
        assert self.armor >= 0
        assert self.damage >= 0
        assert self.add_mana >= 0

    def __repr__(self) -> str:
        tn = type(self).__name__
        lasts = f'lasts={self.lasts!r}'
        armor = f', armor={self.armor!r}' if self.armor else ''
        dmg = f', damage={self.damage!r}' if self.damage else ''
        mana = f', add_mana={self.add_mana!r}' if self.add_mana else ''
        return f'{tn}({self.name!r}, {lasts}{armor}{dmg}{mana})'

    @classmethod
    def from_dict(cls, name, d: dict) -> 'Effect':
        return cls(name, **d)


class Battle:
    def __init__(
        self,
        player: Character,
        boss: Character,
        spellbook: SpellBook,
        hard: bool = False
    ):
        self.player = player
        self.boss = boss
        self.spellbook = spellbook
        self.hard = hard
        assert self.player.damage == 0
        assert self.boss.mana == 0
        assert self.boss.damage > 0

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.player!r}, {self.boss!r})'

    def initial_state(self, logging: bool = False) -> 'BattleState':
        return BattleState(
            battle=self,
            player_hp=self.player.hit_points,
            player_armor=0,
            player_mana=self.player.mana,
            boss_hp=self.boss.hit_points,
            active_effects={},
            logging=logging,
        )

    def victory_state(self) -> 'BattleState':
        return BattleState(
            battle=self,
            player_hp=1,
            player_mana=0,
            player_armor=0,
            boss_hp=0,
            active_effects={},
            logging=False
        )

    def run(self, *spells: Spell | str, logging: bool = False) -> 'BattleState':
        state = self.initial_state(logging)
        for spell in spells:
            state = state.after_turn(spell)
        return state


class BattleState:
    def __init__(
        self,
        battle: Battle,
        *,
        player_hp: int,
        player_mana: int,
        player_armor: int,
        boss_hp: int,
        active_effects: dict[Effect, int],
        logging: bool
    ):
        self.battle = battle
        self.player_hp = player_hp
        self.player_mana = player_mana
        self.player_armor = player_armor
        self.boss_hp = boss_hp
        self.active_effects = dict(active_effects)
        self.logging = logging

        assert self.player_mana >= 0
        assert self.player_armor >= 0

    def __repr__(self) -> str:
        return (
            f'{type(self).__name__}('
            f'{self.battle!r}, '
            f'player_hp={self.player_hp!r}, '
            f'player_mana={self.player_mana!r}, '
            f'player_armor={self.player_armor!r}, '
            f'boss_hp={self.boss_hp!r}, '
            f'active_effects={self.active_effects!r}, '
            f'logging={self.logging!r})'
        )

    def __str__(self) -> str:
        def hp_str(hps: int) -> str:
            return "1 hit point" if hps == 1 else f"{hps} hit points"

        if self.player_wins:
            winner = "\nPlayer wins!"
        elif self.boss_wins:
            winner = "\nBoss wins!"
        else:
            winner = ""

        return (
            f"- Player has {hp_str(self.player_hp)}, {self.player_armor} armor, "
            f"{self.player_mana} mana\n"
            f"- Boss has {hp_str(self.boss_hp)}{winner}"
        )

    def _key(self) -> tuple:
        # all winning states are considered the same:
        if self.player_wins:
            return ('player wins',)
        if self.boss_wins:
            return ('boss wins',)

        # otherwise consider other values
        return (
            self.player_hp,
            self.player_mana,
            self.boss_hp,
            tuple(sorted((timer, ef.name) for ef, timer in self.active_effects.items()))
        )

    def __hash__(self) -> int:
        return hash(self._key())

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        assert self.battle is other.battle
        return self._key() == other._key()

    @property
    def player_wins(self) -> bool:
        return self.boss_hp <= 0

    @property
    def boss_wins(self) -> bool:
        return self.player_hp <= 0

    @property
    def has_winner(self) -> bool:
        return self.player_wins or self.boss_wins

    @property
    def potential_player_mana(self) -> int:
        return self.player_mana + sum(effect.add_mana for effect in self.active_effects)

    def castable_spells(self) -> Iterable[Spell]:
        if self.has_winner:
            return ()

        return (
            spell
            for spell in self.battle.spellbook.spells
            if spell.cost <= self.potential_player_mana
            if (spell.effect is None or self.active_effects.get(spell.effect, 0) <= 1)
        )

    def copy(self) -> 'BattleState':
        return type(self)(
            battle=self.battle,
            player_hp=self.player_hp,
            player_armor=self.player_armor,
            player_mana=self.player_mana,
            boss_hp=self.boss_hp,
            active_effects=self.active_effects,
            logging=self.logging,
        )

    def after_turn(self, spell: Spell | str) -> 'BattleState':
        new_state = self.copy()
        try:
            new_state.do_turn(spell)
        except BattleEnds:
            assert new_state.player_hp <= 0 or new_state.boss_hp <= 0

        return new_state

    def do_turn(self, spell: Spell | str) -> None:
        assert not self.has_winner
        # Player turn
        self._log_turn("Player")
        self._apply_handicap()
        self._apply_effects()
        self._cast_player_spell(spell)
        # Boss turn
        self._log_turn("Boss")
        self._apply_effects()
        self._boss_attack()

    def _log_turn(self, active_name: str) -> None:
        self.log(f"-- {active_name} turn --")
        self.log(self)

    def _apply_handicap(self) -> None:
        if self.battle.hard:
            assert self.player_hp > 0
            self.player_hp -= 1
            descr = "Player loses 1 hit point because of hard difficulty."
            if self.player_hp > 0:
                self.log(descr)
            else:
                self.log(descr + " This kills the player, and the boss wins.")
                raise BattleEnds()

    def _apply_effects(self) -> None:
        wearing_off: list[Effect] = []

        for effect, timer in self.active_effects.items():
            assert timer > 0
            timer -= 1
            self.active_effects[effect] = timer

            if effect.damage:
                self.boss_hp -= effect.damage
                descr = f"{effect.name} deals {effect.damage} damage"
                if self.boss_hp > 0:
                    self.log(f"{descr}; its timer is now {timer}.")
                else:
                    self.log(f"{descr}. This kills the boss, and the player wins.")
                    raise BattleEnds()

            elif effect.add_mana:
                self.player_mana += effect.add_mana
                descr = f"{effect.name} provides {effect.add_mana} mana"
                self.log(f"{descr}; its timer is now {timer}.")

            else:
                self.log(f"{effect.name}'s timer is now {timer}.")

            if timer == 0:
                wearing_off.append(effect)
                descr = f"{effect.name} wears off"
                if effect.armor:
                    self.player_armor -= effect.armor
                    self.log(f"{descr}, decreasing armor by {effect.armor}.")
                else:
                    self.log(f"{descr}.")

        for effect in wearing_off:
            del self.active_effects[effect]

    def _cast_player_spell(self, spell: Spell | str) -> None:
        if not isinstance(spell, Spell):
            spell = self.battle.spellbook[spell]

        self.player_mana -= spell.cost
        assert self.player_mana >= 0
        spell_results = []

        if spell.damage:
            self.boss_hp -= spell.damage
            spell_results.append(f"dealing {spell.damage} damage")

        if spell.heal:
            self.player_hp += spell.heal
            spell_results.append(f"healing {spell.heal} hit points")

        if spell.effect:
            assert spell.effect not in self.active_effects
            self.active_effects[spell.effect] = spell.effect.lasts
            if spell.effect.armor:
                self.player_armor += spell.effect.armor
                spell_results.append(f"increasing armor by {spell.effect.armor}")

        spell_str = f", {join_and(spell_results, True)}" if spell_results else ""
        self.log(f"Player casts {spell.name}{spell_str}.")

    def _boss_attack(self) -> None:
        boss_damage = max(self.battle.boss.damage - self.player_armor, 1)
        self.player_hp -= boss_damage

        if self.player_armor:
            boss_damage_str = f"{self.battle.boss.damage} - {self.player_armor} = {boss_damage}"
        else:
            boss_damage_str = str(boss_damage)
        descr = f"Boss attacks for {boss_damage_str} damage!"

        if self.player_hp > 0:
            self.log(descr)
        else:
            self.log(descr + " This kills the player and the boss wins.")
            raise BattleEnds()

    def log(self, *args, **kwargs) -> None:
        if self.logging:
            print(*args, **kwargs)


class BattleEnds(Exception):
    pass


def optimal_victory_sequence(battle: Battle) -> tuple[int, list[Spell]]:
    return shortest_path(
        start=battle.initial_state(),
        target=battle.victory_state(),
        edges=lambda state: (
            (state.after_turn(spell), spell, spell.cost)
            for spell in state.castable_spells()
        ),
        description="finding victory sequence" + (" (hard)" if battle.hard else "")
    )


def total_cost(spells: Iterable[Spell]) -> int:
    return sum(spell.cost for spell in spells)


if __name__ == '__main__':
    player_ = Character.from_file('data/22-player.txt')
    boss_ = Character.from_file('data/22-input.txt')
    spellbook_ = SpellBook.from_file('data/22-spells.yaml')
    part_1(player_, boss_, spellbook_)
    part_2(player_, boss_, spellbook_)
