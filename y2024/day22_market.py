"""
Advent of Code 2024
Day 22: Monkey Market
https://adventofcode.com/2024/day/22
"""

from itertools import islice
from typing import Iterable, Iterator

from tqdm import tqdm

from common.file import relative_path
from common.iteration import first_key_dict, maxk, maybe_next, zip1


def part_1(initial_numbers: Iterable[int]) -> int:
    """
    As you're all teleported deep into the jungle, a monkey (y2022/day11_monkeys.py) steals
    The Historians' device! You'll need get it back while The Historians are looking for the Chief.

    The monkey that stole the device seems willing to trade it, but only in exchange for an absurd
    number of bananas. Your only option is to buy bananas on the Monkey Exchange Market.

    You aren't sure how the Monkey Exchange Market works, but one of The Historians senses trouble
    and comes over to help. Apparently, they've been studying these monkeys for a while and have
    deciphered their secrets.

    Today, the Market is full of monkeys buying **good hiding spots**. Fortunately, because of the
    time you recently spent in this jungle, you know lots of good hiding spots you can sell! If you
    sell enough hiding spots, you should be able to get enough bananas to buy the device back.

    On the Market, the buyers seem to use random prices, but their prices are actually only
    pseudorandom! If you know the secret of how they pick their prices, you can wait for the perfect
    time to sell.

    The part about secrets is literal, the Historian explains. Each buyer produces a pseudorandom
    sequence of secret numbers where each secret is derived from the previous.

    In particular, each buyer's **secret** number evolves into the next secret number in the
    sequence via the following process:

      - Calculate the result of **multiplying the secret number by `64`**.
        Then, **mix** this result into the secret number. Finally, **prune** the secret number.
      - Calculate the result of **dividing the secret number by `32`**.
        Round the result down to the nearest integer.
        Then, **mix** this result into the secret number. Finally, **prune** the secret number.
      - Calculate the result of **multiplying the secret number by `2048`**.
        Then, **mix** this result into the secret number. Finally, **prune** the secret number.

    Each step of the above process involves **mixing** and **pruning**:

      - To **mix** a value into the secret number, calculate the bitwise XOR of the given value and
        the secret number. Then, the secret number becomes the result of that operation.
        (If the secret number is `42` and you were to mix `15` into the secret number, the secret
        number would become `37`).

        >>> 42 ^ 15
        37

      - To **prune** the secret number, calculate the value of the secret number modulo `16777216`.
        Then, the secret number becomes the result of that operation.
        (If the secret number is `100000000` and you were to prune the secret number, the secret
        number would become `16113920`.)

        >>> 2 **24
        16777216
        >>> bin(PRUNE_MASK)
        '0b111111111111111111111111'
        >>> len(_) - 2
        24
        >>> 100000000 & ((1 << 24) - 1)
        16113920

    After this process completes, the buyer is left with the next secret number in the sequence.
    The buyer can repeat this process as many times as necessary to produce more secret numbers.

    So, if a buyer had a secret number of `123`, that buyer's next ten secret numbers would be:

        >>> list(islice(secret_sequence(123), 1, 11))  # doctest: +NORMALIZE_WHITESPACE
        [15887950, 16495136, 527345, 704524, 1553684,
         12683156, 11100544, 12249484, 7753432, 5908254]

    Each buyer uses their own secret number when choosing their price, so it's important to be able
    to predict the sequence of secret numbers for each buyer. Fortunately, the Historian's research
    has uncovered the **initial secret number of each buyer** (your puzzle input). For example:

        >>> example_nums = numbers_from_text('''
        ...     1
        ...     10
        ...     100
        ...     2024
        ... ''')
        >>> example_nums
        [1, 10, 100, 2024]

    This list describes the **initial secret number** of four different secret-hiding-spot-buyers on
    the Monkey Exchange Market. If you can simulate secret numbers from each buyer, you'll be able
    to predict all of their future prices.

    In a single day, buyers each have time to generate `2000` **new** secret numbers. In this
    example, for each buyer, their initial secret number and the 2000th new secret number they would
    generate are:

        >>> {num: next_secret(num, nth=2000) for num in example_nums}
        {1: 8685429, 10: 4700978, 100: 15273692, 2024: 8667524}

    Adding up the 2000th new secret number for each buyer produces **`37327623`**:

        >>> sum(n_2000th for n_2000th in _.values())
        37327623

    For each buyer, simulate the creation of 2000 new secret numbers.
    **What is the sum of the 2000th secret number generated by each buyer?**

        >>> part_1(example_nums)
        part 1: the sum of all the 2000th secret numbers is 37327623
        37327623
    """

    result = sum(next_secret(num, nth=2000) for num in initial_numbers)

    print(f"part 1: the sum of all the 2000th secret numbers is {result}")
    return result


