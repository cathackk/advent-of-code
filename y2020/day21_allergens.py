"""
Advent of Code 2020
Day 21: Allergen Assessment
https://adventofcode.com/2020/day/21
"""

from typing import Dict
from typing import Iterable
from typing import Set

from utils import parse_line
from utils import single_value


def part_1(food_list: list['Food']) -> int:
    """
    You need a few days' worth of food for your journey. You don't speak the local language, so you
    can't read any ingredients lists. However, sometimes, allergens are listed in a language you do
    understand. You should be able to use this information to determine which ingredient contains
    which allergen and work out which foods are safe to take with you on your trip.

    You start by compiling a list of foods (your puzzle input), one food per line. Each line
    includes that food's ingredients list followed by some or all of the allergens the food
    contains.

    Each allergen is found in exactly one ingredient. Each ingredient contains zero or one
    allergen. *Allergens aren't always marked*; when they're listed (as in
    `(contains nuts, shellfish)` after an ingredients list), the ingredient that contains each
    listed allergen will be *somewhere in the corresponding ingredients list*. However, even if an
    allergen isn't listed, the ingredient that contains that allergen could still be present: maybe
    they forgot to label it, or maybe it was labeled in a language you don't know.

    For example, consider the following list of foods:

        >>> foods = foods_from_text('''
        ...     mxmxvkd kfcds sqjhc nhms (contains dairy, fish)
        ...     trh fvjkl sbzzf mxmxvkd (contains dairy)
        ...     sqjhc fvjkl (contains soy)
        ...     sqjhc mxmxvkd sbzzf (contains fish)
        ... ''')
        >>> len(foods)
        4

    The first food in the list has four ingredients (written in a language you don't understand):

        >>> foods[0].ingredients
        ['mxmxvkd', 'kfcds', 'sqjhc', 'nhms']

    While the food might contain other allergens, a few allergens the food definitely contains are
    listed afterward:

        >>> foods[0].allergens
        ['dairy', 'fish']

    The first step is to determine which ingredients *can't possibly* contain any of the allergens
    in any food in your list. In the above example, none of the ingredients `kfcds`, `nhms`,
    `sbzzf`, or `trh` can contain an allergen.

        >>> matched_ingrs = set(ingr for ingr, _ in match_allergens(foods))
        >>> all_ingrs = set(ingr for f in foods for ingr in f.ingredients)
        >>> sorted(all_ingrs - matched_ingrs)
        ['kfcds', 'nhms', 'sbzzf', 'trh']

    Counting the number of times any of these ingredients appear in any ingredients list produces
    *5*: they all appear once each except `sbzzf`, which appears twice.

        >>> sum(1 for f in foods for ingr in f.ingredients if ingr not in matched_ingrs)
        5

    Determine which ingredients cannot possibly contain any of the allergens in your list.
    *How many times do any of those ingredients appear?*

        >>> part_1(foods)
        part 1: ingredients without allergens appear 5 times
        5
    """

    matched_ingredients = set(ingr for ingr, _ in match_allergens(food_list))
    result = sum(
        1
        for food in food_list
        for ingr in food.ingredients
        if ingr not in matched_ingredients
    )

    print(f"part 1: ingredients without allergens appear {result} times")
    return result


def part_2(food_list: list['Food']) -> str:
    r"""
    Now that you've isolated the inert ingredients, you should have enough information to figure
    out which ingredient contains which allergen.

    In the above example:

        >>> foods = foods_from_text('''
        ...     mxmxvkd kfcds sqjhc nhms (contains dairy, fish)
        ...     trh fvjkl sbzzf mxmxvkd (contains dairy)
        ...     sqjhc fvjkl (contains soy)
        ...     sqjhc mxmxvkd sbzzf (contains fish)
        ... ''')
        >>> m = dict(match_allergens(foods))
        >>> print("\n".join(f"- {ingr!r} contains {alrg!r}." for ingr, alrg in m.items()))
        - 'mxmxvkd' contains 'dairy'.
        - 'sqjhc' contains 'fish'.
        - 'fvjkl' contains 'soy'.

    Arrange the ingredients *alphabetically by their allergen* and separate them by commas to
    produce your *canonical dangerous ingredient list*.

        >>> ",".join(sorted(m.keys(), key=m.get))
        'mxmxvkd,sqjhc,fvjkl'

    Time to stock your raft with supplies. *What is your canonical dangerous ingredient list?*

        >>> part_2(foods)
        part 2: ingredient list: mxmxvkd,sqjhc,fvjkl
        'mxmxvkd,sqjhc,fvjkl'
    """

    i2a = dict(match_allergens(food_list))
    result = ",".join(sorted(i2a.keys(), key=i2a.get))

    print(f"part 2: ingredient list: {result}")
    return result


Ingredient = str
Allergen = str


class Food:
    def __init__(self, ingredients: Iterable[Ingredient], allergens: Iterable[Allergen]):
        self.ingredients = list(ingredients)
        self.allergens = list(allergens)

    @classmethod
    def from_line(cls, line: str):
        # mxmxvkd kfcds sqjhc nhms (contains dairy, fish)
        ingredients, allergens = parse_line(line, "$ (contains $)")
        return cls(ingredients.split(" "), allergens.split(", "))


def match_allergens(foods: list[Food]) -> Iterable[tuple[Ingredient, Allergen]]:
    # initialize unmatched allergens and their possible ingredients
    unmatched_a2is: Dict[Allergen, Set[Ingredient]] = dict()
    for food in foods:
        for allergen in food.allergens:
            if allergen not in unmatched_a2is:
                unmatched_a2is[allergen] = set(food.ingredients)
            else:
                unmatched_a2is[allergen] = unmatched_a2is[allergen] & set(food.ingredients)

    # then
    while unmatched_a2is:
        # find allergen with only one possible ingredient match
        m_ingredient, m_allergen = next(
            (single_value(ingrs), allergen)
            for allergen, ingrs in unmatched_a2is.items()
            if len(ingrs) == 1
        )
        yield m_ingredient, m_allergen

        # mark both as matched
        del unmatched_a2is[m_allergen]
        for ingredients in unmatched_a2is.values():
            ingredients.discard(m_ingredient)


def foods_from_file(fn: str) -> list[Food]:
    return list(foods_from_lines(open(fn)))


def foods_from_text(text: str) -> list[Food]:
    return list(foods_from_lines(text.strip().split("\n")))


def foods_from_lines(lines: Iterable[str]) -> Iterable[Food]:
    return (Food.from_line(line.strip()) for line in lines)


if __name__ == '__main__':
    food_list_ = foods_from_file("data/21-input.txt")
    assert len(food_list_) == 42

    part_1(food_list_)
    part_2(food_list_)
