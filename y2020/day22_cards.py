"""
Advent of Code 2020
Day 22: Crab Combat
https://adventofcode.com/2020/day/22
"""

from dataclasses import dataclass
from typing import Iterable
from typing import Optional

from common.chain import Link
from common.utils import line_groups
from common.utils import relative_path


def part_1(deck_1: 'Deck', deck_2: 'Deck', print_progress: bool = False) -> int:
    """
    Before the game starts, split the cards so each player has their own deck (your puzzle input).
    Then, the game consists of a series of *rounds*: both players draw their top card, and the
    player with the higher-valued card wins the round. The winner keeps both cards, placing them on
    the bottom of their own deck so that the winner's card is above the other card. If this causes
    a player to have all of the cards, they win, and the game ends.

    For example, consider the following starting decks:

        >>> d1, d2 = decks_from_text('''
        ...     Player 1:
        ...     9
        ...     2
        ...     6
        ...     3
        ...     1
        ...
        ...     Player 2:
        ...     5
        ...     8
        ...     4
        ...     7
        ...     10
        ... ''')

    This means that player 1's deck contains 5 cards, with `9` on top and `1` on the bottom:

        >>> d1
        Deck([9, 2, 6, 3, 1])
        >>> len(d1), d1.peek_top(), d1.peek_bottom()
        (5, 9, 1)

    Player 2's deck also contains 5 cards, with `5` on top and `10` on the bottom:

        >>> d2
        Deck([5, 8, 4, 7, 10])
        >>> len(d2), d2.peek_top(), d2.peek_bottom()
        (5, 5, 10)

    The first round begins with both players drawing the top card of their decks: `9` and `5`.
    Player 1 has the higher card, so both cards move to the bottom of player 1's deck such that
    `9` is above `5`:

        >>> game = Game(d1, d2)
        >>> game.play(rounds=5, print_progress=True)
        -- Round 1 --
        Player 1's deck: 9, 2, 6, 3, 1
        Player 2's deck: 5, 8, 4, 7, 10
        Player 1 plays: 9
        Player 2 plays: 5
        Player 1 wins the round!
        -- Round 2 --
        Player 1's deck: 2, 6, 3, 1, 9, 5
        Player 2's deck: 8, 4, 7, 10
        Player 1 plays: 2
        Player 2 plays: 8
        Player 2 wins the round!
        -- Round 3 --
        Player 1's deck: 6, 3, 1, 9, 5
        Player 2's deck: 4, 7, 10, 8, 2
        Player 1 plays: 6
        Player 2 plays: 4
        Player 1 wins the round!
        -- Round 4 --
        Player 1's deck: 3, 1, 9, 5, 6, 4
        Player 2's deck: 7, 10, 8, 2
        Player 1 plays: 3
        Player 2 plays: 7
        Player 2 wins the round!
        -- Round 5 --
        Player 1's deck: 1, 9, 5, 6, 4
        Player 2's deck: 10, 8, 2, 7, 3
        Player 1 plays: 1
        Player 2 plays: 10
        Player 2 wins the round!

    ...several more rounds pass...

        >>> game.play(rounds=21, print_progress=False)

    In total, it takes 29 rounds before a player has all of the cards:

        >>> winner = game.play(print_progress=True)
        -- Round 27 --
        Player 1's deck: 5, 4, 1
        Player 2's deck: 8, 9, 7, 3, 2, 10, 6
        Player 1 plays: 5
        Player 2 plays: 8
        Player 2 wins the round!
        -- Round 28 --
        Player 1's deck: 4, 1
        Player 2's deck: 9, 7, 3, 2, 10, 6, 8, 5
        Player 1 plays: 4
        Player 2 plays: 9
        Player 2 wins the round!
        -- Round 29 --
        Player 1's deck: 1
        Player 2's deck: 7, 3, 2, 10, 6, 8, 5, 9, 4
        Player 1 plays: 1
        Player 2 plays: 7
        Player 2 wins the round!
        == Post-game results ==
        Player 1's deck: (empty)
        Player 2's deck: 3, 2, 10, 6, 8, 5, 9, 4, 7, 1
        >>> winner.winning_player
        2
        >>> winner.winning_deck
        Deck([3, 2, 10, 6, 8, 5, 9, 4, 7, 1])

    Once the game ends, you can calculate the winning player's *score*. The bottom card in their
    deck is worth the value of the card multiplied by 1, the second-from-the-bottom card is worth
    the value of the card multiplied by 2, and so on. With 10 cards, the top card is worth the
    value on the card multiplied by 10. In this example, the winning player's score is:

        >>> print(' + '.join(f'{c}*{m}' for c, m in zip(winner.winning_deck, range(10, 0, -1))))
        3*10 + 2*9 + 10*8 + 6*7 + 8*6 + 5*5 + 9*4 + 4*3 + 7*2 + 1*1

    So, once the game ends, the winning player's score is *`306`*.

        >>> winner.final_score
        306

    Play the small crab in a game of Combat using the two decks you just dealt.
    *What is the winning player's score?*

        >>> part_1(d1, d2)
        part 1: player 2 wins with score 306
        306
    """

    victory = Game(deck_1, deck_2).play(print_progress=print_progress)
    result = victory.final_score

    print(f"part 1: player {victory.winning_player} wins with score {result}")
    return result


