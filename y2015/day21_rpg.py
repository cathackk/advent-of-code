"""
Advent of Code 2015
Day 21: RPG Simulator 20XX
https://adventofcode.com/2015/day/21
"""

from itertools import combinations
from typing import Iterable

from common.file import relative_path
from common.iteration import maxk
from common.iteration import mink
from common.text import parse_line


def part_1(boss: 'Character', player_hp: int, shop: 'Shop') -> int:
    """
    Little Henry Case got a new video game for Christmas. It's an RPG, and he's stuck on a boss. He
    needs to know what equipment to buy at the shop. He hands you the controller.

    In this game, the player (you) and the enemy (the boss) take turns attacking. The player always
    goes first. Each attack reduces the opponent's hit points by at least `1`. The first character
    at or below 0 hit points loses.

    Damage dealt by an attacker each turn is equal to the attacker's damage score minus
    the defender's armor score. An attacker always does at least `1` damage. So, if the attacker has
    a damage score of `8`, and the defender has an armor score of `3`, the defender loses `5` hit
    points. If the defender had an armor score of `300`, the defender would still lose `1` hit
    point.

    Your damage score and armor score both start at zero. They can be increased by buying items in
    exchange for gold. You start with no items and have as much gold as you need. Your total damage
    or armor is equal to the sum of those stats from all of your items. You have **100 hit points**.

    Here is what the item shop is selling:

        >>> the_shop = Shop.from_file('data/21-shop.txt')
        >>> print(the_shop)
        Weapons:    Cost  Damage  Armor
        Dagger        8     4       0
        Shortsword   10     5       0
        Warhammer    25     6       0
        Longsword    40     7       0
        Greataxe     74     8       0
        <BLANKLINE>
        Armor:      Cost  Damage  Armor
        Leather      13     0       1
        Chainmail    31     0       2
        Splintmail   53     0       3
        Bandedmail   75     0       4
        Platemail   102     0       5
        <BLANKLINE>
        Rings:      Cost  Damage  Armor
        Damage +1    25     1       0
        Damage +2    50     2       0
        Damage +3   100     3       0
        Defense +1   20     0       1
        Defense +2   40     0       2
        Defense +3   80     0       3

    You must buy exactly one weapon; no dual-wielding. Armor is optional, but you can't use more
    than one. You can buy 0-2 rings (at most one for each hand). You must use any items you buy.
    The shop only has one of each item, so you can't buy, for example, two rings of Damage +3.

    For example, suppose you have `8` hit points, Shortsword, Splintmail and Ring of Defense +2,
    and that the boss has `12` hit points, `7` damage, and `2` armor:

        >>> example_equipment = the_shop.get_items('Shortsword', 'Splintmail', 'Defense +2')
        >>> example_equipment  # doctest: +NORMALIZE_WHITESPACE
        [Item('Shortsword', cost=10, damage=5),
         Item('Splintmail', cost=53, armor=3),
         Item('Defense +2', cost=40, armor=2)]
        >>> player = Character('player', hit_points=8)
        >>> player_equipped = player.with_equipment(example_equipment)
        >>> player_equipped
        Character('player', hit_points=8, damage=5, armor=5)
        >>> example_boss = Character('boss', hit_points=12, damage=7, armor=2)
        >>> winner = battle(player_equipped, example_boss, log=True)
        The player deals 5-2 = 3 damage; the boss goes down to 9 hit points.
        The boss deals 7-5 = 2 damage; the player goes down to 6 hit points.
        The player deals 5-2 = 3 damage; the boss goes down to 6 hit points.
        The boss deals 7-5 = 2 damage; the player goes down to 4 hit points.
        The player deals 5-2 = 3 damage; the boss goes down to 3 hit points.
        The boss deals 7-5 = 2 damage; the player goes down to 2 hit points.
        The player deals 5-2 = 3 damage; the boss goes down to 0 hit points.

    In this scenario, the player wins! (Barely.)

        >>> winner.name
        'player'

    If the player had only Longsword and Ring of Damage +1, they would win as well:

        >>> example_equipment_2 = the_shop.get_items('Longsword', 'Damage +1')
        >>> example_equipment_2
        [Item('Longsword', cost=40, damage=7), Item('Damage +1', cost=25, damage=1)]
        >>> example_player_equipped_2 = player.with_equipment(example_equipment_2)
        >>> example_player_equipped_2
        Character('player', hit_points=8, damage=8, armor=0)
        >>> winner = battle(example_player_equipped_2, example_boss, log=True)
        The player deals 8-2 = 6 damage; the boss goes down to 6 hit points.
        The boss deals 7-0 = 7 damage; the player goes down to 1 hit point.
        The player deals 8-2 = 6 damage; the boss goes down to 0 hit points.

    But with cheaper equipment!

        >>> total_cost(example_equipment)
        103
        >>> total_cost(example_equipment_2)
        65

    You have **100 hit points**. The boss's actual stats are in your puzzle input.
    What is **the least amount of gold you can spend** and still win the fight?

        >>> part_1(example_boss, player_hp=8, shop=the_shop)
        part 1: you can beat the boss by spending only 65 gold: Longsword, Damage +1
        65
    """

    winning_builds = (
        build
        for build in shop.generate_builds()
        if is_beating_boss(build, boss, player_hp)
    )
    cheapest_build, cost = mink(winning_builds, key=total_cost)

    build_str = ", ".join(item.name for item in cheapest_build)
    print(f"part 1: you can beat the boss by spending only {cost} gold: {build_str}")
    return cost


