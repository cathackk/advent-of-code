"""
Advent of Code 2018
Day 14: Chocolate Charts
https://adventofcode.com/2018/day/14
"""

from itertools import islice
from typing import Iterable

from tqdm import tqdm

from common.file import relative_path
from common.iteration import ifind


def part_1(recipes_count: int, scores_count: int = 10) -> str:
    """
    You finally have a chance to look at all of the produce moving around. Chocolate, cinnamon,
    mint, chili peppers, nutmeg, vanilla... the Elves must be growing these plants to make **hot
    chocolate**! As you realize this, you hear a conversation in the distance. When you go to
    investigate, you discover two Elves in what appears to be a makeshift underground
    kitchen/laboratory.

    The Elves are trying to come up with the ultimate hot chocolate recipe; they're even maintaining
    a scoreboard which tracks the quality **score** (`0`-`9`) of each recipe.

    Only two recipes are on the board: the first recipe got a score of `3`, the second, `7`. Each of
    the two Elves has a **current recipe**: the first Elf starts with the first recipe, and the
    second Elf starts with the second recipe.

    To create new recipes, the two Elves combine their current recipes. This creates new recipes
    from the **digits of the sum** of the current recipes' scores. With the current recipes' scores
    of `3` and `7`, their sum is `10`, and so two new recipes would be created: the first with score
    `1` and the second with score `0`:

        >>> combine_recipes(7, 3)
        [1, 0]

    If the current recipes' scores were `2` and `3`, the sum, `5`, would only create one recipe
    (with a score of `5`) with its single digit:

        >>> combine_recipes(2, 3)
        [5]

    The new recipes are added to the end of the scoreboard in the order they are created. So, after
    the first round, the scoreboard is `3`, `7`, `1`, `0`:

    After all new recipes are added to the scoreboard, each Elf picks a new current recipe. To do
    this, the Elf steps forward through the scoreboard a number of recipes equal to **1 plus the
    score of their current recipe**. So, after the first round, the first Elf moves forward
    `1 + 3 = 4` times, while the second Elf moves forward `1 + 7 = 8` times. If they run out of
    recipes, they loop back around to the beginning. After the first round, both Elves happen to
    loop around until they land on the same recipe that they had in the beginning; in general, they
    will move to different recipes.

    Drawing the first Elf as parentheses and the second Elf as square brackets, they continue this
    process:

        >>> first_20_scores = list(islice(score_sequence(log=True), 20))
        (3)[7]
        (3)[7] 1  0
         3  7  1 [0](1) 0
         3  7  1  0 [1] 0 (1)
        (3) 7  1  0  1  0 [1] 2
         3  7  1  0 (1) 0  1  2 [4]
         3  7  1 [0] 1  0 (1) 2  4  5
         3  7  1  0 [1] 0  1  2 (4) 5  1
         3 (7) 1  0  1  0 [1] 2  4  5  1  5
         3  7  1  0  1  0  1  2 [4](5) 1  5  8
         3 (7) 1  0  1  0  1  2  4  5  1  5  8 [9]
         3  7  1  0  1  0  1 [2] 4 (5) 1  5  8  9  1  6
         3  7  1  0  1  0  1  2  4  5 [1] 5  8  9  1 (6) 7
         3  7  1  0 (1) 0  1  2  4  5  1  5 [8] 9  1  6  7  7
         3  7 [1] 0  1  0 (1) 2  4  5  1  5  8  9  1  6  7  7  9
         3  7  1  0 [1] 0  1  2 (4) 5  1  5  8  9  1  6  7  7  9  2
        >>> first_20_scores
        [3, 7, 1, 0, 1, 0, 1, 2, 4, 5, 1, 5, 8, 9, 1, 6, 7, 7, 9, 2]

    The Elves think their skill will improve after making a few recipes (your puzzle input).
    However, that could take ages; you can speed this up considerably by identifying **the scores of
    the ten recipes** after that. For example:

        >>> scores_after(9)
        '5158916779'
        >>> scores_after(5)
        '0124515891'
        >>> scores_after(18)
        '9251071085'

    **What are the scores of the ten recipes immediately after the number of recipes in your puzzle
    input?**

        >>> part_1(2018)
        part 1: 10 recipes immediately after the first 2018 have scores 5941429882
        '5941429882'
    """

    result = scores_after(recipes_count)

    print(
        f"part 1: {scores_count} recipes immediately after the first {recipes_count} "
        f"have scores {result}"
    )
    return result


def part_2(scores_to_find: str) -> int:
    """
    As it turns out, you got the Elves' plan backwards. They actually want to know how many recipes
    appear on the scoreboard to the left of the first recipes whose scores are the digits from your
    puzzle input:

        >>> find_scores('51589')
        9
        >>> find_scores('01245')
        5
        >>> find_scores('92510')
        18
        >>> find_scores('59414')
        2018

    **How many recipes appear on the scoreboard to the left of the score sequence in your puzzle
    input?**

        >>> part_2('59414')
        part 2: sequence '59414' appears just after 2018 recipes
        2018
    """

    result = find_scores(scores_to_find)
    print(f"part 2: sequence {scores_to_find!r} appears just after {result} recipes")
    return result


def combine_recipes(score_1: int, score_2: int) -> list[int]:
    return [int(char) for char in str(score_1 + score_2)]


def score_sequence(initial: Iterable[int] = (3, 7), log: bool = False) -> Iterable[int]:
    scores = list(initial)
    pos_1, pos_2 = 0, 1

    def print_scores() -> None:
        def char(pos: int, score: int) -> str:
            if pos == pos_1:
                return f"({score})"
            elif pos == pos_2:
                return f"[{score}]"
            else:
                return f" {score} "
        print("".join(char(*ps) for ps in enumerate(scores)).rstrip())

    if log:
        print_scores()
    yield from scores

    while True:
        score_1, score_2 = scores[pos_1], scores[pos_2]
        scores.extend(new_scores := combine_recipes(score_1, score_2))
        pos_1 = (pos_1 + score_1 + 1) % len(scores)
        pos_2 = (pos_2 + score_2 + 1) % len(scores)

        if log:
            print_scores()
        yield from new_scores


def scores_after(recipes_count: int, scores_count: int = 10) -> str:
    return "".join(
        str(score)
        for score in islice(score_sequence(), recipes_count, recipes_count + scores_count)
    )


def find_scores(scores_to_find: str) -> int:
    return ifind(
        tqdm(score_sequence(), unit=" recipes", unit_scale=True, delay=0.5),
        (int(score) for score in scores_to_find)
    )


def input_from_file(fn: str) -> str:
    return open(relative_path(__file__, fn)).readline().strip()


if __name__ == '__main__':
    input_ = input_from_file('data/14-input.txt')
    part_1(recipes_count=int(input_))
    part_2(scores_to_find=input_)
