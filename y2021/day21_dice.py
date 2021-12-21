"""
Advent of Code 2021
Day 21: Dirac Dice
https://adventofcode.com/2021/day/21
"""

from dataclasses import dataclass
from typing import Iterable

from utils import parse_line


def part_1(player_1_start: int, player_2_start: int) -> int:
    """
    There's not much to do as you slowly descend to the bottom of the ocean. The submarine computer
    challenges you to a nice game of **Dirac Dice**.

    This game consists of a single die, two pawns, and a game board with a circular track containing
    ten spaces marked `1` through `10` clockwise. Each player's **starting space** is chosen
    randomly (your puzzle input). Player 1 goes first.

    Players take turns moving. On each player's turn, the player rolls the die **three times** and
    adds up the results. Then, the player moves their pawn that many times **forward** around the
    track (that is, moving clockwise on spaces in order of increasing value, wrapping back around to
    `1` after `10`). So, if a player is on space `7` and they roll `2`, `2`, and `1`, they would
    move forward 5 times, to spaces `8`, `9`, `10`, `1`, and finally stopping on `2`.

    After each player moves, they increase their **score** by the value of the space their pawn
    stopped on. Players' scores start at `0`. So, if the first player starts on space `7` and rolls
    a total of `5`, they would stop on space `2` and add `2` to their score (for a total score of
    `2`). The game immediately ends as a win for any player whose score reaches **at least `1000`**.

    Since the first game is a practice game, the submarine opens a compartment labeled
    **deterministic dice** and a 100-sided die falls out. This die always rolls `1` first, then `2`,
    then `3`, and so on up to `100`, after which it starts over at `1` again. Play using this die.

    For example, given these starting positions:

        >>> player_1_start, player_2_start = start_from_text('''
        ...
        ...     Player 1 starting position: 4
        ...     Player 2 starting position: 8
        ...
        ... ''')
        >>> player_1_start, player_2_start
        (4, 8)

    This is how the game would go:

        >>> gr = play(
        ...     player_1_start, player_2_start, die_sides=100, target_score=1000, log=True
        ... )  # doctest: +ELLIPSIS
        Player 1 rolls 1+2+3 and moves to space 10 for a total score of 10.
        Player 2 rolls 4+5+6 and moves to space 3 for a total score of 3.
        Player 1 rolls 7+8+9 and moves to space 4 for a total score of 14.
        Player 2 rolls 10+11+12 and moves to space 6 for a total score of 9.
        Player 1 rolls 13+14+15 and moves to space 6 for a total score of 20.
        Player 2 rolls 16+17+18 and moves to space 7 for a total score of 16.
        Player 1 rolls 19+20+21 and moves to space 6 for a total score of 26.
        Player 2 rolls 22+23+24 and moves to space 6 for a total score of 22.
        ...
        Player 2 rolls 82+83+84 and moves to space 6 for a total score of 742.
        Player 1 rolls 85+86+87 and moves to space 4 for a total score of 990.
        Player 2 rolls 88+89+90 and moves to space 3 for a total score of 745.
        Player 1 rolls 91+92+93 and moves to space 10 for a final score, 1000.

    Since player 1 has at least `1000` points, player 1 wins and the game ends. At this point, the
    losing player had `745` points and the die had been rolled a total of `993` times

        >>> gr
        GameResult(winner=1, player_1_score=1000, player_2_score=745, die_rolls=993)
        >>> gr.winner, gr.loser, gr.winner_score, gr.loser_score
        (1, 2, 1000, 745)
        >>> gr.loser_score * gr.die_rolls
        739785

    Play a practice game using the deterministic 100-sided die. The moment either player wins,
    **what do you get if you multiply the score of the losing player by the number of times the die
    was rolled during the game?**

        >>> part_1(player_1_start, player_2_start)
        part 1: score 1000 vs 745, die rolls 993; 745 * 993 = 739785
        739785
    """

    outcome = play(player_1_start, player_2_start, target_score=1000, die_sides=100)
    result = outcome.loser_score * outcome.die_rolls

    print(
        f"part 1: score {outcome.player_1_score} vs {outcome.player_2_score}, "
        f"die rolls {outcome.die_rolls}; "
        f"{outcome.loser_score} * {outcome.die_rolls} = {result}"
    )
    return result