def part_2(initial_numbers: Iterable[int]) -> int:
    """
    Of course, the secret numbers aren't the prices each buyer is offering! That would be
    ridiculous. Instead, the **prices** the buyer offers are just the **ones digit** of each of
    their secret numbers.

    So, if a buyer starts with a secret number of `123`, that buyer's first ten **prices** would be:

        >>> [num % 10 for num in islice(secret_sequence(123), 10)]
        [3, 0, 6, 5, 4, 4, 6, 4, 4, 2]

    This price is the number of **bananas** that buyer is offering in exchange for your information
    about a new hiding spot. However, you still don't speak monkey (y2022/day21_math_tree.py),
    so you can't negotiate with the buyers directly. The Historian speaks a little, but not enough
    to negotiate; instead, he can ask another monkey to negotiate on your behalf.

    Unfortunately, the monkey only knows how to decide when to sell by looking at the **changes** in
    price. Specifically, the monkey will only look for a specific sequence of **four consecutive
    changes** in price, then immediately sell when it sees that sequence.

    So, if a buyer starts with a secret number of `123`, that buyer's first ten secret numbers,
    prices, and the associated changes would be:

        >>> print_market(initial_secret=123, length=10)
             123: 3
        15887950: 0 (-3)
        16495136: 6 (+6)
          527345: 5 (-1)
          704524: 4 (-1)
         1553684: 4 (+0)
        12683156: 6 (+2)
        11100544: 4 (-2)
        12249484: 4 (+0)
         7753432: 2 (-2)

    Note that the first price has no associated change because there was no previous price to
    compare it with.

    In this short example, within just these first few prices, the highest price will be `6`, so it
    would be nice to give the monkey instructions that would make it sell at that time. The first
    `6` occurs after only two changes, so there's no way to instruct the monkey to sell then, but
    the second `6` occurs after the changes `-1,-1,0,2`. So, if you gave the monkey that sequence of
    changes, it would wait until the first time it sees that sequence and then immediately sell your
    hiding spot information at the current price, winning you `6` bananas.

        >>> profit(initial_secret=123, target_sequence=[-1, -1, 0, 2])
        6

    Each buyer only wants to buy one hiding spot, so after the hiding spot is sold, the monkey will
    move on to the next buyer. If the monkey never hears that sequence of price changes from
    a buyer, the monkey will **never** sell, and will instead just move on to the next buyer.

    Worse, you can only give the monkey **a single sequence** of four price changes to look for. You
    can't change the sequence between buyers.

    You're going to need as many bananas as possible, so you'll need to **determine which sequence**
    of four price changes will cause the monkey to get you the **most bananas overall**. Each buyer
    is going to generate `2000` secret numbers after their initial secret number, so, for each
    buyer, you'll have **`2000` price changes** in which your sequence can occur.

    Suppose the initial secret number of each buyer is:

        >>> example_nums = numbers_from_file('data/22-example.txt')
        >>> example_nums
        [1, 2, 3, 2024]

    There are many sequences of four price changes you could tell the monkey, but for these four
    buyers, the sequence that will get you the most bananas is `-2,1,-1,3`. Using that sequence,
    the monkey will make the following sales:

        >>> [profit(initial_secret=num, target_sequence=[-2, 1, -1, 3]) for num in example_nums]
        [7, 7, None, 9]

    So, by asking the monkey to sell the first time each buyer's prices go down `2`, then up `1`,
    then down `1`, then up `3`, you would get **`23`** (`7 + 7 + 9`) bananas!

        >>> sum(b or 0 for b in _)
        23

    Figure out the best sequence to tell the monkey so that by looking for that same sequence of
    changes in every buyer's future prices, you get the most bananas in total.
    **What is the most bananas you can get?**

        >>> part_2(example_nums)
        part 2: by using the sell sequence (-2, 1, -1, 3) you can get 23 bananas
        23
    """

    max_seq, result = max_profit(initial_numbers)

    print(f"part 2: by using the sell sequence {max_seq} you can get {result} bananas")
    return result


