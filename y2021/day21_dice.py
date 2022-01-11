"""
Advent of Code 2021
Day 21: Dirac Dice
https://adventofcode.com/2021/day/21
"""

import itertools
from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from common.utils import parse_line
from common.utils import relative_path


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

        >>> p1_start, p2_start = start_from_text('''
        ...     Player 1 starting position: 4
        ...     Player 2 starting position: 8
        ... ''')
        >>> p1_start, p2_start
        (4, 8)

    This is how the game would go:

        >>> gr = play(p1_start, p2_start, die_sides=100, target_score=1000, log=True)
        ... # doctest: +ELLIPSIS
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
        GameResult(player_1_score=1000, player_2_score=745, die_rolls=993)
        >>> gr.winner, gr.loser, gr.winner_score, gr.loser_score
        (1, 2, 1000, 745)
        >>> gr.loser_score * gr.die_rolls
        739785

    Play a practice game using the deterministic 100-sided die. The moment either player wins,
    **what do you get if you multiply the score of the losing player by the number of times the die
    was rolled during the game?**

        >>> part_1(p1_start, p2_start)
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
        QuantumGameResult(player_1_wins=444356092776315, player_2_wins=341960390180808)
        >>> gr.multiverse_winner, gr.multiverse_loser, gr.multiverse_winner_wins
        (1, 2, 444356092776315)

    Using your given starting positions, determine every possible outcome. **Find the player that
    wins in more universes; in how many universes does that player win?**

        >>> part_2(4, 8)
        part 2: player 1 wins in 444356092776315 universes
        444356092776315
    """

    outcome = play_quantum(player_1_start, player_2_start, target_score=21, die_sides=3)
    result = outcome.multiverse_winner_wins

    print(f"part 2: player {outcome.multiverse_winner} wins in {result} universes")
    return result


@dataclass(frozen=True)
class PlayerState:
    pos: int
    score: int

    def after_turn(self, roll_sum: int, board_size: int) -> 'PlayerState':
        return PlayerState(
            pos=(new_pos := 1 + (self.pos + roll_sum - 1) % board_size),
            score=self.score + new_pos
        )


@dataclass(frozen=True)
class GameState:
    p1_state: PlayerState
    p2_state: PlayerState
    winner: int | None = None

    @classmethod
    def initial(cls, p1_position: int, p2_position: int) -> 'GameState':
        return cls(
            p1_state=PlayerState(pos=p1_position, score=0),
            p2_state=PlayerState(pos=p2_position, score=0)
        )

    def state_for(self, player: int):
        if player == 1:
            return self.p1_state
        elif player == 2:
            return self.p2_state
        else:
            raise ValueError(player)

    def after_turn(self, active_player: int, roll: int, board_size: int, target_score: int):
        assert self.winner is None

        if active_player == 1:
            return GameState(
                p1_state=(new_p1_state := self.p1_state.after_turn(roll, board_size)),
                p2_state=self.p2_state,
                winner=1 if new_p1_state.score >= target_score else None
            )

        elif active_player == 2:
            return GameState(
                p1_state=self.p1_state,
                p2_state=(new_p2_state := self.p2_state.after_turn(roll, board_size)),
                winner=2 if new_p2_state.score >= target_score else None
            )

        else:
            raise ValueError(active_player)

    def _key(self) -> tuple:
        if self.winner is None:
            return self.p1_state, self.p2_state
        else:
            # all universes with winner=1 (or winner=2) are the same
            # ie. states are ignored if there is a winner
            return (self.winner,)

    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and self._key() == other._key()

    def __hash__(self) -> int:
        return hash(self._key())


@dataclass(frozen=True)
class GameResult:
    player_1_score: int
    player_2_score: int
    die_rolls: int

    @property
    def winner(self) -> int:
        return 1 if self.player_1_score > self.player_2_score else 2

    @property
    def loser(self) -> int:
        return 1 if self.player_1_score < self.player_2_score else 2

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
    board_size: int = 10,
    starting_player: int = 1,
    log: bool = False
) -> GameResult:
    assert 1 <= player_1_start <= board_size
    assert 1 <= player_2_start <= board_size
    assert target_score > 0
    assert die_sides > 0
    assert die_rolls_per_turn > 0
    assert board_size > 1
    assert starting_player in (1, 2)

    game = GameState.initial(player_1_start, player_2_start)
    die_rolls_count = 0
    active_player = starting_player

    while True:
        rolls = tuple(1 + (die_rolls_count + n) % die_sides for n in range(die_rolls_per_turn))
        die_rolls_count += die_rolls_per_turn

        game = game.after_turn(
            active_player=active_player,
            roll=sum(rolls),
            board_size=board_size,
            target_score=target_score,
        )

        if game.winner is not None:
            final_state = game.state_for(active_player)
            if log:
                print(
                    f"Player {active_player} rolls {_rolls_str(rolls)} "
                    f"and moves to space {final_state.pos} "
                    f"for a final score, {final_state.score}."
                )
            return GameResult(
                player_1_score=game.p1_state.score,
                player_2_score=game.p2_state.score,
                die_rolls=die_rolls_count,
            )

        if log:
            current_state = game.state_for(active_player)
            print(
                f"Player {active_player} rolls {_rolls_str(rolls)} "
                f"and moves to space {current_state.pos} "
                f"for a total score of {current_state.score}."
            )

        active_player = 1 + active_player % 2


@dataclass(frozen=True)
class QuantumGameResult:
    player_1_wins: int
    player_2_wins: int

    @property
    def multiverse_winner(self) -> int:
        assert self.player_1_wins != self.player_2_wins
        return 1 if self.player_1_wins > self.player_2_wins else 2

    @property
    def multiverse_loser(self) -> int:
        assert self.player_1_wins != self.player_2_wins
        return 1 if self.player_1_wins < self.player_2_wins else 2

    @property
    def multiverse_winner_wins(self) -> int:
        return self.player_1_wins if self.multiverse_winner == 1 else self.player_2_wins

    @property
    def multiverse_loser_wins(self) -> int:
        return self.player_1_wins if self.multiverse_loser == 1 else self.player_2_wins


# pylint: disable=too-many-locals
def play_quantum(
    player_1_start: int,
    player_2_start: int,
    target_score: int,
    die_sides: int,
    die_rolls_per_turn: int = 3,
    board_size: int = 10,
    starting_player: int = 1
) -> QuantumGameResult:
    assert 1 <= player_1_start <= board_size
    assert 1 <= player_2_start <= board_size
    assert target_score > 0
    assert die_sides > 0
    assert die_rolls_per_turn > 0
    assert board_size > 1
    assert starting_player in (1, 2)

    roll_sum_probs = Counter(
        sum(rolls)
        for rolls in itertools.product(range(1, die_sides + 1), repeat=die_rolls_per_turn)
    )

    # at the start there is only one universe
    initial_universe = GameState.initial(player_1_start, player_2_start)
    universe_counts: Counter[GameState] = Counter({initial_universe: 1})

    # split the universes one turn at a time
    for turn in itertools.count(0):
        active_player = 1 + (starting_player + turn - 1) % 2
        new_universe_counts: Counter[GameState] = Counter()
        any_split = False

        # split each universe without a winner
        for universe, universe_quantity in universe_counts.items():
            if universe.winner is None:
                for roll, roll_quantity in roll_sum_probs.items():
                    new_universe = universe.after_turn(
                        active_player=active_player,
                        roll=roll,
                        board_size=board_size,
                        target_score=target_score,
                    )
                    new_universe_counts[new_universe] += universe_quantity * roll_quantity
                any_split = True
            else:
                # already has a winner, just copy
                new_universe_counts[universe] += universe_quantity

        if not any_split:
            # no more universe splits -> we are done
            break

        universe_counts = new_universe_counts

    # evaluation
    wins_count = Counter()
    for universe, quantity in universe_counts.items():
        wins_count[universe.winner] += quantity

    assert len(wins_count) == 2

    return QuantumGameResult(player_1_wins=wins_count[1], player_2_wins=wins_count[2])


def start_from_text(text: str) -> tuple[int, int]:
    return start_from_lines(text.strip().split('\n'))


def start_from_file(fn: str) -> tuple[int, int]:
    return start_from_lines(open(relative_path(__file__, fn)))


def start_from_lines(lines: Iterable[str]) -> tuple[int, int]:
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
