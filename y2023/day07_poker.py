"""
Advent of Code 2023
Day 7: Camel Cards
https://adventofcode.com/2023/day/7
"""

from collections import Counter
from enum import Enum
from typing import Iterable

from common.file import relative_path


def part_1(game: 'Game') -> int:
    """
    Your all-expenses-paid trip turns out to be a one-way, five-minute ride in an airship.
    (At least it's a cool airship!) It drops you off at the edge of a vast desert and descends back
    to Island Island.

    "Did you bring the parts?"

    You turn around to see an Elf completely covered in white clothing, wearing goggles, and riding
    a large camel.

    "Did you bring the parts?" she asks again, louder this time. You aren't sure what parts she's
    looking for; you're here to figure out why the sand stopped.

    "The parts! For the sand, yes! Come with me; I will show you." She beckons you onto the camel.

    After riding a bit across the sands of Desert Island, you can see what look like very large
    rocks covering half of the horizon. The Elf explains that the rocks are all along the part of
    Desert Island that is directly above Island Island, making it hard to even get there. Normally,
    they use big machines to move the rocks and filter the sand, but the machines have broken down
    because Desert Island recently stopped receiving the parts they need to fix the machines.

    You've already assumed it'll be your job to figure out why the parts stopped when she asks if
    you can help. You agree automatically.

    Because the journey will take a few days, she offers to teach you the game of **Camel Cards**.
    Camel Cards is sort of similar to poker except it's designed to be easier to play while riding
    a camel.

    In Camel Cards, you get a list of **hands**, and your goal is to order them based on the
    **strength** of each hand. A hand consists of **five cards** labeled one of `A`, `K`, `Q`, `J`,
    `T`, `9`, `8`, `7`, `6`, `5`, `4`, `3`, or `2`. The relative strength of each card follows this
    order, where `A` is the highest and `2` is the lowest.

        >>> ''.join(sorted('3J9A4Q7T2K', key=card_strength))
        '23479TJQKA'

    Every hand is exactly one **type**. From strongest to weakest, they are:

      - **Five of a kind**, where all five cards have the same label:

        >>> HandType.from_hand('AAAAA')
        HandType.FIVE_OF_A_KIND

      - **Four of a kind**, where four cards have the same label and one card has a different label:

        >>> HandType.from_hand('AA8AA')
        HandType.FOUR_OF_A_KIND

      - **Full house**, where three cards have the same label, and the remaining two cards share
        a different label:

        >>> HandType.from_hand('23332')
        HandType.FULL_HOUSE

      - **Three of a kind**, where three cards have the same label, and the remaining two cards are
        each different from any other card in the hand:

        >>> HandType.from_hand('TTT98')
        HandType.THREE_OF_A_KIND

      - **Two pair**, where two cards share one label, two other cards share a second label,
        and the remaining card has a third label:

        >>> HandType.from_hand('23432')
        HandType.TWO_PAIR

      - **One pair**, where two cards share one label, and the other three cards have a different
        label from the pair and each other:

        >>> HandType.from_hand('A23A4')
        HandType.ONE_PAIR

      - **High card**, where all cards' labels are distinct:

        >>> HandType.from_hand('23456')
        HandType.HIGH_CARD

    Hands are primarily ordered based on type; for example, every **full house** is stronger than
    any **three of a kind**.

        >>> HandType.FULL_HOUSE > HandType.THREE_OF_A_KIND
        True

    If two hands have the same type, a second ordering rule takes effect. Start by comparing the
    **first card in each hand**. If these cards are different, the hand with the stronger first card
    is considered stronger. If the first card in each hand have the **same label**, however, then
    move on to considering the **second card in each hand**. If they differ, the hand with the
    higher second card wins; otherwise, continue with the third card in each hand, then the fourth,
    then the fifth.

    So, `33332` and `2AAAA` are both **four of a kind** hands, but 33332 is stronger because its
    first card is stronger.

        >>> HandType.from_hand('33332')
        HandType.FOUR_OF_A_KIND
        >>> HandType.from_hand('2AAAA')
        HandType.FOUR_OF_A_KIND
        >>> hand_strength('33332') > hand_strength('2AAAA')
        True

    Similarly, `77888` and `77788` are both a **full house**, but `77888` is stronger because its
    third card is stronger (and both hands have the same first and second card).

        >>> HandType.from_hand('77888')
        HandType.FULL_HOUSE
        >>> HandType.from_hand('77788')
        HandType.FULL_HOUSE
        >>> hand_strength('77888') > hand_strength('77788')
        True

    To play Camel Cards, you are given a list of hands and their corresponding **bid** (your puzzle
    input). For example:

        >>> game_ = game_from_text('''
        ...     32T3K 765
        ...     T55J5 684
        ...     KK677 28
        ...     KTJJT 220
        ...     QQQJA 483
        ... ''')
        >>> game_
        [('32T3K', 765), ('T55J5', 684), ('KK677', 28), ('KTJJT', 220), ('QQQJA', 483)]

    This example shows five hands; each hand is followed by its **bid** amount. Each hand wins
    an amount equal to its **bid** multiplied by its **rank**, where the weakest hand gets rank 1,
    the second-weakest hand gets rank 2, and so on up to the strongest hand. Because there are five
    hands in this example, the strongest hand will have rank 5 and its bid will be multiplied by 5.

    So, the first step is to put the hands in order of strength:

      - `32T3K` is the only **one pair** and the other hands are all a stronger type,
        so it gets rank **1**.

        >>> hand_strength('32T3K')
        (HandType.ONE_PAIR, 3, 2, 10, 3, 13)

      - `KK677` and `KTJJT` are both **two pair**. Their first cards both have the same label,
        but the second card of `KK677` is stronger (`K` vs `T`), so `KTJJT` gets rank **2**
        and `KK677` gets rank **3**.

        >>> hand_strength('KK677')
        (HandType.TWO_PAIR, 13, 13, 6, 7, 7)
        >>> hand_strength('KTJJT')
        (HandType.TWO_PAIR, 13, 10, 11, 11, 10)

      - `T55J5` and `QQQJA` are both **three of a kind**. `QQQJA` has a stronger first card,
        so it gets rank **5** and `T55J5` gets rank **4**.

        >>> hand_strength('T55J5')
        (HandType.THREE_OF_A_KIND, 10, 5, 5, 11, 5)
        >>> hand_strength('QQQJA')
        (HandType.THREE_OF_A_KIND, 12, 12, 12, 11, 14)

        >>> rank_hands(hand for hand, _ in game_)
        {'32T3K': 1, 'T55J5': 4, 'KK677': 3, 'KTJJT': 2, 'QQQJA': 5}

    Now, you can determine the total winnings of this set of hands by adding up the result of
    multiplying each hand's bid with its rank. So the **total winnings** in this example are
    **`6440`**.

        >>> total_winnings(game_)
        6440

    Find the rank of every hand in your set. **What are the total winnings?**

        >>> part_1(game_)
        part 1: total winnings are 6440
        6440
    """

    result = total_winnings(game)

    print(f"part 1: total winnings are {result}")
    return result