PRUNE_MASK = (1 << 24) - 1


def secret_sequence(initial_num: int) -> Iterator[int]:
    num = initial_num
    while True:
        yield num
        num = next_secret(num)


def next_secret(num: int, nth: int = 1) -> int:
    for _ in range(nth):
        num = (num ^ (num << 6)) & PRUNE_MASK
        num = (num ^ (num >> 5)) & PRUNE_MASK
        num = (num ^ (num << 11)) & PRUNE_MASK

    return num


def price_change_sequences(
    initial_secret: int,
    sequence_length: int = 4,
    changes_count: int = 2000,
) -> Iterable[tuple[list[int], int]]:  # seq, profit
    prices = (num % 10 for num in secret_sequence(initial_secret))
    changes_buff: list[int] = []
    for prev_price, current_price in islice(zip1(prices), changes_count):
        changes_buff.append(current_price - prev_price)
        if len(changes_buff) >= sequence_length:
            yield changes_buff[-sequence_length:], current_price


def profit(
    initial_secret: int,
    target_sequence: list[int],
    changes_count: int = 2000,
) -> int | None:
    return maybe_next(
        price
        for seq, price in price_change_sequences(
            initial_secret=initial_secret,
            sequence_length=len(target_sequence),
            changes_count=changes_count,
        )
        if seq == target_sequence
    )


def max_profit(
    initial_secrets: Iterable[int],
    changes_count: int = 2000,
) -> tuple[tuple[int, ...], int]:
    # build dict of seq -> profit for each buyer:
    stp_dicts = [
        first_key_dict(
            (tuple(seq), price)
            for seq, price in price_change_sequences(secret, changes_count=changes_count)
        )
        for secret in tqdm(initial_secrets, desc="building stpds", delay=1.0)
    ]

    # consider each 4-item sequence
    all_sequences = {seq for stpd in stp_dicts for seq in stpd}
    # and return the best one
    return maxk(
        tqdm(all_sequences, desc="finding max profit", unit=" seqs", delay=1.0),
        key=lambda seq: sum(stpd.get(seq, 0) for stpd in stp_dicts)
    )


def print_market(initial_secret: int, length: int) -> None:
    # only used in doctests
    num = initial_secret
    price = 0
    for tick in range(length):
        price_change = num % 10 - price
        price = num % 10

        message = f"{num:8}: {price}"
        if tick > 0:
            message += f" ({price_change:+})"
        print(message)

        num = next_secret(num)


def numbers_from_file(fn: str) -> list[int]:
    return list(numbers_from_lines(open(relative_path(__file__, fn))))


def numbers_from_text(text: str) -> list[int]:
    return list(numbers_from_lines(text.strip().splitlines()))


def numbers_from_lines(lines: Iterable[str]) -> Iterable[int]:
    return (int(line) for line in lines)


def main(input_fn: str = 'data/22-input.txt') -> tuple[int, int]:
    numbers = numbers_from_file(input_fn)
    result_1 = part_1(numbers)
    result_2 = part_2(numbers)
    return result_1, result_2


if __name__ == '__main__':
    main()