def part_2(deck_1: 'Deck', deck_2: 'Deck', print_progress: bool = False) -> int:
    """
    *Recursive Combat* still starts by splitting the cards into two decks (you offer to play with
    the same starting decks as before - it's only fair). Then, the game consists of a series of
    *rounds* with a few changes:

        - Before either player deals a card, if there was a previous round in this game that had
          exactly the same cards in the same order in the same players' decks, the *game* instantly
          ends in a win for *player 1*. Previous rounds from other games are not considered. (This
          prevents infinite games of Recursive Combat, which everyone agrees is a bad idea.)
        - Otherwise, this round's cards must be in a new configuration; the players begin the round
          by each drawing the top card of their deck as normal.
        - If both players have at least as many cards remaining in their deck as the value of the
          card they just drew, the winner of the round is determined by playing a new game of
          Recursive Combat (see below).
        - Otherwise, at least one player must not have enough cards left in their deck to recurse;
          the winner of the round is the player with the higher-value card.

    As in regular Combat, the winner of the round (even if they won it by winning a sub-game) takes
    the two cards dealt at the beginning of the round and places them on the bottom of their own
    deck (again so that the winner's card is above the other card). Note that the winner's card
    might be the lower-valued of the two cards if they won the round due to winning a sub-game.
    If collecting cards by winning the round causes a player to have all of the cards, they win,
    and the game ends.

    During a round of Recursive Combat, if both players have at least as many cards in their own
    decks as the number on the card they just dealt, the winner of the round is determined by
    recursing into a sub-game of Recursive Combat. (For example, if player 1 draws the `3` card,
    and player 2 draws the `7` card, this would occur if player 1 has at least 3 cards left and
    player 2 has at least 7 cards left, not counting the `3` and `7` cards that were drawn.)

    To play a sub-game of Recursive Combat, each player creates a new deck by making a *copy* of
    the next cards in their deck (the quantity of cards copied is equal to the number on the card
    they drew to trigger the sub-game). During this sub-game, the game that triggered it is on hold
    and completely unaffected; no cards are removed from players' decks to form the sub-game. (For
    example, if player 1 drew the 3 card, their deck in the sub-game would be copies of the next
    three cards in their deck.)

    Here is a complete example of gameplay, where Game 1 is the primary game of Recursive Combat:

        >>> d1, d2 = Deck([9, 2, 6, 3, 1]), Deck([5, 8, 4, 7, 10])
        >>> game = Game(d1, d2, recursive=True)
        >>> winner = game.play(print_progress=True)
        === Game 1 ===
        -- Round 1 (Game 1) --
        Player 1's deck: 9, 2, 6, 3, 1
        Player 2's deck: 5, 8, 4, 7, 10
        Player 1 plays: 9
        Player 2 plays: 5
        Player 1 wins round 1 of game 1!
        -- Round 2 (Game 1) --
        Player 1's deck: 2, 6, 3, 1, 9, 5
        Player 2's deck: 8, 4, 7, 10
        Player 1 plays: 2
        Player 2 plays: 8
        Player 2 wins round 2 of game 1!
        -- Round 3 (Game 1) --
        Player 1's deck: 6, 3, 1, 9, 5
        Player 2's deck: 4, 7, 10, 8, 2
        Player 1 plays: 6
        Player 2 plays: 4
        Player 1 wins round 3 of game 1!
        -- Round 4 (Game 1) --
        Player 1's deck: 3, 1, 9, 5, 6, 4
        Player 2's deck: 7, 10, 8, 2
        Player 1 plays: 3
        Player 2 plays: 7
        Player 2 wins round 4 of game 1!
        -- Round 5 (Game 1) --
        Player 1's deck: 1, 9, 5, 6, 4
        Player 2's deck: 10, 8, 2, 7, 3
        Player 1 plays: 1
        Player 2 plays: 10
        Player 2 wins round 5 of game 1!
        -- Round 6 (Game 1) --
        Player 1's deck: 9, 5, 6, 4
        Player 2's deck: 8, 2, 7, 3, 10, 1
        Player 1 plays: 9
        Player 2 plays: 8
        Player 1 wins round 6 of game 1!
        -- Round 7 (Game 1) --
        Player 1's deck: 5, 6, 4, 9, 8
        Player 2's deck: 2, 7, 3, 10, 1
        Player 1 plays: 5
        Player 2 plays: 2
        Player 1 wins round 7 of game 1!
        -- Round 8 (Game 1) --
        Player 1's deck: 6, 4, 9, 8, 5, 2
        Player 2's deck: 7, 3, 10, 1
        Player 1 plays: 6
        Player 2 plays: 7
        Player 2 wins round 8 of game 1!
        -- Round 9 (Game 1) --
        Player 1's deck: 4, 9, 8, 5, 2
        Player 2's deck: 3, 10, 1, 7, 6
        Player 1 plays: 4
        Player 2 plays: 3
        Playing a sub-game to determine the winner...
            === Game 2 ===
            -- Round 1 (Game 2) --
            Player 1's deck: 9, 8, 5, 2
            Player 2's deck: 10, 1, 7
            Player 1 plays: 9
            Player 2 plays: 10
            Player 2 wins round 1 of game 2!
            -- Round 2 (Game 2) --
            Player 1's deck: 8, 5, 2
            Player 2's deck: 1, 7, 10, 9
            Player 1 plays: 8
            Player 2 plays: 1
            Player 1 wins round 2 of game 2!
            -- Round 3 (Game 2) --
            Player 1's deck: 5, 2, 8, 1
            Player 2's deck: 7, 10, 9
            Player 1 plays: 5
            Player 2 plays: 7
            Player 2 wins round 3 of game 2!
            -- Round 4 (Game 2) --
            Player 1's deck: 2, 8, 1
            Player 2's deck: 10, 9, 7, 5
            Player 1 plays: 2
            Player 2 plays: 10
            Player 2 wins round 4 of game 2!
            -- Round 5 (Game 2) --
            Player 1's deck: 8, 1
            Player 2's deck: 9, 7, 5, 10, 2
            Player 1 plays: 8
            Player 2 plays: 9
            Player 2 wins round 5 of game 2!
            -- Round 6 (Game 2) --
            Player 1's deck: 1
            Player 2's deck: 7, 5, 10, 2, 9, 8
            Player 1 plays: 1
            Player 2 plays: 7
            Player 2 wins round 6 of game 2!
            The winner of game 2 is player 2!
        ...anyway, back to game 1.
        Player 2 wins round 9 of game 1!
        -- Round 10 (Game 1) --
        Player 1's deck: 9, 8, 5, 2
        Player 2's deck: 10, 1, 7, 6, 3, 4
        Player 1 plays: 9
        Player 2 plays: 10
        Player 2 wins round 10 of game 1!
        -- Round 11 (Game 1) --
        Player 1's deck: 8, 5, 2
        Player 2's deck: 1, 7, 6, 3, 4, 10, 9
        Player 1 plays: 8
        Player 2 plays: 1
        Player 1 wins round 11 of game 1!
        -- Round 12 (Game 1) --
        Player 1's deck: 5, 2, 8, 1
        Player 2's deck: 7, 6, 3, 4, 10, 9
        Player 1 plays: 5
        Player 2 plays: 7
        Player 2 wins round 12 of game 1!
        -- Round 13 (Game 1) --
        Player 1's deck: 2, 8, 1
        Player 2's deck: 6, 3, 4, 10, 9, 7, 5
        Player 1 plays: 2
        Player 2 plays: 6
        Playing a sub-game to determine the winner...
            === Game 3 ===
            -- Round 1 (Game 3) --
            Player 1's deck: 8, 1
            Player 2's deck: 3, 4, 10, 9, 7, 5
            Player 1 plays: 8
            Player 2 plays: 3
            Player 1 wins round 1 of game 3!
            -- Round 2 (Game 3) --
            Player 1's deck: 1, 8, 3
            Player 2's deck: 4, 10, 9, 7, 5
            Player 1 plays: 1
            Player 2 plays: 4
            Playing a sub-game to determine the winner...
                === Game 4 ===
                -- Round 1 (Game 4) --
                Player 1's deck: 8
                Player 2's deck: 10, 9, 7, 5
                Player 1 plays: 8
                Player 2 plays: 10
                Player 2 wins round 1 of game 4!
                The winner of game 4 is player 2!
            ...anyway, back to game 3.
            Player 2 wins round 2 of game 3!
            -- Round 3 (Game 3) --
            Player 1's deck: 8, 3
            Player 2's deck: 10, 9, 7, 5, 4, 1
            Player 1 plays: 8
            Player 2 plays: 10
            Player 2 wins round 3 of game 3!
            -- Round 4 (Game 3) --
            Player 1's deck: 3
            Player 2's deck: 9, 7, 5, 4, 1, 10, 8
            Player 1 plays: 3
            Player 2 plays: 9
            Player 2 wins round 4 of game 3!
            The winner of game 3 is player 2!
        ...anyway, back to game 1.
        Player 2 wins round 13 of game 1!
        -- Round 14 (Game 1) --
        Player 1's deck: 8, 1
        Player 2's deck: 3, 4, 10, 9, 7, 5, 6, 2
        Player 1 plays: 8
        Player 2 plays: 3
        Player 1 wins round 14 of game 1!
        -- Round 15 (Game 1) --
        Player 1's deck: 1, 8, 3
        Player 2's deck: 4, 10, 9, 7, 5, 6, 2
        Player 1 plays: 1
        Player 2 plays: 4
        Playing a sub-game to determine the winner...
            === Game 5 ===
            -- Round 1 (Game 5) --
            Player 1's deck: 8
            Player 2's deck: 10, 9, 7, 5
            Player 1 plays: 8
            Player 2 plays: 10
            Player 2 wins round 1 of game 5!
            The winner of game 5 is player 2!
        ...anyway, back to game 1.
        Player 2 wins round 15 of game 1!
        -- Round 16 (Game 1) --
        Player 1's deck: 8, 3
        Player 2's deck: 10, 9, 7, 5, 6, 2, 4, 1
        Player 1 plays: 8
        Player 2 plays: 10
        Player 2 wins round 16 of game 1!
        -- Round 17 (Game 1) --
        Player 1's deck: 3
        Player 2's deck: 9, 7, 5, 6, 2, 4, 1, 10, 8
        Player 1 plays: 3
        Player 2 plays: 9
        Player 2 wins round 17 of game 1!
        The winner of game 1 is player 2!
        == Post-game results ==
        Player 1's deck: (empty)
        Player 2's deck: 7, 5, 6, 2, 4, 1, 10, 8, 9, 3

    After the game, the winning player's score is calculated from the cards they have in their
    original deck using the same rules as regular Combat. In the above game, the winning player's
    score is *`291`*.

        >>> winner.final_score
        291

    Defend your honor as Raft Captain by playing the small crab in a game of Recursive Combat using
    the same two decks as before. *What is the winning player's score?*

        >>> part_2(d1, d2)
        part 2: player 2 wins with score 291
        291
    """

    victory = Game(deck_1, deck_2, recursive=True).play(print_progress=print_progress)
    result = victory.final_score

    print(f"part 2: player {victory.winning_player} wins with score {result}")
    return result


