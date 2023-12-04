"""
Advent of Code 2023
Day 4: Scratchcards
https://adventofcode.com/2023/day/4
"""
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable

from common.file import relative_path
from common.text import parse_line


def part_1(cards: list['Card']) -> int:
    """
    The gondola takes you up. Strangely, though, the ground doesn't seem to be coming with you;
    you're not climbing a mountain. As the circle of Snow Island recedes below you, an entire new
    landmass suddenly appears above you! The gondola carries you to the surface of the new island
    and lurches into the station.

    As you exit the gondola, the first thing you notice is that the air here is much **warmer** than
    it was on Snow Island. It's also quite humid. Is this where the water source is?

    The next thing you notice is an Elf sitting on the floor across the station in what seems to be
    a pile of colorful square cards.

    "Oh! Hello!" The Elf excitedly runs over to you. "How may I be of service?" You ask about water
    sources.

    "I'm not sure; I just operate the gondola lift. That does sound like something we'd have, though
    - this is **Island Island**, after all! I bet the **gardener** would know. He's on a different
    island, though - er, the small kind surrounded by water, not the floating kind. We really need
    to come up with a better naming scheme. Tell you what: if you can help me with something quick,
    I'll let you **borrow my boat** and you can go visit the gardener. I got all these scratchcards
    as a gift, but I can't figure out what I've won."

    The Elf leads you over to the pile of colorful cards. There, you discover dozens of
    scratchcards, all with their opaque covering already scratched off. Picking one up, it looks
    like each card has two lists of numbers separated by a vertical bar (`|`): a list of **winning
    numbers** and then a list of **numbers you have**. You organize the information into a table
    (your puzzle input).

    As far as the Elf has been able to figure out, you have to figure out which of the **numbers
    you have** appear in the list of **winning numbers**. The first match makes the card worth
    **one point** and each match after the first **doubles** the point value of that card.

    For example:

        >>> cards_ = cards_from_text('''
        ...     Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
        ...     Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19
        ...     Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1
        ...     Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83
        ...     Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36
        ...     Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11
        ... ''')
        >>> len(cards_)
        6

    In the above example, card 1 has five winning numbers and eight numbers you have:

        >>> cards_[0]
        Card(no=1, you_have=[41, 48, 83, 86, 17], winning=[83, 86, 6, 31, 17, 9, 48, 53])

    Of the numbers you have, four of them (`48`, `83`, `17`, and `86`) are winning numbers!
    That means card 1 is worth **`8`** points (1 for the first match, then doubled three times for
    each of the three matches after the first).

        >>> cards_[0].point_value()
        8

      - Card 2 has two winning numbers (`32` and `61`), so it is worth **`2`** points.

        >>> cards_[1].point_value()
        2

      - Card 3 has two winning numbers (`1` and `21`), so it is worth **`2`** points.

        >>> cards_[2].point_value()
        2

      - Card 4 has one winning number (`84`), so it is worth **`1`** point.

        >>> cards_[3].point_value()
        1

      - Card 5 has no winning numbers, so it is worth no points.
      - Card 6 has no winning numbers, so it is worth no points.

        >>> cards_[4].point_value(), cards_[5].point_value()
        (0, 0)

    So, in this example, the Elf's pile of scratchcards is worth **`13`** points.

        >>> sum(card.point_value() for card in cards_)
        13

    Take a seat in the large pile of colorful cards. **How many points are they worth in total?**

        >>> part_1(cards_)
        part 1: cards are worth of total 13 points
        13
    """

    result = sum(card.point_value() for card in cards)

    print(f"part 1: cards are worth of total {result} points")
    return result


