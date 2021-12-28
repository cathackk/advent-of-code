from itertools import combinations
from typing import Iterable
from typing import NamedTuple

from common.utils import maxk
from common.utils import mink


class Item(NamedTuple):
    name: str
    cost: int
    damage: int
    armor: int

    def __str__(self):
        return f"{self.name} (${self.cost})"


weapons = [
    Item("Dagger",      8, 4, 0),
    Item("Shortsword", 10, 5, 0),
    Item("Warhammer",  25, 6, 0),
    Item("Longsword",  40, 7, 0),
    Item("Greataxe",   74, 8, 0)
]
armors = [
    Item("Leather",    13, 0, 1),
    Item("Chainmail",  31, 0, 2),
    Item("Splintmail", 53, 0, 3),
    Item("Bandedmail", 75, 0, 4),
    Item("Platemail", 102, 0, 5)
]
rings = [
    Item("Damage +1",  25, 1, 0),
    Item("Damage +2",  50, 2, 0),
    Item("Damage +3", 100, 3, 0),
    Item("Defense +1", 20, 0, 1),
    Item("Defense +2", 40, 0, 2),
    Item("Defense +3", 80, 0, 3)
]


def generate_inventories() -> Iterable[list[Item]]:
    for weapon in weapons:
        yield [weapon]
        yield from ([weapon, ring] for ring in rings)
        yield from ([weapon, r1, r2] for r1, r2 in combinations(rings, 2))
        for armor in armors:
            yield [weapon, armor]
            yield from ([weapon, armor, ring] for ring in rings)
            yield from ([weapon, armor, r1, r2] for r1, r2 in combinations(rings, 2))


class Character(NamedTuple):
    hit_points: int
    damage: int
    armor: int

    def __str__(self):
        return f"HP={self.hit_points:3}, DM={self.damage:2}, AR={self.armor:2}"


def battle(player: Character, boss: Character) -> bool:
    hp_player = player.hit_points
    hp_boss = boss.hit_points

    while True:
        hp_boss -= max(player.damage - boss.armor, 1)
        if hp_boss <= 0:
            return True
        hp_player -= max(boss.damage - player.armor, 1)
        if hp_player <= 0:
            return False


def is_beating_boss(items: list[Item], boss: Character):
    return battle(
        player=Character(
            hit_points=100,
            damage=sum(item.damage for item in items),
            armor=sum(item.armor for item in items)
        ),
        boss=boss
    )


def part_1(boss: Character) -> int:
    inventory, cost = mink(
        (
            inventory
            for inventory in generate_inventories()
            if is_beating_boss(inventory, boss)
        ),
        key=lambda inv: sum(item.cost for item in inv)
    )
    print(f"part 1: min cost is {cost} ({' + '.join(str(item) for item in inventory)})")
    return cost


def part_2(boss: Character) -> int:
    inventory, cost = maxk(
        (
            inventory
            for inventory in generate_inventories()
            if not is_beating_boss(inventory, boss)
        ),
        key=lambda inv: sum(item.cost for item in inv)
    )
    print(f"part 2: max cost is {cost} ({' + '.join(str(item) for item in inventory)})")
    return cost


if __name__ == '__main__':
    b = Character(
        hit_points=100,
        damage=8,
        armor=2
    )
    part_1(b)
    part_2(b)