def part_2(boss: 'Character', player_hp: int, shop: 'Shop') -> int:
    """
    Turns out the shopkeeper is working with the boss, and can persuade you to buy whatever items he
    wants. The other rules still apply, and he still only has one of each item.

        >>> (example_boss := Character.from_file("boss", 'data/21-example-boss.txt'))
        Character('boss', hit_points=12, damage=7, armor=2)
        >>> the_shop = Shop.from_file('data/21-shop.txt')
        >>> expensive_equipment = the_shop.get_items('Dagger', 'Damage +3', 'Defense +3')
        >>> expensive_equipment  # doctest: +NORMALIZE_WHITESPACE
        [Item('Dagger', cost=8, damage=4),
         Item('Damage +3', cost=100, damage=3),
         Item('Defense +3', cost=80, armor=3)]
        >>> (player := Character('player', hit_points=8).with_equipment(expensive_equipment))
        Character('player', hit_points=8, damage=7, armor=3)
        >>> winner = battle(player, example_boss, log=True)
        The player deals 7-2 = 5 damage; the boss goes down to 7 hit points.
        The boss deals 7-3 = 4 damage; the player goes down to 4 hit points.
        The player deals 7-2 = 5 damage; the boss goes down to 2 hit points.
        The boss deals 7-3 = 4 damage; the player goes down to 0 hit points.
        >>> winner.name
        'boss'

    What is the **most** amount of gold you can spend and still lose the fight?

        >>> part_2(example_boss, player_hp=8, shop=the_shop)
        part 2: you can spend 188 gold and still lose the fight: Dagger, Damage +3, Defense +3
        188
    """

    losing_builds = (
        build
        for build in shop.generate_builds()
        if not is_beating_boss(build, boss, player_hp)
    )
    most_expensive_build, cost = maxk(losing_builds, key=total_cost)

    build_str = ", ".join(item.name for item in most_expensive_build)
    print(f"part 2: you can spend {cost} gold and still lose the fight: {build_str}")
    return cost


class Item:
    def __init__(self, name, cost, damage=0, armor=0):
        self.name = str(name).replace("_", " ")
        self.cost = int(cost)
        self.damage = int(damage)
        self.armor = int(armor)

    def __repr__(self) -> str:
        damage_repr = f', damage={self.damage!r}' if self.damage else ''
        armor_repr = f', armor={self.armor!r}' if self.armor else ''
        return f'{type(self).__name__}({self.name!r}, cost={self.cost!r}{damage_repr}{armor_repr})'

    @classmethod
    def from_line(cls, line: str) -> 'Item':
        return cls(*line.split())


def total_cost(items: Iterable[Item]) -> int:
    return sum(item.cost for item in items)