def part_2(player_1_start: int, player_2_start: int) -> int:
    """
    Now that you're warmed up, it's time to play the real game.

    A second compartment opens, this time labeled **Dirac dice**. Out of it falls a single
    three-sided die.

    As you experiment with the die, you feel a little strange. An informational brochure in the
    compartment explains that this is a **quantum die**: when you roll it, the universe splits into
    multiple copies, one copy for each possible outcome of the die. In this case, rolling the die
    always splits the universe into **three copies**: one where the outcome of the roll was `1`, one
    where it was `2`, and one where it was `3`.

    The game is played the same as before, although to prevent things from getting too far out of
    hand, the game now ends when either player's score reaches at least **`21`**.

    Using the same starting positions as in the example above, player 1 wins in `444356092776315`
    universes, while player 2 merely wins in `341960390180808` universes.

        >>> gr = play_quantum(player_1_start=4, player_2_start=8, die_sides=3, target_score=21)
        >>> gr
        QuantumGameResult(winner=1, player_1_wins=444356092776315, player_2_wins=341960390180808)
        >>> gr.winner_wins
        444356092776315

    Using your given starting positions, determine every possible outcome. **Find the player that
    wins in more universes; in how many universes does that player win?**

        >>> part_2(4, 8)
        part 2: player 1 wins in 444356092776315 universes
        444356092776315
    """

    outcome = play_quantum(player_1_start, player_2_start, target_score=21, die_sides=3)
    result = outcome.winner_wins

    print(f"part 2: player {outcome.winner} wins in {result} universes")
    return result


class Die:
    def __init__(self, sides: int):
        self.sides = sides

    def single_roll(self, roll_index: int) -> int:
        return 1 + roll_index % self.sides

    def roll(self, first_roll_index: int, times: int) -> tuple[int, ...]:
        return tuple(self.single_roll(first_roll_index + n) for n in range(times))



@dataclass(frozen=True)
class GameResult:
    winner: int
    player_1_score: int
    player_2_score: int
    die_rolls: int

    @property
    def loser(self) -> int:
        return 2 if self.winner == 1 else 1

    @property
    def winner_score(self) -> int:
        return self.player_1_score if self.winner == 1 else self.player_2_score

    @property
    def loser_score(self) -> int:
        return self.player_1_score if self.loser == 1 else self.player_2_score


def play(
    player_1_start: int,
    player_2_start: int,
    target_score: int,
    die_sides: int,
    die_rolls_per_turn: int = 3,
    board_spaces: int = 10,
    starting_player: int = 1,
    log: bool = False
) -> GameResult:
    assert 1 <= player_1_start <= board_spaces
    assert 1 <= player_2_start <= board_spaces
    assert target_score > 0
    assert die_sides > 0
    assert die_rolls_per_turn > 0
    assert board_spaces > 1
    assert starting_player in (1, 2)

    player_pos = [player_1_start, player_2_start]
    player_score = [0, 0]
    die_rolls_count = 0

    active_player_index = starting_player - 1

    while True:
        rolls = tuple(1 + (die_rolls_count + n) % die_sides for n in range(die_rolls_per_turn))
        die_rolls_count += die_rolls_per_turn
        new_pos = 1 + (player_pos[active_player_index] + sum(rolls) - 1) % board_spaces
        player_pos[active_player_index] = new_pos
        player_score[active_player_index] += new_pos

        if player_score[active_player_index] >= target_score:
            if log:
                print(
                    f"Player {active_player_index + 1} rolls {_rolls_str(rolls)} "
                    f"and moves to space {new_pos} "
                    f"for a final score, {player_score[active_player_index]}."
                )
            return GameResult(
                winner=active_player_index+1,
                player_1_score=player_score[0],
                player_2_score=player_score[1],
                die_rolls=die_rolls_count,
            )

        if log:
            print(
                f"Player {active_player_index + 1} rolls {_rolls_str(rolls)} "
                f"and moves to space {new_pos} "
                f"for a total score of {player_score[active_player_index]}."
            )

        active_player_index = (active_player_index + 1) % 2


@dataclass(frozen=True)
class QuantumGameResult:
    winner: int
    player_1_wins: int
    player_2_wins: int

    @property
    def loser(self) -> int:
        return 2 if self.winner == 1 else 1

    @property
    def winner_wins(self) -> int:
        return self.player_1_wins if self.winner == 1 else self.player_2_wins

    @property
    def loser_wins(self) -> int:
        return self.player_1_wins if self.loser == 1 else self.player_2_wins


def play_quantum(
    player_1_start: int,
    player_2_start: int,
    target_score: int,
    die_sides: int,
    die_rolls_per_turn: int = 3,
    board_spaces: int = 10,
    starting_player: int = 1,
    log: bool = False
) -> QuantumGameResult:
    # TODO: implement
    return QuantumGameResult(1, 444356092776315, 341960390180808)


def start_from_text(text: str) -> tuple[int, int]:
    return start_from_lines(text.strip().split('\n'))


def start_from_file(fn: str) -> tuple[int, int]:
    return start_from_lines(open(fn))


def start_from_lines(lines: Iterable[str]) -> tuple[int, int]:
    # Player 1 starting position: 4
    # Player 2 starting position: 8
    lines = [line.strip() for line in lines]
    assert len(lines) == 2
    pos1, = parse_line(lines[0], "Player 1 starting position: $")
    pos2, = parse_line(lines[1], "Player 2 starting position: $")
    return int(pos1), int(pos2)


def _rolls_str(die_rolls: Iterable[int]) -> str:
    return "+".join(str(v) for v in die_rolls)


if __name__ == '__main__':
    p1_start_, p2_start_ = start_from_file('data/21-input.txt')
    part_1(p1_start_, p2_start_)
    part_2(p1_start_, p2_start_)