# TODO: extract to reusable class Chain?
class Deck:
    def __init__(self, cards: Iterable[int]):
        self.top_card, self.bottom_card, self.length = Link.build_chain(cards)

    def __repr__(self):
        cards_repr = ", ".join(str(c) for c in self)
        return f"{type(self).__name__}([{cards_repr}])"

    def __str__(self):
        if self:
            return ", ".join(str(c) for c in self)
        else:
            return "(empty)"

    def state_hash(self) -> int:
        # it would take too long (O(N)) to iterate all values
        # -> instead let's hash only top & bottom value + length
        # and hope it will be enough for infinite loop detection
        if self:
            return hash((self.top_card.value, self.bottom_card.value, self.length))
        else:
            return hash((None, None, 0))

    def _raise_if_empty(self):
        if not self:
            raise IndexError("empty deck")

    def peek_top(self) -> int:
        self._raise_if_empty()
        return self.top_card.value

    def peek_bottom(self) -> int:
        self._raise_if_empty()
        return self.bottom_card.value

    def draw_top(self) -> int:
        self._raise_if_empty()
        drawn_card = self.top_card
        self.top_card = drawn_card.next_link
        if not self.top_card:
            self.bottom_card = None

        drawn_card.disconnect()
        self.length -= 1
        return drawn_card.value

    def extend_bottom(self, values: Iterable[int]):
        for value in values:
            card = Link(value)
            if self.bottom_card:
                card.connect_to(prev_link=self.bottom_card)
            self.bottom_card = card
            if self.top_card is None:
                self.top_card = self.bottom_card
            self.length += 1

    def __bool__(self):
        return self.top_card is not None

    def __iter__(self):
        head = self.top_card
        while head:
            yield head.value
            head = head.next_link

    def __reversed__(self):
        head = self.bottom_card
        while head:
            yield head.value
            head = head.prev_link

    def __getitem__(self, item):
        self._raise_if_empty()

        if isinstance(item, int):
            if item >= 0:
                return self.top_card.follow(item).value
            else:
                return self.bottom_card.follow(item+1).value

        elif isinstance(item, slice):
            start, stop, step = item.indices(self.length)

            def values():
                head = self.top_card.follow(start)
                for _ in range(start, stop, step):
                    yield head.value
                    head = head.follow(step)

            return values()

        else:
            raise TypeError(type(item))

    def __len__(self):
        return self.length