class Shop:
    def __init__(self, weapons: Iterable[Item], armor: Iterable[Item], rings: Iterable[Item]):
        self.weapons = list(weapons)
        self.armor = list(armor)
        self.rings = list(rings)
        self.items_by_name = {item.name: item for item in self.weapons + self.armor + self.rings}

    def __repr__(self) -> str:
        tn = type(self).__name__
        return f'{tn}(weapons={self.weapons!r}, armor={self.armor!r}, rings={self.rings!r})'

    def __str__(self) -> str:
        def header(name: str) -> str:
            return f"{name+':':12}Cost  Damage  Armor"

        def item_row(item: Item) -> str:
            return f"{item.name:12}{item.cost:3}{item.damage:6}{item.armor:8}"

        def lines() -> Iterable[str]:
            yield header("Weapons")
            yield from (item_row(weapon) for weapon in self.weapons)
            yield ''
            yield header("Armor")
            yield from (item_row(armor) for armor in self.armor)
            yield ''
            yield header("Rings")
            yield from (item_row(ring) for ring in self.rings)

        return "\n".join(lines())

    @classmethod
    def from_file(cls, fn: str) -> 'Shop':
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Shop':
        lines_it = (line.strip() for line in lines)

        def category_from_lines(cat_name: str) -> Iterable[Item]:
            header = next(lines_it, None)
            if header is None:
                raise ValueError(f"no more lines for {cat_name}")

            assert header.startswith(cat_name + ":")
            for line in lines_it:
                if not line:
                    return
                yield Item.from_line(line)

        return cls(
            weapons=category_from_lines("Weapons"),
            armor=category_from_lines("Armor"),
            rings=category_from_lines("Rings")
        )

    def get_items(self, *names: str) -> list[Item]:
        return [self.items_by_name[name] for name in names]

    def generate_builds(self) -> Iterable[list[Item]]:
        for weapon in self.weapons:
            # weapon only
            yield [weapon]
            # weapon + 1 ring
            yield from ([weapon, ring] for ring in self.rings)
            # weapon + 2 rings
            yield from ([weapon, r1, r2] for r1, r2 in combinations(self.rings, 2))
            for armor in self.armor:
                # weapon + armor
                yield [weapon, armor]
                # weapon + armor + 1 ring
                yield from ([weapon, armor, ring] for ring in self.rings)
                # weapon + armor + 2 rings
                yield from ([weapon, armor, r1, r2] for r1, r2 in combinations(self.rings, 2))


class Character:
    def __init__(self, name: str, hit_points: int, damage: int = 0, armor: int = 0):
        self.name = name
        self.hit_points = hit_points
        self.damage = damage
        self.armor = armor

    def __repr__(self) -> str:
        return (
            f'{type(self).__name__}({self.name!r}, hit_points={self.hit_points!r}, '
            f'damage={self.damage!r}, armor={self.armor!r})'
        )

    @classmethod
    def from_file(cls, name: str, fn: str) -> 'Character':
        return cls.from_lines(name, open(relative_path(__file__, fn)))

    @classmethod
    def from_lines(cls, name: str, lines: Iterable[str]) -> 'Character':
        lines = (line.strip() for line in lines)
        hit_points, = parse_line(next(lines), "Hit Points: $")
        damage, = parse_line(next(lines), "Damage: $")
        armor, = parse_line(next(lines), "Armor: $")
        return cls(name, hit_points=int(hit_points), damage=int(damage), armor=int(armor))

    def with_equipment(self, items: Iterable[Item]) -> 'Character':
        return type(self)(
            name=self.name,
            hit_points=self.hit_points,
            damage=self.damage + sum(item.damage for item in items),
            armor=self.armor + sum(item.armor for item in items)
        )


def battle(character_1: Character, character_2: Character, log: bool = False) -> Character:
    hp_1, hp_2 = character_1.hit_points, character_2.hit_points

    dmg_1 = max(character_1.damage - character_2.armor, 1)
    dmg_1_str = f"{character_1.damage}-{character_2.armor} = {dmg_1} damage"
    dmg_2 = max(character_2.damage - character_1.armor, 1)
    dmg_2_str = f"{character_2.damage}-{character_1.armor} = {dmg_2} damage"

    def log_state(attacker: Character, defender: Character, dmg_str: str, hps: int) -> None:
        hp_str = "hit point" if hps == 1 else "hit points"
        print(
            f"The {attacker.name} deals {dmg_str}; the {defender.name} goes down to {hps} {hp_str}."
        )

    while True:
        hp_2 -= dmg_1
        if log:
            log_state(character_1, character_2, dmg_1_str, hp_2)
        if hp_2 <= 0:
            return character_1

        hp_1 -= dmg_2
        if log:
            log_state(character_2, character_1, dmg_2_str, hp_1)
        if hp_1 <= 0:
            return character_2


def is_beating_boss(items: list[Item], boss: Character, player_hp: int):
    player = Character('player', hit_points=player_hp).with_equipment(items)
    winner = battle(player, boss)
    return winner is player


if __name__ == '__main__':
    boss_ = Character.from_file("boss", 'data/21-input.txt')
    PLAYER_HP = 100
    shop_ = Shop.from_file('data/21-shop.txt')

    part_1(boss_, PLAYER_HP, shop_)
    part_2(boss_, PLAYER_HP, shop_)