def part_2(game: 'Game') -> int:
    """
    To make things a little more interesting, the Elf introduces one additional rule. Now, `J` cards
    are **jokers** - wildcards that can act like whatever card would make the hand the strongest
    type possible.

    To balance this, **`J` cards are now the weakest** individual cards, weaker even than `2`.
    The other cards stay in the same order:

        >>> ''.join(sorted('365K4T7J28A9Q', key=lambda card: card_strength(card, jokers=True)))
        'J23456789TQKA'

    `J` cards can pretend to be whatever card is best for the purpose of determining hand type;
    for example, `QJJQ2` is now considered four of a kind.

        >>> HandType.from_hand('QJJQ2', jokers=True)
        HandType.FOUR_OF_A_KIND

    However, for the purpose of breaking ties between two hands of the same type, `J` is always
    treated as `J`, not the card it's pretending to be: `JKKK2` is weaker than `QQQQ2` because `J`
    is weaker than `Q`.

        >>> hand_strength('JKKK2', jokers=True) < hand_strength('QQQQ2', jokers=True)
        True

    Now, the above example goes very differently:

        >>> (game_ := game_from_file('data/07-example.txt'))
        [('32T3K', 765), ('T55J5', 684), ('KK677', 28), ('KTJJT', 220), ('QQQJA', 483)]

      - `32T3K` is still the only **one pair**; it doesn't contain any jokers, so its strength
        doesn't increase.

        >>> hand_strength('32T3K', jokers=True)
        (HandType.ONE_PAIR, 3, 2, 10, 3, 13)

      - `KK677` is now the only **two pair**, making it the second-weakest hand.

        >>> hand_strength('KK677', jokers=True)
        (HandType.TWO_PAIR, 13, 13, 6, 7, 7)

      - `T55J5`, `KTJJT`, and `QQQJA` are now all **four of a kind**!

        >>> hand_strength('T55J5', jokers=True)
        (HandType.FOUR_OF_A_KIND, 10, 5, 5, 1, 5)
        >>> hand_strength('KTJJT', jokers=True)
        (HandType.FOUR_OF_A_KIND, 13, 10, 1, 1, 10)
        >>> hand_strength('QQQJA', jokers=True)
        (HandType.FOUR_OF_A_KIND, 12, 12, 12, 1, 14)

        `T55J5` gets rank 3, `QQQJA` gets rank 4, and `KTJJT` gets rank 5.

        >>> rank_hands((hand for hand, _ in game_), jokers=True)
        {'32T3K': 1, 'T55J5': 3, 'KK677': 2, 'KTJJT': 5, 'QQQJA': 4}

    With the new joker rule, the total winnings in this example are **`5905`**:

        >>> total_winnings(game_, jokers=True)
        5905

    Using the new joker rule, find the rank of every hand in your set.
    **What are the new total winnings?**

        >>> part_2(game_)
        part 2: total winnings with the joker rule are 5905
        5905
    """

    result = total_winnings(game, jokers=True)

    print(f"part 2: total winnings with the joker rule are {result}")
    return result


