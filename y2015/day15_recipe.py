from typing import Iterable
from typing import NamedTuple

from common.utils import maxk


class Ingredient(NamedTuple):
    name: str
    capacity: int
    durability: int
    flavor: int
    texture: int
    calories: int


def load_ingredients(fn: str) -> Iterable[Ingredient]:
    for line in open(fn):
        """
        Sprinkles: capacity 5, durability -1, flavor 0, texture 0, calories 5
        """
        name, data = line.strip().split(': ')
        data_parts = [d.split(' ') for d in data.split(', ')]
        data_names = [name for name, _ in data_parts]
        assert data_names == ["capacity", "durability", "flavor", "texture", "calories"]
        data_values = [int(value) for _, value in data_parts]
        yield Ingredient(name, *data_values)


def recipe_score(amounts: list[tuple[Ingredient, int]], required_calories: int = None) -> int:
    amounts = dict(amounts)
    capacity =   max(sum(i.capacity   * amount for i, amount in amounts.items()), 0)
    durability = max(sum(i.durability * amount for i, amount in amounts.items()), 0)
    flavor =     max(sum(i.flavor     * amount for i, amount in amounts.items()), 0)
    texture =    max(sum(i.texture    * amount for i, amount in amounts.items()), 0)

    score = capacity * durability * flavor * texture

    if required_calories is None:
        return score

    calories = sum(i.calories * amount for i, amount in amounts.items())
    return score if calories == required_calories else -1


def generate_recipes(
        ingredients: list[Ingredient],
        limit: int
) -> Iterable[list[tuple[Ingredient, int]]]:
    if len(ingredients) == 1:
        yield [(ingredients[0], limit)]
        return

    ingr = ingredients[0]
    for amount in range(limit+1):
        for subrecipe in generate_recipes(ingredients[1:], limit - amount):
            yield [(ingr, amount)] + subrecipe



def part_1(ingredients: list[Ingredient]) -> int:
    best_recipe, score = maxk(generate_recipes(ingredients, 100), key=recipe_score)
    best_recipe_d = {ingr.name: amount for ingr, amount in best_recipe}
    print(f"part 1: best recipe {best_recipe_d}, score {score}")
    return score


def part_2(ingredients: list[Ingredient]) -> int:
    best_recipe, score = maxk(
        generate_recipes(ingredients, 100),
        key=lambda r: recipe_score(r, required_calories=500)
    )
    best_recipe_d = {ingr.name: amount for ingr, amount in best_recipe}
    print(f"part 2: best recipe {best_recipe_d}, score {score}")
    return score


if __name__ == '__main__':
    ingredients = list(load_ingredients("data/15-input.txt"))
    part_1(ingredients)
    part_2(ingredients)
