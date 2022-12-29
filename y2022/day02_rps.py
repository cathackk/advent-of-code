"""
Advent of Code 2022
Day 2: Rock Paper Scissors
https://adventofcode.com/2022/day/2
"""

from typing import Iterable

from meta.aoc_tools import data_path


def part_1(rounds: Iterable[str]) -> int:
    """
    The Elves begin to set up camp on the beach. To decide whose tent gets to be closest to
    the snack storage, a giant Rock Paper Scissors tournament is already in progress.

    Rock Paper Scissors is a game between two players. Each game contains many rounds; in each
    round, the players each simultaneously choose one of Rock, Paper, or Scissors using a hand
    shape. Then, a winner for that round is selected: Rock defeats Scissors, Scissors defeats Paper,
    and Paper defeats Rock. If both players choose the same shape, the round instead ends in a draw.

    Appreciative of your help yesterday, one Elf gives you an **encrypted strategy guide** (your
    puzzle input) that they say will be sure to help you win. "The first column is what your
    opponent is going to play: `A` for Rock, `B` for Paper, and `C` for Scissors. The second
    column--" Suddenly, the Elf is called away to help with someone's tent.

    The second column, you reason, must be what you should play in response: `X` for Rock,
    `Y` for Paper, and `Z` for Scissors. Winning every time would be suspicious, so the responses
    must have been carefully chosen.

    The winner of the whole tournament is the player with the highest score. Your **total score** is
    the sum of your scores for each round. The score for a single round is the score for
    the **shape you selected** (1 for Rock, 2 for Paper, and 3 for Scissors) plus the score for
    the outcome of the round (0 if you lost, 3 if the round was a draw, and 6 if you won).

    Since you can't be sure if the Elf is trying to help you or trick you, you should calculate
    the score you would get if you were to follow the strategy guide.

    For example, suppose you were given the following strategy guide:

        >>> rnds = rounds_from_text('''
        ...     A Y
        ...     B X
        ...     C Z
        ... ''')

    This strategy guide predicts and recommends the following:

      - In the first round, your opponent will choose Rock (`A`), and you should choose Paper (`Y`).

        >>> rnds[0]
        'A Y'

        This ends in a win for you with a score of **8** (2 because you chose Paper + 6 because
        you won).

        >>> round_score(rnds[0])
        8

      - In the second round, your opponent will choose Paper (`B`) and you should choose Rock (`X`).
        This ends in a loss for you with a score of **1** (1 + 0).

        >>> rnds[1]
        'B X'
        >>> round_score(rnds[1])
        1

      - The third round is a draw with both players choosing Scissors,
        giving you a score of 3 + 3 = **6**.

        >>> rnds[2]
        'C Z'
        >>> round_score(rnds[2])
        6

    In this example, if you were to follow the strategy guide, you would get a total score of **15**
    (8 + 1 + 6).

        >>> total_score(rnds)
        15

    **What would your total score be if everything goes exactly according to your strategy guide?**

        >>> part_1(rnds)
        part 1: total score is 15
        15
    """

    result = total_score(rounds)

    print(f"part 1: total score is {result}")
    return result


def part_2(rounds: Iterable[str]) -> int:
    """
    The Elf finishes helping with the tent and sneaks back over to you. "Anyway, the second column
    says how the round needs to end: `X` means you need to lose, `Y` means you need to end the round
    in a draw, and `Z` means you need to win. Good luck!"

    The total score is still calculated in the same way, but now you need to figure out what shape
    to choose so the round ends as indicated. The example above now goes like this:

      - In the first round, your opponent will choose Rock (`A`), and you need the round to end in
        a draw (`Y`), so you also choose Rock. This gives you a score of 1 + 3 = **4**:

        >>> round_score(('A Y'), part=2)
        4

      - In the second round, your opponent will choose Paper (`B`), and you choose Rock, so you lose
        (`X`) with a score of 1 + 0 = **1**:

        >>> round_score(('B X'), part=2)
        1

      - In the third round, you will defeat your opponent's Scissors with Rock for a score of
        1 + 6 = **7**:

        >>> round_score(('C Z'), part=2)
        7

    Now that you're correctly decrypting the ultra top secret strategy guide, you would get a total
    score of **12**.

        >>> total_score(rnds := [('A Y'), ('B X'), ('C Z')], part=2)
        12

    Following the Elf's instructions for the second column, **what would your total score be if
    everything goes exactly according to your strategy guide?**

        >>> part_2(rnds)
        part 2: total score is 12
        12
    """

    result = total_score(rounds, part=2)

    print(f"part 2: total score is {result}")
    return result


OUTCOMES_PART_1 = {
    # (opp vs you)
    'A X': 4,  # R vs R -> draw -> 1 + 3 = 4
    'A Y': 8,  # R vs P -> win  -> 2 + 6 = 8
    'A Z': 3,  # R vs S -> loss -> 3 + 0 = 3
    'B X': 1,  # P vs R -> loss -> 1 + 0 = 1
    'B Y': 5,  # P vs P -> draw -> 2 + 3 = 5
    'B Z': 9,  # P vs S -> win  -> 3 + 6 = 9
    'C X': 7,  # S vs R -> win  -> 1 + 6 = 7
    'C Y': 2,  # S vs P -> loss -> 2 + 0 = 2
    'C Z': 6,  # S vs S -> draw -> 3 + 3 = 6
}
OUTCOMES_PART_2 = {
    # (opp vs outcome)
    'A X': 3,  # R vs loss -> S -> 3 + 0 = 3
    'A Y': 4,  # R vs draw -> R -> 1 + 3 = 4
    'A Z': 8,  # R vs win  -> P -> 2 + 6 = 8
    'B X': 1,  # P vs loss -> R -> 1 + 0 = 1
    'B Y': 5,  # P vs draw -> P -> 2 + 3 = 5
    'B Z': 9,  # P vs win  -> S -> 3 + 6 = 9
    'C X': 2,  # S vs loss -> P -> 2 + 0 = 2
    'C Y': 6,  # S vs draw -> S -> 3 + 3 = 6
    'C Z': 7,  # S vs win  -> R -> 1 + 6 = 7
}


def round_score(round_: str, part: int = 1) -> int:
    if part == 1:
        return OUTCOMES_PART_1[round_]
    elif part == 2:
        return OUTCOMES_PART_2[round_]
    else:
        raise ValueError('part must be 1 or 2')


def total_score(rounds: Iterable[str], part: int = 1) -> int:
    return sum(round_score(round_, part) for round_ in rounds)


def rounds_from_file(fn: str) -> list[str]:
    return [line.strip() for line in open(fn)]


def rounds_from_text(text: str) -> list[str]:
    return [line.strip() for line in text.strip().splitlines()]


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    rounds = rounds_from_file(input_path)
    result_1 = part_1(rounds)
    result_2 = part_2(rounds)
    return result_1, result_2


if __name__ == '__main__':
    main()