def part_2(cards: list['Card']) -> int:
    """
    Just as you're about to report your findings to the Elf, one of you realizes that the rules have
    actually been printed on the back of every card this whole time.

    There's no such thing as "points". Instead, scratchcards only cause you to **win more
    scratchcards** equal to the number of winning numbers you have.

    Specifically, you win **copies** of the scratchcards below the winning card equal to the number
    of matches. So, if card 10 were to have 5 matching numbers, you would win one copy each of cards
    11, 12, 13, 14, and 15.

    Copies of scratchcards are scored like normal scratchcards and have the **same card number** as
    the card they copied. So, if you win a copy of card 10, and it has 5 matching numbers, it would
    then win a copy of the same cards that the original card 10 won: cards 11, 12, 13, 14, and 15.
    This process repeats until none of the copies cause you to win any more cards. (Cards will never
    make you copy a card past the end of the table.)

    This time, the above example goes differently:

        >>> cards_ = cards_from_text('''
        ...     Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
        ...     Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19
        ...     Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1
        ...     Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83
        ...     Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36
        ...     Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11
        ... ''')

      - Card 1 has four matching numbers, so you win one copy each of the next four cards:
        cards 2, 3, 4, and 5.

        >>> win_copies(cards_, index=0, copies=1)  # doctest: +ELLIPSIS
        Counter({Card(no=2, ...): 1, Card(no=3, ...): 1, Card(no=4, ...): 1, Card(no=5, ...): 1})

      - Your original card 2 has two matching numbers, so you win one copy each of cards 3 and 4.
      - Your copy of card 2 also wins one copy each of cards 3 and 4.

        >>> win_copies(cards_, index=1, copies=2)  # doctest: +ELLIPSIS
        Counter({Card(no=3, ...): 2, Card(no=4, ...): 2})

      - Your four instances of card 3 (one original and three copies) have two matching numbers,
        so you win **four** copies each of cards 4 and 5.

        >>> win_copies(cards_, index=2, copies=4)  # doctest: +ELLIPSIS
        Counter({Card(no=4, ...): 4, Card(no=5, ...): 4})

      - Your eight instances of card 4 (one original and seven copies) have one matching number,
        so you win **eight** copies of card 5.

        >>> win_copies(cards_, index=3, copies=8)  # doctest: +ELLIPSIS
        Counter({Card(no=5, ...): 8})

      - Your fourteen instances of card 5 (one original and thirteen copies) have no matching
        numbers and win no more cards.

        >>> win_copies(cards_, index=4, copies=14)
        Counter()

      - Your one instance of card 6 (one original) has no matching numbers and wins no more cards.

        >>> win_copies(cards_, index=5, copies=1)
        Counter()

    Once all of the originals and copies have been processed, you end up with **`1`** instance of
    card 1, **`2`** instances of card 2, **`4`** instances of card 3, **`8`** instances of card 4,
    **`14`** instances of card 5, and **`1`** instance of card 6.

        >>> process_cards(cards_)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        Counter({Card(no=5, ...): 14, Card(no=4, ...): 8, Card(no=3, ...): 4,
                 Card(no=2, ...):  2, Card(no=1, ...): 1, Card(no=6, ...): 1})

    In total, this example pile of scratchcards causes you to ultimately have **`30`** scratchcards!

        >>> sum(_.values())
        30

    Process all of the original and copied scratchcards until no more scratchcards are won.
    Including the original set of scratchcards, **how many total scratchcards do you end up with?**

        >>> part_2(cards_)
        part 2: you end up with total 30 cards
        30
    """

    result = sum(process_cards(cards).values())

    print(f"part 2: you end up with total {result} cards")
    return result


@dataclass(frozen=True)
class Card:
    no: int
    you_have: list[int] = field(hash=False)
    winning: list[int] = field(hash=False)

    @classmethod
    def from_line(cls, line: str) -> 'Card':
        # 'Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53'
        no, you_have, winning = parse_line(line.strip(), 'Card $: $ | $')
        return cls(
            no=int(no),
            you_have=[int(v) for v in you_have.strip().split()],
            winning=[int(v) for v in winning.strip().split()],
        )

    def matches_count(self) -> int:
        return len(set(self.you_have) & set(self.winning))

    def point_value(self) -> int:
        matches = self.matches_count()
        return 2 ** (matches - 1) if matches else 0


def win_copies(cards: list[Card], index: int, copies: int) -> Counter[Card]:
    card = cards[index]
    return Counter({
        cards[win_index]: copies
        for win_index in range(index + 1, index + 1 + card.matches_count())
    })


def process_cards(cards: list[Card]) -> Counter[Card]:
    inventory = Counter({card: 1 for card in cards})

    for index, card in enumerate(cards):
        inventory.update(win_copies(cards, index=index, copies=inventory[card]))

    return inventory


def cards_from_file(fn: str) -> list[Card]:
    return list(cards_from_lines(open(relative_path(__file__, fn))))


def cards_from_text(text: str) -> list[Card]:
    return list(cards_from_lines(text.strip().splitlines()))


def cards_from_lines(lines: Iterable[str]) -> Iterable[Card]:
    return (Card.from_line(line) for line in lines)


def main(input_fn: str = 'data/04-input.txt') -> tuple[int, int]:
    cards = cards_from_file(input_fn)
    result_1 = part_1(cards)
    result_2 = part_2(cards)
    return result_1, result_2


if __name__ == '__main__':
    main()
