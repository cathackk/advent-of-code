"""
Advent of Code 2015
Day 15: Science for Hungry People
https://adventofcode.com/2015/day/15
"""

import math
from typing import Iterable, Self

from common.iteration import maxk
from common.text import parse_line
from meta.aoc_tools import data_path


def part_1(ingredients: list['Ingredient']) -> int:
    """
    Today, you set out on the task of perfecting your milk-dunking cookie recipe. All you have to
    do is find the right balance of ingredients.

    Your recipe leaves room for exactly `100` teaspoons of ingredients. You make a list of the
    **remaining ingredients you could use to finish the recipe** (your puzzle input) and their
    **properties per teaspoon**:

      - `capacity` (how well it helps the cookie absorb milk)
      - `durability` (how well it keeps the cookie intact when full of milk)
      - `flavor` (how tasty it makes the cookie)
      - `texture` (how it improves the feel of the cookie)
      - `calories` (how many calories it adds to the cookie)

    You can only measure ingredients in whole-teaspoon amounts accurately, and you have to be
    accurate so you can reproduce your results in the future. The **total score** of a cookie can be
    found by adding up each of the properties (negative totals become `0`) and then multiplying
    together everything except calories.

    For instance, suppose you have these two ingredients:

        >>> butterscotch, cinnamon = ingredients_from_text('''
        ...     Butterscotch: capacity -1, durability -2, flavor 6, texture 3, calories 8
        ...     Cinnamon: capacity 2, durability 3, flavor -2, texture -1, calories 3
        ... ''')
        >>> butterscotch
        Ingredient('Butterscotch', capacity=-1, durability=-2, flavor=6, texture=3, calories=8)
        >>> cinnamon
        Ingredient('Cinnamon', capacity=2, durability=3, flavor=-2, texture=-1, calories=3)

    Then, choosing to use `44` teaspoons of butterscotch and `56` teaspoons of cinnamon (because the
    amounts of each ingredient must add up to `100`) would result in a cookie with the following
    properties:

      - A `capacity`   of `44*-1 + 56* 2 =  68`
      - A `durability` of `44*-2 + 56* 3 =  80`
      - A `flavor`     of `44* 6 + 56*-2 = 152`
      - A `texture`    of `44* 3 + 56*-1 =  76`

    Multiplying these together (`68 * 80 * 152 * 76`, ignoring `calories` for now) results in
    a total score of `62842880`, which happens to be the best score possible given these
    ingredients.

        >>> recipe_score({butterscotch: 44, cinnamon: 56})
        62842880

    If any properties had produced a negative total, it would have instead become zero,
    causing the whole score to multiply to zero.

        >>> recipe_score({butterscotch: 66, cinnamon: 34})
        0

    Given the ingredients in your kitchen and their properties, what is the **total score** of the
    highest-scoring cookie you can make?

        >>> part_1([butterscotch, cinnamon])
        part 1: best recipe (44 Butterscotch, 56 Cinnamon) has score 62842880
        62842880
    """

    best_recipe, score = maxk(generate_recipes(ingredients, 100), key=recipe_score)
    print(f"part 1: best recipe ({recipe_str(best_recipe)}) has score {score}")
    return score


def part_2(ingredients: list['Ingredient'], calories: int = 500) -> int:
    """
    Your cookie recipe becomes wildly popular! Someone asks if you can make another recipe that has
    exactly `500` calories per cookie (so they can use it as a meal replacement). Keep the rest of
    your award-winning process the same (`100` teaspoons, same ingredients, same scoring system).

    For example, given the ingredients above, if you had instead selected `40` teaspoons of
    butterscotch and `60` teaspoons of cinnamon (which still adds to `100`), the total calorie count
    would be `40*8 + 60*3 = 500`. The total score would go down, though: only `57600000`, the best
    you can do in such trying circumstances.

        >>> butterscotch, cinnamon = ingredients_from_file(data_path(__file__, 'example.txt'))
        >>> recipe_score({butterscotch: 40, cinnamon: 60}, required_calories=500)
        57600000
        >>> recipe_score({butterscotch: 44, cinnamon: 56}, required_calories=500)
        -1

    Given the ingredients in your kitchen and their properties, what is the **total score** of the
    highest-scoring cookie you can make with a calorie total of `500`?

        >>> part_2([butterscotch, cinnamon])
        part 2: best recipe with 500 calories (40 Butterscotch, 60 Cinnamon) has score 57600000
        57600000
    """

    best_recipe, score = maxk(
        generate_recipes(ingredients, 100),
        key=lambda r: recipe_score(r, required_calories=calories)
    )
    print(
        f"part 2: best recipe with {calories} calories ({recipe_str(best_recipe)}) "
        f"has score {score}"
    )
    return score


class Ingredient:
    # pylint: disable=too-many-positional-arguments
    def __init__(self, name, capacity, durability, flavor, texture, calories):
        self.name = str(name)
        self.capacity = int(capacity)
        self.durability = int(durability)
        self.flavor = int(flavor)
        self.texture = int(texture)
        self.calories = int(calories)

    def attrs(self) -> Iterable[tuple[str, int]]:
        return (
            (attr, getattr(self, attr))
            for attr in ['capacity', 'durability', 'flavor', 'texture', 'calories']
        )

    def __repr__(self) -> str:
        attrs_repr = ', '.join(f'{key}={value!r}' for key, value in self.attrs())
        return f'{type(self).__name__}({self.name!r}, {attrs_repr})'

    def __str__(self) -> str:
        attrs_str = ", ".join(f"{key} {value}" for key, value in self.attrs())
        return f"{self.name}: {attrs_str}"

    @classmethod
    def from_str(cls, line: str) -> Self:
        args = parse_line(line, "$: capacity $, durability $, flavor $, texture $, calories $")
        # pylint: disable=no-value-for-parameter
        return cls(*args)


def recipe_score(amounts: Iterable[tuple[Ingredient, int]], required_calories: int = None) -> int:
    amounts_dict = dict(amounts)
    score = math.prod(
        max(sum(getattr(i, attr) * amount for i, amount in amounts_dict.items()), 0)
        for attr in ['capacity', 'durability', 'flavor', 'texture']
    )

    if required_calories is None:
        return score

    calories = sum(i.calories * amount for i, amount in amounts_dict.items())
    return score if calories == required_calories else -1


def recipe_str(recipe: Iterable[tuple[Ingredient, int]]) -> str:
    return ", ".join(f"{amount} {ingr.name}" for ingr, amount in recipe)


def generate_recipes(
    ingredients: list[Ingredient],
    limit: int
) -> Iterable[list[tuple[Ingredient, int]]]:
    if len(ingredients) == 1:
        return ([(ingredients[0], limit)],)

    return (
        [(ingredients[0], amount)] + subrecipe
        for amount in range(limit + 1)
        for subrecipe in generate_recipes(ingredients[1:], limit - amount)
    )


def ingredients_from_text(text: str) -> list[Ingredient]:
    return list(ingredients_from_lines(text.strip().splitlines()))


def ingredients_from_file(fn: str) -> list[Ingredient]:
    return list(ingredients_from_lines(open(fn)))


def ingredients_from_lines(lines: Iterable[str]) -> Iterable[Ingredient]:
    return (Ingredient.from_str(line.strip()) for line in lines)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    ingredients = ingredients_from_file(input_path)
    result_1 = part_1(ingredients)
    result_2 = part_2(ingredients)
    return result_1, result_2


if __name__ == '__main__':
    main()