Hand = str


class HandType(Enum):
    FIVE_OF_A_KIND = (5,)
    FOUR_OF_A_KIND = (4, 1)
    FULL_HOUSE = (3, 2)
    THREE_OF_A_KIND = (3, 1, 1)
    TWO_PAIR = (2, 2, 1)
    ONE_PAIR = (2, 1, 1, 1)
    HIGH_CARD = (1, 1, 1, 1, 1)

    @classmethod
    def from_hand(cls, hand: Hand, jokers: bool = False):
        assert len(hand) == 5

        if not jokers:
            counts = tuple(sorted(Counter(hand).values(), reverse=True))
        else:
            # count non-joker cards
            nonjoker_counter = Counter(card for card in hand if card != 'J')
            nonjoker_counts = sorted(nonjoker_counter.values(), reverse=True) or [0]
            # bump the largest count with number of jokers
            jokers_count = 5 - sum(nonjoker_counts)
            nonjoker_counts[0] += jokers_count
            counts = tuple(nonjoker_counts)

        try:
            return next(ht for ht in cls if ht.value == counts)
        except StopIteration:
            # pylint: disable=raise-missing-from
            raise KeyError(counts)

    def __gt__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError

        return self.value > other.value

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


CARD_STRENGTHS = {label: strength for strength, label in enumerate('23456789TJQKA', start=2)}


def card_strength(card: str, jokers: bool = False) -> int:
    assert len(card) == 1
    if jokers and card == 'J':
        return 1
    return CARD_STRENGTHS[card]


def hand_strength(hand: Hand, jokers: bool = False) -> tuple:
    assert len(hand) == 5
    return (HandType.from_hand(hand, jokers),) + tuple(card_strength(card, jokers) for card in hand)


def rank_hands(hands: Iterable[Hand], jokers: bool = False) -> dict[Hand, int]:
    hands_list = list(hands)
    ranks = {
        hand: rank
        for rank, hand in enumerate(
            sorted(hands_list, key=lambda card: hand_strength(card, jokers)),
            start=1
        )
    }
    # reorder the dict to the given order
    return {hand: ranks[hand] for hand in hands_list}


Game = list[tuple[Hand, int]]


def total_winnings(game: Game, jokers: bool = False) -> int:
    ranks = rank_hands((hand for hand, _ in game), jokers)
    return sum(bid * ranks[hand] for hand, bid in game)


def game_from_file(fn: str) -> Game:
    return list(game_from_lines(open(relative_path(__file__, fn))))


def game_from_text(text: str) -> Game:
    return list(game_from_lines(text.strip().splitlines()))


def game_from_lines(lines: Iterable[str]) -> Iterable[tuple[Hand, int]]:
    for line in lines:
        hand, bid = line.strip().split()
        assert len(hand) == 5
        yield hand, int(bid)


def main(input_fn: str = 'data/07-input.txt') -> tuple[int, int]:
    game = game_from_file(input_fn)
    result_1 = part_1(game)
    result_2 = part_2(game)
    return result_1, result_2


if __name__ == '__main__':
    main()