Decks = tuple[Deck, Deck]


def decks_from_file(fn: str) -> Decks:
    return decks_from_lines(relative_path(__file__, fn))


def decks_from_text(text: str) -> Decks:
    return decks_from_lines(text.strip().split("\n"))


def decks_from_lines(lines: Iterable[str]) -> Decks:
    lines_1, lines_2 = line_groups(lines)

    assert lines_1[0] == "Player 1:"
    deck_1 = Deck(int(line) for line in lines_1[1:])

    assert lines_2[0] == "Player 2:"
    deck_2 = Deck(int(line) for line in lines_2[1:])

    return deck_1, deck_2


@dataclass
class Victory:
    deck_1: Deck
    deck_2: Deck

    @property
    def winning_player(self) -> int:
        # if infinite loop was detected, then both decks are non-empty -> player 1 still wins
        return 1 if self.deck_1 else 2

    @property
    def winning_deck(self) -> Deck:
        return self.deck_1 or self.deck_2

    @property
    def final_score(self) -> int:
        return sum(
            (index + 1) * card
            for index, card in enumerate(reversed(self.winning_deck))
        )


# TODO: Game could be refactored to look better

# pylint: disable=too-few-public-methods
class Game:
    def __init__(
            self,
            deck_1: Iterable[int],
            deck_2: Iterable[int],
            recursive: bool = False,
            game_number: int = 1,
            level: int = 0
    ):
        self.deck_1 = Deck(deck_1)
        self.deck_2 = Deck(deck_2)
        self.recursive = recursive
        self.game_number = game_number
        self.level = level
        # states
        self.round_number = 0
        self.victory: Optional[Victory] = None
        self.next_subgame_number = game_number + 1

        # checks
        assert len(self.deck_1) >= 1, (self.game_number, self.deck_1, self.deck_2)
        assert len(self.deck_2) >= 1, (self.game_number, self.deck_1, self.deck_2)

    # pylint: disable=too-many-branches,too-many-statements
    def play(self, rounds: int = None, print_progress: bool = False) -> Optional[Victory]:
        def log(text: str):
            if print_progress:
                print("    " * self.level + text)

        if self.recursive:
            log(f"=== Game {self.game_number} ===")

        remaining_rounds = rounds
        seen_states: set[tuple[int, int]] = set()

        while remaining_rounds != 0 and self.victory is None:
            self.round_number += 1

            # peek top cards
            value_1 = self.deck_1.peek_top()
            value_2 = self.deck_2.peek_top()

            # report current state
            if self.recursive:
                log(f"-- Round {self.round_number} (Game {self.game_number}) --")
            else:
                log(f"-- Round {self.round_number} --")
            log(f"Player 1's deck: {self.deck_1}")
            log(f"Player 2's deck: {self.deck_2}")
            log(f"Player 1 plays: {value_1}")
            log(f"Player 2 plays: {value_2}")

            # decide round winner
            decide_by_subgame = (
                self.recursive
                and (value_1 < len(self.deck_1))
                and (value_2 < len(self.deck_2))
            )
            if decide_by_subgame:
                # ... either by subgame
                subgame = Game(
                    deck_1=self.deck_1[1:value_1+1],
                    deck_2=self.deck_2[1:value_2+1],
                    recursive=True,
                    game_number=self.next_subgame_number,
                    level=self.level + 1
                )
                log("Playing a sub-game to determine the winner...")
                subgame_winner = subgame.play(print_progress=print_progress)

                log(f"...anyway, back to game {self.game_number}.")
                self.next_subgame_number = subgame.next_subgame_number
                round_winner = subgame_winner.winning_player

            else:
                # ... or simply by card values
                if value_1 > value_2:
                    round_winner = 1
                elif value_2 > value_1:
                    round_winner = 2
                else:
                    raise ValueError(f"round is draw: {value_1} == {value_2}")

            # report round winner
            if self.recursive:
                log(f"Player {round_winner} wins round {self.round_number} "
                    f"of game {self.game_number}!")
            else:
                log(f"Player {round_winner} wins the round!")

            # modify decks
            card_1 = self.deck_1.draw_top()
            card_2 = self.deck_2.draw_top()
            if round_winner == 1:
                self.deck_1.extend_bottom([card_1, card_2])
            else:
                self.deck_2.extend_bottom([card_2, card_1])

            # check for victory by gaining all cards
            if not self.deck_1 or not self.deck_2:
                self.victory = Victory(self.deck_1, self.deck_2)

            # check for victory by infinite loop
            state_hashes = (self.deck_1.state_hash(), self.deck_2.state_hash())
            if state_hashes not in seen_states:
                seen_states.add(state_hashes)
            else:
                # infinite loop detected -> player 1 wins
                self.victory = Victory(self.deck_1, self.deck_2)

            # report winner
            if self.victory:
                if self.recursive:
                    log(f"The winner of game {self.game_number} is "
                        f"player {self.victory.winning_player}!")
                if self.level == 0:
                    log("== Post-game results ==")
                    log(f"Player 1's deck: {self.deck_1}")
                    log(f"Player 2's deck: {self.deck_2}")

            # next round ...
            if remaining_rounds is not None:
                remaining_rounds -= 1

        # game finished
        return self.victory


if __name__ == '__main__':
    deck_1_, deck_2_ = decks_from_file("data/22-input.txt")
    assert len(deck_1_) == len(deck_2_) == 25

    part_1(deck_1_, deck_2_)
    part_2(deck_1_, deck_2_)
