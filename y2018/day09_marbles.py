"""
Advent of Code 2018
Day 9: Marble Mania
https://adventofcode.com/2018/day/9
"""

from tqdm import tqdm

from common.chain import Circle
from common.file import relative_path
from common.text import parse_line


def part_1(players_count: int, last_marble: int) -> int:
    """
    You talk to the Elves while you wait for your navigation system to initialize. To pass the time,
    they introduce you to their favorite marble game.

    The Elves play this game by taking turns arranging the marbles in a **circle** according to very
    particular rules. The marbles are numbered starting with `0` and increasing by `1` until every
    marble has a number.

    First, the marble numbered `0` is placed in the circle. At this point, while it contains only
    a single marble, it is still a circle: the marble is both clockwise from itself and counter-
    clockwise from itself. This marble is designated the **current marble**.

    Then, each Elf takes a turn placing the **lowest-numbered remaining marble** into the circle
    between the marbles that are `1` and `2` marbles **clockwise** of the current marble. (When the
    circle is large enough, this means that there is one marble between the marble that was just
    placed and the current marble.) The marble that was just placed then becomes the **current
    marble**.

    However, if the marble that is about to be placed has a number which is a multiple of `23`,
    **something entirely different happens**. First, the current player keeps the marble they would
    have placed, adding it to their **score**. In addition, the marble `7` marbles counter-clockwise
    from the current marble is **removed** from the circle and **also** added to the current
    player's score. The marble located immediately **clockwise** of the marble that was removed
    becomes the new current marble.

    For example, suppose there are 9 players. After the marble with value `0` is placed in the
    middle, each player (shown in square brackets) takes a turn. The result of each of those turns
    would produce circles of marbles like this, where clockwise is to the right and the resulting
    current marble on the first position:

        >>> example_score = game(players_count=9, last_marble=25, log=True)
        [-]  0
        [1]  1  0
        [2]  2  1  0
        [3]  3  0  2  1
        [4]  4  2  1  3  0
        [5]  5  1  3  0  4  2
        [6]  6  3  0  4  2  5  1
        [7]  7  0  4  2  5  1  6  3
        [8]  8  4  2  5  1  6  3  7  0
        [9]  9  2  5  1  6  3  7  0  8  4
        [1] 10  5  1  6  3  7  0  8  4  9  2
        [2] 11  1  6  3  7  0  8  4  9  2 10  5
        [3] 12  6  3  7  0  8  4  9  2 10  5 11  1
        [4] 13  3  7  0  8  4  9  2 10  5 11  1 12  6
        [5] 14  7  0  8  4  9  2 10  5 11  1 12  6 13  3
        [6] 15  0  8  4  9  2 10  5 11  1 12  6 13  3 14  7
        [7] 16  8  4  9  2 10  5 11  1 12  6 13  3 14  7 15  0
        [8] 17  4  9  2 10  5 11  1 12  6 13  3 14  7 15  0 16  8
        [9] 18  9  2 10  5 11  1 12  6 13  3 14  7 15  0 16  8 17  4
        [1] 19  2 10  5 11  1 12  6 13  3 14  7 15  0 16  8 17  4 18  9
        [2] 20 10  5 11  1 12  6 13  3 14  7 15  0 16  8 17  4 18  9 19  2
        [3] 21  5 11  1 12  6 13  3 14  7 15  0 16  8 17  4 18  9 19  2 20 10
        [4] 22 11  1 12  6 13  3 14  7 15  0 16  8 17  4 18  9 19  2 20 10 21  5
        [5] 19  2 20 10 21  5 22 11  1 12  6 13  3 14  7 15  0 16  8 17  4 18
        [6] 24 20 10 21  5 22 11  1 12  6 13  3 14  7 15  0 16  8 17  4 18 19  2
        [7] 25 10 21  5 22 11  1 12  6 13  3 14  7 15  0 16  8 17  4 18 19  2 24 20

    The goal is to be the **player with the highest score** after the last marble is used up.
    Assuming the example above ends after the marble numbered `25`, the winning score is `23+9=32`
    (because player 5 kept marble `23` and removed marble `9`, while no other player got any points
    in this very short example game).

    Here are a few more examples:

        >>> game(players_count=10, last_marble=1618)
        8317
        >>> game(players_count=13, last_marble=7999)
        146373
        >>> game(players_count=17, last_marble=1104)
        2764
        >>> game(players_count=21, last_marble=6111)
        54718

    **What is the winning Elf's score?**

        >>> part_1(players_count=30, last_marble=5807)
        part 1: winning Elf has score 37305
        37305
    """

    result = game(players_count, last_marble)
    print(f"part 1: winning Elf has score {result}")
    return result


def part_2(players_count: int, last_marble: int) -> int:
    """
    Amused by the speed of your answer, the Elves are curious:

    **What would the new winning Elf's score be if the number of the last marble were
    100 times larger?**

        >>> players, marble = parameters_from_line("30 players; last marble is worth 5807 points")
        >>> players, marble
        (30, 5807)
        >>> part_2(players_count=players, last_marble=marble * 100)
        part 2: winning Elf has score 320997431
        320997431
    """

    result = game(players_count, last_marble)
    print(f"part 2: winning Elf has score {result}")
    return result


def game(players_count: int, last_marble: int, log: bool | int = False) -> int:
    player_scores = {p: 0 for p in range(players_count)}

    marbles = Circle([0])
    current_player = 0

    if log:
        print("[-]  0")

    for turn in tqdm(range(1, last_marble + 1), unit=" turns", unit_scale=True, delay=0.5):
        # Each Elf takes a turn placing the lowest-numbered remaining marble into the circle
        new_marble = turn
        if new_marble % 23 != 0:
            # ... between the marbles that are 1 and 2 marbles clockwise of the current marble.
            marbles.insert(+1, new_marble)
        else:
            # However, if the marble that is about to be placed has a number
            # which is a multiple of 23, something entirely different happens.
            # First, the current player keeps the marble they would have placed,
            # adding it to their score.
            player_scores[current_player] += new_marble
            # In addition, the marble 7 marbles counter-clockwise from the current marble
            # is removed from the circle ...
            removed_marble = marbles.pop(-7)
            # ... and also added to the current player's score.
            player_scores[current_player] += removed_marble

        if log and turn % int(log) == 0:
            marbles_str = " ".join(f"{m.value:2}" for m in marbles)
            print(f"[{current_player + 1}] {marbles_str}")

        current_player = (current_player + 1) % players_count

    # return high score
    high_score = max(player_scores.values())
    # print(f"game(player_count={players_count}, last_marble={last_marble}) -> {high_score}")
    return high_score


def parameters_from_file(fn: str) -> tuple[int, int]:
    return parameters_from_line(open(relative_path(__file__, fn)).readline().strip())


def parameters_from_line(line: str) -> tuple[int, int]:
    # "123 players; last marble is worth 123456 points"
    players_count, last_marble = parse_line(line, "$ players; last marble is worth $ points")
    return int(players_count), int(last_marble)


if __name__ == '__main__':
    player_count_, last_marble_ = parameters_from_file('data/09-input.txt')
    part_1(player_count_, last_marble_)
    part_2(player_count_, last_marble_ * 100)
